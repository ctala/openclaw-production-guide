# Memory Management for Long-Running Agents

> How to keep an agent's memory lean, searchable, and consistent across restarts — without context bloat killing your budget.

---

## Overview

Long-running agents (60+ days of production) accumulate memory. Without active management, context size grows until it's too expensive to run, or until the agent loses track of what's current vs historical.

**The problem in numbers:**
- Unmanaged MEMORY.md after 60 days: 40KB+ (10,000+ tokens)
- Bootstrap cost at 40KB: ~$0.04 per session start
- 100 sessions/month: $4/month just for loading stale memory
- After memory optimization: 4KB MEMORY.md = $0.004/session start = $0.40/month (90% savings)

---

## 1. Memory Hierarchy

### Three Layers

```
Working Memory (MEMORY.md)        ← Current: ≤4KB, AI reads every session
Daily Logs (memory/YYYY-MM-DD.md) ← Raw: no size limit, searchable
Archive (memory/ARCHIVE-*.md)     ← Historical: compressed, long-term
```

### Working Memory (MEMORY.md)

**Purpose:** Critical context that the agent needs to function correctly in any session.
**Size target:** ≤4KB (1,000 tokens)
**Content:** Active projects, pending decisions, recent critical events, key facts

**What belongs in MEMORY.md:**
- Currently active projects (5-10, with status)
- Pending decisions requiring human input
- Critical configurations (model overrides, channel preferences)
- Recent incidents or changes affecting behavior
- High-priority tasks for current week

**What does NOT belong in MEMORY.md:**
- Historical events older than 7 days (unless still relevant)
- Detailed logs (that's daily logs)
- Completed tasks (archive them)
- Routine recurring notes (put in AGENTS.md or skill files)

### Daily Logs

**Purpose:** Raw, comprehensive record of what happened.
**Format:** `memory/YYYY-MM-DD.md`
**Size:** Unconstrained — log everything

```markdown
# 2026-03-10

## 09:15 - LinkedIn Posting Party
- Set up tracking sheet for 12 participants
- Unipile returned 0 for 2nd-degree connections (known issue)
- Used browser fallback for Bob, Carol, Dave, Eve (4 participants)
- Party completion: 132/144 (91.6%)

## 11:30 - WordPress Plugin Update
- Lean CTAs v2.1.0 deployed to cristiantala.com via SFTP
- PHP version issue on WPMU DEV resolved (specified /usr/local/php83/bin/php)
- Plugin Check: 0 warnings remaining

## 14:00 - Cloudflare Pages Optimization
- Performance: 81 → 97 (Lighthouse)
- Accessibility: 76 → 95 (Lighthouse)
- robots.txt was causing 507 errors — added and fixed
```

### Archive

**Purpose:** Historical record for reference, not active context.
**Format:** `memory/ARCHIVE-YYYY-MM.md` (monthly archives)
**When:** Entries >7 days old moved from MEMORY.md

```markdown
# ARCHIVE-2026-02

## Feb 19: Memory Optimization (-69.8% context)
Context reduced from 85KB to 27KB.
Key change: MEMORY.md moved from 40KB to 4KB.
Impact: $135/month savings.

## Feb 15: n8n-specialist sub-agent operational
First specialized sub-agent deployed in production.
Skills evolved to include Agent Identity section.
```

---

## 2. Size Targets

| File | Target | Hard Limit | Action if Over |
|------|--------|------------|----------------|
| `MEMORY.md` | ≤4KB | 6KB | Archive entries >7 days old |
| `AGENTS.md` | ≤4KB | 5KB | Move detailed instructions to sub-files |
| `TOOLS.md` | ≤10KB | 12KB | Move detailed docs to `docs/tools-modules/` |
| `SOUL.md` | ≤1KB | 2KB | Persona core only, no examples |
| Daily logs | Unconstrained | N/A | Move to archive after 30 days |

### Why These Targets?

Every file in the workspace is potentially loaded into the agent's bootstrap context. If MEMORY.md is 40KB, that's 10,000 tokens added to every session start — whether the content is relevant or not.

At $0.003 per 1K tokens (Sonnet), a 40KB MEMORY.md costs:
- `10,000 tokens × $0.003/1K = $0.03 per session`
- `100 sessions/month × $0.03 = $3/month` just for loading stale memory

A 4KB MEMORY.md costs $0.30/month. **Same information density, 10x cheaper.**

---

## 3. Memory Flush Pre-Compaction

OpenClaw compacts context when it approaches the token limit. Before compaction, the agent loses recent context. The **memory flush** pattern preserves critical information:

### What Memory Flush Does

When context approaches limit:
1. Agent detects approaching limit (via `session_status`)
2. Writes critical recent context to `MEMORY.md` before compaction
3. Archives completed tasks and old entries
4. Compaction happens with leaner context
5. Next session loads updated MEMORY.md with preserved context

### Implementation

```python
# In HEARTBEAT.md or as triggered process
def pre_compaction_memory_flush():
    """
    Run before context compaction to preserve critical information.
    """
    # 1. Check if compaction is imminent
    status = session_status()
    if status.context_usage < 0.85:  # 85% threshold
        return  # Not needed yet
    
    # 2. Write recent critical events to MEMORY.md
    # (whatever happened in last 2 hours that must survive compaction)
    
    # 3. Archive MEMORY.md entries >7 days old
    
    # 4. Confirm MEMORY.md ≤ 4KB
```

**Practical usage:** The agent should check context usage at natural breakpoints (after completing a significant task) and flush if above 80%.

---

## 4. Nightly Optimization Cron (3 AM)

**Schedule:** Daily at 3:00 AM (local time) via OpenClaw cron
**Model:** Haiku (simple operations, no creative reasoning needed)
**Session type:** Isolated

### What It Does

```
1. Validate file references (find broken paths in AGENTS.md, TOOLS.md, skills)
2. Clean orphan entries (MEMORY.md entries for completed tasks)
3. Archive old entries (move entries >7 days to ARCHIVE-YYYY-MM.md)
4. Size check (alert if any file exceeds target)
5. Git commit (backup workspace changes to GitHub)
6. Report summary to Telegram
```

### Reference Validation

Check for broken file references in key docs:

```bash
#!/bin/bash
# validate-refs.sh - Find broken file references in markdown files

WORKSPACE="~/clawd"
ISSUES=0

grep -rh '\`[^`]*\`' "$WORKSPACE/AGENTS.md" "$WORKSPACE/TOOLS.md" | \
  grep -oE '~/clawd/[a-zA-Z0-9/_.-]+' | \
  while read path; do
    expanded="${path/\~\/clawd/$WORKSPACE}"
    if [ ! -e "$expanded" ]; then
      echo "BROKEN REF: $path"
      ISSUES=$((ISSUES + 1))
    fi
  done

echo "Reference validation complete. Issues found: $ISSUES"
```

