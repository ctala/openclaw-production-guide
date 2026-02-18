# Ready-to-Use Configs

These configs are tested in production. Copy, paste, restart.

---

## 🚀 Quick Start

### 1. Embeddings Optimization

**File:** [`embeddings-optimized.json`](embeddings-optimized.json)

**What it does:**
- ✅ Enables Batch API (async, non-blocking)
- ✅ Increases debounce to 30s (prevents constant reindexing)
- ✅ Disables sync on session start (lazy indexing)
- ✅ Enables embedding cache (50K entries)

**Benefit:**
- No more frozen conversations
- Background indexing
- ~$0.003 one-time cost

**Apply:**
```bash
openclaw gateway config.patch embeddings-optimized.json
openclaw gateway restart
```

[Full guide →](../01-cost-optimization/embeddings.md)

---

### 2. Model Routing

**File:** [`model-routing.json`](model-routing.json)

**What it does:**
- ✅ Sonnet for main work
- ✅ Haiku for heartbeats
- ✅ Opus as fallback

**Benefit:**
- 95% reduction in heartbeat costs
- Quality maintained for main work

**Apply:**
```bash
openclaw gateway config.patch model-routing.json
openclaw gateway restart
```

[Full guide →](../01-cost-optimization/heartbeats.md)

---

### 3. Context Pruning

**File:** [`context-pruning.json`](context-pruning.json)

**What it does:**
- ✅ Limits context accumulation
- ✅ Sets TTL for tool outputs (6h)
- ✅ Enables default compaction

**Benefit:**
- 20-30% token reduction
- Faster responses

**Apply:**
```bash
openclaw gateway config.patch context-pruning.json
openclaw gateway restart
```

[Full guide →](../01-cost-optimization/context-management.md)

---

## 🎯 All-in-One (Coming Soon)

**File:** `full-optimized.json`

All optimizations combined. Use if you want everything at once.

**Coming soon** — Testing complete integration first.

---

## ⚠️ Before Applying

### 1. Backup Your Config

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup-$(date +%Y%m%d)
```

### 2. Understand What You're Changing

Read the guide for each optimization. Don't apply blindly.

### 3. Apply One at a Time

**Don't apply all three at once.**

- Day 1: Embeddings
- Day 2: Model routing (if embeddings worked)
- Day 3: Context pruning (if both worked)

**Why?** If something breaks, you'll know what caused it.

---

## 🔧 How Config Patch Works

OpenClaw's `config.patch` merges your changes with existing config.

**Example:**

**Your config:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      }
    }
  }
}
```

**You apply:** `model-routing.json`
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "model": "anthropic/claude-haiku-4-5"
      }
    }
  }
}
```

**Result:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      },
      "heartbeat": {
        "model": "anthropic/claude-haiku-4-5"
      }
    }
  }
}
```

**It merges, doesn't replace.** Safe to apply.

---

## 🚨 Troubleshooting

### Config patch failed

**Check:**
1. JSON valid? Validate with `jq`:
   ```bash
   jq . embeddings-optimized.json
   ```

2. Gateway running?
   ```bash
   openclaw gateway status
   ```

### Changes not applied

**Solution:**
```bash
# Restart gateway
openclaw gateway restart

# Verify changes
openclaw config.get | jq '.agents.defaults.memorySearch'
```

### Want to rollback

```bash
# Restore backup
cp ~/.openclaw/openclaw.json.backup-YYYYMMDD ~/.openclaw/openclaw.json

# Restart
openclaw gateway restart
```

---

## 📝 Customizing Configs

Feel free to modify these configs for your use case.

**Common customizations:**

**Embeddings:**
- Adjust `watchDebounceMs` (higher = less frequent indexing)
- Change `maxResults` (more results = broader search)
- Adjust `minScore` (higher = stricter matching)

**Models:**
- Use different primary model
- Add more fallbacks
- Use Nano instead of Haiku (even cheaper)

**Context:**
- Adjust TTL (shorter = more aggressive pruning)
- Change compaction mode

---

## 🤝 Contributing Better Configs

Have a config that works better? **Submit a PR.**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Questions?** Open an issue or check the [FAQ](../06-community/faq.md).
