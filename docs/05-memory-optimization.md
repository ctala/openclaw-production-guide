# Memory Optimization

> **"From 21,400 tokens to 6,500 tokens (-69.8%) in ~2 hours of work"**

Context size is the silent killer of AI agent costs. Every turn loads your entire workspace into the model's context window — and you pay for every token.

This guide shows how to optimize OpenClaw's memory footprint based on real production data.

---

## 🎯 The Problem: Context Bloat

**Reality check (before optimization):**

| File | Size | Tokens | % of Bootstrap |
|------|------|--------|----------------|
| MEMORY.md | 42KB | 10,200 | 47.7% |
| AGENTS.md | 23KB | 5,500 | 25.7% |
| TOOLS.md | 9.6KB | 2,350 | 11.0% |
| USER.md | 9.7KB | 2,350 | 11.0% |
| SOUL.md | 1.5KB | 370 | 1.7% |
| Other context | ~2KB | 630 | 2.9% |
| **Total** | **~85KB** | **~21,400** | **100%** |

**The pain:**
- Every conversational turn: 21,400 input tokens
- Every cron run: 21,400 input tokens
- Every isolated session: 21,400 input tokens

**At scale:**
- 100 turns/day × 21,400 tokens = 2,140,000 input tokens/day
- Claude Sonnet 4.5: $3 per 1M input tokens
- **Daily cost:** $6.42 just for context loading
- **Monthly:** ~$193

**The kicker:** 48% of that context is MEMORY.md — and most of it is historical data that's rarely accessed.

---

## ✅ The Solution: Layered Memory Architecture

### Concept

```
Working Memory (MEMORY.md, ≤4KB)
  ↓
  Active context only (last 7 days + current projects)
  Loaded every turn
  
Archive (memory/ARCHIVE-YYYY-MM.md)
  ↓
  Historical data (>7 days old)
  Loaded only when needed (via memory_search)
  
Daily Logs (memory/YYYY-MM-DD.md)
  ↓
  Raw event logs
  Searchable but never loaded by default
```

**Key insight:** Not all memory needs to be loaded all the time.

---

## 📊 Results (Real Production Data)

**After optimization:**

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| MEMORY.md | 42KB (10,200 tokens) | 2.7KB (650 tokens) | **-94%** |
| AGENTS.md | 23KB (5,500 tokens) | 3.7KB (890 tokens) | **-84%** |
| TOOLS.md | 9.6KB (2,350 tokens) | 9.6KB (2,350 tokens) | 0% (modular now) |
| USER.md | 9.7KB (2,350 tokens) | 7.9KB (1,900 tokens) | **-19%** |
| **Total Bootstrap** | **~85KB (21,400 tokens)** | **~27KB (6,472 tokens)** | **-69.8%** |

**Cost impact:**
- Before: 100 turns/day × 21,400 = 2.14M tokens/day
- After: 100 turns/day × 6,472 = 647K tokens/day
- **Reduction:** -70% input tokens
- **Savings:** ~$4.50/day = **$135/month** (context loading only)

**Nothing was lost:**
- All historical data → `memory/ARCHIVE-2026-02.md` (searchable via `memory_search`)
- All user stories → `memory/USER-STORIES.md` (searchable)
- All daily logs → `memory/YYYY-MM-DD.md` (persistent)

---

## 🛠️ Implementation

### Step 1: Audit Current Context Size

```bash
cd ~/clawd

# Measure file sizes
wc -c MEMORY.md AGENTS.md TOOLS.md USER.md SOUL.md

# Estimate tokens (rough: 1 token ≈ 4 chars)
wc -c MEMORY.md | awk '{print $1 / 4 " tokens"}'
```

**Example output:**
```
42000 MEMORY.md
23000 AGENTS.md
9600 TOOLS.md
9700 USER.md
1500 SOUL.md
85800 total

MEMORY.md: ~10,200 tokens
```

**Target:** MEMORY.md ≤ 4KB (≤ 1,000 tokens)

---

### Step 2: Create Archive Structure

```bash
mkdir -p ~/clawd/memory

# Create monthly archive
touch memory/ARCHIVE-$(date +%Y-%m).md
```

**Archive format:**

