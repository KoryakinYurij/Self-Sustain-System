# 03. Кросс-платформенная совместимость

> **Источники:**
> - [Agent Skills Specification](https://agentskills.io/specification)
> - [Gemini CLI: Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)
> - OpenCode AI documentation (opencode.ai)

---

## Открытый стандарт Agent Skills

Agent Skills — это **открытый стандарт**, инициированный Anthropic и принятый ведущими платформами. Скиллы, созданные по этому стандарту, **портабельны** между различными AI-агентами.

> *"Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows."*
>
> Источник: [agentskills.io](https://agentskills.io)

### Платформы, поддерживающие стандарт

| Платформа | Статус поддержки |
|-----------|------------------|
| **Gemini CLI** | ✅ Полная поддержка |
| **OpenCode AI** | ✅ Полная поддержка |
| **Claude Code** | ✅ Полная поддержка (инициатор стандарта) |
| **Cursor** | ✅ Поддержка |
| **GitHub Copilot** | ✅ Поддержка |

---

## Gemini CLI — специфика

### Обнаружение скиллов

| Уровень | Пути | Приоритет |
|---------|------|-----------|
| Workspace | `.gemini/skills/`, `.agents/skills/` | Высший |
| User | `~/.gemini/skills/`, `~/.agents/skills/` | Средний |
| Extension | Встроенные расширения | Низший |

**Приоритет при конфликте имён:** Workspace > User > Extension.
В пределах одного уровня `.agents/skills/` приоритетнее `.gemini/skills/`.

### Установка созданного скилла

Универсальный путь для всех платформ:
```
cp -r my-skill ~/.agents/skills/
```

> Источник: [Gemini CLI: skills.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md), [opencode.ai/docs](https://opencode.ai/docs/customization/skills)

---

## Таблица совместимости полей

> Все платформы реализуют стандарт agentskills.io. Обязательные поля (`name`, `description`) поддерживаются везде. Опциональные поля зависят от реализации.

| Поле frontmatter | agentskills.io (стандарт) | Gemini CLI | OpenCode AI |
|-------------------|--------------------------|------------|-------------|
| `name` (обязательно) | ✅ | ✅ | ✅ |
| `description` (обязательно) | ✅ | ✅ | ✅ |
| `license` | ✅ | ✅ | ✅ |
| `compatibility` | ✅ | Поддержка | Поддержка |
| `metadata` | ✅ | Поддержка | Поддержка |
| `allowed-tools` | ✅ (экспериментально) | Зависит от версии | Зависит от версии |

### Директории

| Директория | agentskills.io | Gemini CLI | OpenCode AI |
|------------|----------------|------------|-------------|
| `scripts/` | ✅ | ✅ | ✅ |
| `references/` | ✅ | ✅ | ✅ |
| `assets/` | ✅ | ✅ | ✅ |

---

## Рекомендации для кросс-платформенной совместимости

1. **Следуйте стандарту agentskills.io** — он является общим знаменателем
2. **Используйте forward slashes** в путях (`scripts/helper.py`, не `scripts\helper.py`)
3. **Имя =  директория** — `name` в frontmatter должно совпадать с именем папки
4. **SKILL.md — заглавными буквами** — это требование стандарта и всех платформ
5. **Не используйте platform-specific фичи** в ядре скилла — добавляйте их в `compatibility` поле
6. **Валидируйте** скилл через `skills-ref validate` перед распространением

---

## Алиас `.agents/skills/`

Стандарт поддерживает **универсальный алиас** `.agents/skills/` (на уровне проекта) и `~/.agents/skills/` (глобально). Этот путь:
- Работает в Gemini CLI
- Работает в OpenCode AI
- Обеспечивает интуитивный путь для агент-специфичных скиллов
- Совместим с различными AI-инструментами

> Источник: [Gemini CLI: skills.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md) — *"This generic alias provides an intuitive path for managing agent-specific expertise that remains compatible across different AI agent tools."*
