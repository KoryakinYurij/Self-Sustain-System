# 05. Продвинутые паттерны — Скрипты, Workflows, Feedback Loops

> **Источники:**
> - [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts)
> - [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
> - [Agent Skills Specification](https://agentskills.io/specification)

---

## Скрипты в скиллах

### Два подхода: One-off команды vs. bundled скрипты

#### One-off команды (без локальных файлов)

Используйте пакетные запуски через менеджеры:

| Runner | Пример | Требования |
|--------|--------|------------|
| `npx` | `npx eslint@9 --fix .` | Node.js (входит в комплект) |
| `uvx` | `uvx ruff@0.8.0 check .` | uv (отдельная установка) |
| `bunx` | `bunx create-vite@6 my-app` | Bun |
| `deno run` | `deno run npm:create-vite@6 my-app` | Deno |
| `go run` | `go run golang.org/x/tools/cmd/goimports@v0.28.0 .` | Go |

**Рекомендации:**
- **Всегда пиньте версии**: `npx eslint@9.0.0` — для воспроизводимости
- **Указывайте prerequisites** в SKILL.md вместо предположений
- **Сложные команды → скрипты** — если команда слишком длинная, перенесите в `scripts/`
- Для системных требований используйте поле `compatibility` в frontmatter

> Источник: [agentskills.io/skill-creation/using-scripts — One-off commands](https://agentskills.io/skill-creation/using-scripts#one-off-commands)

#### Bundled скрипты (самодостаточные)

##### Python (PEP 723)

```python
# /// script
# dependencies = [
#     "beautifulsoup4",
# ]
# ///
from bs4 import BeautifulSoup
# ...
```

Запуск: `uv run scripts/extract.py`

##### Deno

```typescript
#!/usr/bin/env -S deno run
import * as cheerio from "npm:cheerio@1.0.0";
// ...
```

Запуск: `deno run scripts/extract.ts`

##### Bun

```typescript
#!/usr/bin/env bun
import * as cheerio from "cheerio@1.0.0";
// ...
```

Запуск: `bun run scripts/extract.ts`

> Источник: [agentskills.io/skill-creation/using-scripts — Self-contained scripts](https://agentskills.io/skill-creation/using-scripts#self-contained-scripts)

### Ссылки на скрипты из SKILL.md

```markdown
## Available scripts
- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data

## Workflow
1. Run the validation script:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```
2. Process the results:
   ```bash
   python3 scripts/process.py --input results.json
   ```
```

> Источник: [agentskills.io/skill-creation/using-scripts — Referencing scripts](https://agentskills.io/skill-creation/using-scripts#referencing-scripts-from-skill-md)

---

## Проектирование скриптов для агентного использования

### 1. Никаких интерактивных промптов

```bash
# ❌ Плохо — зависнет, ожидая ввод
$ python scripts/deploy.py
Target environment: _

# ✅ Хорошо — ясная ошибка с подсказкой
$ python scripts/deploy.py
Error: --env is required.
Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

### 2. Документируйте через --help

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Process input data and produce a summary report.

Options:
  --format FORMAT  Output format: json, csv, table (default: json)
  --output FILE    Write output to FILE instead of stdout
  --verbose        Print progress to stderr

Examples:
  scripts/process.py data.csv
  scripts/process.py --format csv --output report.csv data.csv
```

### 3. Полезные сообщения об ошибках

```
Error: --format must be one of: json, csv, table. Received: "xml"
```

### 4. Структурированный вывод

```bash
# ❌ Плохо — сложно парсить
NAME          STATUS    CREATED
my-service    running   2025-01-15

# ✅ Хорошо — JSON с однозначными полями
{"name": "my-service", "status": "running", "created": "2025-01-15"}
```

### 5. Дополнительные принципы

| Принцип | Описание |
|---------|----------|
| **Идемпотентность** | "Create if not exists" вместо "create and fail on duplicate" |
| **Ограничения входа** | Отклоняйте неоднозначный ввод с ясной ошибкой |
| **Dry-run** | Флаг `--dry-run` для деструктивных операций |
| **Exit codes** | Различные коды для разных типов ошибок, документировать в `--help` |
| **Безопасные дефолты** | `--confirm` / `--force` для опасных операций |
| **Предсказуемый размер вывода** | Дефолт: summary. `--offset` для пагинации. `--output` для записи в файл |

> Источник: [agentskills.io/skill-creation/using-scripts — Designing scripts for agentic use](https://agentskills.io/skill-creation/using-scripts#designing-scripts-for-agentic-use)

---

## Workflows (Рабочие процессы)

Для сложных операций — разбивайте на чёткие шаги с чеклистом прогресса.

### Паттерн: Workflow с чеклистом

```markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
This extracts form fields and saves to `fields.json`.

**Step 2: Create field mapping**
Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**
Run: `python scripts/validate_fields.py fields.json`
Fix any validation errors before continuing.
```

> Источник: [Best Practices — Use workflows for complex tasks](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## Feedback Loops (Петли обратной связи)

### Паттерн: Run → Validate → Fix → Repeat

Значительно улучшает качество выхода.

#### Без кода (через reference-документы)

```markdown
## Content review process
1. Draft your content following STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
```

#### С кодом (через скрипты валидации)

```markdown
## Document editing process
1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python scripts/pack.py unpacked_dir/ output.docx`
```

> Источник: [Best Practices — Implement feedback loops](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## Итеративная разработка скиллов

### Подход: Создание → Оценка → Улучшение

1. **Создайте минимум 3 теста** — конкретные сценарии использования
2. **Тестируйте с разными моделями** — что работает для мощных моделей, может требовать больше деталей для лёгких
3. **Наблюдайте** — как агент навигирует по скиллу? Какие ошибки совершает?
4. **Итерируйте** — уточняйте инструкции на основе наблюдений
5. **Собирайте фидбек** — если скилл используется командой

> Источник: [Best Practices — Evaluation and iteration](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## Пример: Полная структура сложного скилла

```
pdf-processing/
├── SKILL.md               # Основные инструкции (загружается при активации)
├── FORMS.md               # Гайд по заполнению форм (загружается по необходимости)
├── reference.md           # API справочник (загружается по необходимости)
├── examples.md            # Примеры использования (загружается по необходимости)
└── scripts/
    ├── analyze_form.py    # Утилита (исполняется, не загружается в контекст)
    ├── fill_form.py       # Скрипт заполнения форм
    └── validate.py        # Скрипт валидации
```

> Источник: [Best Practices — Visual overview: From simple to complex](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## Subagent-Driven Development (Оркестрация)

Для задач с высоким риском ошибок разделяйте роли между агентами:

### Паттерн: Исполнитель → Ревьюер ТЗ → Ревьюер Кода

```
Агент-Исполнитель → реализация
       ↓
Агент-Ревьюер ТЗ → «Соответствует ли результат спецификации?»
       ↓ (если нет → вернуть Исполнителю)
Агент-Ревьюер Кода → «Качество кода, edge cases, безопасность?»
       ↓ (если нет → вернуть Исполнителю)
Результат ✅
```

**Порядок важен:** сначала spec compliance, потом code quality. Нет смысла полировать код, который не соответствует ТЗ.

### Prompt-шаблоны для субагентов

```markdown
## Spec Reviewer prompt
You are a specification compliance reviewer. Your ONLY job is to verify
that the implementation matches the requirements.

**Requirements:**
[paste spec here]

**Implementation:**
[paste code here]

**Instructions:**
1. List each requirement from the spec
2. For each: mark ✅ (met) or ❌ (not met) with evidence
3. If ANY requirement is ❌, the review FAILS
4. Do NOT comment on code quality — only spec compliance
```

```markdown
## Code Reviewer prompt
You are a code quality reviewer. The spec compliance has ALREADY been verified.
Your ONLY job is code quality.

**Review for:**
- Edge cases and error handling
- Security vulnerabilities
- Performance issues
- Maintainability

**Do NOT re-check spec compliance — that is already done.**
```

---

## Eval-тестирование скиллов (Evals-as-Code)

> 📎 **Anthropic Evals**: code graders + model graders + human graders, интегрированные в pipeline.

Evals — это **непрерывный мониторинг** качества после деплоя (отличие от TDD, который применяется при создании).

### Два типа graders

#### 1. Code-based grader (детерминированный)

Для скиллов с предсказуемым выходом:

```python
# scripts/eval_grader.py
import json, sys

result = json.load(open(sys.argv[1]))

checks = {
    "has_output_file": "output" in result,
    "valid_json": isinstance(result.get("data"), dict),
    "exit_code_zero": result.get("exit_code") == 0,
    "no_errors": len(result.get("errors", [])) == 0,
}

passed = all(checks.values())
print(json.dumps({"passed": passed, "checks": checks}))
sys.exit(0 if passed else 1)
```

#### 2. LLM-as-judge grader (для open-ended выхода)

Для скиллов, где качество субъективно (тексты, анализы, отчёты):

```markdown
## Eval rubric for code-review skill
Rate the output on a 1-5 scale for each criterion:

1. **Completeness** — were all files reviewed?
2. **Specificity** — are suggestions actionable (not generic)?
3. **Accuracy** — are the identified issues real?
4. **Prioritization** — are critical issues flagged first?

Score >= 4 on ALL criteria = PASS
Any score < 3 = FAIL
```

### Интеграция в workflow

```
При каждом изменении скилла:
1. Запусти code-based graders → pass/fail
2. Запусти LLM-as-judge → score
3. Если fail или score < threshold → блокируй деплой
4. Логируй результаты для trend-анализа
```

