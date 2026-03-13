# 10 улучшений для перехода Research Module на новый уровень

> Каждое улучшение основано на конкретных узких местах, найденных в текущем коде и workflow. Ранжировано по impact × feasibility.

---

## 1. 🔍 Automated Source Discovery Pipeline

**Проблема сейчас:** Источники собираются вручную — человек сам ищет в Google, заходит на сайты, копирует URL в `sources.md`. Это самый медленный шаг в цикле.

**Что добавить:**
- Скрипт `scripts/discover_sources.py`, который по заданному `plan.md` (research question + target keywords) автоматически:
  - ищет через поисковые API (Google, Exa, Bright Data) релевантные документы;
  - скрейпит и извлекает ключевые сигналы;
  - автоматически присваивает Trust Tier по домену (anthropic.com → T1, medium.com → T3, twitter.com → T4);
  - генерирует черновик `sources.md` с уже заполненными полями.
- Человек только ревьюит и утверждает, а не пишет с нуля.

**Impact:** Сокращение времени на шаг 2 (сбор источников) с часов до минут.

---

## 2. 📊 Cross-Campaign Analytics Dashboard

**Проблема сейчас:** Каждый campaign живёт изолированно. Нет способа увидеть: сколько campaigns закрыто, какой % принят, какие темы повторяются, какие паттерны чаще всего rejected.

**Что добавить:**
- Скрипт `scripts/campaign_analytics.py`, который парсит frontmatter всех campaigns и генерирует `artifacts/research-dashboard.md`:
  - воронка: planned → in_progress → completed → accepted/rejected;
  - таблица незавершённых campaigns с возрастом (дней в статусе);
  - Top N повторяющихся тем и target_modules;
  - hit rate: % accepted из всех закрытых campaigns;
  - time-to-close: среднее время от created_at до decision.closed.

**Impact:** Превращает research-loop из «отдельных записок» в **управляемую систему** с метриками.

---

## 3. 🔗 Campaign Chaining & Follow-Up Runs

**Проблема сейчас:** Первый campaign (`agent-instruction-patterns`) завершился с `needs-more-testing`, но нет механизма для создания follow-up run. Человек должен вручную помнить, что нужно вернуться.

**Что добавить:**
- Поле `parent_campaign` в frontmatter schema для `plan.md` — ссылка на предыдущий campaign;
- Поле `iteration` (1, 2, 3...) — номер итерации по одной теме;
- В `decision.md` добавить поле `next_run_plan` — конкретный план для следующей итерации;
- Скрипт `scripts/open_followups.py` — показывает все campaigns со статусом `needs-more-testing` или `inconclusive` и проверяет, есть ли у них follow-up campaign;
- Валидатор проверяет: если `outcome = needs-more-testing`, то `next_run_plan` не пуст.

**Impact:** Закрывает главную дыру MVP — campaigns перестают «зависать» без продолжения.

---

## 4. 🤖 Agent-Executable Research Workflow

**Проблема сейчас:** Workflow описан в markdown для человека. Агент (Gemini/Codex) читает workflow.md и пытается повторить шаги, но у него нет формализованного протокола. Каждый раз — импровизация.

**Что добавить:**
- Файл `.agents/workflows/run-research-campaign.md` (конвертация текущего workflow в agent-executable формат с `// turbo` аннотациями);
- Workflow описывает каждый шаг как конкретное действие с входом/выходом:
  ```
  1. Создать папку campaigns/<date>-<topic>/
  2. Заполнить plan.md из шаблона
  // turbo
  3. Запустить discover_sources.py
  4. Ревью sources.md (человек)
  5. Сгенерировать reviews.md по каждому источнику
  ...
  // turbo
  9. Запустить validate_campaign.py
  ```
- Добавить slash-команду `/research` для быстрого запуска.

**Impact:** Агент может запускать research loop semi-автономно, а не пытаться интерпретировать markdown-инструкции каждый раз.

---

## 5. 📐 Evidence-Grade Scoring для Experiments

**Проблема сейчас:** Experiment entry собирает текстовое описание результатов, но нет объективной шкалы. Первый эксперимент показал: оценки типа «weak support», «plausible but unproven» — субъективны и несравнимы.

**Что добавить:**
- В шаблон `experiment-entry.md` добавить шкалу evidence strength:
  ```
  ## Evidence Strength Score (1-5)
  - 1: Только документационное изменение, нет поведенческих данных
  - 2: Есть 1 кейс, но без сравнения с baseline
  - 3: Есть before/after сравнение, но на 1 кейсе
  - 4: Before/after на 2-3 кейсах, инварианты проверены
  - 5: Автоматизированный A/B тест с количественными метриками
  ```
- Минимальный порог для acceptance: score ≥ 3;
- Валидатор проверяет наличие `evidence_score` в frontmatter experiment.md;
- Analytics dashboard считает средний evidence score по campaigns.

**Impact:** Объективизирует решения accept/reject. Текущий campaign был бы score=1 — что сразу сигнализирует о недостаточности.

---

## 6. 🧠 Structured Memory с индексацией

**Проблема сейчас:** `accepted-patterns.md` и `anti-patterns.md` — плоские markdown-файлы. При 20+ паттернах поиск станет мучением. Нет способа быстро найти: «какие паттерны для agents-lab с confidence=high?»

**Что добавить:**
- Перейти на формат `memory/patterns/<pattern-id>.md` — один файл на паттерн, с frontmatter:
  ```yaml
  ---
  id: pattern-repo-grounding
  applies_to: agents-lab
  confidence: high
  valid_for: Gemini 2.5 Pro
  source_campaign: 2026-03-11-agent-instruction-patterns
  last_reviewed: 2026-03-13
  review_due: 2026-06-13
  sync_status: updated
  sync_target: agents-lab/templates/agent-instructions.md
  ---
  ```
