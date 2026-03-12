# Research Loop Workflow

## Режим хранения результатов

Основной режим — **campaign-first**:
- каждый run создаётся в `campaigns/<date-topic>/`;
- внутри run хранится полный трейс одного цикла.

Legacy-папки (`sources/`, `reviews/`, `proposals/`, `experiments/`) сохраняются только для миграции старых материалов; новые активные run-ы создаются исключительно в `campaigns/`.

---

## Source Trust Tiers

При сборе источников каждый из них должен быть отмечен уровнем доверия:

| Tier | Описание | Примеры |
|------|----------|---------|
| **T1** | Official docs / primary sources | Документация OpenAI, Anthropic, Google; первоисточники авторов |
| **T2** | Сильные инженерные write-ups | Технические блоги от практиков, подробные post-mortems |
| **T3** | Хорошие репозитории / примеры | Проверенный open-source код, сильные community-решения |
| **T4** | Exploratory / слабые сигналы | Twitter-треды, неподтверждённые идеи, мнения без данных |

Источники T4 допускаются, но должны быть **явно помечены** и не могут быть единственным основанием для proposal.

---

## Базовый цикл (campaign mode)

### Шаг 1. Выбрать тему
Создать папку `campaigns/<YYYY-MM-DD-topic>/` и заполнить `plan.md`.

### Шаг 2. Собрать источники
Заполнить `sources.md` (3–5 качественных источников, каждому присвоить Trust Tier).

### Шаг 3. Сделать review
Заполнить `reviews.md`:
- почему источник заслуживает внимания;
- что именно полезно;
- что нельзя переносить бездумно;
- к какому модулю относится потенциальная польза.

### Шаг 4. Сформировать proposal
В `proposal.md` зафиксировать конкретное изменение.

### Шаг 5. Провести experiment
В `experiment.md` обязательно зафиксировать Baseline и 2–3 инвариантных кейса.

### Шаг 6. Принять решение
В `decision.md` зафиксировать outcome:
- accepted
- rejected
- inconclusive
- needs-more-testing

### Шаг 7. Promote / reject / defer
- accepted → в `memory/accepted-patterns.md` + обновление целевого шаблона;
- rejected → в `memory/anti-patterns.md`;
- inconclusive/needs-more-testing → оставить в campaign с планом next run.

### Шаг 8. Провести структурную валидацию
Проверить run скриптом:

```bash
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```

И убедиться, что frontmatter соответствует `campaigns/frontmatter-schema.md`.

---

## Definition of Done (одного campaign run)

Цикл считается **завершённым**, когда:

- [ ] есть заполненный `plan.md`;
- [ ] есть минимум 3 источника с Trust Tier в `sources.md`;
- [ ] есть конкретный proposal;
- [ ] есть experiment с зафиксированным baseline;
- [ ] есть финальный статус в `decision.md`;
- [ ] принято решение: promote / reject / defer;
- [ ] run проходит автоматическую валидацию структуры/frontmatter и семантических правил lifecycle.

Без этих пунктов run не должен считаться закрытым.

---

## Rollback Rule

Если внедрённый proposal сломал поведение или дал негативный эффект:

1. **Откатить** изменение к состоянию до эксперимента.
2. **Записать** причину отката в `experiment.md`.
3. **Перенести** паттерн в `memory/anti-patterns.md` с пометкой `rolled back`.
4. **Не удалять** campaign — он остаётся как документация неудачной попытки.
