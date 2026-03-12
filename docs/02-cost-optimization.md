# Cost Optimization

> **Real numbers from 90+ days in production. Realistic savings, not inflated claims.**

---

## The Honest Overview

Before you read a word about optimization, run the cost calculator:

```bash
python3 scripts/cost-calculator.py
```

**Why:** You cannot optimize what you haven't measured. Most "save 80%!" guides assume you're running Sonnet everywhere for everything. Your actual baseline is probably different.

**My baseline (Feb 2026):**
- ~$90/month → ~$45/month after optimization (50% reduction)
- Biggest wins: context reduction ($135/month) and heartbeat optimization ($30-40/month)
- Honest model routing savings: ~$15/month (not $624/year as some guides claim)

---

## 1. Model Selection Strategy

### The Routing Framework

The core principle: **right model for right task, not cheapest model everywhere.**

"Use Haiku for everything" fails because only 25–33% of real production tasks are viable with Haiku. For the rest, you get degraded output — and your time fixing it costs more than the savings.

### Current Production Setup (March 2026)

| Role | Model | Provider | Cost/Call | Monthly Share |
|------|-------|----------|-----------|---------------|
| **Default (chat, general)** | Mistral Large 2512 | Mistral | $0.004 | ~40% of calls |
| **Editorial + community** | Sonnet 4.6 | Anthropic | $0.015 | ~30% of calls |
| **Strategic crons** | Opus 4.6 | Anthropic | $0.075 | ~5% of calls |
| **Heartbeats** | Groq Llama 3.3 70B | Groq | $0.0001 | ~20% of calls |
| **Simple mechanical tasks** | Haiku 4.5 | Anthropic | $0.0025 | ~5% of calls |

### Auto-Upgrade Rules

Mistral Large is the default. The system auto-upgrades to Sonnet for:
- Editorial content (blog posts, newsletters, social threads)
- Community responses (Skool, LinkedIn replies)
- Complex code generation
- Anything where founder voice or quality is non-negotiable

Upgrades to Opus for:
- Daily task optimization cron (NocoDB analysis)
- SEO weekly report (gap analysis)
- Multi-agent orchestration (3+ agents or strategic decisions)

### Why Not Haiku as Default?

Tested for 30 days. Results:

| Task Type | Haiku Result | Verdict |
|-----------|-------------|---------|
| Blog posts | Reads like content mill output | ❌ Fail |
| Community responses | Generic, no founder voice | ❌ Fail |
| LinkedIn replies | "Great point! I agree that..." | ❌ Fail |
| API data fetch | Correct | ✅ Pass |
| Config value read | Correct | ✅ Pass |
| Heartbeat check | Correct | ✅ Pass |

**Only 25–33% of actual tasks pass Haiku viability.** The rest require at minimum Mistral Large or Sonnet. Full analysis in [Case 5: Why Haiku Failed](../cases/05-why-haiku-failed.md).

### Model Selection Decision Tree

```
Is this a heartbeat / background check?
  YES → Groq Llama (3.3 70B) — $0.0001
  NO  ↓

Is quality non-negotiable? (public-facing, founder voice, relationships)
  YES → Sonnet 4.6 — $0.015
  NO  ↓

Is this strategic analysis or multi-agent orchestration?
  YES → Opus 4.6 — $0.075
  NO  ↓

Is this a purely mechanical operation? (fetch, extract, format)
  YES → Haiku 4.5 — $0.0025
  NO  → Mistral Large 2512 — $0.004 (default)
```

### Cost Comparison (100 Tasks/Month)

| Task Mix | All-Sonnet | Routed (This Setup) | Savings |
|----------|------------|---------------------|---------|
| 40 heartbeats | $0.60 | $0.004 | -99% |
| 20 chat/general | $0.30 | $0.08 | -73% |
| 15 community | $0.225 | $0.225 | — |
| 15 editorial | $0.225 | $0.225 | — |
| 5 strategic crons | $0.075 | $0.375 | +400% (worth it) |
| 5 mechanical | $0.075 | $0.0125 | -83% |
| **Total** | **$1.51** | **$0.92** | **-39%** |

Note: Strategic crons cost *more* with routing (Opus vs Sonnet). That's intentional — daily task optimization with Opus produces measurably better prioritization than Sonnet.

---

## 2. Embedding Optimization

### The Problem

Embeddings disabled = every file search is a linear scan. At 38+ files, this is slow and unreliable.

Embeddings enabled with sync mode = frozen conversations every time a file changes. Blocking.

### The Fix: Batch API + Lazy Indexing

```bash
# Apply the optimized config
openclaw gateway config.patch configs/embeddings-optimized.json
openclaw gateway restart
```

What the config does:
- **Batch API:** Async, non-blocking. No more frozen conversations.
- **30s debounce:** Files must stop changing for 30s before reindexing. Prevents thrashing during active editing sessions.
- **Lazy indexing:** No sync on session start. Index on first search, then cache.
- **50K entry cache:** Embeddings persist across restarts.

### Cost

- One-time indexing (38 files, 382 chunks): ~$0.003
- Monthly re-indexing (files change ~20% per month): ~$0.001
- **Total: effectively free**

