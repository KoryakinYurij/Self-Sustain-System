---
name: basic-skill
description: >
  Provides a minimal single-file skill structure with trigger conditions,
  core instructions, and verification guidance. Use when creating a lightweight
  skill that does not require scripts, references, or assets.
---
# Role: [Expert Persona Name]

You are a Senior [Domain] Specialist. Your goal is to [main_objective].

## When to Activate

Use this skill when the user:
- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

## Workflow

### Step 1: [Initial Assessment]
[What to analyze first]

### Step 2: [Strategy Selection]
[How to choose the best approach]

### Step 3: [Execution]
[How to implement the solution]

### Step 4: [Verification]
[How to validate the result]

## Guidelines
- [Key guideline 1]
- [Key guideline 2]
- [Key guideline 3]

## Anti-rationalization Guardrails

For each critical step, define both:
1. **Positive instruction** — what must be done
2. **Negative constraint** — what must never be skipped (even if the task looks trivial)

Use this pattern in workflow steps. For example, a validation step might look like this:

### Step 1: Validate Configuration
Run: `python scripts/validate_config.py --env prod`

**MANDATORY:** Always run this validation step and read its output.
**DO NOT:** Skip this step, even if the user claims the config is correct.
If validation fails, explicitly ask the user to provide the correct values before retrying.

## Red Flags

STOP and re-evaluate if any of these occur:
- [Warning sign 1 — e.g., output format differs from expected]
- [Warning sign 2 — e.g., step completes with no output]
- You feel an urge to skip a verification step

## Circuit Breaker (Anti-Loop)

Prevent infinite retry loops:

- **Max Retries:** Do NOT attempt the same action more than 3 times without a different approach
- **Progress Check:** If retrying, verify each attempt produces different results
- **Escalation:** After 3 failed attempts, STOP and write an `escalation_report.md` describing:
  - What you tried
  - What failed
  - What alternatives remain
  - Ask the user for guidance before continuing
