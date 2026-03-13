---
id: campaign-2026-03-11-agent-instruction-patterns-reviews
status: completed
target_module: agents-lab
updated_at: 2026-03-13
---

# Reviews

- Source: S1 (Anthropic)
- Why credible: Primary research from Anthropic on how to move from simple prompts to complex agentic systems.
- Useful pattern: "Agent-Computer Interface" (ACI) pattern—treating tool schemas and documentation as the primary interface for LLM performance.
- Transfer risk: Low; emphasizes that simplicity and transparency (thinking steps) are more effective than complex frameworks.
- Candidate target: agents-lab

- Source: S2 (OpenAI)
- Why credible: Official documentation for OpenAI's approach to lightweight multi-agent orchestration.
- Useful pattern: "Handoffs" pattern—explicit delegation between specialized agents (e.g., researcher to coder) instead of one bloated generalist.
- Transfer risk: Medium; depends on the underlying model's ability to maintain context during handoffs.
- Candidate target: agents-lab

- Source: S3 (Claude Code)
- Why credible: Practical application of autonomous CLI agents in production by Anthropic.
- Useful pattern: "Grounding File" pattern (CLAUDE.md)—a concise repository map (<120 lines) used for tech-stack and workflow onboarding.
- Transfer risk: Low; widely applicable across different AI-native IDEs and CLI agents.
- Candidate target: agents-lab

- Source: S4 (TowardsAI / Failures)
- Why credible: Engineering analysis of common failure modes in autonomous agent deployment.
- Useful pattern: "Anti-Proxy Optimization"—guardrails against agents deleting code to "fix" linting errors or exhausting tokens in loops.
- Transfer risk: Low; critical for any agent with file-edit or shell execution capabilities.
- Candidate target: agents-lab

- Source: S5 (Google)
- Why credible: Official architectural guidance for building agentic systems with Gemini.
- Useful pattern: "Self-Correction Loop" pattern—enforcing a mandatory review step where the agent critiques its own output against constraints.
- Transfer risk: High; requires models with strong reasoning capabilities to avoid "hallucinated corrections".
- Candidate target: agents-lab
