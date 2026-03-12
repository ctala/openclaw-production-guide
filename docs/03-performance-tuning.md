# Performance Tuning

> **Faster responses, lower latency, fewer wasted tokens — without changing your workflows.**

---

## Overview

Cost and performance are the same problem viewed from different angles. Wasted tokens = higher cost. Bloated context = slower responses. Redundant tool calls = both.

This guide covers the production-tested techniques that moved the needle.

---

## 1. Memory Search (Vector Embeddings)

### Why Embeddings Change Everything

Without embeddings: OpenClaw scans files linearly. At 38 files, this is slow and misses context that's not in the most recent conversation turns.

With embeddings: Semantic search across all indexed files. Instant recall. Surfacing relevant context even when it's in a file you haven't touched in weeks.

### Setup

```bash
# One-click setup
bash scripts/enable-optimized-embeddings.sh

# Or manual config patch
openclaw gateway config.patch configs/embeddings-optimized.json
openclaw gateway restart
```

### Configuration That Matters

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "model": "text-embedding-3-small",
    "batchApi": true,
    "watchDebounceMs": 30000,
    "syncOnStart": false,
    "cache": {
      "enabled": true,
      "maxEntries": 50000
    },
    "search": {
      "maxResults": 10,
      "minScore": 0.7
    }
  }
}
```

**Key settings:**
- `batchApi: true` — Async indexing, never blocks conversation
- `watchDebounceMs: 30000` — 30s settle time before reindex; prevents thrashing during active edits
- `syncOnStart: false` — Lazy indexing; don't freeze on session start
- `minScore: 0.7` — Filters noise; lower for broader recall, higher for precision

### Tuning `minScore`

| Value | Behavior | Use When |
|-------|----------|----------|
| 0.5 | Broad recall; more noise | Small knowledge base (<20 files) |
| 0.7 | Balanced (recommended) | Medium knowledge base (20-100 files) |
| 0.85 | High precision; may miss edge cases | Large, well-structured knowledge base |

### Production Numbers

- Files indexed: 38 (382 chunks, 0 failures)
- Indexing cost (one-time): $0.003
- Monthly re-index cost: ~$0.001
- Search latency: <100ms
- Recall improvement vs linear scan: significant (qualitative — hard to benchmark precisely)

---

## 2. Session Management

### Context Limit Reality

OpenClaw context limits aren't just about cost — they affect response quality. Studies on transformer models show measurable capability loss at high token counts (>32K context in a single session).

**Practical implications:**
- Long sessions = slower, potentially degraded responses
- Background crons don't need your full conversation history
- Specialized tasks (SEO report, workflow generation) need focused context, not full workspace

### Compaction

Compaction summarizes old conversation turns when context approaches the limit. Enable it:

```json
{
  "session": {
    "compaction": {
      "enabled": true,
      "mode": "auto",
      "triggerAt": 0.75,
      "targetRatio": 0.4
    }
  }
}
```

`triggerAt: 0.75` — compact when context hits 75% of limit  
`targetRatio: 0.4` — compact down to 40% (keeps recent turns, summarizes old)

**When compaction kicks in:**
- Long chat sessions
- Research workflows with many tool calls
- Any session that's been running for hours

### Memory Flush Before Compaction

Always flush working memory before compaction to preserve what matters:

```
Before compaction:
1. Write important context to MEMORY.md
2. Save any decisions/outcomes to daily log
3. Then allow compaction

