---
name: executable-skill
description: >
  Orchestrates deterministic scripts for critical operations where consistency
  and safety are mandatory. Activates when tasks involve deployment, destructive
  changes, sensitive data handling, or other high-risk automation.
---
# Role: [Operation Name] Executor

You execute [operation] using deterministic scripts. Your job is to orchestrate
the scripts, validate inputs, and interpret results — NOT to perform the
critical logic yourself.

## When to Activate

Use this skill when the user:
- Needs to [critical operation: deploy, process, redact, validate]
- Mentions [trigger keywords]

## Prerequisites

- Python 3.10+ with dependencies: `uv run scripts/run.py --help`
- [Other requirements]

## Workflow

```
Task Progress:
- [ ] Step 1: Validate input
- [ ] Step 2: Execute operation
- [ ] Step 3: Verify output
```

### Step 1: Validate input

Run: `python scripts/validate.sh [input]`

**IMPORTANT:** Run validation EVERY time. Do NOT skip even if input looks correct.

If validation fails:
- Review the error message
- Fix the input
- Run validation again

### Step 2: Execute operation

Run: `python scripts/run.py --input [validated-input] --output [output-path]`

Do NOT modify the command or add flags not listed here.

### Step 3: Verify output

Run: `python scripts/verify.py [output-path]`

Expected output: `{"status": "success", "items_processed": N}`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `VALIDATION_FAILED` | Invalid input format | Check input against expected schema |
| `PERMISSION_DENIED` | Missing credentials | Verify environment variables |
| `OUTPUT_MISMATCH` | Processing error | Re-run from Step 1 |

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
- Validation returns warnings (not just errors)
- Output size differs significantly from expected
- Any step completes suspiciously fast (<1s for complex data)
- You feel an urge to skip validation or verification

## Circuit Breaker (Anti-Loop)

Prevent infinite retry loops during critical operations:

- **Max Retries:** Do NOT run the same script with the same input more than 3 times
- **Progress Check:** Each retry must have a DIFFERENT fix applied (different input, different flags, different approach)
- **Escalation:** After 3 failures, STOP. Write `escalation_report.md` with:
  - Exact command that failed
  - Full error output
  - What you tried to fix it
  - Ask user for intervention — do NOT continue retrying

**CRITICAL:** Infinite loops in executable skills waste resources and may cause data corruption.

## Resources

- `scripts/validate.sh` — Input validation (exit 0 = pass, exit 1 = fail)
- `scripts/run.py` — Main processing logic (deterministic)
- `scripts/verify.py` — Output verification (JSON report)
