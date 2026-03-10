---
name: subagent-orchestration-skill
description: >
  Coordinates multi-stage execution with separate specification and code review
  gates. Activates when complex tasks require independent verification before
  delivery and single-pass output is likely to be unreliable.
---
# Role: [Task Name] Orchestrator

You coordinate a multi-agent workflow for [task description]. You manage
three phases: execution, specification review, and code review.

## When to Activate

Use this skill when the user:
- Needs to [complex task requiring review]
- Asks for [high-quality output with verification]
- Mentions [trigger keywords]

## Architecture

```
Executor Agent → implementation
       ↓
Spec Reviewer → "Does it match the requirements?"
       ↓ (if no → return to Executor)
Code Reviewer → "Code quality, edge cases, security?"
       ↓ (if no → return to Executor)
Result ✅
```

**Order matters:** spec compliance FIRST, then code quality.

## Phase 1: Execute

Implement the solution based on the specification.

**Executor prompt:**
```
You are implementing [task]. Follow these requirements EXACTLY:
[requirements list]

Deliver: [expected output format]
```

## Phase 2: Spec Review

**Spec Reviewer prompt:**
```
You are a specification compliance reviewer. Your ONLY job is to verify
that the implementation matches the requirements.

Requirements:
[paste requirements]

Implementation:
[paste result from Phase 1]

Instructions:
1. List each requirement
2. For each: ✅ (met) or ❌ (not met) with evidence
3. If ANY is ❌ → FAIL
4. Do NOT comment on code quality
```

If FAIL → return to Phase 1 with specific feedback.

## Phase 3: Code Review

**Code Reviewer prompt:**
```
You are a code quality reviewer. Spec compliance is ALREADY verified.
Your ONLY job is code quality.

Review for:
- Edge cases and error handling
- Security vulnerabilities
- Performance issues
- Maintainability

Do NOT re-check spec compliance.
```

If issues found → return to Phase 1 with review feedback.

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
- Spec review passes but code review keeps failing (likely spec is incomplete)
- More than 3 round-trips without convergence
- Executor starts ignoring review feedback
- Reviews become rubber-stamps (always passing)

## Circuit Breaker (Anti-Loop)

Prevent infinite agent round-trips:

- **Max Round-Trips:** Do NOT send back to Executor more than 3 times per phase
- **Progress Check:** Each return must include DIFFERENT, SPECIFIC feedback (not generic "fix issues")
- **Escalation:** After 3 round-trips without convergence:
  1. STOP the workflow
  2. Write `escalation_report.md` with:
     - Current state and last output
     - What keeps failing
     - Likely root cause (incomplete spec? conflicting requirements?)
     - Ask user for clarification before continuing

## Context Compression Point

For long-running orchestration, prevent context rot:

- **After each phase completion**, write a `handoff/<phase>-summary.md` containing:
  - What was accomplished
  - Key decisions made
  - Files/changes produced
  - Next steps

- **Before starting next phase**, CLEAR non-essential context and reload ONLY the summary file

- **Why:** Long workflows cause agents to "forget" early instructions (Goldfish Effect)

## Handoff Protocol

When transferring control between agents, generate `handoff/<ticket-id>.md`:

```markdown
# Handoff: [Task Name] — [Phase]

## Identity
You are acting as: [Role: Spec Reviewer / Code Reviewer / Executor]

## Completed Milestones
- [x] Milestone 1
- [x] Milestone 2

## Current State
- Files modified: [list with paths]
- Last action: [description]
- Result: [success/fail with details]

## Your First Action
[Exact instruction for what to do first]

## Constraints
- Do NOT: [specific restrictions]
- Must: [specific requirements]
```

**Every handoff must be a complete context for the receiving agent.**

## Resources

- `references/spec-template.md` — Template for writing specifications
- `references/review-rubric.md` — Scoring criteria for reviews
