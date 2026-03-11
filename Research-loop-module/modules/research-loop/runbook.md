# Research Loop Runbook

## Цель runbook

Этот документ нужен, чтобы человек или агент мог быстро запустить один цикл research-loop без долгого размышления о процессе.

## Минимальный запуск

### Вход
- 1 тема исследования
- 3–5 источников
- 1 целевой модуль (`agents-lab` или `skills-lab`)
- 1 маленький тест

### Выход (Full mode)
- 3–5 source entries
- 3–5 review entries
- 1–3 proposal entries
- 1 experiment entry
- при успехе — 1 запись в memory + обновлённый шаблон
- при неудаче — 1 запись в anti-patterns

### Выход (Lightweight mode)
- 1 research-digest.md
- при необходимости — переход в full mode

## Рекомендуемая последовательность

1. взять тему из `inbox/`
2. определить режим: lightweight или full
3. завести source entries (или digest)
4. сделать review entries
5. из review сделать proposal
6. выбрать один proposal для эксперимента
7. провести тест (с baseline!)
8. записать результат
9. promote / reject / defer (см. `pattern-promotion-policy.md`)

## Важное правило

Если исследование интересное, но не привело к наблюдаемому улучшению, его всё равно можно сохранить как:
- полезный контекст;
- отложенное направление;
- неподтверждённую гипотезу.

Но оно не должно автоматически становиться accepted pattern.
