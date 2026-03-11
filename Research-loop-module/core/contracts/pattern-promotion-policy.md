# Pattern Promotion Policy

Этот документ описывает процесс перехода паттерна от эксперимента к рабочему шаблону.

## Когда применяется

После того как experiment получил статус `accepted`.

## Шаги продвижения (promotion)

### 1. Записать в memory
Создать запись в `memory/accepted-patterns.md` по шаблону.
Обязательно заполнить:
- `valid_for` (модель/архитектура)
- `synchronization target` (какой шаблон обновлять)
- `confidence` (high / medium / low)

### 2. Обновить целевой шаблон
Перейти в указанный `synchronization target` (напр. `agents-lab/templates/...` или `skills-lab/templates/...`) и внести изменение, чтобы паттерн начал применяться по умолчанию.

### 3. Отметить синхронизацию
В записи `accepted-patterns.md` отметить:
- `Статус синхронизации: [x] обновлено`

### 4. Закрыть experiment
В experiment entry добавить пометку, что promotion выполнен.

## Шаги отклонения (rejection)

### 1. Записать в anti-patterns
Создать запись в `memory/anti-patterns.md` по шаблону.
Обязательно указать причину отказа и ссылку на experiment.

### 2. Откатить изменения (если были)
Если proposal уже был внедрён до получения финального статуса — откатить к baseline.

### 3. Закрыть experiment
В experiment entry зафиксировать `rejected` и причину.

## Важно

- Promotion без обновления шаблона = незавершённый promotion.
- Rejection без записи в anti-patterns = потерянный опыт.
- Оба варианта должны заканчиваться закрытием experiment entry.
