# 10 Улучшений для Research-модуля

**Проект:** Self-Sustain-System
**Основание:** Анализ 5 SOTA-статей об AI-агентах

---

## Источники анализа

| № | Статья | Ключевой инсайт |
|---|--------|-----------------|
| 1 | Anthropic: Building effective agents | Простые компонуемые паттерны > сложные фреймворки |
| 2 | Anthropic: Memory tool docs | Memory-артефакты для продолжения между сессиями |
| 3 | HumanLayer: Writing CLAUDE.md | CLAUDE.md — единственный файл в каждом разговоре |
| 4 | Gemini CLI: Skills docs | Skill = модульный пакет с персоной и ресурсами |
| 5 | Agent Factory: Gemini CLI deep dive | Tight feedback loop для human-AI collaboration |

---

## Резюме

Проведён анализ репозитория Self-Sustain-System и сопоставление его текущей архитектуры research-loop модуля с лучшими практиками от Anthropic, HumanLayer и Google.

**Текущее состояние research-loop** уже содержит сильные элементы:
- Campaign-first архитектура
- Trust Tier система для источников (T1–T4)
- Definition of Done для цикла
- Валидация через скрипты

Однако статьи раскрывают дополнительные паттерны, которые могут существенно усилить систему.

---

## Улучшение 1: Session Handoff Protocol

**Источник:** Anthropic Memory Tool Docs

### Контекст

Anthropic Memory Tool Docs описывает паттерн для долгих проектов: первая сессия создаёт memory-артефакты до начала работы — progress log (что сделано и что дальше), feature checklist и ссылку на init-скрипт. Каждая следующая сессия подхватывает работу точно с того места, где остановилась.

Это именно то, что research-loop строит через `plan.md` + `decision.md` + `artifacts/`, но **не имеет механизма автоматического восстановления контекста**.

### Конкретное изменение

Добавить в начало каждой campaign директории файл `SESSION_STATE.md` с machine-readable структурой:

```yaml
---
current_step: reviews        # Текущий этап workflow
last_action: "Completed sources.md with 4 sources"
next_action: "Write reviews.md for each source"
blockers: []                 # Если есть
context_summary: "Researching agent instruction patterns..."
updated_at: 2026-03-15
---
```

**Как это работает:**
- Файл обновляется после каждого шага цикла
- При старте новой сессии агент читает `SESSION_STATE.md`
- Продолжает с нужного места без необходимости читать все файлы campaign

**Приоритет:** 🔴 High

---

## Улучшение 2: CLAUDE.md как Grounding File для Research-Loop

**Источник:** HumanLayer: Writing a good CLAUDE.md

### Контекст

HumanLayer подчёркивает: **coding agents ничего не знают о проекте в начале каждой сессии**. CLAUDE.md — единственный файл, который по умолчанию попадает в каждый разговор.

Это имеет три важных следствия:
1. Агент должен быть снабжён всем важным заново при каждом запуске
2. CLAUDE.md — предпочтительный способ доставки контекста
3. Это критично для эффективности работы

### Конкретное изменение

Создать `RESEARCH_LOOP.md` в корне `modules/research-loop/` с критически важной информацией:

```markdown
# Research Loop — Quick Context

## Структура
- campaigns/ — активные и завершённые research-циклы
- templates/ — шаблоны для записей
- scripts/validate_campaign.py — валидация

## Активные campaigns
| Campaign | Статус | Следующий шаг |
|----------|--------|---------------|
| agent-instruction-patterns | in_progress | reviews.md |

## Последние принятые patterns
- [ссылка на pattern] — краткое описание

## Критические anti-patterns
- [ссылка] — чего избегать

## Команда валидации
python modules/research-loop/scripts/validate_campaign.py modules/research-loop/campaigns
```

**Результат:** Экономия токенов на объяснение структуры каждый раз.

**Приоритет:** 🔴 High

---

## Улучшение 3: Workflow vs Agent Distinction в Experiment Phase

**Источник:** Anthropic: Building effective agents

### Контекст

Anthropic делает важное архитектурное различие:

| Тип | Определение | Пример в research-loop |
|-----|-------------|------------------------|
| **Workflow** | LLMs и инструменты оркестрируются через предопределённые пути кода | Сбор источников, заполнение templates |
| **Agent** | LLMs динамически направляют свои процессы | Формирование proposal, интерпретация experiment |

### Конкретное изменение

Разделить `experiment.md` на две секции с разными подходами:

```markdown
# Experiment

## Procedure [WORKFLOW]
Детерминированные шаги — следовать точно:
1. Открыть файлы: [список]
2. Запустить команды: [команды]
3. Собрать метрики: [метрики]

## Analysis [AGENT-DRIVEN]
Интерпретация результатов — агент имеет полную свободу:
- Выявить паттерны
- Сформулировать выводы
- Оценить соответствие proposal
```

**Результат:** Агент понимает, где нужно следовать инструкции, а где проявлять инициативу.

**Приоритет:** 🟡 Medium

---

## Улучшение 4: Progressive Disclosure для Campaign Templates

