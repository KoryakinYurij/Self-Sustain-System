# Agent Skills Creation — Knowledge Base

You are creating an Agent Skill following the open standard [agentskills.io](https://agentskills.io).
Target platforms: Gemini CLI, OpenCode AI (compatible with Cursor, GitHub Copilot, Claude Code).

## Workflow

1. Read `guides/01-skill-anatomy.md` — understand the required structure
2. Read `guides/02-writing-effective-skills.md` — learn SOTA writing techniques
3. Choose a template from `templates/` that matches the task type
4. Create the skill, following guides 03–06 as needed
5. Validate against `checklists/quality-checklist.md`
6. Install to `~/.agents/skills/` (universal path for all platforms)

## File Map

### Guides (read in order when creating a skill)

| File | When to read |
|------|-------------|
| `guides/01-skill-anatomy.md` | Always — structure, frontmatter rules, directories, naming conventions |
| `guides/02-writing-effective-skills.md` | Always — description triggers (CSO), progressive disclosure, scripts vs LLM, DOT graphs, post-generation review |
| `guides/03-cross-platform.md` | When targeting multiple platforms — compatibility tables, paths |
| `guides/04-anti-patterns.md` | Before finalizing — common mistakes, rationalization traps, Red Flags pattern |
| `guides/05-advanced-patterns.md` | When using scripts, workflows, feedback loops, subagent orchestration, or evals |
| `guides/06-security.md` | When the skill includes `scripts/` |

### Templates (copy and fill)

| Template | Use when |
|----------|---------|
| `templates/basic-skill/` | Simple skill — only SKILL.md, no scripts |
| `templates/mcp-tool-skill/` | Skill integrating an MCP tool with REST fallback |
| `templates/workflow-automation-skill/` | Multi-step process with checklist tracking |
| `templates/knowledge-domain-skill/` | Domain expert with reference files |
| `templates/executable-skill/` | Critical operations wrapped in deterministic scripts |
| `templates/subagent-orchestration-skill/` | Multi-agent workflow with spec and code review gates |
| `templates/skill-evals/` | Eval test suite with code graders and LLM-as-judge |

### Reference (real-world examples for studying patterns)

| Path | Contains |
|------|---------|
| `research/obra-superpowers/skills/` | 14 production-tested skills (TDD, debugging, code review, subagent orchestration) |
| `research/obra-superpowers/analysis.md` | Extracted patterns: CSO, anti-rationalization, token efficiency, naming conventions |

### Quality

| File | When to use |
|------|------------|
| `checklists/quality-checklist.md` | Before installing — final validation checklist |

## Key Rules

- `name` in frontmatter MUST match the directory name
- `name` should use gerund/verb-first form (`processing-pdfs`, not `pdf-helper`)
- `description` = WHAT + WHEN — never HOW (no workflow steps)
- 1 skill = 1 task — micro-skills chained together beat monoliths
- `SKILL.md` filename MUST be uppercase
- Body word limit: simple < 150 words, complex < 500 words; rest goes to `references/`
- No `@skills/name` references — use text mentions instead
- Critical operations → `scripts/`, not LLM prose
- Every template includes a `## Red Flags` section
- Install path: `~/.agents/skills/<name>/SKILL.md`
- All file paths use forward slashes

## Sources

All information is verified against these official sources:

| Source | URL |
|--------|-----|
| Agent Skills Specification | [agentskills.io/specification](https://agentskills.io/specification) |
| Agent Skills: Using scripts | [agentskills.io/skill-creation/using-scripts](https://agentskills.io/skill-creation/using-scripts) |
| Gemini CLI: Skills | [github.com/.../skills.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md) |
| Skill Authoring Best Practices | [platform.claude.com/.../best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| Anthropic: Complete Guide to Skills | [docs.anthropic.com/.../skills](https://docs.anthropic.com/en/docs/agents-and-tools/skills) |
| Anthropic: Evals & Testing | [docs.anthropic.com/.../develop-tests](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests) |
