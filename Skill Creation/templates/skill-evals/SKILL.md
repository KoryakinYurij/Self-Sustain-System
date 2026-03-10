---
name: skill-evals
description: >
  Builds automated evaluation suites to measure skill quality over time.
  Activates when teams need pre-deploy validation, continuous monitoring,
  or metric-driven assessment of trigger accuracy and output quality.
---
# Role: Skill Evaluation Framework

This skill provides templates and patterns for testing other skills using
automated evaluations (evals).

## When to Activate

Use this skill when the user:
- Needs to test or evaluate an existing skill
- Wants to set up continuous quality monitoring
- Asks about skill quality metrics or grading

## Two Types of Graders

### 1. Code-based Grader (deterministic)

For skills with predictable output. Create `scripts/eval_code_grader.py`:

```python
# scripts/eval_code_grader.py
"""
Code-based grader for [skill-name].
Checks deterministic properties of skill output.

Usage: python scripts/eval_code_grader.py <result.json>
Exit 0 = PASS, Exit 1 = FAIL
"""
import json, sys

result = json.load(open(sys.argv[1]))

checks = {
    "has_output": "output" in result,
    "valid_format": isinstance(result.get("data"), dict),
    "no_errors": len(result.get("errors", [])) == 0,
    # Add skill-specific checks:
    # "required_fields": all(f in result["data"] for f in REQUIRED),
}

passed = all(checks.values())
print(json.dumps({"passed": passed, "checks": checks}, indent=2))
sys.exit(0 if passed else 1)
```

### 2. LLM-as-Judge Grader (open-ended)

For skills where output quality is subjective. Create `references/eval_rubric.md`:

```markdown
## Eval Rubric for [skill-name]

Rate output on a 1-5 scale for each criterion:

1. **Completeness** — Does the output cover all required aspects?
2. **Accuracy** — Are the facts and recommendations correct?
3. **Specificity** — Are suggestions actionable (not generic)?
4. **Format** — Does the output match the expected structure?

### Scoring
- Score >= 4 on ALL criteria = PASS
- Any score < 3 = FAIL
- Score 3 on any criterion = REVIEW NEEDED
```

## Eval Workflow

```
For each skill change:
1. Run code-based graders → pass/fail
2. Run LLM-as-judge with rubric → score
3. Compare against baseline metrics
4. If fail OR regression → block deploy
5. Log results for trend analysis
```

### Running Evals

```bash
# Code-based eval
python scripts/eval_code_grader.py test_output.json

# LLM-as-judge (manual)
# Paste rubric from references/eval_rubric.md + skill output
# into Claude/Gemini and ask for scoring
```

## Key Metrics to Track

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Trigger rate | > 80% | 10 relevant prompts |
| False trigger rate | < 10% | 5 irrelevant prompts |
| Grader pass rate | > 90% | Automated eval runs |
| Token consumption | Stable ±10% | API logs |

## Anti-rationalization Guardrails

For each critical step, define both:
1. **Positive instruction** — what must be done
2. **Negative constraint** — what must never be skipped (even if the task looks trivial)

Use this pattern in workflow steps:

```markdown
### Step X: [Critical Step Name]
Run: [exact command or procedure]

**MANDATORY:** Always run this step.
**DO NOT:** Skip, shortcut, or assume success without evidence.
If this step fails, fix the issue and re-run before continuing.
```

## Red Flags

STOP and re-evaluate if any of these occur:
- Grader pass rate drops below 70%
- Token consumption increases by >30% after a change
- LLM-as-judge scores diverge significantly from human assessment
- Evals pass but real-world usage shows failures

## Resources

- `scripts/eval_code_grader.py` — Deterministic output checker
- `references/eval_rubric.md` — LLM-as-judge scoring criteria