**Common broken refs:**
- Skill files that were renamed or moved
- Scripts referenced in TOOLS.md that were deleted
- Config files referenced before they were created

### Archive Automation

```python
# archive-old-entries.py
import re
from datetime import datetime, timedelta

def archive_old_entries(memory_path, archive_dir):
    """Move MEMORY.md entries older than 7 days to monthly archive."""
    
    with open(memory_path, 'r') as f:
        content = f.read()
    
    cutoff_date = datetime.now() - timedelta(days=7)
    
    # Parse entries with dates
    entries_to_archive = []
    entries_to_keep = []
    
    # ... parsing logic ...
    
    # Write updated MEMORY.md (kept entries only)
    # Append to ARCHIVE-YYYY-MM.md (archived entries)
```

---

## 5. Git as Backup

Workspace files should be committed to GitHub daily. This provides:
- Version history for all memory files
- Recovery point if server fails
- Diff view to see what changed over time

### Daily Git Commit (5 AM Cron)

```bash
#!/bin/bash
# daily-git-commit.sh

cd ~/clawd

git add -A
git commit -m "Daily backup $(date +%Y-%m-%d)" || echo "Nothing to commit"
git push origin main
```

**What gets committed:**
- MEMORY.md (current state)
- Daily log files (new entries)
- Archive files (newly archived entries)
- Skill updates
- Config changes

**What does NOT get committed:**
- `.secrets/` (API keys, credentials — in .gitignore)
- Temporary files
- Large media files

---

## 6. Embeddings for Semantic Search

### Purpose

With 38+ files in workspace, keyword search is insufficient. Embeddings enable: "find entries related to LinkedIn engagement" → returns relevant entries from MEMORY.md, daily logs, and skill files.

### Configuration

```json
// OpenClaw config.json
{
  "embeddings": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "batchApi": true,
    "debounceMs": 30000,
    "lazyIndexing": true,
    "excludePaths": [".secrets/", "*.zip", "*.jpg", "*.png"]
  }
}
```

**Key settings:**
- `batchApi: true` — Use OpenAI Batch API (50% cost reduction vs real-time)
- `debounceMs: 30000` — Don't re-index until 30 seconds after last change (prevents re-indexing on every keystroke)
- `lazyIndexing: true` — Index on first search, not on file change
- `excludePaths` — Skip binary files and secrets

### Cost

- OpenAI text-embedding-3-small: $0.02 per 1M tokens
- Initial indexing of 38 files (~200K tokens total): **$0.004** (one-time)
- Incremental updates (daily changes): ~$0.0001/day

**Total embedding cost:** Negligible.

---

## 7. Quick Reference

### Memory Health Check

```bash
# Check file sizes
wc -c ~/clawd/MEMORY.md     # Should be < 4096 bytes
wc -c ~/clawd/AGENTS.md     # Should be < 4096 bytes
wc -c ~/clawd/TOOLS.md      # Should be < 10240 bytes

# Count entries in MEMORY.md
grep -c "^##" ~/clawd/MEMORY.md  # Should be < 20 active entries

# Check for broken refs (run validate-refs.sh)
bash ~/clawd/scripts/validate-refs.sh
```

### Emergency Memory Reduction

If MEMORY.md is over 6KB and causing issues:

```bash
# 1. View current entries
cat ~/clawd/MEMORY.md | grep "^##"

# 2. Identify oldest entries
# Any entry with date >7 days old → move to archive

# 3. Create/append to archive
cat >> ~/clawd/memory/ARCHIVE-$(date +%Y-%m).md << 'EOF'
# Entries archived from MEMORY.md on $(date +%Y-%m-%d)
[paste old entries here]
EOF

# 4. Remove old entries from MEMORY.md
# (manual edit or script)
```

---

## Related Resources

- [docs/05-memory-optimization.md](05-memory-optimization.md) — Deep dive on context optimization
- [Case 5: Why Haiku Failed](../cases/05-why-haiku-failed.md) — Degradation from over-optimization
- `scripts/validate-refs.sh` — Reference validation script

---

*Last updated: 2026-03-12 | Version: 1.2.0*
