#!/usr/bin/env python3
"""Validate research-loop campaign structure, frontmatter, and lifecycle semantics.

Usage:
  python scripts/validate_campaign.py modules/research-loop/campaigns
  python scripts/validate_campaign.py modules/research-loop/campaigns --check-urls
"""

from __future__ import annotations

import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

REQUIRED_FILES = [
    "plan.md",
    "sources.md",
    "reviews.md",
    "proposal.md",
    "experiment.md",
    "decision.md",
]

STATUS_ENUM = {
    "plan.md": {"planned", "in_progress", "completed", "blocked"},
    "sources.md": {"draft", "in_progress", "completed"},
    "reviews.md": {"draft", "in_progress", "completed"},
    "proposal.md": {"draft", "in_review", "approved", "rejected"},
    "experiment.md": {"not_started", "running", "completed", "rolled_back"},
    "decision.md": {"open", "closed"},
}

OUTCOME_ENUM = {"pending", "accepted", "rejected", "inconclusive", "needs-more-testing"}

REQUIRED_FIELDS = {
    "plan.md": {"id", "status", "target_module", "created_at", "updated_at"},
    "sources.md": {"id", "status", "target_module", "updated_at"},
    "reviews.md": {"id", "status", "target_module", "updated_at"},
    "proposal.md": {"id", "status", "target_module", "updated_at"},
    "experiment.md": {"id", "status", "target_module", "updated_at"},
    "decision.md": {
        "id",
        "status",
        "outcome",
        "target_module",
        "updated_at",
        "proposal_ref",
        "experiment_ref",
    },
}

DATE_TOPIC = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
DATE_VALUE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCALAR_LINE = re.compile(r"^[A-Za-z0-9_-]+:\s*.*$")
SOURCE_ROW = re.compile(r"^\|\s*S\d+\s*\|", re.MULTILINE)
# Extracts markdown URLs: [text](url)
# Updated regex to handle optional titles in markdown links correctly, e.g. [text](url "title")
MD_URL = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)[^)]*\)")


