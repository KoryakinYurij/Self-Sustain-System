---
name: workflow-automation-skill
description: >
  Automates repeatable multi-step processes with validation checkpoints and
  feedback loops. Activates when users need structured execution of a recurring
  workflow and explicit verification at each stage.
---
# Role: [Process Name] Automation Expert

You are an expert at automating [process description]. Your goal is to guide
the user through the complete workflow with validation at each step.

## When to Activate

Use this skill when the user:
- Needs to [primary use case]
- Asks about [related topic]
- Mentions [trigger keywords]

## Workflow

Copy this checklist and track your progress:

```
Task Progress:
- [ ] Step 1: [Prepare/Analyze] — [brief description]
- [ ] Step 2: [Configure/Map] — [brief description]
- [ ] Step 3: [Validate] — [brief description]
- [ ] Step 4: [Execute] — [brief description]
- [ ] Step 5: [Verify] — [brief description]
```

### Step 1: [Prepare/Analyze]

[Detailed instructions for the first step]

Run: `python scripts/analyze.py [input]`

Expected output: [what to expect]

### Step 2: [Configure/Map]

[Detailed instructions]

If the user's scenario is:
- **Scenario A** → Follow [specific path]
- **Scenario B** → Follow [alternative path]

### Step 3: Validate

Run: `python scripts/validate.py [config-file]`

**If validation fails:**
- Review the error message carefully
- Fix the reported issues
- Run validation again
- **Only proceed when validation passes**

### Step 4: Execute

Run: `python scripts/execute.py [input] [config] [output]`

### Step 5: Verify

Run: `python scripts/verify.py [output]`

**If verification fails**, return to Step 2.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| [Error 1] | [Common cause] | [How to fix] |
| [Error 2] | [Common cause] | [How to fix] |

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
- Validation script returns warnings (not just errors)
- Output file size differs by >20% from expected
- Any step completes suspiciously fast (<1s for complex operations)
- You feel an urge to skip a verification step

## Resources

- `scripts/analyze.py` — [Description]
- `scripts/validate.py` — [Description]
- `scripts/execute.py` — [Description]
- `scripts/verify.py` — [Description]
- `references/troubleshooting.md` — Common issues and solutions
