# 06. Безопасность скиллов

> **Источники:**
> - [Agent Skills Specification](https://agentskills.io/specification)
> - [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts)
> - [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

## Основной риск

Скиллы с `scripts/` могут **исполнять произвольный код** на машине пользователя. Агент запускает скрипты через shell/terminal — с теми же правами, что и текущий пользователь.

---

## Правила безопасности

### 1. Никаких секретов в скилле

```markdown
# ❌ Никогда
API_KEY = "sk-1234567890abcdef"
password = "admin123"

# ✅ Правильно — переменные окружения
API_KEY = os.environ["MY_API_KEY"]
```

Скиллы часто коммитятся в git или распространяются публично. Любой хардкод секретов — утечка.

### 2. Ревью скриптов перед использованием

Перед установкой чужого скилла с `scripts/`:
- Прочитайте **каждый скрипт** вручную
- Проверьте: что скрипт делает, какие файлы читает/пишет, куда обращается по сети
- Обратите внимание на обфускацию или подозрительные команды

### 3. Деструктивные операции — с защитой

```bash
# ❌ Без защиты — может удалить всё
rm -rf $TARGET_DIR

# ✅ С подтверждением
if [ "$CONFIRM" != "yes" ]; then
  echo "Error: pass --confirm yes to proceed with deletion"
  exit 1
fi
```

Используйте:
- `--dry-run` для предпросмотра действий
- `--confirm` / `--force` для опасных операций
- Проверку путей — не удалять за пределами рабочей директории

> Источник: [agentskills.io/skill-creation/using-scripts — Further considerations](https://agentskills.io/skill-creation/using-scripts#further-considerations)

### 4. Path awareness — осознание путей

Скрипты должны работать **только внутри рабочей директории** скилла или проекта:

```python
# ❌ Опасно — доступ к произвольным путям
with open(user_input_path) as f:
    data = f.read()

# ✅ Безопасно — валидация пути
import os
resolved = os.path.realpath(user_input_path)
if not resolved.startswith(os.path.realpath(ALLOWED_DIR)):
    raise ValueError(f"Access denied: {user_input_path}")
```

### 5. Зависимости — пиньте версии

```python
# ❌ Непредсказуемо
# dependencies = ["requests"]

# ✅ Пинить конкретные версии
# dependencies = ["requests>=2.31,<3"]
```

```bash
# ❌ Непредсказуемо
npx some-tool

# ✅ Пинить версию
npx some-tool@2.1.0
```

Без пиннинга вы можете получить вредоносную версию пакета (supply chain attack).

> Источник: [agentskills.io/skill-creation/using-scripts — One-off commands](https://agentskills.io/skill-creation/using-scripts#one-off-commands)

### 6. Платформенные механизмы защиты

| Платформа | Механизм |
|-----------|----------|
| **Gemini CLI** | Consent prompt — пользователь подтверждает активацию скилла в UI |
| **OpenCode AI** | Permissions в `opencode.json` (allow/deny/ask) |

Эти механизмы — **первая линия обороны**, но не заменяют ручной ревью скриптов.

> Источник: [Gemini CLI: skills.md — How it Works](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)

---

## Чеклист безопасности (краткий)

- [ ] Нет хардкодированных секретов (API ключи, пароли, токены)
- [ ] Скрипты не обращаются к путям за пределами рабочей директории
- [ ] Деструктивные операции защищены `--confirm` / `--dry-run`
- [ ] Зависимости пиннированы с конкретными версиями
- [ ] Нет обфусцированного или минифицированного кода в `scripts/`
- [ ] Сетевые запросы идут только к документированным эндпоинтам
