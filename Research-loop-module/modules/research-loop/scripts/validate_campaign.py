#!/usr/bin/env python3
"""Validate research-loop campaign structure and frontmatter.

Usage:
  python scripts/validate_campaign.py modules/research-loop/campaigns
"""

from __future__ import annotations

import re
import sys
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

DATE_TOPIC = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter start")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter end")

    fm = text[4:end].splitlines()
    data: dict[str, str] = {}
    for line in fm:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_campaign(campaign_dir: Path) -> list[str]:
    errors: list[str] = []

    if not DATE_TOPIC.match(campaign_dir.name):
        errors.append(f"{campaign_dir}: invalid name format, expected YYYY-MM-DD-topic")

    for filename in REQUIRED_FILES:
        file_path = campaign_dir / filename
        if not file_path.exists():
            errors.append(f"{campaign_dir}: missing {filename}")
            continue

        try:
            fm = parse_frontmatter(file_path)
        except ValueError as exc:
            errors.append(f"{file_path}: {exc}")
            continue

        if "id" not in fm:
            errors.append(f"{file_path}: missing frontmatter field 'id'")
        if "status" not in fm:
            errors.append(f"{file_path}: missing frontmatter field 'status'")
        else:
            allowed = STATUS_ENUM[filename]
            if fm["status"] not in allowed:
                errors.append(
                    f"{file_path}: invalid status '{fm['status']}', allowed={sorted(allowed)}"
                )

        if filename == "decision.md":
            if "outcome" not in fm:
                errors.append(f"{file_path}: missing frontmatter field 'outcome'")
            elif fm["outcome"] not in OUTCOME_ENUM:
                errors.append(
                    f"{file_path}: invalid outcome '{fm['outcome']}', allowed={sorted(OUTCOME_ENUM)}"
                )

    artifacts = campaign_dir / "artifacts"
    if not artifacts.exists() or not artifacts.is_dir():
        errors.append(f"{campaign_dir}: missing artifacts/ directory")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_campaign.py <campaigns_dir>")
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Error: campaigns directory not found: {root}")
        return 2

    all_errors: list[str] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        if child.name == "README.md":
            continue
        all_errors.extend(validate_campaign(child))

    if all_errors:
        print("Validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Validation passed: all campaigns are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
