#!/usr/bin/env python3
"""Aggregate Skill QA reports into trend artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_metrics(reports_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not reports_root.exists():
        return rows

    for skill_dir in sorted(p for p in reports_root.iterdir() if p.is_dir() and p.name != "_meta"):
        for run_dir in sorted(p for p in skill_dir.iterdir() if p.is_dir()):
            metrics_file = run_dir / "metrics.json"
            if not metrics_file.exists():
                continue
            try:
                data = json.loads(metrics_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            data["skill"] = data.get("skill", skill_dir.name)
            data["run_id"] = run_dir.name
            rows.append(data)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "timestamp_utc",
        "skill",
        "run_id",
        "qa_passed",
        "checks_passed",
        "checks_total",
        "trigger_rate",
        "false_trigger_rate",
        "success_delta",
        "token_delta",
        "tool_calls_delta",
        "strict_mode",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# Skill QA Trends", ""]
    if not rows:
        lines.append("No reports found.")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    total = len(rows)
    passed = sum(1 for r in rows if r.get("qa_passed") is True)
    lines.append(f"- Total runs: {total}")
    lines.append(f"- Passed runs: {passed}")
    lines.append(f"- Pass rate: {passed/total:.2%}")
    lines.append("")

    latest_by_skill: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda r: (str(r.get("skill", "")), str(r.get("timestamp_utc", "")))):
        latest_by_skill[str(row.get("skill", "unknown"))] = row

    lines.append("## Latest by skill")
    lines.append("")
    lines.append("| Skill | Timestamp | Result | Trigger rate | False trigger rate | Success delta |")
    lines.append("|---|---|---:|---:|---:|---:|")

    for skill, row in sorted(latest_by_skill.items()):
        result = "PASS" if row.get("qa_passed") else "FAIL"
        lines.append(
            f"| {skill} | {row.get('timestamp_utc', '')} | {result} | {row.get('trigger_rate', '')} | {row.get('false_trigger_rate', '')} | {row.get('success_delta', '')} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate Skill QA report metrics into trend artifacts.")
    parser.add_argument("--reports-root", type=Path, default=Path("Skill Creation/reports"))
    parser.add_argument("--out-dir", type=Path, default=Path("Skill Creation/reports/_meta"))
    args = parser.parse_args()

    rows = load_metrics(args.reports_root)
    write_csv(args.out_dir / "metrics.csv", rows)
    write_summary(args.out_dir / "summary.md", rows)
    print(f"Aggregated {len(rows)} report(s) into {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