After compaction, context picks up from summary + current files.
```

### Isolated Sessions for Background Jobs

Crons and automated workflows should run in isolated sessions:

```json
{
  "schedule": "0 5 * * *",
  "sessionTarget": "isolated",
  "contextFiles": ["AGENTS.md", "TOOLS.md"],
  "model": "anthropic/claude-opus-4-6"
}
```

**Why isolated:**
- Cron loads only what it needs (5-10KB vs 27KB main)
- Failure doesn't corrupt main session state
- Token usage is accounted separately (easier cost tracking)
- Parallel runs don't interfere

---

## 3. Tool Call Efficiency

### Output TTL

Tool outputs (API calls, file reads, web fetches) stay in context by default. For expensive or slow tools, set a TTL to avoid re-fetching unnecessarily — and evict stale data that's bloating context.

```json
{
  "tools": {
    "outputTtl": {
      "default": "6h",
      "web_fetch": "1h",
      "exec": "30m",
      "read": "12h"
    }
  }
}
```

**Practical impact:**
- Fetched a Serpstat API report at 9 AM? Still in context at 3 PM. No re-fetch.
- Read a config file? Cached for 12 hours. File didn't change.
- Ran a bash command? Evicted after 30 minutes (commands produce stale data quickly).

### Context Limit Overrides Per Tool

Some tools produce large outputs that rarely need to stay in context long:

```json
{
  "tools": {
    "contextLimits": {
      "exec": 2000,
      "web_fetch": 5000,
      "read": "full"
    }
  }
}
```

`exec: 2000` — Truncate command output at 2K chars in context (full output still logged). Prevents a `cat largefile.json` from flooding context.

---

## 4. Anti-Patterns That Burn Tokens

### Anti-Pattern 1: Reading Large Files Every Turn

```
# BAD: Agent reads MEMORY.md every single turn
Turn 1: read MEMORY.md (8KB)
Turn 2: read MEMORY.md (8KB)
Turn 3: read MEMORY.md (8KB)
→ 24KB wasted across 3 turns
```

```
# GOOD: Read once per session, then trust context
Turn 1: read MEMORY.md → in context
Turn 2-N: file stays in context via embeddings/cache
```

**Fix:** Set `read` TTL to 12h. Files read once per session.

### Anti-Pattern 2: Full Workspace Context for Specialized Tasks

```
# BAD: SEO report cron loads 27KB main workspace
schedule: SEO report
sessionTarget: main   ← loads everything
→ Model must filter signal from noise across 27KB
```

```
# GOOD: SEO report cron loads only what it needs
schedule: SEO report
sessionTarget: isolated
contextFiles: ["skills/serpstat-api/SKILL.md", "TOOLS.md#seo"]
→ Model works with 5KB focused context
```

**Fix:** Isolated sessions with targeted `contextFiles`.

### Anti-Pattern 3: Polling in Tight Loops

```
# BAD: Heartbeat every 5 minutes
"heartbeat": { "intervalMinutes": 5 }
→ 288 calls/day × $0.015 = $4.32/day = $129/month
```

```
# GOOD: Heartbeat every 30 minutes, Groq model
"heartbeat": { "intervalMinutes": 30, "model": "groq/groq-llama" }
→ 48 calls/day × $0.0001 = $0.0048/day = $0.14/month
```

**Fix:** 30-minute minimum interval for heartbeats. Use Groq.

### Anti-Pattern 4: Sub-Agent with Full Context

```
# BAD: n8n specialist loads full main workspace
agents/n8n-specialist/AGENTS.md → links to main workspace files
→ 27KB context in a sub-agent that only needs n8n docs
```

```
# GOOD: n8n specialist has focused context
agents/n8n-specialist/AGENTS.md → only n8n patterns
agents/n8n-specialist/TOOLS.md  → only n8n instances
Total: 5KB
```

**Fix:** Sub-agent workspaces must be minimal. See [Multi-Agent Architecture](06-multi-agent-architecture.md).

### Anti-Pattern 5: Storing Outputs in MEMORY.md

```
# BAD: MEMORY.md grows unbounded
## 10:00 - SEO Report
Full 3,000-word report pasted here...

## 11:00 - Workflow Output  
Full workflow JSON (8KB) pasted here...
```

```
# GOOD: MEMORY.md stores pointers, not payloads
## 10:00 - SEO Report
Generated. See memory/2026-03-12.md#seo-report. Key finding: 23 gaps in startup keywords.

## 11:00 - Workflow Output
Generated lead-capture-workflow.json (6.5KB). Deployed to n8n staging.
```

**Fix:** MEMORY.md ≤ 4KB always. Summaries + pointers, not raw payloads.

---

## 5. Response Time Optimization

### Model Speed Reference

| Model | Typical Latency | Use Case |
|-------|----------------|----------|
| Groq Llama 3.3 70B | 88ms | Heartbeats, boolean checks |
| Haiku 4.5 | 1–2s | Simple mechanical tasks |
| Mistral Large 2512 | 2–3s | Default chat, general tasks |
| Gemini 2.5 Pro | 3–5s | Synthesis, content |
| Sonnet 4.6 | 5–8s | Editorial, community, code |
| Opus 4.6 | 15–25s | Strategic analysis, deep cron jobs (NOT orchestration) |

For interactive workflows (user waiting for response), Mistral Large at 2–3s is the practical cap for "feels instant." Sonnet at 5–8s is acceptable. Opus at 15–25s should be cron-only or async.

### Async by Default for Long Tasks

Never run Opus or complex workflows synchronously in a user-facing session. Use crons or explicit "I'll do this in the background":

```
# Good pattern
User: "Generate this week's SEO report"
Agent: "Starting now, will message you when done." → spawns isolated cron session
... (15 minutes later) ...
Agent: "SEO report complete. [summary]. Full report in memory/2026-03-12.md"
```

---

## 6. Monitoring Performance

### What to Track

```bash
# Check session context size
openclaw session_status | jq '.context.tokens'

# Check embedding index health
openclaw config.get | jq '.memorySearch'

# Check cron last run
openclaw cron.list | jq '.[] | {name, lastRun, nextRun}'
```

### Metrics Dashboard (NocoDB)

Track weekly:

| Metric | Target | Red Flag |
|--------|--------|----------|
| Avg session context (tokens) | <8,000 | >20,000 |
| Heartbeat cost/month | <$1 | >$5 |
| Main session cost/day | <$2 | >$5 |
| Compaction frequency | <2x/day | >5x/day |
| Cron failure rate | <5% | >20% |

---

## Related Resources

- [Cost Optimization](02-cost-optimization.md) — Model selection, embeddings, heartbeats
- [Memory Optimization](05-memory-optimization.md) — Context architecture, archival
- [Multi-Agent Architecture](06-multi-agent-architecture.md) — Sub-agent context efficiency
- [configs/context-pruning.json](../configs/context-pruning.json) — Ready-to-apply config

---

**Last Updated:** 2026-03-12 | **Version:** 1.3.0
