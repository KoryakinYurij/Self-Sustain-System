---
id: campaign-2026-03-11-agent-instruction-patterns-experiment
status: completed
target_module: agents-lab
updated_at: 2026-03-13
---

# Experiment

## Baseline

В `agents-lab/README.md` перечислены общие категории улучшений agent instructions, но нет явного указания на краткую карту репозитория как отдельный паттерн grounding.

## Test case(s)

- Case 1: агенту дают задачу изменить файл в существующем модуле; проверяем, упоминает ли инструкция необходимость сначала опереться на карту репозитория.
- Case 2: агенту дают задачу в незнакомой части проекта; проверяем, становится ли путь поиска файлов более локальным и менее хаотичным.
- Case 3: агенту дают простую правку в известном файле; проверяем, не добавляет ли новый паттерн лишние обязательные шаги.

## Result

- Case 1
  - What was checked: whether the current repo-grounding change adds an explicit instruction-level cue to consult a short repo map before editing a file in an existing module.
  - Improvement signal: task instructions or agent behavior consistently mention repo structure first, instead of jumping straight to file edits.
  - Assessment: weak support. The change adds `краткую карту репозитория для grounding` to `agents-lab/README.md` as an allowed improvement area, but it does not yet require that pattern in agent instructions or show a tested prompt/output example. This is not enough evidence to claim the signal is achieved.
- Case 2
  - What was checked: whether the change is sufficient to make file discovery in an unfamiliar area more local and less chaotic.
  - Improvement signal: narrower, repo-aware search paths and fewer broad exploratory steps when the agent is dropped into an unfamiliar part of the codebase.
  - Assessment: not enough support. The new bullet names the pattern, which may help future proposals converge on it, but by itself it does not add search heuristics, examples, or enforcement. There is no run evidence showing more local exploration behavior.
- Case 3
  - What was checked: whether the repo-grounding addition avoids turning simple known-file edits into a heavier required workflow.
  - Improvement signal: simple edits remain simple; the agent can use repo grounding when useful without adding mandatory overhead for obvious tasks.
  - Assessment: plausible but unproven. Because the change is only a permissive bullet in a README, it does not appear to force extra steps. Still, there is no test evidence demonstrating non-regression on a simple edit flow.
- Overall assessment
  - Evidence strength: weak.
  - The current patch is documentation-level only and is too small to justify acceptance on behavioral grounds.
  - Likely outcome: needs-more-testing.
  - Conservative conclusion: the change usefully names the repo-grounding pattern, but it does not by itself demonstrate improvement across the three cases.
