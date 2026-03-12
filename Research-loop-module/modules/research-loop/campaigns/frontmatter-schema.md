# Campaign Frontmatter Schema (MVP)

Документ фиксирует минимальные machine-readable поля для campaign mode.

## Общие правила

- Все campaign-файлы (`plan.md`, `sources.md`, `reviews.md`, `proposal.md`, `experiment.md`, `decision.md`) должны начинаться с YAML frontmatter.
- Минимально обязательные поля для каждого файла:
  - `id`
  - `status`
- Для `decision.md` дополнительно обязательно поле `outcome`.

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

## Naming convention

Имя campaign-директории должно соответствовать шаблону:

`YYYY-MM-DD-topic-slug`

Пример: `2026-03-11-agent-instruction-patterns`.

## Automated check

Для валидации используйте:

```bash
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```
