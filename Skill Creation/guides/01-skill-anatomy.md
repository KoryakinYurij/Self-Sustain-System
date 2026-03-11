# 01. Анатомия Agent Skill — Полная структура

> **Источники:**
> - [Agent Skills Specification](https://agentskills.io/specification) — официальная спецификация
> - [Gemini CLI: Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)
> - [Gemini CLI: Creating Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/creating-skills.md)

---

## Что такое Agent Skill?

Agent Skills — это **открытый формат** для расширения возможностей AI-агентов специализированными знаниями и рабочими процессами. Скилл — это самодостаточная директория, упаковывающая инструкции и ресурсы в обнаруживаемую способность.

> Источник: [agentskills.io](https://agentskills.io) — *"A simple, open format for giving agents new capabilities and expertise."*

### Три ключевых свойства скиллов

1. **Self-documenting** — автор или пользователь может прочитать `SKILL.md` и понять, что скилл делает
2. **Extensible** — от простых текстовых инструкций до исполняемого кода и шаблонов
3. **Portable** — это просто файлы, которые легко редактировать, версионировать и делиться

> Источник: [agentskills.io/what-are-skills](https://agentskills.io/what-are-skills)

---

## Структура директории

```
my-skill/
├── SKILL.md       # (Обязательно) Инструкции + метаданные
├── scripts/       # (Опционально) Исполняемый код
├── references/    # (Опционально) Статическая документация
└── assets/        # (Опционально) Шаблоны и ресурсы
```

> Источник: [agentskills.io/specification — Directory structure](https://agentskills.io/specification#directory-structure)

---

## SKILL.md — сердце скилла

### YAML Frontmatter (обязательно)

```yaml
---
name: my-skill
description: Описание ЧТО делает и КОГДА использовать.
---
```

#### Обязательные поля

| Поле | Правила | Источник |
|------|---------|----------|
| `name` | 1-64 символа. Unicode строчные буквенно-цифровые символы и дефисы. Не начинается/не заканчивается на `-`. Без `--`. **Должно совпадать с именем родительской директории.** | [Spec: name](https://agentskills.io/specification#name-field) |
| `description` | 1-1024 символа. Описывает ЧТО делает скилл и КОГДА его использовать. Должно содержать конкретные ключевые слова для обнаружения агентом. | [Spec: description](https://agentskills.io/specification#description-field) |

#### Опциональные поля

| Поле | Описание | Источник |
|------|----------|----------|
| `license` | Лицензия скилла. Короткое имя или ссылка на файл. | [Spec: license](https://agentskills.io/specification#license-field) |
| `compatibility` | 1-500 символов. Требования к окружению: ОС, пакеты, сеть. | [Spec: compatibility](https://agentskills.io/specification#compatibility-field) |
| `metadata` | Произвольные key-value пары (string→string). Для кастомных свойств. | [Spec: metadata](https://agentskills.io/specification#metadata-field) |
| `allowed-tools` | Список инструментов с предварительным одобрением. Экспериментальное поле. | [Spec: allowed-tools](https://agentskills.io/specification#allowed-tools-field) |

#### Примеры name — правильные и неправильные

```yaml
# ✅ Правильно
name: pdf-processing
name: data-analysis
name: code-review

# ❌ Неправильно
name: PDF-Processing    # uppercase запрещён
name: -pdf              # нельзя начинать с дефиса
name: pdf--processing   # двойные дефисы запрещены
```

> Источник: [agentskills.io/specification — name field](https://agentskills.io/specification#name-field)

#### Примеры description

> **Важно:** Для многострочных значений в YAML используйте `>` (сохраняет переносы как пробелы) или `|` (сохраняет переносы строк).

```yaml
# ✅ Хороший — конкретный, с триггерами
description: >
  Extract text and tables from PDF files, fill forms, merge documents.
  Use when working with PDF documents or when the user mentions PDFs, forms, or
  document extraction.

# ❌ Плохой — слишком общий
description: Helps with PDFs.
```

> Источник: [agentskills.io/specification — description field](https://agentskills.io/specification#description-field)

### Стандарт именования: Герундий (Verb-first)

Имя скилла должно начинаться с **действия** (герундий или глагольная форма):

```yaml
# ✅ Правильно — действие/герундий
name: creating-skills
name: systematic-debugging
name: processing-pdfs
name: deploying-apps

# ❌ Неправильно — существительное/агент
name: skill-creator        # кто, а не что
name: debugging-guide      # документ, а не действие
name: pdf-helper           # слишком общее
```

**Почему:** герундий точнее описывает *что скилл делает*, а не *чем является*, что помогает агенту при discovery.

### Body Content (Markdown)

Тело `SKILL.md` — это Markdown с инструкциями для агента:
- Пошаговые инструкции
- Примеры входов/выходов
- Обработка граничных случаев

> Источник: [agentskills.io/specification — Body content](https://agentskills.io/specification#body-content)

---

## Опциональные директории

### `scripts/`
Исполняемый код (Python, Bash, Node.js, Deno, Bun, Ruby, Go). Скрипты должны:
- Быть самодостаточными или чётко документировать зависимости
- Включать полезные сообщения об ошибках
- Корректно обрабатывать граничные случаи

### `references/`
Статическая документация, на которую ссылается `SKILL.md`. Имена файлов ниже — это только возможные примеры, а не строгий стандарт:
- `REFERENCE.md` — пример детального технического справочника
- `FORMS.md` — пример шаблонов форм или структурированных данных
- Доменные файлы (`finance.md`, `legal.md` и т.д.)

### `assets/`
- Шаблоны (документов, конфигураций)
- Изображения (диаграммы, примеры)
- Файлы данных (таблицы, схемы)

> Источник: [agentskills.io/specification — Optional directories](https://agentskills.io/specification#optional-directories)

---

## Progressive Disclosure — Прогрессивное раскрытие

Ключевая концепция эффективности скиллов — **трёхуровневое раскрытие информации**:

| Уровень | Что загружается | Когда | Бюджет |
|---------|----------------|-------|--------|
| 1. Метаданные | `name` + `description` | При старте сессии для ВСЕХ скиллов | ~100 токенов |
| 2. Инструкции | Полное тело `SKILL.md` | Когда агент активирует скилл | < 5000 токенов (рекомендовано) |
| 3. Ресурсы | Файлы из `scripts/`, `references/`, `assets/` | Только по необходимости | По запросу |

> Источник: [agentskills.io/specification — Progressive disclosure](https://agentskills.io/specification#progressive-disclosure)

---

## Ссылки на файлы внутри SKILL.md

Используйте стандартный Markdown для ссылок на ресурсы скилла:

```markdown
See [the reference guide](references/REFERENCE.md) for details.
Run the extraction script: scripts/extract.py
```

> Источник: [agentskills.io/specification — File references](https://agentskills.io/specification#file-references)

---

## Валидация

Официальная библиотека для валидации скиллов — [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref) (Python):

```bash
# Установка (Python venv)
pip install -e .  # из склонированного репо agentskills/agentskills/skills-ref

# Валидация
skills-ref validate path/to/my-skill

# Чтение метаданных (JSON)
skills-ref read-properties path/to/my-skill
```

> ⚠️ `skills-ref` позиционируется как **demonstration/reference** библиотека, не production-инструмент.

> Источник: [agentskills.io/specification — Validation](https://agentskills.io/specification#validation), [github.com/agentskills/agentskills/skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)

---

## Жизненный цикл скилла в агенте

```
Discovery → Activation → Execution
```

1. **Discovery**: При старте агент сканирует директории и загружает `name` + `description` всех скиллов в системный промпт
2. **Activation**: Когда задача соответствует описанию скилла, агент читает полный `SKILL.md` в контекст
3. **Execution**: Агент следует инструкциям, при необходимости загружая файлы и выполняя скрипты

> Источник: [agentskills.io/what-are-skills — How skills work](https://agentskills.io/what-are-skills#how-skills-work)

### Детали активации в Gemini CLI

В Gemini CLI процесс включает дополнительные шаги:

1. **Discovery** — сканирование трёх уровней (Workspace > User > Extension)
2. **Activation** — вызов инструмента `activate_skill`
3. **Consent** — подтверждение от пользователя в UI
4. **Injection** — тело `SKILL.md` и структура папки добавляются в историю
5. **Execution** — агент приоритизирует инструкции скилла

> Источник: [Gemini CLI: skills.md — How it Works](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)

---

## Обнаружение скиллов по платформам

### Gemini CLI

| Уровень | Путь | Приоритет |
|---------|------|-----------|
| Workspace | `.gemini/skills/` или `.agents/skills/` | Высший |
| User | `~/.gemini/skills/` или `~/.agents/skills/` | Средний |
| Extension | Встроенные расширения | Низший |

> При конфликте имён: **Workspace > User > Extension**.
> В пределах одного уровня `.agents/skills/` имеет приоритет над `.gemini/skills/`.

> Источник: [Gemini CLI: skills.md — Skill Discovery Tiers](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)

### OpenCode AI

| Уровень | Пути (проверяются все) |
|---------|------------------------|
| Project | `.opencode/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, `.agents/skills/<name>/SKILL.md` |
| Global | `~/.config/opencode/skills/<name>/SKILL.md`, `~/.claude/skills/<name>/SKILL.md`, `~/.agents/skills/<name>/SKILL.md` |

> OpenCode обходит дерево директорий от CWD до корня, собирая `SKILL.md` файлы.
> Имя `SKILL.md` **обязательно** заглавными буквами. Поле `name` во frontmatter должно совпадать с именем папки.

> Источник: [opencode.ai/docs — Skills](https://opencode.ai/docs/customization/skills)

---

## Управление скиллами

### Gemini CLI

```bash
# Список всех скиллов
gemini skills list

# Установить скилл из Git-репозитория
gemini skills install https://github.com/user/repo.git

# Установить из локальной директории
gemini skills install /path/to/local/skill

# Установить конкретный скилл из монорепы
gemini skills install https://github.com/org/skills.git --path skills/frontend-design

# Привязать через symlink
gemini skills link /path/to/my-skills-repo

# Включить/отключить
gemini skills enable my-skill
gemini skills disable my-skill --scope workspace

# Удалить
gemini skills uninstall my-skill --scope workspace
```

### Внутри интерактивной сессии Gemini CLI

```
/skills list              — показать все скиллы
/skills link <path>       — привязать скиллы из директории
/skills disable <name>    — отключить скилл
/skills enable <name>     — включить скилл
/skills reload            — обновить список скиллов
```

> Источник: [Gemini CLI: skills.md — Managing Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)

### OpenCode AI

В OpenCode управление правами доступа к скиллам осуществляется через `opencode.json`:
- `allow` — скилл загружается автоматически
- `deny` — скилл скрыт, доступ отклонён
- `ask` — запрос подтверждения у пользователя

Каждый скилл функционирует как отдельный инструмент (например, `skills_my_skill`), что позволяет гранулярный контроль per-agent.

> Источник: [opencode.ai/docs — Skills](https://opencode.ai/docs/customization/skills)