**Источник:** Gemini CLI Skills Docs + Anthropic Best Practices

### Контекст

Gemini CLI Skills Docs описывает, что skill при активации загружает инструкции и ресурсы в контекст. Но Best Practices от Anthropic подчёркивают:

> Progressive Disclosure критичен — не грузить всё сразу.
> - Тело SKILL.md: < 150 слов для простых задач, < 500 для сложных
> - Остальное выносится в `references/`

Текущие templates research-loop уже компактны, но нет явного паттерна для расширения.

### Конкретное изменение

Для каждого template создать `references/` директорию:

```
templates/
├── source-entry.md          # ~100 слов — базовый шаблон
└── references/
    └── source-entry-examples.md  # 3-5 примеров разных Trust Tier
```

**Как работает:**
- Агент обращается к examples только когда нужно
- Не загружает их по умолчанию
- Снижает токен-нагрузку при простых campaign
- Даёт глубину при сложных

**Приоритет:** 🟡 Medium

---

## Улучшение 5: Human-Governed Feedback Loop

**Источник:** Agent Factory — Deep Dive into Gemini CLI

### Контекст

Taylor Mullen из команды Gemini CLI объясняет:

> Реальный challenge не поднять AI с нуля, а создать **tight feedback loop для human-AI collaboration at scale**. Принцип: делай то, что делал бы человек, и не срезай углы.

Это ровно модель research-loop: human-governed loop. Но в текущей реализации **нет явного checkpoint для человеческого review**.

### Конкретное изменение

Добавить обязательный `REVIEW_CHECKPOINT.md` в каждый campaign:

```markdown
# Review Checkpoint

## Summary
[1-2 абзаца для быстрого чтения человеком]

## Proposed Change
[Что именно предлагается изменить]

## Risk Assessment
- Риск 1: [описание и митигация]
- Риск 2: [описание и митигация]

## Approval Criteria
- [ ] Критерий 1
- [ ] Критерий 2

## Sign-off
- Reviewed by: ____________
- Date: ____________
- Approved: [ ] Yes [ ] No [ ] Needs revision
```

**Правило:** Эксперимент не запускается без подтверждённого sign-off.

**Валидация:** Скрипт проверяет наличие sign-off перед разрешением перехода к experiment фазе.

**Приоритет:** 🔴 High

---

## Улучшение 6: Simple Composable Patterns Over Frameworks

**Источник:** Anthropic: Building effective agents

### Контекст

Anthropic формулирует ключевой вывод года работы с dozens of teams:

> **The most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns.**

Это прямо относится к архитектуре research-loop: текущая структура — это именно composable pattern.

### Конкретное изменение

Документировать каждый шаг цикла как независимый **composable unit** с чётким интерфейсом:

```markdown
# Unit: sources-collection

## Вход
- topic: тема исследования
- trust_tiers: допустимые уровни доверия

## Выход
- sources.md: файл с 3+ источниками
- каждый источник имеет Trust Tier

## Инварианты
- минимум 1 источник T1 или T2
- все источники релевантны теме
```

**Результат:**
- Комбинирование шагов в разных последовательностях
- Переиспользование отдельных шагов
- Изолированное тестирование

**Документ:** Создать `PATTERNS.md` в `core/contracts/`

**Приоритет:** 🟡 Medium

---

## Улучшение 7: Just-In-Time Context Retrieval Pattern

**Источник:** Anthropic Memory Tool Docs

### Контекст

Memory Tool Docs описывает ключевой примитив:

> **Just-in-time context retrieval** — rather than loading all relevant information upfront, agents store what they learn in memory and pull it back on demand.

Это критично для long-running workflows, где загрузка всего сразу переполнит context window.

### Конкретное изменение

Реорганизовать `accepted-patterns.md` из плоского списка в структурированный индекс:

```markdown
# Accepted Patterns Index

## Agent Instructions
| Pattern | Trigger | Location |
|---------|---------|----------|
| CSO Description | writing skill description | patterns/cso-description.md |
| Progressive Disclosure | skill > 150 words | patterns/progressive-disclosure.md |

## Code Quality
| Pattern | Trigger | Location |
|---------|---------|----------|
| Deterministic Scripts | critical operations | patterns/deterministic-scripts.md |
```

**Как работает:**
1. Агент сканирует индекс
2. Определяет релевантные паттерны по trigger conditions
3. Загружает полные описания только нужных

**Результат:** Reduces context bloat при каждом обращении к memory.

**Приоритет:** 🟡 Medium

---

## Улучшение 8: Agent-Computer Interface (ACI) для Research Artifacts

**Источник:** Anthropic: Building effective agents

### Контекст

Anthropic вводит концепцию **Agent-Computer Interface (ACI)**:

> Интерфейс между агентом и компьютером должен быть оптимизирован так же, как UI оптимизирован для людей.

Для research-loop это означает: артефакты должны быть максимально удобны для обработки агентом, а не только для чтения человеком.

### Конкретное изменение

Добавить machine-readable слои к ключевым артефактам:

