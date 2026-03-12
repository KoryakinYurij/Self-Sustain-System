# Research Loop Runbook

## Цель runbook

Этот документ нужен, чтобы человек или агент мог быстро запустить один cycle в `campaigns/` без долгой навигации по модулю.

## Минимальный запуск

### Вход
- 1 тема исследования
- 3–5 источников
- 1 целевой модуль (`agents-lab` или `skills-lab`)
- 1 маленький тест

### Выход (campaign mode)
- 1 папка `campaigns/<date-topic>/`
- `plan.md`
- `sources.md`
- `reviews.md`
- `proposal.md`
- `experiment.md`
- `decision.md`
- `artifacts/` (по необходимости)
- при успехе — 1 запись в memory + обновлённый шаблон
- при неудаче — 1 запись в anti-patterns

## Рекомендуемая последовательность

1. выбрать тему (из `inbox/` или вручную);
2. создать campaign-папку и заполнить `plan.md`;
3. собрать источники в `sources.md`;
4. сделать `reviews.md`;
5. собрать конкретный `proposal.md`;
6. провести тест и записать `experiment.md` (с baseline);
7. закрыть run через `decision.md`;
8. выполнить promote / reject / defer (см. `pattern-promotion-policy.md`);
9. проверить campaign-структуру и frontmatter через validator.

## Команда валидации

```bash
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```

Дополнительно ориентироваться на `campaigns/frontmatter-schema.md`.

## Важное правило

Если исследование интересное, но не привело к наблюдаемому улучшению, его можно сохранить как:
- полезный контекст;
- отложенное направление;
- неподтверждённую гипотезу.

Но оно не должно автоматически становиться accepted pattern.
