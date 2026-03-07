---
name: executable-skill
description: >
  Template for skills that wrap critical operations in deterministic scripts.
  Use when building skills that involve deployment, data processing, file
  operations, PII redaction, or any operation where LLM creativity is a risk.
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

## Red Flags

STOP and re-evaluate if any of these occur:
- Validation returns warnings (not just errors)
- Output size differs significantly from expected
- Any step completes suspiciously fast (<1s for complex data)
- You feel an urge to skip validation or verification

## Resources

- `scripts/validate.sh` — Input validation (exit 0 = pass, exit 1 = fail)
- `scripts/run.py` — Main processing logic (deterministic)
- `scripts/verify.py` — Output verification (JSON report)
