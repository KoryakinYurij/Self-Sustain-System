# Campaign Frontmatter Schema (MVP+)

Документ фиксирует machine-readable контракт для campaign mode.

## Ограничение формата frontmatter

Для совместимости с текущим валидатором допускаются только **простые scalar-поля** вида:

`key: value`

Не допускаются списки, вложенные структуры и многострочные значения. Если нужны сложные структуры — требуется migration валидатора на полноценный YAML parser.

## Общие правила

- Все campaign-файлы (`plan.md`, `sources.md`, `reviews.md`, `proposal.md`, `experiment.md`, `decision.md`) должны начинаться с YAML frontmatter.
- Обязательные глобальные поля:
  - `id`
  - `status`
  - `target_module`
  - `updated_at` (дата `YYYY-MM-DD`)
- Для `plan.md` дополнительно обязательно `created_at`.
- Для `decision.md` дополнительно обязательны:
  - `outcome`
  - `proposal_ref` (непустой, путь должен существовать)
  - `experiment_ref` (непустой, путь должен существовать)

## Enumerations

### `plan.md`
- `status`: `planned` | `in_progress` | `completed` | `blocked`

### `sources.md`
- `status`: `draft` | `in_progress` | `completed`

### `reviews.md`
- `status`: `draft` | `in_progress` | `completed`

### `proposal.md`
- `status`: `draft` | `in_review` | `approved` | `rejected`

### `experiment.md`
- `status`: `not_started` | `running` | `completed` | `rolled_back`

### `decision.md`
- `status`: `open` | `closed`
- `outcome`: `pending` | `accepted` | `rejected` | `inconclusive` | `needs-more-testing`

## Semantic rules

- Если `decision.status = closed`, то `decision.outcome` не может быть `pending`.
- Если `decision.outcome = accepted`, поле `promotion_ref` обязательно и не может быть пустым.
- Если `decision.outcome = rejected`, поле `rejection_ref` обязательно и не может быть пустым.
- Если run закрыт (`decision.status = closed`), в `experiment.md` baseline не может быть `TBD`.
- Если run закрыт (`decision.status = closed`), в `sources.md` должно быть минимум 3 source entry (поддерживаются markdown-таблица и markdown-список, а не только шаблон `| S1 | ...`).

## Naming convention

Имя campaign-директории должно соответствовать шаблону:

`YYYY-MM-DD-topic-slug`

Пример: `2026-03-11-agent-instruction-patterns`.

## Automated check

Для валидации используйте:

```bash
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```
