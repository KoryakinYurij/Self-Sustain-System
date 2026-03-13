---
id: campaign-2026-03-11-agent-instruction-patterns-sources
status: completed
target_module: agents-lab
updated_at: 2026-03-13
---

# Sources

| id | source | trust_tier | notes |
|---|---|---|---|
| S1 | [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) | T1 | Distinguishes between workflows (chaining/routing) and autonomous agents; emphasizes ACI (Agent-Computer Interface). |
| S2 | [OpenAI: Agents SDK](https://openai.github.io/openai-agents-python) | T1 | Lightweight orchestration via "Handoffs", "Guardrails", and focus on "Traceability" of multi-agent interactions. |
| S3 | [Claude Code & CLAUDE.md Patterns](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | T2 | Standardizes repository-level grounding via CLAUDE.md (tech stack, onboarding, project map). |
| S4 | [Real-world Agent Failures and Guardrails](https://towardsai.net/p/l-m-s-m-e-n-t-a-l-m-o-d-e-l-s-a-n-d-f-a-i-l-u-r-e-s) | T2 | Covers "Proxy Reward Abuse" and "Context Pressure" where agents optimize for metrics over intent. |
| S5 | [Google: Agentic Design Patterns](https://cloud.google.com/blog/products/ai-machine-learning/agentic-design-patterns-with-gemini) | T1 | Details Reasoning-Action (ReAct) loops, self-correction, and grounding in tool-specific schemas. |