- Скрипт `scripts/query_memory.py` для фильтрации: `--applies-to agents-lab --confidence high`;
- Автоматический alert: паттерны с просроченным `review_due`;
- Индексный файл `memory/INDEX.md` генерируется автоматически.

**Impact:** Memory превращается из журнала в **queryable knowledge base**.

---

## 7. 📋 Campaign Scaffold Generator

**Проблема сейчас:** Создание нового campaign = ручное копирование 6 файлов, заполнение frontmatter, создание папки с правильным именем. Муторно и error-prone.

**Что добавить:**
- Скрипт `scripts/new_campaign.py`:
  ```bash
  python scripts/new_campaign.py "tool-routing-patterns" --target agents-lab
  ```
  - создаёт папку `campaigns/2026-03-13-tool-routing-patterns/`;
  - генерирует все 6 файлов с правильным frontmatter;
  - создаёт `artifacts/` директорию;
  - подставляет даты, id, target_module;
  - если указан `--parent`, заполняет `parent_campaign` и `iteration`.

**Impact:** Запуск нового campaign — 1 команда вместо 10 минут ручной работы.

---

## 8. 🔄 Bi-Directional Traceability Links

**Проблема сейчас:** `decision.md` ссылается на proposal и experiment через `proposal_ref` / `experiment_ref`, но обратных ссылок нет. Из `accepted-patterns.md` (когда она заполнена) невозможно быстро перейти к эксперименту, который подтвердил паттерн.

**Что добавить:**
- В каждый campaign-файл добавить секцию `## Trace links` с полным графом:
  ```
  plan ← sources ← reviews → proposal → experiment → decision → memory
  ```
- Автоматическая генерация: скрипт `scripts/generate_trace_links.py` проходит по campaign и вставляет ссылки;
- В `memory/patterns/*.md` добавить обратную ссылку на campaign;
- Валидатор проверяет: все `_ref` поля в frontmatter указывают на существующие файлы.

**Impact:** Полный audit trail — от исходного источника до применённого паттерна и обратно.

---

## 9. ⏰ Stale Campaign Detection & Nudging

**Проблема сейчас:** Campaign может «зависнуть» в `in_progress` на недели. Нет напоминаний. Нет SLA.

**Что добавить:**
- В `config/research-topics.example.yaml` добавить `max_age_days: 14` — дефолтный SLA на один campaign;
- В валидатор добавить `--check-stale` флаг:
  - если `plan.status = in_progress` и `updated_at` старше `max_age_days` → warning;
  - если `decision.status = open` и campaign старше 30 дней → error;
- Скрипт `scripts/stale_campaigns.py` — выводит все «залипшие» campaigns с рекомендацией: close / continue / archive;
- При запуске нового campaign автоматически проверяет: нет ли незакрытых campaigns по той же теме.

**Impact:** Система сама напоминает о забытых исследованиях. Борьба с «research debt».

---

## 10. 🧪 Reproducible Experiment Artifacts

**Проблема сейчас:** Experiment фиксирует текстовое описание результатов, но не сохраняет сами артефакты: логи агента, diff промптов, before/after outputs. Первый experiment — это 39 строк текста. Проверить его нельзя.

**Что добавить:**
- В `campaign/artifacts/` добавить подпапки:
  ```
  artifacts/
  ├── baseline/          # снапшоты ДО изменения
  │   ├── agent_output_case1.md
  │   └── prompt_before.md
  ├── treatment/         # снапшоты ПОСЛЕ изменения
  │   ├── agent_output_case1.md
  │   └── prompt_after.md
  └── diffs/             # автоматически сгенерированные diff-ы
      └── prompt_diff.patch
  ```
- Скрипт `scripts/capture_baseline.py` — сохраняет текущее состояние целевых файлов перед экспериментом;
- Скрипт `scripts/capture_treatment.py` — сохраняет состояние после;
- Скрипт `scripts/generate_diff.py` — создаёт diff между baseline и treatment;
- Валидатор проверяет: если `experiment.status = completed`, folders `baseline/` и `treatment/` не пустые.

**Impact:** Эксперименты становятся **воспроизводимыми и верифицируемыми**, а не просто «я попробовал и вот что вышло».

---

## Матрица приоритетов

| # | Улучшение | Impact | Effort | Priority |
|---|-----------|--------|--------|----------|
| 7 | Campaign Scaffold Generator | 🟢 High | 🟢 Low | **P0** |
| 3 | Campaign Chaining | 🟢 High | 🟢 Low | **P0** |
| 5 | Evidence-Grade Scoring | 🟢 High | 🟢 Low | **P0** |
| 9 | Stale Campaign Detection | 🟡 Med | 🟢 Low | **P1** |
| 2 | Cross-Campaign Analytics | 🟢 High | 🟡 Med | **P1** |
| 6 | Structured Memory | 🟢 High | 🟡 Med | **P1** |
| 8 | Bi-Directional Traceability | 🟡 Med | 🟡 Med | **P2** |
| 10 | Reproducible Experiments | 🟢 High | 🟡 Med | **P2** |
| 4 | Agent-Executable Workflow | 🟢 High | 🔴 High | **P2** |
| 1 | Auto Source Discovery | 🔴 Very High | 🔴 High | **P3** |

> **Рекомендация:** Начни с P0 (scaffold, chaining, scoring) — три быстрых улучшения, которые сразу поменяют ощущение от работы с модулем. Затем P1 для системного контроля. P2-P3 — стратегические вложения.