```markdown
# Memory Archive - February 2026

Last updated: 2026-02-19

## Archive Policy

Content here is >7 days old and moved from MEMORY.md to reduce context size.

Access via `memory_search` when needed.

---

## 2026-02-12 - Project XYZ Completed

[Historical content here]

---

## 2026-02-10 - Decision: Use NocoDB Instead of Asana

[Historical content here]
```

---

### Step 3: Archive Old Entries

**Manual approach (first time):**

1. Open MEMORY.md
2. Identify entries >7 days old
3. Cut and paste to `memory/ARCHIVE-YYYY-MM.md`
4. Keep only:
   - Active projects (status: in progress)
   - Current decisions (referenced this week)
   - Top 5 lessons learned (recent)

**Automated approach (create skill):**

See `skills/nightly-optimization/SKILL.md` → Memory Maintenance section.

**Cron job (3 AM daily):**
```bash
# Part of nightly-optimization skill
# 1. Check MEMORY.md size
# 2. If >4KB, archive old entries
# 3. Keep only active context
```

---

### Step 4: Optimize USER.md

**Before:**
```markdown
## Anécdotas Personales

### Hospitalización 2015
[5 paragraphs of story]

### Viaje a Rumania
[4 paragraphs of story]

### Primera Startup
[6 paragraphs of story]
```

**After:**
```markdown
## Anécdotas Personales

*Detalles completos → `memory/USER-STORIES.md` (buscable via memory_search)*

### Hospitalización 2015
Estuvo internado por issue X. Lección: Y.

### Viaje a Rumania
Voluntariado en orfanato. Experiencia formativa.

### Primera Startup
Fundó X en año Y. Exit: Z.
```

**Result:**
- USER.md: 9.7KB → 7.9KB (-19%)
- Full stories still accessible via `memory_search`

---

### Step 5: Optimize AGENTS.md

**Before:**
```markdown
## Proceso de Generación de Contenido

1. Leer IDEAS-BANCO.md
2. Seleccionar idea
3. Generar borrador
4. Revisar
5. Publicar
6. Actualizar IDEAS-BANCO.md

[10 more paragraphs of detailed instructions]
```

**After:**
```markdown
## Proceso de Generación de Contenido

Ver `content-strategy/STANDARD-BLOG-POST.md` para workflow completo.

**Quick reference:**
1. Check IDEAS-BANCO → 2. Generate draft → 3. Review → 4. Publish

Detalles específicos por plataforma en `content-strategy/STANDARD-*.md`.
```

**Principle:** AGENTS.md = **index**, not encyclopedia.

**Result:**
- AGENTS.md: 23KB → 3.7KB (-84%)
- All procedures still accessible (just referenced, not duplicated)

---

### Step 6: Eliminate Cross-File Redundancy

**Common problem:**

```
AGENTS.md:
  "Skills están en skills/INDEX.md"

TOOLS.md:
  "Skills completas: late-api, wordpress-api, ..."
  [Duplicated list from skills/INDEX.md]
```

**Solution:**

```
TOOLS.md:
  "Skills disponibles: Ver skills/INDEX.md"
  [NO duplicated list]
```

**Rule:** Every fact should live in **exactly one place**.

---

## 🎯 Memory Optimization Targets

| File | Target Size | Purpose | Archival |
|------|-------------|---------|----------|
| MEMORY.md | ≤ 4KB | Active context only | >7 days → ARCHIVE |
| AGENTS.md | ≤ 4KB | Structure + rules | Procedures → skills |
| TOOLS.md | ≤ 10KB | Config + credentials | Details → docs/tools-modules |
| USER.md | ≤ 8KB | Profile + preferences | Stories → USER-STORIES.md |
| SOUL.md | ≤ 2KB | Personality | Static (rarely changes) |

**Total target:** ≤ 28KB (~7,000 tokens)

---

## 🔍 Memory Search Integration

### How It Works

```bash
# OpenClaw memory_search tool
memory_search("proyecto BeaTrix-PF setup")

# Returns:
{
  "results": [
    {
      "path": "memory/ARCHIVE-2026-02.md",
      "startLine": 145,
      "endLine": 178,
      "score": 0.92,
      "snippet": "## 18/02 - BeaTrix-PF Instalación..."
    }
  ]
}
```

