# Research: Frontiers for V3 (Agent Skills SOTA 2026)

Этот документ содержит результаты SOTA-исследования (конец 2025 - 2026) по продвинутым паттернам создания Markdown-навыков (skills) для автономных ИИ-агентов. Эти концепции предназначены для следующего масштабного обновления фреймворка "Skill Factory".

## 🧠 1. Advanced Context & Memory (Context Engineering)

**Суть паттерна:**
Вместо надежды на гигантские контекстные окна (которые ведут к "context rot" — деградации внимания), SOTA-системы внедряют **Structured Note-Taking**. Агент не хранит в памяти всю историю долгой задачи, а сбрасывает "снимки состояния" в markdown-файлы или использует **Hierarchical Summarization** (многоуровневое сжатие контекста).

**Как перенести в `SKILL.md`:**
Добавить в шаблоны сложных скиллов правило `Context Compression Point`:
```markdown
## Context Management
- After completing every 3 steps, invoke `scripts/summarize_state.py` or write a `<session-id>-state.md` file.
- CLEAR your context and reload ONLY the `state.md` file before proceeding to the next phase to avoid "Goldfish Effect" (forgetting early instructions).
```
*Источники: [Anthropic: Complete Guide to Skills], [Thenewstack: Agent Memory]*

---

## 🔄 2. Loop Detection & Cognitive Circuit Breakers

**Суть паттерна:**
Классическая проблема: агент застревает в бесконечном цикле (например, тест падает -> сгенерирован фикс -> фикс не работает -> сгенерирован тот же фикс). В 2026 стандартом стали **"Когнитивные предохранители" (Cognitive Circuit Breakers)**. Они отслеживают не просто синтаксические повторения, а *Semantic Progress* (рост токенов без улучшения качества).

**Как перенести в `SKILL.md`:**
Обязательное условие `Max Retry Limit` и `Progress Check` в секции Red Flags:
```markdown
## 🛑 Circuit Breaker (Anti-Loop)
- **Max Retries:** DO NOT attempt the same fix or tool call more than 3 times.
- **Progress Check:** If you are looping, STOP. Write an `escalation_report.md` detailing the loop and ask the USER for intervention. Do not silently consume tokens.
```
*Источники: [Medium: Circuit Breakers in LLM Agents], [Sitepoint: Cost monitoring in Reflective Loops]*

---

## 🤝 3. Agent-to-Agent (A2A) Handoff Protocols

**Суть паттерна:**
Когда Orchestrator вызывает Subagent-а (или при передаче задачи между сессиями), весь контекст не копируется. Используются **Structured Handoff Reports in Markdown** (часто называемые Agent-Flavored Markdown или AFM). Обязательные артефакты: `migration_snapshot.md` или `escalation_report.md`.

**Как перенести в `SKILL.md`:**
В шаблон `subagent-orchestration-skill` добавить формат передачи состояния:
```markdown
## Handoff Protocol
When transferring control to the Code Reviewer subagent, generate a `handoff/<ticket-id>.md` document containing:
1. **Identity/Role:** Who the receiving agent needs to act as.
2. **Milestones:** What has been completed.
3. **Current State:** Links to the exact diffs to review.
4. **First Action Prompt:** The exact instruction the new agent should execute first.
```
*Источники: [WSO2: Agent-Flavored Markdown], [GitHub Copilot Custom Agents .agent.md]*

---

## 🔌 4. Advanced MCP Integration: Chaining & Code APIs

**Суть паттерна:**
Вместо того чтобы выдавать агенту 50 отдельных инструментов (tools), SOTA-паттерном стала оркестрация MCP-серверов. Скиллы требуют от агента **Multi-Step Tool Chaining** (обновление единого контекстного файла результатами разных MCP). Также набирает популярность представление MCP серверов как **Code APIs**, где агент пишет скрипты для пакетного взаимодействия с MCP, а не дергает инструменты напрямую по одному.

**Как перенести в `SKILL.md`:**
```markdown
## Tool Orchestration Strategy (MCP)
- Do not make 10 sequential tool calls to fetch data.
- Instead, use the `scripts/query_mcp_batch.py` to write a short filtering script that interacts with the Vector DB MCP and Git MCP concurrently, returning only the final reduced dataset.
```
*Источники: [ModelContextProtocol.io], [Anthropic: MCP Architectural Patterns]*

---

## 🛡️ 5. Graceful Degradation & Fallbacks

**Суть паттерна:**
Если MCP сервер или внешний API недоступны, скилл не должен просто падать. SOTA-скиллы включают четкие пути деградации (Graceful Degradation).

**Как перенести в `SKILL.md`:**
```markdown
## Graceful Degradation
- If the `git-mcp` tool is unresponsive, fallback to native shell commands (`git log`, `git status`).
- If the required Vector Database is offline, fallback to `grep_search` across local markdown files. Warn the user about reduced accuracy.
```

---
*Документ автоматически сгенерирован Research Agent (v1) на основе SOTA-практик (2026).*
