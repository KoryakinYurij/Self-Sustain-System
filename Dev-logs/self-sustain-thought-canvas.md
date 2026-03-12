# Thought Canvas

A running log of evolving thoughts.

---

## Thought 1 — Исходная цель: self-sustain loop на CLI-агентах

**Raw thought**
Хочется запустить loop на агентах не по API, а через команды к headless-режимам: Gemini CLI, Codex CLI, возможно Jules. Чтобы они искали, помогали дорабатывать модуль и постепенно развивали систему, которая сама себя улучшает.

**Structured note**
Исходная цель — не просто автоматизировать отдельные задачи, а построить самоподдерживающийся контур улучшения на базе CLI-агентов. Важное ограничение с самого начала: опора не на API, а на реально запускаемые headless/CLI backend-ы.

**Open thread**
Что именно должно самоулучшаться в первую очередь: оркестрация, шаблоны агентов, скиллы, memory, evaluation или вся система сразу.

---

## Thought 2 — Первый архитектурный сдвиг: не swarm, а controlled loop

**Raw thought**
Хочется уже запустить loop на агентах, но сначала понять, как это сделать правильно и без лишней магии.

**Structured note**
Первый важный вывод: не надо начинать с многоагентного swarm. Сначала нужен один контролируемый improvement loop с разделением ролей и понятным trace. Иначе любая замена backend-а превратится в переписывание ядра.

Базовая логика loop-а:
- Goal selector
- Context collector
- Agent runner
- Patch evaluator
- Test/QA verifier
- Governor
- Log

**Open thread**
Нужен ли сначала универсальный multi-agent orchestrator, или достаточно одного run-а с жёстким governance и сменными CLI backend-ами.

---

## Thought 3 — Что реально видно по repo и Dev-logs

**Raw thought**
Нужно было не фантазировать, а сначала понять, что уже заложено в репозитории и в Dev-logs.

**Structured note**
После просмотра repo стало видно, что проект уже движется не как набор случайных файлов, а как framework/tooling для skill creation и research-loop. По Dev-logs проявились несколько устойчивых идей:
- `research-loop` как первый MVP;
- модульность вместо смешивания всего в одну кучу;
- проверенные источники как база изменений;
- baseline, anti-patterns, active memory и rejection как защита от ложных improvement-ов.

**Open thread**
Какой следующий шаг действительно следует из логов: продолжать улучшать архитектуру или уже запускать первый реальный цикл.

---

## Thought 4 — Критический fork: вертикальные run-ы или горизонтальные папки

**Raw thought**
Нужно понять, лучше ли делать vertical campaign-runner, или хороший skill и понятная горизонтальная структура по папкам могут всё компенсировать.

**Structured note**
Возник реальный архитектурный fork:

Вариант A — вертикальный run:
каждый цикл лежит рядом в одной папке: plan, sources, reviews, proposal, experiment, decision.

Вариант B — горизонтальная knowledge-структура:
`sources/`, `reviews/`, `proposals/`, `experiments/`, `memory/`, `evaluations/`, а навигацию компенсирует сильный skill/project memory.

После критики стало ясно, что чисто вертикальная схема плохо работает как долговременная knowledge base, а чисто горизонтальная — неудобна для выполнения одного CLI run-а из-за рассыпания операционного контекста.

**Open thread**
Нужно не выбирать одну идеологию, а отделить operational trace и canonical knowledge.

---

## Thought 5 — Итог по структуре: hybrid architecture

**Raw thought**
Чисто vertical — слишком радикально. Чисто horizontal — тяжело для CLI-агентов. Нужен компромисс.

**Structured note**
Сформировался итоговый вывод: лучшая база — гибрид.

Горизонтальный слой остаётся каноническим:
- `memory/`
- `evaluations/`
- `agents-lab/`
- `skills-lab/`
- policies / contracts / ADR

Вертикальный слой становится операционным:
- `modules/research-loop/campaigns/<date-topic>/`
- `plan.md`
- `sources.md`
- `reviews.md`
- `proposal.md`
- `experiment.md`
- `decision.md`
- `artifacts/`

**Open thread**
Как закрепить этот гибрид не только в рассуждении, но и в рабочем контракте для системы и агентов.

---

## Thought 6 — Проверка идеи через PR: формализация hybrid architecture

