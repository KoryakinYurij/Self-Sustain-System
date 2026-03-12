# Campaigns (Runs)

`campaigns/` хранит вертикальные операционные эпизоды research-loop.

Каждая папка — один завершённый или активный run в формате:

```text
campaigns/
  YYYY-MM-DD-topic/
    plan.md
    sources.md
    reviews.md
    proposal.md
    experiment.md
    decision.md
    artifacts/
```

## Правила

- один run = одна тема;
- все файлы run лежат рядом;
- run закрывается только через `decision.md`;
- accepted/rejected выводы должны быть продвинуты по `pattern-promotion-policy.md`;
- frontmatter должен соответствовать `frontmatter-schema.md`.

## Validation

```bash
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```
