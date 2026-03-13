#!/usr/bin/env python3
"""Validate research-loop campaign structure, frontmatter, and lifecycle semantics.

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
TABLE_ROW = re.compile(r"^\|(?P<row>.+)\|\s*$")
LIST_ROW = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(?P<row>.+)$")


def split_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter start")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing YAML frontmatter end")

    raw_fm = text[4:end]
    body = text[end + 5 :]

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


def resolve_ref_path(ref: str, campaign_dir: Path) -> Path | None:
    candidate = Path(ref.strip())
    if candidate.is_absolute():
        return candidate if candidate.exists() else None

    checked: set[Path] = set()
    roots = [campaign_dir, Path.cwd(), *campaign_dir.parents]
    for root in roots:
        resolved = (root / candidate).resolve()
        if resolved in checked:
            continue
        checked.add(resolved)
        if resolved.exists():
            return resolved

    return None


def count_source_entries(sources_body: str) -> int:
    entries: set[str] = set()
    for raw_line in sources_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        table_match = TABLE_ROW.match(line)
        if table_match:
            cells = [cell.strip() for cell in table_match.group("row").split("|")]
            first_cell = cells[0].lower() if cells else ""
            if first_cell in {"id", "---", ":---", "---:"}:
                continue
            if all(set(cell) <= {":", "-"} for cell in cells):
                continue
            entries.add(line)
            continue

        list_match = LIST_ROW.match(line)
        if list_match:
            entries.add(list_match.group("row").strip())

    return len(entries)


def validate_campaign(campaign_dir: Path) -> list[str]:
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

    decision_fm = content.get("decision.md", ({}, ""))[0]
    experiment_fm, experiment_body = content.get("experiment.md", ({}, ""))
    sources_body = content.get("sources.md", ({}, ""))[1]

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

        for ref_field in ("proposal_ref", "experiment_ref"):
            ref_value = decision_fm.get(ref_field)
            if is_blank(ref_value):
                errors.append(
                    f"{campaign_dir / 'decision.md'}: requires non-empty '{ref_field}'"
                )
                continue

            if resolve_ref_path(ref_value or "", campaign_dir) is None:
                errors.append(
                    f"{campaign_dir / 'decision.md'}: '{ref_field}' path not found: {ref_value}"
                )

        if decision_fm.get("status") == "closed":
            if re.search(r"^##\s*Baseline\s*\n\s*TBD\s*$", experiment_body, flags=re.MULTILINE):
                errors.append(
                    f"{campaign_dir / 'experiment.md'}: closed run requires non-TBD baseline"
                )

            source_count = count_source_entries(sources_body)
            if source_count < 3:
                errors.append(
                    f"{campaign_dir / 'sources.md'}: closed run requires at least 3 source entries"
                )

            if experiment_fm.get("status") == "not_started":
                errors.append(
                    f"{campaign_dir / 'experiment.md'}: closed run cannot keep experiment status 'not_started'"
                )

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
        all_errors.extend(validate_campaign(child))

    if all_errors:
        print("Validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Validation passed: all campaigns are structurally and semantically valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