def split_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter start")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter end")

    raw_fm = text[4:end]
    body = text[end + 5:]

    data: dict[str, str] = {}
    for idx, line in enumerate(raw_fm.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line.startswith(" ") or line.startswith("\t"):
            raise ValueError(
                f"frontmatter line {idx}: nested YAML is not supported, use scalar 'key: value'"
            )
        if not SCALAR_LINE.match(line):
            raise ValueError(
                f"frontmatter line {idx}: invalid format, expected scalar 'key: value'"
            )

        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    return data, body


def is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def check_url(url: str, timeout: int = 8) -> tuple[bool, str]:
    """Return (ok, reason). Uses HEAD, falls back to GET on 405."""
    headers = {"User-Agent": "research-loop-validator/1.0"}
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return True, str(resp.status)
        except urllib.error.HTTPError as e:
            if e.code == 405 and method == "HEAD":
                continue  # retry with GET
            return False, f"HTTP {e.code}"
        except urllib.error.URLError as e:
            return False, str(e.reason)
        except Exception as e:
            return False, str(e)
    return False, "HEAD and GET both failed"


def validate_urls(sources_path: Path) -> list[str]:
    """Extract and check all markdown URLs from sources.md."""
    errors: list[str] = []
    text = sources_path.read_text(encoding="utf-8")
    urls = MD_URL.findall(text)  # list of (title, url)

    if not urls:
        return errors

    print(f"  Checking {len(urls)} URL(s) in {sources_path.name}...")
    for title, url in urls:
        ok, reason = check_url(url)
        status = "OK" if ok else f"FAIL ({reason})"
        print(f"    [{status}] {title}: {url}")
        if not ok:
            errors.append(
                f"{sources_path}: broken URL '{url}' (title: '{title}', reason: {reason})"
            )

    return errors


def validate_campaign(campaign_dir: Path, check_urls: bool = False) -> list[str]:
    errors: list[str] = []
    content: dict[str, tuple[dict[str, str], str]] = {}

    if not DATE_TOPIC.match(campaign_dir.name):
        errors.append(f"{campaign_dir}: invalid name format, expected YYYY-MM-DD-topic")

    for filename in REQUIRED_FILES:
        file_path = campaign_dir / filename
        if not file_path.exists():
            errors.append(f"{campaign_dir}: missing {filename}")
            continue

        try:
            fm, body = split_frontmatter(file_path)
        except ValueError as exc:
            errors.append(f"{file_path}: {exc}")
            continue

        content[filename] = (fm, body)

        for field in REQUIRED_FIELDS[filename]:
            if field not in fm:
                errors.append(f"{file_path}: missing frontmatter field '{field}'")

        status = fm.get("status")
        if status and status not in STATUS_ENUM[filename]:
            errors.append(
                f"{file_path}: invalid status '{status}', allowed={sorted(STATUS_ENUM[filename])}"
            )

        if filename == "decision.md":
            outcome = fm.get("outcome")
            if outcome and outcome not in OUTCOME_ENUM:
                errors.append(
                    f"{file_path}: invalid outcome '{outcome}', allowed={sorted(OUTCOME_ENUM)}"
                )

        for date_field in ("created_at", "updated_at"):
            if date_field in fm and not DATE_VALUE.match(fm[date_field]):
                errors.append(
                    f"{file_path}: invalid {date_field} '{fm[date_field]}', expected YYYY-MM-DD"
                )

    artifacts = campaign_dir / "artifacts"
    if not artifacts.exists() or not artifacts.is_dir():
        errors.append(f"{campaign_dir}: missing artifacts/ directory")

    decision_data = content.get("decision.md")
    decision_fm = decision_data[0] if decision_data else {}
    
    experiment_data = content.get("experiment.md")
    experiment_fm = experiment_data[0] if experiment_data else {}
    experiment_body = experiment_data[1] if experiment_data else ""
    
    sources_data = content.get("sources.md")
    sources_body = sources_data[1] if sources_data else ""

    if decision_fm:
        if decision_fm.get("status") == "closed" and decision_fm.get("outcome") == "pending":
            errors.append(
                f"{campaign_dir / 'decision.md'}: closed decision cannot have outcome 'pending'"
            )

        outcome = decision_fm.get("outcome")
        if outcome == "accepted" and is_blank(decision_fm.get("promotion_ref")):
            errors.append(
                f"{campaign_dir / 'decision.md'}: outcome=accepted requires non-empty 'promotion_ref'"
            )
        if outcome == "rejected" and is_blank(decision_fm.get("rejection_ref")):
            errors.append(
                f"{campaign_dir / 'decision.md'}: outcome=rejected requires non-empty 'rejection_ref'"
            )

        if decision_fm.get("status") == "closed":
            if re.search(r"^##\s*Baseline\s*\n\s*TBD\s*$", experiment_body, flags=re.MULTILINE):
                errors.append(
                    f"{campaign_dir / 'experiment.md'}: closed run requires non-TBD baseline"
                )

            source_count = len(SOURCE_ROW.findall(sources_body))
            if source_count < 3:
                errors.append(
                    f"{campaign_dir / 'sources.md'}: closed run requires at least 3 source entries"
                )

            if experiment_fm.get("status") == "not_started":
                errors.append(
                    f"{campaign_dir / 'experiment.md'}: closed run cannot keep experiment status 'not_started'"
                )

    if check_urls:
        sources_data = content.get("sources.md")
        sources_fm = sources_data[0] if sources_data else {}
        if sources_fm.get("status") == "completed":
            sources_path = campaign_dir / "sources.md"
            if sources_path.exists():
                errors.extend(validate_urls(sources_path))

    return errors


def main() -> int:
    args = sys.argv[1:]
    check_urls = "--check-urls" in args
    positional = [a for a in args if not a.startswith("--")]

    if len(positional) != 1:
        print("Usage: python scripts/validate_campaign.py <campaigns_dir> [--check-urls]")
        return 2

    root = Path(positional[0]).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Error: campaigns directory not found: {root}")
        return 2

    if check_urls:
        print("URL checking enabled.\n")

    all_errors: list[str] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        all_errors.extend(validate_campaign(child, check_urls=check_urls))

    if all_errors:
        print("\nValidation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("\nValidation passed: all campaigns are structurally and semantically valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