**Then:**
```bash
# Read specific lines
memory_get("memory/ARCHIVE-2026-02.md", from=145, lines=34)
```

**Result:** Only load relevant 34 lines, not entire 40KB archive.

---

### When to Use Memory Search

**Mandatory before answering:**
- "What did we decide about X?"
- "When did we finish project Y?"
- "What was the outcome of Z?"

**Pattern:**
```
User: "What did we decide about Skool scoring thresholds?"

Agent:
  1. memory_search("Skool scoring thresholds decision")
  2. Read top result (specific lines)
  3. Answer based on retrieved context
```

**Anti-pattern:**
- ❌ Load all archives into context "just in case"
- ❌ Keep historical data in MEMORY.md "for reference"

---

## 📊 Metrics to Track

### Bootstrap Size Over Time

```bash
# Daily measurement (add to nightly optimization)
echo "$(date +%Y-%m-%d),$(wc -c MEMORY.md AGENTS.md TOOLS.md USER.md | tail -1 | awk '{print $1}')" >> logs/context-size.csv
```

**Graph:**
```
50000 |                    *
      |                  *
40000 |                *
      |              *
30000 |            *
      |          *      *---*---*  (Optimized, stable)
20000 |        *
      |      *
10000 |    *
      |  *
    0 +---------------------------
      Jan  Feb  Mar  Apr  May
```

**Target:** Stable at ~27KB after optimization.

---

### Cost Savings

**Formula:**
```
Daily input tokens = (bootstrap tokens) × (turns per day)
Daily cost = (daily input tokens / 1M) × (input price per 1M)
Monthly savings = (cost before - cost after) × 30
```

**Example:**
```
Before: 21,400 tokens × 100 turns = 2.14M tokens/day
After:   6,472 tokens × 100 turns = 647K tokens/day
Reduction: 1.49M tokens/day

Sonnet 4.5 input: $3 / 1M tokens
Daily savings: (1.49M / 1M) × $3 = $4.47
Monthly savings: $4.47 × 30 = $134
```

**Plus:** Faster response times (less context to process).

---

## 🛠️ Automation: Nightly Optimization Skill

**Location:** `skills/nightly-optimization/SKILL.md`

**Cron:** 3:00 AM daily (isolated session, Opus 4.6)

**Process:**
```
1. MEMORY.md Maintenance (CRITICAL - DO FIRST):
   - Measure size (wc -c MEMORY.md)
   - IF > 4KB:
     - Archive entries >7 days old
     - Condense active entries
     - Verify memory_search works
   - Report: size before/after

2. Validate cross-file refs
3. Eliminate redundancies
4. Generate optimization report
5. Git commit + push
```

**Example report:**
```markdown
## 03:00 - Optimización Núcleo (Nightly)

**Salud:** 9/10
**MEMORY.md:** 5.2KB → 3.1KB (18 entries archived)

### Acciones Ejecutadas
- Archivado 18 entradas >7 días a ARCHIVE-2026-02.md
- Condensado 4 secciones redundantes
- Eliminado 2 referencias fantasma

### Commit
- hash: d9712af
```

---

## 💡 Advanced: Context-Aware Model Routing

**Idea:** Use smaller models for lean context sessions.

**Implementation:**
```
IF context size < 8KB:
  → Use Haiku (cheaper, faster)
ELSE IF context size < 15KB:
  → Use Mistral Large
ELSE:
  → Use Sonnet (complex context)
```

**Example:**
- Isolated cron with 7KB context → Haiku
- Main session with 27KB context → Sonnet
- Heartbeat with 3KB context → Groq Fast (Nano)

**Savings:** Additional 30-40% on model costs.

---

## 🚀 Quick Wins (Prioritized)

### 1. Archive MEMORY.md (Biggest Win)

**Time:** 30 minutes  
**Reduction:** -8,650 tokens  
**Savings:** ~$80/month

**Steps:**
1. Create `memory/ARCHIVE-2026-02.md`
2. Move entries >7 days old
3. Verify `memory_search` works
4. Keep only active context

---

### 2. Dedup AGENTS ↔ TOOLS

