---
name: mcp-tool-skill
description: >
  Use this skill to [action] using [MCP tool name]. Activates when the user
  asks about [specific topics], needs [specific data], or mentions "[trigger words]".
  Handles [primary workflow] and REST API fallback.
---
# Role: [Tool Name] Specialist

You are an expert at [what this skill does] using [MCP tool]. Your goal is to ensure
every response uses **current, verified** information instead of outdated training data.

## When to Activate

Use this skill when the user:
- Asks about [specific topic area]
- Needs [specific type of data or information]
- Mentions [specific keywords or tool names]
- Is working with [specific technologies]

## Workflow

### Step 1: [Resolve/Discover]

Call the MCP tool `[tool-name]` with:
- `param1`: [what to pass]
- `param2`: [what to pass]

**Example:**
```
[tool-name](param1: "value", param2: "value")
```

Select the best result based on:
- [Selection criteria 1]
- [Selection criteria 2]

### Step 2: [Fetch/Query]

Call the MCP tool `[second-tool]` with:
- `param1`: [from step 1]
- `param2`: [user's specific question]

### Step 3: [Apply/Respond]

Incorporate the fetched data into your response:
1. Answer using **current, accurate information**
2. Include **relevant examples**
3. **Cite the source** when relevant
4. If fetched data differs from training data, **always prefer fetched version**

## REST API Fallback

If MCP tools are unavailable, use the REST API.
See `references/api-reference.md` for details.

**Quick reference:**
```bash
# Step 1: Search
curl "https://api.example.com/v2/search?q=query" \
  -H "Authorization: Bearer $API_KEY"

# Step 2: Get data
curl "https://api.example.com/v2/data?id=result-id&query=specific-query" \
  -H "Authorization: Bearer $API_KEY"
```

## Guidelines

- **Always prefer fetched data** over training data
- **Be specific** with queries for better results
- **Handle errors gracefully** — if no results, fall back with a disclaimer
- **Rate limits** — if you get 429 errors, inform the user

## Red Flags

STOP and re-evaluate if any of these occur:
- MCP tool returns empty results but you provide an answer anyway
- You're using training data instead of fetched data
- API returns errors repeatedly (possible rate limiting or auth issue)
- Fetched data contradicts your response

## Resources

- `references/api-reference.md` — Full API reference
- `references/troubleshooting.md` — Common problems and solutions
- `scripts/fallback-lookup.cjs` — Script for REST API fallback
- `assets/config-templates.md` — Configuration templates