```yaml
---
# Расширенный frontmatter
id: campaign-2026-03-15-topic
status: in_progress
computed_fields:
  sources_count: 4
  avg_trust_tier: 1.75
  proposal_confidence: high
---

# Content...

## Structured Data
```json
{
  "sources": ["S1", "S2", "S3", "S4"],
  "trust_tiers": {"T1": 2, "T2": 2, "T3": 0, "T4": 0},
  "artifacts_generated": ["sources.md", "reviews.md"]
}
```
```

**Валидация:** Скрипт проверяет как структуру, так и семантику через анализ computed fields.

**Приоритет:** 🟢 Low

---

## Улучшение 9: Skill-подобная Модульность для Campaign Types

**Источник:** Gemini CLI Skills Docs

### Контекст

Gemini CLI Skills Docs определяет skill как:

> Self-contained directory, который packs instructions and assets into discoverable capability. При активации skill загружает свой контекст в сессию.

Это близко к концепции campaign, но campaigns сейчас унифицированы по структуре, хотя **типы исследований могут требовать разных подходов**.

### Конкретное изменение

Создать систему campaign-types как специализированные skill-подобные модули:

| Type | Фокус | Особенности |
|------|-------|-------------|
| `literature-review` | Сбор и анализ текстов | Акцент на sources.md, reviews.md |
| `code-analysis` | Исследование кодовых баз | Дополнительные артефакты: codebase-map.md |
| `experiment-driven` | Тестирование гипотез | Акцент на experiment.md, metrics |
| `pattern-extraction` | Выявление паттернов | Акцент на proposal.md, pattern-candidates.md |

**Реализация:**

```
templates/
├── literature-review/
│   ├── SKILL.md
│   └── required_artifacts.txt
├── code-analysis/
│   ├── SKILL.md
│   └── required_artifacts.txt
```

Frontmatter campaign указывает `type`, валидация применяется соответственно.

**Приоритет:** 🟢 Low

---

## Улучшение 10: Explicit Trust Tier Enforcement

**Источник:** Anthropic: Building effective agents + Composite Analysis

### Контекст

`workflow.md` уже содержит Trust Tier систему (T1–T4), но она **не имеет программного enforcement**.

Anthropic подчёркивает: guardrails и ограничения критичны для надёжности.

**Текущее правило:** T4 источники допускаются, но должны быть явно помечены и **не могут быть единственным основанием для proposal**.

**Проблема:** Без enforcement это правило соблюдается только вручную.

### Конкретное изменение

Расширить `validate_campaign.py` для проверки Trust Tier правил:

```python
def validate_trust_tiers(campaign_path):
    """Проверка Trust Tier правил"""
    sources = parse_sources_md(campaign_path / "sources.md")
    proposal = parse_proposal_md(campaign_path / "proposal.md")

    errors = []
    warnings = []

    # 1. Каждый источник должен иметь Trust Tier
    for s in sources:
        if not s.trust_tier:
            errors.append(f"Source {s.id} missing Trust Tier")

    # 2. Минимум один T1 или T2 источник
    high_trust = [s for s in sources if s.trust_tier in ['T1', 'T2']]
    if len(high_trust) == 0:
        errors.append("No T1/T2 sources found")

    # 3. Proposal основан исключительно на T3/T4?
    if proposal.evidence_only_t3_t4():
        warnings.append("Proposal based only on T3/T4 sources")

    return ValidationResult(errors, warnings)
```

**Результат валидации:** Trust Tier Report с рекомендациями по усилению evidence base.

**Приоритет:** 🔴 High

---

## Сводная таблица

| № | Улучшение | Источник | Приоритет |
|---|-----------|----------|-----------|
| 1 | Session Handoff Protocol | Anthropic Memory | 🔴 High |
| 2 | CLAUDE.md Grounding File | HumanLayer | 🔴 High |
| 3 | Workflow vs Agent Distinction | Anthropic Agents | 🟡 Medium |
| 4 | Progressive Disclosure Templates | Gemini + Anthropic | 🟡 Medium |
| 5 | Human-Governed Feedback Loop | Agent Factory | 🔴 High |
| 6 | Composable Patterns Documentation | Anthropic Agents | 🟡 Medium |
| 7 | Just-In-Time Context Retrieval | Anthropic Memory | 🟡 Medium |
| 8 | ACI для Artifacts | Anthropic Agents | 🟢 Low |
| 9 | Campaign Types System | Gemini Skills | 🟢 Low |
| 10 | Trust Tier Enforcement | Composite | 🔴 High |

---

## Заключение

Предложенные 10 улучшений основаны на production-проверенных паттернах от Anthropic, Google и опытных практиков из HumanLayer.

**Каждое улучшение:**
- Имеет чёткую реализацию
- Не требует фундаментальной перестройки архитектуры
- Основано на реальном опыте production-систем

**Приоритетные улучшения для ближайшего спринта:** 1, 2, 5, 10

---

> **Ключевой инсайт из всех пяти статей:** успешные AI-системы строятся не на сложности, а на правильных абстракциях и tight feedback loops. Research-loop модуль уже движется в этом направлении — предложенные улучшения ускоряют и усиливают этот курс.