**Time:** 20 minutes  
**Reduction:** -1,500 tokens  
**Savings:** ~$14/month

**Steps:**
1. Identify duplicated sections
2. Keep in ONE place (usually TOOLS or skill)
3. Add reference in other file

---

### 3. Condense AGENTS.md

**Time:** 40 minutes  
**Reduction:** -2,250 tokens  
**Savings:** ~$21/month

**Steps:**
1. Convert procedures → references
2. Keep only structure + rules
3. Move details to skills/ or docs/

---

**Total quick wins:** ~70 minutes, -12,400 tokens, **~$115/month savings**

---

## 📝 Checklist: Memory Optimization Sprint

**Pre-work (5 min):**
- [ ] Audit current context size
- [ ] Identify MEMORY.md % of total
- [ ] Set target (<4KB)

**Archive MEMORY.md (30 min):**
- [ ] Create `memory/ARCHIVE-YYYY-MM.md`
- [ ] Move entries >7 days old
- [ ] Keep active projects + recent decisions
- [ ] Test `memory_search` retrieval

**Optimize USER.md (20 min):**
- [ ] Create `memory/USER-STORIES.md`
- [ ] Move detailed anecdotes
- [ ] Keep summary + reference

**Optimize AGENTS.md (40 min):**
- [ ] Identify procedures
- [ ] Move to skills/ or content-strategy/
- [ ] Replace with references
- [ ] Keep only structure

**Eliminate redundancy (20 min):**
- [ ] Find duplicated content (AGENTS ↔ TOOLS)
- [ ] Keep in ONE place
- [ ] Add cross-references

**Setup automation (40 min):**
- [ ] Create/update nightly-optimization skill
- [ ] Add MEMORY.md maintenance
- [ ] Configure cron (3 AM daily)
- [ ] Test run

**Measure (5 min):**
- [ ] Record new context size
- [ ] Calculate reduction %
- [ ] Estimate monthly savings
- [ ] Document in CHANGELOG

---

## 🎯 Maintenance

**Daily (automated):**
- Nightly optimization cron (3 AM)
- MEMORY.md size check
- Auto-archive if >4KB

**Weekly (manual):**
- Review optimization reports
- Adjust archival rules if needed
- Update targets if workspace grows

**Monthly (review):**
- Compare context size trends
- Measure actual cost savings
- Refine automation

---

## 📖 Case Study: Real Optimization Sprint

**Date:** 2026-02-19  
**Duration:** ~2 hours  
**Agent:** Nyx (OpenClaw main session)

**Results:**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| MEMORY.md | 42KB | 2.7KB | -94% |
| AGENTS.md | 23KB | 3.7KB | -84% |
| USER.md | 9.7KB | 7.9KB | -19% |
| **Total bootstrap** | **85KB (21,400 tokens)** | **27KB (6,472 tokens)** | **-69.8%** |
| Estimated monthly savings | - | - | **$135** |

**What was archived:**
- 40KB of MEMORY.md → `ARCHIVE-2026-02.md`
- User anecdotes → `USER-STORIES.md`
- Historical decisions (still searchable)

**What stayed:**
- Active projects
- Current decisions
- Top lessons learned
- User profile essentials

**Outcome:**
- ✅ Context 70% smaller
- ✅ Nothing lost (all searchable)
- ✅ Responses faster (less context to process)
- ✅ Costs reduced significantly

**Commit:** `d9712af` (v2.4.0)

---

## 🔗 Related Resources

- **Skill:** `skills/nightly-optimization/SKILL.md`
- **Changelog:** v2.4.0 - Memory optimization
- **Case Study:** Blog post "Backup Automático de OpenClaw con GitHub"
- **Production Guide:** This document

---

## 💭 Final Thoughts

**Context size = silent cost multiplier.**

Every 1KB you add to bootstrap context:
- Increases input tokens per turn
- Compounds across 100+ turns/day
- Adds up to $10-20/month

**Optimization is one-time work with permanent savings.**

2 hours of work → $135/month savings = **$1,620/year ROI**

**Plus:** Faster responses, cleaner workspace, easier debugging.

---

**Last Updated:** 2026-02-19  
**Status:** Production-tested, actively maintained
