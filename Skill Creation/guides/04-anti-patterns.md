# 04. Анти-паттерны — Типичные ошибки при создании скиллов

> **Источники:**
> - [Skill Authoring Best Practices — Anti-patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
> - [Agent Skills Specification](https://agentskills.io/specification)

---

## ❌ 1. Мега-скилл (Too Broad Scope)

**Проблема:** Один скилл пытается покрыть слишком много задач.

**Почему плохо:** Перегружает контекстное окно, размывает описание (агент не может точно определить, когда активировать), сложно поддерживать.

```yaml
# ❌ Плохо
name: do-everything
description: Handles all code tasks including review, testing, deployment, monitoring.

# ✅ Хорошо — разделить на атомарные скиллы
name: reviewing-code
description: Performs thorough code reviews analyzing structure, bugs, and conventions.

name: deploying-apps
description: Deploys applications to production with verification and rollback support.
```

---

## ❌ 2. Перегрузка SKILL.md (Context Window Bloat)

**Проблема:** Вся документация запихнута в `SKILL.md` вместо использования progressive disclosure.

**Почему плохо:** Тело `SKILL.md` оптимально до **500 строк**. Перегрузка приводит к тому, что критическая информация теряется среди шума.

```markdown
# ❌ Плохо — 2000 строк в одном файле
---
name: api-integration
description: ...
---
[Тысячи строк справочника по API, примеров, ошибок, миграций...]

# ✅ Хорошо — progressive disclosure
---
name: api-integration
description: ...
---
# API Integration

## Quick start
[50 строк основных инструкций]

## Detailed reference
See [REFERENCE.md](references/REFERENCE.md) for complete API docs
See [EXAMPLES.md](references/EXAMPLES.md) for usage patterns
See [MIGRATION.md](references/MIGRATION.md) for version upgrades
```

> Источник: [Best Practices — Token budgets](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 3. Размытые описания (Vague Descriptions)

**Проблема:** Описание не содержит конкретных ключевых слов для обнаружения.

**Почему плохо:** Агент выбирает скилл из 100+ доступных, сравнивая запрос пользователя с описаниями. Размытое описание = скилл никогда не активируется.

```yaml
# ❌ Плохо
description: Helps with documents
description: Processes data
description: Does stuff with files

# ✅ Хорошо — что + когда
description: >
  Analyze Excel spreadsheets, create pivot tables, generate charts.
  Use when analyzing Excel files, spreadsheets, tabular data,
  or .xlsx files.
```

> Источник: [Best Practices — Writing effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 4. Windows-style пути

**Проблема:** Использование обратных слешей в путях.

**Почему плохо:** Unix-style пути работают везде. Windows-пути ломаются на Unix-системах.

```markdown
# ❌ Плохо
Run `scripts\helper.py`
See `reference\guide.md`

# ✅ Хорошо
Run `scripts/helper.py`
See `reference/guide.md`
```

> Источник: [Best Practices — Avoid Windows-style paths](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 5. Слишком много вариантов (Too Many Options)

**Проблема:** Представление множества альтернативных подходов без чёткой рекомендации.

**Почему плохо:** Агент запутается в выборе. Предоставьте **один основной путь** с escape hatch для особых случаев.

```markdown
# ❌ Плохо — слишком много выбора
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

# ✅ Хорошо — дефолт + escape hatch
Use pdfplumber for text extraction:
```python
import pdfplumber
```
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

> Источник: [Best Practices — Avoid offering too many options](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 6. Глубокая вложенность ссылок (Deep Nesting)

**Проблема:** Файлы ссылаются на файлы, которые ссылаются на ещё файлы.

**Почему плохо:** Агент может использовать `head -100` для предпросмотра вложенных файлов, получая **неполную информацию**.

```markdown
# ❌ Плохо — глубокая вложенность
SKILL.md → advanced.md → details.md → actual-info.md

# ✅ Хорошо — один уровень
SKILL.md → advanced.md
SKILL.md → reference.md
SKILL.md → examples.md
```

> Источник: [Best Practices — Avoid deeply nested references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 7. Несогласованная терминология

**Проблема:** Одно и то же понятие называется по-разному в разных частях скилла.

**Почему плохо:** Смешивание терминов сбивает агент с толку.

```
# ❌ Плохо
То "API endpoint", то "URL", то "API route", то "path"
То "field", то "box", то "element", то "control"

# ✅ Хорошо
Всегда "API endpoint"
Всегда "field"
Всегда "extract"
```

> Источник: [Best Practices — Use consistent terminology](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 8. Время-зависимая информация

**Проблема:** Инструкции привязаны к конкретным датам.

**Почему плохо:** Информация устаревает, но скилл продолжает использоваться.

```markdown
# ❌ Плохо
If you're doing this before August 2025, use the old API.

# ✅ Хорошо
## Current method
Use the v2 API endpoint.

## Old patterns
<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
</details>
```

> Источник: [Best Practices — Avoid time-sensitive information](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## ❌ 9. Несовпадение name и директории

**Проблема:** Поле `name` в frontmatter не совпадает с именем папки.

**Почему плохо:** Стандарт **требует** совпадения. Некоторые платформы не обнаружат скилл с несовпадающими именами.

```
# ❌ Плохо
Папка: my-awesome-skill/
name: awesome-skill          # ← не совпадает!

# ✅ Хорошо
Папка: my-awesome-skill/
name: my-awesome-skill       # ← совпадение!
```

> Источник: [agentskills.io/specification — name field](https://agentskills.io/specification#name-field) — *"Must match the parent directory name"*

---

## ❌ 10. Интерактивные скрипты

**Проблема:** Скрипты требуют ввода от пользователя через stdin.

**Почему плохо:** Агент не может взаимодействовать с интерактивными промптами — скрипт зависнет.

```bash
# ❌ Плохо — ждёт ввода, агент зависнет
$ python scripts/deploy.py
Target environment: _

# ✅ Хорошо — аргументы через CLI
$ python scripts/deploy.py --env staging --tag v1.2.3
```

> Источник: [agentskills.io/skill-creation/using-scripts — Avoid interactive prompts](https://agentskills.io/skill-creation/using-scripts#avoid-interactive-prompts)

---

## ❌ 11. Рационализация (Skipping Steps Under Pressure)

**Проблема:** Агент под давлением лимитов контекста или при длинных workflow начинает пропускать шаги — особенно ревью, тесты и валидации.

**Почему плохо:** LLM склонны к «рационализации» — они находят логичное обоснование для пропуска шагов: «этот шаг уже покрыт предыдущим», «в данном случае тест не нужен», «валидация очевидно пройдёт».

```markdown
# ❌ Пропуск шагов (агент «рационализирует»)
## Workflow
1. Generate code
2. Run tests
3. Deploy

# Агент решает: «код простой, тесты не нужны» → deploy без тестов

# ✅ Явное закрытие лазеек
## Workflow
1. Generate code
2. Run tests — **ОБЯЗАТЕЛЬНО, даже если изменения кажутся тривиальными**
3. Deploy — **ТОЛЬКО после успешных тестов, без исключений**

⚠️ НИКОГДА не пропускай шаг 2. Если тесты падают — исправь и запусти снова.
Не рационализируй: «это и так работает» — запусти тесты.
```

### Защита от рационализации в скиллах

Для каждого критического шага используйте двойную формулировку:
1. **Позитивная:** «Делай X»
2. **Негативная:** «Ни в коем случае не пропускай X, даже если...»

```markdown
# Паттерн: Закрытие лазеек
## Step 3: Validate configuration
Run: `python scripts/validate.py config.yaml`

**IMPORTANT:** Run this step EVERY time. Do NOT skip it even if:
- The changes look trivial
- You've validated a similar config before
- The previous step completed without errors
```

### Обязательная секция `## Red Flags` в скиллах

Для workflow-скиллов добавляйте секцию Red Flags — перечень признаков того, что что-то пошло не так:

```markdown
## Red Flags
STOP and re-evaluate if any of these occur:
- Validation script returns warnings (not just errors)
- Output file size differs by >20% from expected
- Any step completes suspiciously fast (<1s for complex operations)
- You feel an urge to skip a verification step
```

---

## ❌ 12. Бесконечные циклы (Infinite Loops)

**Проблема:** Агент застревает в цикле — тест падает → сгенерирован фикс → фикс не работает → сгенерирован тот же фикс → ...

**Почему плохо:** LLM не всегда понимают, что делают одно и то же. Они могут:
- Генерировать идентичные "исправления" каждый раз
- Сжигать токены без прогресса
- Застрять в цикле "попытка → ошибка → та же попытка"

### Обязательная секция `## Circuit Breaker (Anti-Loop)`

Добавляйте во все workflow-скиллы:

```markdown
## Circuit Breaker (Anti-Loop)

Prevent infinite retry loops:

- **Max Retries:** Do NOT attempt the same action more than 3 times without a different approach
- **Progress Check:** If retrying, verify each attempt produces DIFFERENT results
- **Escalation:** After 3 failed attempts, STOP and write an `escalation_report.md` describing:
  - What you tried
  - What failed
  - What alternatives remain
  - Ask the user for guidance before continuing
```

### Типичные паттерны циклов

| Паттерн цикла | Пример | Как разорвать |
|---------------|--------|---------------|
| **Identical retry** | Тест падает → тот же фикс → тест падает | После 2-й попытки: изменить подход |
| **Oscillation** | Fix A → Fix B (отменяет A) → Fix A → ... | После 2-х переключений: STOP, ask user |
| **Rubber stamp** | Ревью всегда "проходит" | Добавить реальные проверки в Red Flags |

> Источники: [Anthropic: Circuit Breakers in LLM Agents], [Context Engineering Best Practices 2026]