**Raw thought**
Нужно было проверить, превратится ли идея гибридной структуры в внятный operational contract, а не просто в красивое описание.

**Structured note**
Через PR была формализована hybrid architecture:
- добавлен ADR про разделение horizontal knowledge и vertical campaign runs;
- введён `campaigns/` как trace layer;
- описана promotion policy;
- добавлен scaffold campaign-run;
- введён validator для структуры и frontmatter.

Первый вывод по review PR:
направление правильное, но начальная версия валидатора проверяла в основном форму, а не смысл lifecycle.

**Open thread**
Как усилить контракт так, чтобы run был не просто красиво оформлен, а реально governance-ready.

---

## Thought 7 — Усиление контракта: schema, semantic rules, legacy governance

**Raw thought**
Если это реальная база под CLI-агентов, нужны строгие поля, статусы, semantic rules и понятное отношение к legacy-слою.

**Structured note**
Следующим шагом был усилен contract layer:
- обязательные поля `target_module`, даты;
- для `decision.md` обязательны `proposal_ref` и `experiment_ref`;
- запрет `closed + pending`;
- `accepted/rejected` требуют явных ссылок на promotion/rejection;
- закрытый run не может иметь `baseline = TBD`;
- legacy-папки зафиксированы как read-only для новых циклов.

Это сдвинуло систему от “хороший MVP” к “достаточно крепкий operational contract”.

**Open thread**
Осталось проверить две мелкие дыры: непустота и существование ref-путей, а также меньше привязать подсчёт источников к одному scaffold-формату.

---

## Thought 8 — Последние мелкие фиксы: refs и sources counting

**Raw thought**
Даже при сильной схеме оставались две мелкие, но реальные дыры: `proposal_ref` / `experiment_ref` могли быть пустыми или указывать в никуда, а проверка `sources.md` слишком зависела от конкретного табличного шаблона.

**Structured note**
Через следующий follow-up PR были закрыты и эти дыры:
- валидатор теперь требует непустые `proposal_ref` / `experiment_ref` и проверяет, что пути реально существуют;
- подсчёт source entries стал работать не только по одному шаблону таблицы, но и по markdown-спискам.

После этого база была признана достаточной для первого живого run-а.

**Open thread**
Что делать дальше: продолжать улучшать infra или остановиться и перейти к реальному эксперименту.

---

## Thought 9 — Главный переход: stop improving infra, start first real run

**Raw thought**
После PR #5 стало понятно, что бесконечно улучшать архитектуру уже не нужно. Следующий шаг — реальный запуск, а не очередной structural fix.

**Structured note**
Ключевой вывод текущего этапа:

Хватит улучшать структуру.
Пора делать первый настоящий campaign run.

То есть:
- не новый infra-PR;
- не multi-agent swarm;
- не новый большой модуль;
- а один governed run по теме `agent-instruction-patterns`.

Предлагаемый режим:
- Gemini CLI — сбор источников и review;
- Codex CLI — proposal и точечное изменение;
- человек — governor;
- один узкий experiment в `agents-lab`;
- outcome только один из: accepted / rejected / needs-more-testing / inconclusive.

**Open thread**
Нужен точный сценарий первого реального run-а: какие источники брать, что делегировать Gemini CLI, что — Codex CLI, и какой experiment выбрать первым.

---

## Thought 10 — Рабочее состояние на сейчас

**Raw thought**
Хочется, чтобы была видна вся линия мысли: от идеи loop-а на CLI-агентах до момента, когда стало ясно, что база уже достаточно крепкая и пора запускать первый реальный цикл.

**Structured note**
История мысли на данный момент выглядит так:
1. идея self-sustain loop на CLI backend-ах;
2. отказ от раннего swarm-подхода;
3. опора на repo и Dev-logs вместо фантазии;
4. архитектурный fork vertical vs horizontal;
5. вывод в пользу hybrid architecture;
6. проверка идеи через PR и критический review;
7. усиление schema/validator/lifecycle governance;
8. закрытие последних мелких дыр;
9. решение остановить infra-work и перейти к первому реальному run-у.

**Open thread**
Следующий живой шаг — спланировать и провести первый campaign run по `agent-instruction-patterns`, используя уже созданную структуру и validator.