### Results

| Before | After |
|--------|-------|
| Memory search: broken/slow | Memory search: instant |
| Session start: sometimes frozen | Session start: clean |
| File changes: blocking | File changes: background |
| Embeddings cost: $0 (disabled) | Embeddings cost: ~$0.003/month |

Full config: [`configs/embeddings-optimized.json`](../configs/embeddings-optimized.json)

---

## 3. Heartbeat Optimization

### Why Heartbeats Are Your Biggest Win

A heartbeat runs every 30 minutes, 24/7. That's 1,440 calls/month per agent.

**With Sonnet:** 1,440 × $0.015 = **$21.60/month** just to answer "nothing to report"
**With Groq:** 1,440 × $0.0001 = **$0.14/month**

**Savings: $21.46/month ($257/year)** per agent. For the main agent + 1 background agent: $514/year.

### What Heartbeats Actually Do

A heartbeat prompt is almost always:
> "Read HEARTBEAT.md if it exists. If nothing needs attention, reply HEARTBEAT_OK."

This is a boolean check. It does not require Sonnet's reasoning capability. Groq Llama 3.3 70B at 88ms handles this flawlessly.

### Implementation

```json
// In model-routing.json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "model": "groq/groq-llama"
      }
    }
  }
}
```

Apply: `openclaw gateway config.patch configs/model-routing.json`

### When Heartbeats Need to Escalate

Groq handles the check. When action is needed, the heartbeat spawns a Sonnet sub-agent for execution. This pattern means 95%+ of heartbeat cycles cost $0.0001, and the rare "action needed" cycles cost $0.015 — exactly when quality matters.

---

## 4. Context Management

### The Context Cost Problem

Every turn costs: `(context tokens + output tokens) × model price`

At 85KB bootstrap (21,400 tokens) with Sonnet:
- 100 turns/day × 21,400 tokens × $3/M = **$6.42/day = $192/month** just for context

After memory optimization (27KB, 6,500 tokens):
- 100 turns/day × 6,500 tokens × $3/M = **$1.95/day = $58.50/month**

**Savings from context reduction alone: $133.50/month**

### The Layered Memory Architecture

```
MEMORY.md          ← Working memory (≤4KB, current week)
memory/YYYY-MM-DD  ← Daily logs (raw, never deleted)
memory/ARCHIVE-*   ← Long-term (searchable, not auto-loaded)
```

**Rule:** If it's older than 7 days and not actively referenced → archive it.

### Context Pruning Config

Apply [`configs/context-pruning.json`](../configs/context-pruning.json):
- Tool output TTL: 6 hours (fetch once, cache, don't re-fetch)
- Compaction: enabled (auto-summarize old conversation turns)
- Session limit: configured per workflow type

Full guide: [docs/05-memory-optimization.md](05-memory-optimization.md)

---

## 5. Cron Optimization

### Isolated Sessions

Background crons should run in isolated sessions — not the main session. Benefits:
- No context pollution (cron's 50K tokens don't bleed into chat)
- Task-specific model override
- Failure doesn't affect main session
- Cleaner logs

```json
{
  "schedule": "0 5 * * *",
  "sessionTarget": "isolated",
  "model": "anthropic/claude-opus-4-6",
  "payload": {
    "message": "Read NocoDB tasks, optimize priorities, update statuses."
  }
}
```

### Right Model Per Cron

| Cron | Schedule | Model | Reasoning |
|------|----------|-------|-----------|
| Task optimization | Daily 5:00 AM | Opus 4.6 | Strategic analysis needs depth |
| Skool engagement | Twice daily | Sonnet 4.6 | Community quality non-negotiable |
| SEO weekly report | Monday 1:00 AM | Opus 4.6 | Gap analysis is strategic thinking |
| Newsletter draft | Weekly | Sonnet 4.6 | Editorial quality required |
| Health check | Every 30 min | Groq | Boolean check, no reasoning |

---

## 6. Real Numbers Summary

**Before optimization (Jan 2026):**
- Monthly cost: ~$90
- Context: 85KB bootstrap
- Embeddings: disabled
- Heartbeats: Sonnet
- No model routing

**After optimization (Mar 2026):**
- Monthly cost: ~$45 (50% reduction)
- Context: 27KB bootstrap (−69.8%)
- Embeddings: active, nearly free
- Heartbeats: Groq (−95% heartbeat cost)
- Strategic routing: Mistral Large default, Sonnet for quality, Opus for analysis

**Primary savings sources:**
1. Context reduction: ~$133/month (biggest win)
2. Heartbeat optimization: ~$30-40/month
3. Model routing: ~$12-15/month
4. Cron isolation: ~$8-10/month

---

## Next Steps

- **Quick wins (2 hours):** Apply embeddings config, switch heartbeats to Groq, implement basic model routing
- **Full optimization (1-2 weeks):** Memory architecture, context pruning, cron isolation
- **Monitor:** Run `scripts/cost-calculator.py` monthly, compare against baseline

---

**Last Updated:** 2026-03-12 | **Version:** 1.3.0
