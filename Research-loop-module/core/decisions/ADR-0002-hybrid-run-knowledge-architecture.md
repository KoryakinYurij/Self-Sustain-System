# ADR-0002 — Hybrid architecture: horizontal knowledge + vertical campaign runs

## Статус
Accepted

## Контекст

В `research-loop` было видно напряжение между двумя подходами:
- горизонтальная структура (`sources/`, `reviews/`, `proposals/`, `experiments/`) удобна как долговременная база правил;
- вертикальная структура (всё по одному run в одной папке) удобна для выполнения одного полного цикла и снижения потери контекста в CLI-режиме.

Практический риск чисто горизонтального подхода — операционный контекст размазывается по нескольким каталогам.
Практический риск чисто вертикального подхода — канонические правила и паттерны расползаются по эпизодам и хуже переиспользуются.

## Решение

Принять **hybrid architecture**:

1. **Горизонтальное ядро (canonical layer)** остаётся источником истины:
   - `memory/`
   - `evaluations/`
   - `agents-lab/`
   - `skills-lab/`
   - `core/contracts/`, `core/decisions/`, runbook/policy-документы

2. **Вертикальный операционный слой (trace layer)** вводится в `modules/research-loop/campaigns/`.
   Каждый campaign/run хранится в отдельной папке и содержит полный трейс одного цикла:
   - `plan.md`
   - `sources.md`
   - `reviews.md`
   - `proposal.md`
   - `experiment.md`
   - `decision.md`
   - `artifacts/`

3. **Promotion policy обязательна**:
   - accepted → `memory/accepted-patterns.md` + обновление шаблона;
   - rejected/rolled back → `memory/anti-patterns.md`;
   - inconclusive → остаётся в campaign с пометкой для повторного прогона.

## Последствия

### Плюсы
- агенту проще пройти один run без лишней навигации;
- проще архивировать и откатывать изменения на уровне одного campaign;
- каноническое знание сохраняется в стабильных горизонтальных модулях;
- trace и knowledge разделены, но связаны через promotion.

### Минусы
- требуется дисциплина закрытия campaign через `decision.md`;
- возрастает число файлов в `campaigns/`;
- нужно поддерживать явные ссылки из campaign в memory/template updates.

## Правило совместимости

Старые горизонтальные папки `sources/`, `reviews/`, `proposals/`, `experiments/` не удаляются мгновенно.
Они считаются legacy-слоем и могут использоваться для миграции прошлых материалов в `campaigns/`.
