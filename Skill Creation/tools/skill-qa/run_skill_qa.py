#!/usr/bin/env python3
"""Run Skill QA checks and produce JSON/Markdown reports.

Phase 1: static SKILL.md validation.
Phase 2: scenario metrics, baseline deltas, scripted command checks.
Hardening: strict mode, input schemas, safer scripted execution.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
WORKFLOW_HINTS_RE = re.compile(r'\b(step\s*\d+|first|then|after that|workflow|run\s+[`"]?\w)', re.IGNORECASE)
THIRD_PERSON_RE = re.compile(r"\b(i\s+can|you\s+can|we\s+can|let's)\b", re.IGNORECASE)
TOKEN_RE = re.compile(r"[a-zA-Z0-9а-яА-ЯёЁ]+", re.UNICODE)


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse YAML configuration using PyYAML."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse config {path}: {exc}") from exc
    except FileNotFoundError:
        return {}


def parse_skill_md(skill_md: Path) -> tuple[dict[str, Any], str, str | None]:
    """Parse SKILL.md frontmatter and body. Returns (frontmatter, body, error)."""
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text, "Missing YAML frontmatter opening delimiter '---'"

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, text, "Missing YAML frontmatter closing delimiter '---'"

    frontmatter_text = "\n".join(lines[1:end_idx])
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            frontmatter = {}
    except yaml.YAMLError as exc:
        return {}, text, f"Invalid YAML frontmatter: {exc}"

    body = "\n".join(lines[end_idx + 1 :])
    return frontmatter, body, None


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def to_token_set(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text)}


def load_json_safe(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"File not found: {path}"
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in {path}: {exc}"


def run_skills_ref_validate(skill_dir: Path, strict: bool, require_skills_ref: bool) -> tuple[bool, str]:
    binary = shutil.which("skills-ref")
    if not binary:
        if require_skills_ref or strict:
            return False, "skills-ref not installed and strict mode requires it"
        return True, "skills-ref not installed; external validation skipped"

    proc = subprocess.run(
        [binary, "validate", str(skill_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    ok = proc.returncode == 0
    return ok, (proc.stdout.strip() or "skills-ref validate produced no output")


def predict_trigger(prompt: str, name: str, description: str, keywords: list[str], min_overlap_tokens: int) -> bool:
    prompt_tokens = to_token_set(prompt)

    if keywords:
        key_tokens: set[str] = set()
        for kw in keywords:
            key_tokens |= to_token_set(str(kw))
    else:
        key_tokens = to_token_set(f"{name} {description}")

    overlap = prompt_tokens & key_tokens
    return len(overlap) >= max(1, min_overlap_tokens)


def validate_scenarios_schema(data: Any) -> tuple[bool, str]:
    if not isinstance(data, list) or not data:
        return False, "must be a non-empty JSON array"
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            return False, f"item {i} must be an object"
        if "prompt" not in item or not isinstance(item.get("prompt"), str):
            return False, f"item {i} requires string field 'prompt'"
        if "relevant" not in item or not isinstance(item.get("relevant"), bool):
            return False, f"item {i} requires boolean field 'relevant'"
        if "keywords" in item and not isinstance(item.get("keywords"), list):
            return False, f"item {i} field 'keywords' must be an array"
    return True, "ok"


def evaluate_scenarios(
    scenarios_path: Path,
    name: str,
    description: str,
    gates: dict[str, Any],
    checks: list[CheckResult],
    metrics: dict[str, Any],
) -> None:
    data, err = load_json_safe(scenarios_path)
    if err:
        checks.append(CheckResult("scenario_file_valid", False, err))
        return

    schema_ok, schema_msg = validate_scenarios_schema(data)
    if not schema_ok:
        checks.append(CheckResult("scenario_file_valid", False, schema_msg))
        return

    scenarios: list[dict[str, Any]] = data
    total_relevant = 0
    total_irrelevant = 0
    true_positive = 0
    false_positive = 0
    min_overlap_tokens = int(gates.get("min_overlap_tokens", 1))

    for i, sc in enumerate(scenarios, start=1):
        prompt = sc["prompt"]
        relevant = sc["relevant"]
        keywords = sc.get("keywords", [])

        pred = predict_trigger(prompt, name, description, keywords, min_overlap_tokens=min_overlap_tokens)
        if relevant:
            total_relevant += 1
            if pred:
                true_positive += 1
        else:
            total_irrelevant += 1
            if pred:
                false_positive += 1

        if not prompt.strip():
            checks.append(CheckResult(f"scenario_{i}_prompt", False, "prompt is empty"))

    trigger_rate = (true_positive / total_relevant) if total_relevant else 1.0
    false_trigger_rate = (false_positive / total_irrelevant) if total_irrelevant else 0.0

    metrics["scenario_count"] = len(scenarios)
    metrics["scenario_relevant_count"] = total_relevant
    metrics["scenario_irrelevant_count"] = total_irrelevant
    metrics["trigger_rate"] = round(trigger_rate, 4)
    metrics["false_trigger_rate"] = round(false_trigger_rate, 4)

    min_trigger_rate = float(gates.get("min_trigger_rate", 0.80))
    max_false_trigger_rate = float(gates.get("max_false_trigger_rate", 0.10))

    checks.append(CheckResult("trigger_rate_gate", trigger_rate >= min_trigger_rate, f"trigger_rate={trigger_rate:.3f} >= {min_trigger_rate:.3f}"))
    checks.append(
        CheckResult(
            "false_trigger_rate_gate",
            false_trigger_rate <= max_false_trigger_rate,
            f"false_trigger_rate={false_trigger_rate:.3f} <= {max_false_trigger_rate:.3f}",
        )
    )


def validate_baseline_schema(data: Any) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "baseline file must be an object"
    rows = data.get("results")
    if not isinstance(rows, list) or not rows:
        return False, "baseline.results must be a non-empty array"
    for i, item in enumerate(rows, start=1):
        if not isinstance(item, dict):
            return False, f"results[{i}] must be an object"
        required = {"id": str, "success": bool, "tokens": (int, float), "tool_calls": (int, float)}
        for field, typ in required.items():
            if field not in item:
                return False, f"results[{i}] missing field '{field}'"
            if not isinstance(item[field], typ):
                return False, f"results[{i}].{field} has invalid type"
    return True, "ok"


def aggregate_baseline(path: Path) -> tuple[dict[str, dict[str, float]], str | None]:
    data, err = load_json_safe(path)
    if err:
        return {}, err

    schema_ok, schema_msg = validate_baseline_schema(data)
    if not schema_ok:
        return {}, schema_msg

    rows = data.get("results", [])
    out: dict[str, dict[str, float]] = {}
    for item in rows:
        sid = str(item.get("id", "")).strip()
        if not sid:
            continue
        out[sid] = {
            "success": 1.0 if bool(item.get("success", False)) else 0.0,
            "tokens": float(item.get("tokens", 0.0)),
            "tool_calls": float(item.get("tool_calls", 0.0)),
        }
    return out, None


def evaluate_baseline_delta(
    without_path: Path,
    with_path: Path,
    gates: dict[str, Any],
    checks: list[CheckResult],
    metrics: dict[str, Any],
) -> None:
    without, without_err = aggregate_baseline(without_path)
    with_skill, with_err = aggregate_baseline(with_path)
    if without_err:
        checks.append(CheckResult("baseline_without_skill_valid", False, without_err))
        return
    if with_err:
        checks.append(CheckResult("baseline_with_skill_valid", False, with_err))
        return

    ids = sorted(set(without) & set(with_skill))
    if not ids:
        checks.append(CheckResult("baseline_delta_inputs", False, "no shared scenario ids between baseline files"))
        return

    success_without = sum(without[i]["success"] for i in ids) / len(ids)
    success_with = sum(with_skill[i]["success"] for i in ids) / len(ids)
    token_without = sum(without[i]["tokens"] for i in ids) / len(ids)
    token_with = sum(with_skill[i]["tokens"] for i in ids) / len(ids)
    tool_without = sum(without[i]["tool_calls"] for i in ids) / len(ids)
    tool_with = sum(with_skill[i]["tool_calls"] for i in ids) / len(ids)

    success_delta = success_with - success_without
    token_delta = token_with - token_without
    tool_calls_delta = tool_with - tool_without

    metrics["baseline_shared_scenarios"] = len(ids)
    metrics["success_without_skill"] = round(success_without, 4)
    metrics["success_with_skill"] = round(success_with, 4)
    metrics["success_delta"] = round(success_delta, 4)
    metrics["token_delta"] = round(token_delta, 2)
    metrics["tool_calls_delta"] = round(tool_calls_delta, 2)

    min_success_delta = float(gates.get("min_success_delta", 0.0))
    max_token_delta = float(gates.get("max_token_delta", 300.0))

    checks.append(CheckResult("success_delta_gate", success_delta >= min_success_delta, f"success_delta={success_delta:.3f} >= {min_success_delta:.3f}"))
    checks.append(CheckResult("token_delta_gate", token_delta <= max_token_delta, f"token_delta={token_delta:.2f} <= {max_token_delta:.2f}"))


def validate_scripted_checks_schema(data: Any) -> tuple[bool, str]:
    if not isinstance(data, list) or not data:
        return False, "must be a non-empty JSON array"
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            return False, f"item {i} must be an object"
        if "cmd" not in item or not isinstance(item.get("cmd"), str):
            return False, f"item {i} requires string field 'cmd'"
        if "expect_exit" in item and not isinstance(item.get("expect_exit"), int):
            return False, f"item {i} field 'expect_exit' must be int"
    return True, "ok"


def command_is_allowed(cmd: str, allow_prefixes: list[str]) -> bool:
    if not allow_prefixes:
        return True
    clean = cmd.strip()
    return any(clean.startswith(prefix) for prefix in allow_prefixes)


def evaluate_scripted_checks(
    scripted_checks_path: Path,
    checks: list[CheckResult],
    metrics: dict[str, Any],
    timeout_seconds: int,
    max_output_chars: int,
    allow_command_prefixes: list[str],
    strict: bool,
) -> None:
    data, err = load_json_safe(scripted_checks_path)
    if err:
        checks.append(CheckResult("scripted_checks_file_valid", False, err))
        return

    schema_ok, schema_msg = validate_scripted_checks_schema(data)
    if not schema_ok:
        checks.append(CheckResult("scripted_checks_file_valid", False, schema_msg))
        return

    scripted: list[dict[str, Any]] = data
    passed = 0

    for i, item in enumerate(scripted, start=1):
        name = str(item.get("name", f"scripted_{i}"))
        cmd = str(item.get("cmd", "")).strip()
        expect_exit = int(item.get("expect_exit", 0))

        if not command_is_allowed(cmd, allow_command_prefixes):
            ok = False if strict else True
            checks.append(
                CheckResult(
                    f"scripted_{name}",
                    ok,
                    f"command not allowed by allowlist: '{cmd}'",
                )
            )
            if ok:
                passed += 1
            continue

        try:
            proc = subprocess.run(
                ["bash", "-lc", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
            output_preview = (proc.stdout or "").strip().replace("\n", " ")[:max_output_chars]
            ok = proc.returncode == expect_exit
            if ok:
                passed += 1
            checks.append(
                CheckResult(
                    f"scripted_{name}",
                    ok,
                    f"exit={proc.returncode}, expected={expect_exit}, output='{output_preview}'",
                )
            )
        except subprocess.TimeoutExpired:
            checks.append(CheckResult(f"scripted_{name}", False, f"timed out after {timeout_seconds}s"))

    metrics["scripted_checks_total"] = len(scripted)
    metrics["scripted_checks_passed"] = passed


def evaluate(
    skill_dir: Path,
    config: dict[str, Any],
    scenarios_path: Path | None,
    baseline_without: Path | None,
    baseline_with: Path | None,
    scripted_checks: Path | None,
    strict: bool,
    require_skills_ref: bool,
    simple_workflow: bool,
    timeout_seconds: int,
    max_output_chars: int,
) -> tuple[list[CheckResult], dict[str, Any]]:
    limits = config.get("limits", {})
    checks_cfg = config.get("checks", {})
    gates = config.get("gates", {})

    skill_md = skill_dir / "SKILL.md"
    results: list[CheckResult] = []
    metrics: dict[str, Any] = {
        "skill": skill_dir.name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    if not skill_md.exists():
        results.append(CheckResult("skill_md_exists", False, "SKILL.md not found"))
        return results, metrics

    frontmatter, body, parse_error = parse_skill_md(skill_md)
    if parse_error:
        results.append(CheckResult("frontmatter_parse", False, parse_error))

    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()

    body_lines = body.splitlines()
    body_words = word_count(body)
    metrics["body_lines"] = len(body_lines)
    metrics["body_words"] = body_words

    if checks_cfg.get("require_name_matches_directory", True):
        ok = name == skill_dir.name
        results.append(CheckResult("name_matches_directory", ok, f"name='{name}', directory='{skill_dir.name}'"))

    results.append(CheckResult("name_format", bool(NAME_RE.match(name)), "must be kebab-case, <=64 chars"))
    results.append(CheckResult("description_length", 1 <= len(description) <= 1024, f"length={len(description)}"))

    if checks_cfg.get("require_third_person_description", True):
        third_person_ok = not THIRD_PERSON_RE.search(description)
        results.append(CheckResult("description_third_person", third_person_ok, "should avoid first/second-person forms"))

    if checks_cfg.get("forbid_workflow_steps_in_description", True):
        no_workflow_steps = not WORKFLOW_HINTS_RE.search(description)
        results.append(CheckResult("description_no_workflow_steps", no_workflow_steps, "description should explain WHAT/WHEN, not HOW"))

    max_lines = int(limits.get("max_skill_lines", 500))
    results.append(CheckResult("body_line_limit", len(body_lines) <= max_lines, f"lines={len(body_lines)} <= {max_lines}"))

    max_complex_words = int(limits.get("max_complex_words", 500))
    results.append(CheckResult("body_word_limit_complex", body_words <= max_complex_words, f"words={body_words} <= {max_complex_words}"))

    if simple_workflow:
        max_simple_words = int(limits.get("max_simple_words", 150))
        results.append(CheckResult("body_word_limit_simple", body_words <= max_simple_words, f"words={body_words} <= {max_simple_words}"))

    ext_ok, ext_details = run_skills_ref_validate(skill_dir, strict=strict, require_skills_ref=require_skills_ref)
    results.append(CheckResult("skills_ref_validate", ext_ok, ext_details))

    if (baseline_without and not baseline_with) or (baseline_with and not baseline_without):
        results.append(
            CheckResult(
                "baseline_inputs_pair",
                False,
                "both --baseline-without-skill and --baseline-with-skill are required together",
            )
        )

    if scenarios_path:
        evaluate_scenarios(scenarios_path, name, description, gates, results, metrics)

    if baseline_without and baseline_with:
        evaluate_baseline_delta(baseline_without, baseline_with, gates, results, metrics)

    if scripted_checks:
        allow_prefixes = [str(p) for p in config.get("scripted", {}).get("allow_command_prefixes", [])]
        evaluate_scripted_checks(
            scripted_checks,
            results,
            metrics,
            timeout_seconds=timeout_seconds,
            max_output_chars=max_output_chars,
            allow_command_prefixes=allow_prefixes,
            strict=strict,
        )

    passed = all(r.passed for r in results)
    metrics["checks_total"] = len(results)
    metrics["checks_passed"] = sum(1 for r in results if r.passed)
    metrics["qa_passed"] = passed
    metrics["strict_mode"] = strict
    return results, metrics


def write_reports(root_dir: Path, skill_name: str, checks: list[CheckResult], metrics: dict[str, Any]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_dir = root_dir / "reports" / skill_name / stamp
    report_dir.mkdir(parents=True, exist_ok=True)

    (report_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Skill QA report — {skill_name}",
        "",
        f"- Timestamp (UTC): {metrics.get('timestamp_utc')}",
        f"- Result: {'PASS' if metrics.get('qa_passed') else 'FAIL'}",
        f"- Checks: {metrics.get('checks_passed')}/{metrics.get('checks_total')}",
        f"- Strict mode: {metrics.get('strict_mode')}",
        f"- Body size: {metrics.get('body_lines')} lines, {metrics.get('body_words')} words",
    ]

    for metric_name in ["trigger_rate", "false_trigger_rate", "success_delta", "token_delta", "tool_calls_delta"]:
        if metric_name in metrics:
            lines.append(f"- {metric_name}: {metrics.get(metric_name)}")

    lines.extend(["", "## Checks"])
    for check in checks:
        icon = "✅" if check.passed else "❌"
        lines.append(f"- {icon} **{check.name}** — {check.details}")

    (report_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skill QA checks and generate reports.")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory containing SKILL.md")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.yaml"), help="Path to QA config file")
    parser.add_argument("--scenarios", type=Path, help="JSON file with scenario prompts and relevance labels")
    parser.add_argument("--baseline-without-skill", type=Path, help="JSON file with baseline results without skill")
    parser.add_argument("--baseline-with-skill", type=Path, help="JSON file with baseline results with skill")
    parser.add_argument("--scripted-checks", type=Path, help="JSON file with scripted command checks")
    parser.add_argument("--strict", action="store_true", help="Fail on skipped external checks and unsafe scripted commands")
    parser.add_argument("--require-skills-ref", action="store_true", help="Require skills-ref binary to be present")
    parser.add_argument("--simple-workflow", action="store_true", help="Also enforce max_simple_words from config")
    parser.add_argument("--script-timeout-seconds", type=int, default=30, help="Timeout per scripted check command")
    parser.add_argument("--script-max-output-chars", type=int, default=200, help="Max scripted command output chars in report")
    args = parser.parse_args()

    try:
        config = parse_simple_yaml(args.config)
    except ValueError as exc:
        print(f"Skill QA Fatal Error: {exc}")
        return 1
    checks, metrics = evaluate(
        skill_dir=args.skill_dir.resolve(),
        config=config,
        scenarios_path=args.scenarios.resolve() if args.scenarios else None,
        baseline_without=args.baseline_without_skill.resolve() if args.baseline_without_skill else None,
        baseline_with=args.baseline_with_skill.resolve() if args.baseline_with_skill else None,
        scripted_checks=args.scripted_checks.resolve() if args.scripted_checks else None,
        strict=args.strict,
        require_skills_ref=args.require_skills_ref,
        simple_workflow=args.simple_workflow,
        timeout_seconds=args.script_timeout_seconds,
        max_output_chars=args.script_max_output_chars,
    )

    reports_root = Path(__file__).resolve().parents[2]
    report_dir = write_reports(reports_root, args.skill_dir.name, checks, metrics)

    print(f"Skill QA result: {'PASS' if metrics.get('qa_passed') else 'FAIL'}")
    print(f"Report directory: {report_dir}")
    return 0 if metrics.get("qa_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
