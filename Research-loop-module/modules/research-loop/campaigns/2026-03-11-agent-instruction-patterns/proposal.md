---
id: campaign-2026-03-11-agent-instruction-patterns-proposal
status: in_review
target_module: agents-lab
updated_at: 2026-03-13
---

# Proposal

## Change

Добавить в `agents-lab` явный паттерн repo-grounding: в списке допустимых улучшений отдельно указать краткую карту репозитория (`repo map`) как часть структуры agent instructions.

## Expected effect

Агенты будут чаще опираться на локальную структуру проекта перед действием, что снизит число расплывчатых инструкций и уменьшит риск лишних шагов в CLI-сценариях.

## Invariants (must not regress)

- выполнение базовых задач без лишних шагов;
- корректная работа с ограничениями инструментов;
- структурированный финальный отчёт.
