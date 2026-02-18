# OpenClaw Production Guide

> **Real-world optimization from a founder who sold his tech startup and now mentors others in tech and automation**

Running OpenClaw in production is different from running it as a toy project. This guide shares hard-earned lessons from **38 files indexed, 99 active tasks, 12 automated workflows, and countless hours optimizing costs without sacrificing quality.**

**Who this is for:** Founders, operators, and technical leaders running OpenClaw 24/7 for real business workflows—not just experimentation.

---

## 🎯 What You'll Learn

- **Cost Optimization** — Why "just use Haiku" doesn't always work (and when it does)
- **Performance Tuning** — Embeddings, memory search, session management, tool efficiency
- **Production Patterns** — Multi-channel routing, subagent orchestration, error handling
- **Real-World Cases** — Skool automation, LinkedIn engagement, newsletter sync, SEO workflows
- **Ready-to-Use Configs** — Drop-in optimizations you can implement today

---

## 📊 Results from Production

**Before optimization:**
- ~$90/month (Sonnet everywhere)
- Embeddings disabled (batch API blocking)
- Manual task management
- Inconsistent model selection

**After optimization:**
- ~$70/month (22% reduction)
- Embeddings active (382 chunks, 0 failures, Batch API enabled)
- Automated task prioritization (Opus 4.6 cron @ 05:30 AM)
- Model routing based on task complexity

**Key insight:** The biggest savings came from **strategic model selection** (not blanket downgrading) and **optimizing heartbeats → Nano** (95% cost reduction for background checks).

---

## 🧠 Why This Guide Exists

Most OpenClaw guides show you how to *set it up*. Few show you how to *run it at scale* when:

- Token costs compound quickly (400K context = $$$ per turn)
- Not every task can use the cheapest model
- You need predictable performance for business workflows
- Downtime = lost revenue or missed opportunities

**My background:**
- Sold my tech startup (fintech), now angel investor and mentor
- 30+ startup investments across Latin America
- Running OpenClaw 24/7 for content automation, community engagement, and business operations
- Mentoring founders in tech, automation, and startup growth

This guide distills **what actually works** when cost, quality, and reliability all matter.

---

## 📚 Table of Contents

### 1. [Introduction](docs/01-introduction.md)
- Who this guide is for
- My production setup (high-level)
- Results and lessons learned

### 2. [Cost Optimization](docs/02-cost-optimization.md)
- **Model Selection Strategy** — Why Haiku failed 67% of my tasks
- **Embeddings Optimization** — OpenAI Batch API + debounce + lazy indexing
- **Heartbeat Efficiency** — Rotating checks + Nano for background jobs
- **Cron Strategy** — Isolated sessions with task-specific models

### 3. [Performance Tuning](docs/03-performance-tuning.md)
- **Session Management** — Context limits, compaction, memory flush
- **Tool Call Efficiency** — Output TTL, context limit overrides
- **Memory Search** — When to use, how to structure
- **Anti-Patterns** — Common pitfalls that burn tokens

### 4. [Production Patterns](docs/04-production-patterns.md)
- **Multi-Channel Routing** — Telegram Topics, Discord channels, email
- **Subagent Orchestration** — When to spawn isolated sessions
- **Error Handling** — Graceful degradation, retry logic
- **Monitoring** — What to track (costs, latency, failure rates)

### 5. [Real-World Cases](cases/)
- [Case 1: Skool Community Automation](cases/01-skool-automation.md) — 93.75% accuracy, inline buttons workflow
- [Case 2: LinkedIn Response System](cases/02-linkedin-responses.md) — Unipile API + Mistral Large 2512
- [Case 3: Newsletter Sync (Listmonk)](cases/03-newsletter-sync.md) — 1,923 subscribers, automated campaigns
- [Case 4: SEO Weekly Reports](cases/04-seo-weekly-reports.md) — Serpstat API + NocoDB tracking
- [Case 5: Why Haiku Failed](cases/05-why-haiku-failed.md) — Real task analysis, honest assessment

### 6. [Ready-to-Use Configs](configs/)
- [Optimized embeddings config](configs/embeddings-optimized.json)
- [Model routing rules](configs/model-routing-rules.json)
- [Heartbeat templates](configs/heartbeat-templates.md)
- [Cron job examples](configs/cron-examples.json)

### 7. [Scripts](scripts/)
- [Enable optimized embeddings](scripts/enable-optimized-embeddings.sh)
- [Cost calculator](scripts/cost-calculator.py)
- [Task complexity analyzer](scripts/analyze-task-complexity.py)

---

## 🚀 Quick Wins (Start Here)

If you're just getting started optimizing, these are the highest ROI changes:

### 1. **Enable Batch Embeddings** (5 min, $0 → works)
```bash
bash scripts/enable-optimized-embeddings.sh
```
**Impact:** Fixes blocking issues, enables memory search, minimal cost increase

### 2. **Switch Heartbeats to Nano** (10 min, 95% cost reduction)
- Heartbeats don't need Sonnet—they just check if something needs attention
- Switch to `groq-fast` or similar Nano model
- **Savings:** ~$15/month if you poll every 30 minutes

### 3. **Audit Your Task Types** (30 min, prevents blanket downgrade mistakes)
```bash
python3 scripts/analyze-task-complexity.py
```
**Reality check:** In my case, only 25-33% of tasks could use Haiku. Don't blindly downgrade.

### 4. **Implement Model Routing** (1h, 15-20% cost reduction)
- Use `configs/model-routing-rules.json` as a starting point
- Route by task type: heartbeats → Nano, editorial → Sonnet, chat → Mistral Large
- **Savings:** $12-18/month without quality loss

### 5. **Optimize Cron Sessions** (1h, isolated + task-specific models)
- Use `sessionTarget: isolated` for background jobs
- Pick model based on task complexity (not one-size-fits-all)
- Example: SEO reports → Opus 4.6 (needs deep analysis), simple checks → Haiku
- **Savings:** $8-12/month by not running Sonnet for trivial tasks

---

## 💡 Key Principles

### 1. **Cost Optimization ≠ Blanket Downgrade**
"Use Haiku for everything" sounds great until your editorial content sounds robotic, your task prioritization misses nuance, or your community responses feel generic.

**Better approach:** Match model to task complexity.

### 2. **Measure Twice, Optimize Once**
Before changing models:
1. Audit your actual tasks (not hypothetical ones)
2. Test model changes on non-critical workflows first
3. Monitor quality + cost for 1-2 weeks
4. Roll out gradually

**My mistake:** I assumed Haiku would handle 80% of tasks. Reality: 25-33%. Measuring first would have saved me hours of testing.

### 3. **Embeddings Are Not Optional at Scale**
Memory search is what makes OpenClaw useful beyond 50-100 files. The cost is negligible compared to the value.

**My setup:** OpenAI text-embedding-3-small, Batch API, 30s debounce, lazy indexing.  
**Cost:** ~$0.003 one-time indexing, then cached.  
**Value:** Instant recall across 38 files, 382 chunks, 0 failures.

### 4. **Heartbeats Should Be Cheap (But Functional)**
Polling every 30 minutes with Sonnet = $45/month just for "nothing to report" responses.

**Solution:** Rotating heartbeat coordinator (Nano model) that spawns Sonnet subagents only when action is needed.

**Savings:** $30-40/month.

### 5. **Production = Boring (On Purpose)**
The best production systems are predictable, monitored, and boring.

- ✅ Crons run at the same time daily
- ✅ Errors send alerts (not silent failures)
- ✅ Cost spikes trigger notifications
- ✅ Task assignments follow clear rules

**Anti-pattern:** Ad-hoc "try this model" experiments in production. Test in isolated sessions first.

---

## 🛠️ Tech Stack (My Setup)

- **OpenClaw Runtime:** agent=main, host=VPS srv1301687
- **Models:** Sonnet 4.5 (primary), Opus 4.6 (crons), Mistral Large 2512 (LinkedIn), Haiku (simple tasks)
- **Embeddings:** OpenAI text-embedding-3-small (Batch API enabled)
- **Task Management:** NocoDB (99 active tasks)
- **Automation:** n8n (3 instances: dev, prod, cloud)
- **Messaging:** Telegram (main), Discord (communities)
- **Content:** WordPress (cristiantala.com), Listmonk (newsletters), Late API (social scheduling)
- **Infrastructure:** Caddy reverse proxy, Docker, Cloudflare DNS

---

## 📖 How to Use This Guide

### If you're just starting OpenClaw in production:
1. Read [Introduction](docs/01-introduction.md)
2. Follow [Quick Wins](#-quick-wins-start-here) (2-3 hours)
3. Implement [Cost Optimization](docs/02-cost-optimization.md) gradually (1-2 weeks)

### If you're already running but costs are high:
1. Run [cost-calculator.py](scripts/cost-calculator.py) to baseline current spend
2. Read [Case 5: Why Haiku Failed](cases/05-why-haiku-failed.md) (avoid my mistakes)
3. Implement [Model Routing](configs/model-routing-rules.json)

### If you're optimizing for performance:
1. Start with [Performance Tuning](docs/03-performance-tuning.md)
2. Read [Production Patterns](docs/04-production-patterns.md)
3. Check [Real-World Cases](cases/) for patterns similar to your use case

---

## 🤝 Contributing

This guide evolves based on real production feedback. If you're running OpenClaw at scale and have lessons to share:

1. **Case Studies:** Share your automation workflow (anonymized OK)
2. **Optimizations:** New cost-saving techniques or performance patterns
3. **Configs:** Production-tested configurations that others can use
4. **Bug Fixes:** Corrections or improvements to existing docs

**Preferred format:** Open an issue first to discuss, then PR with changes.

**Community submissions welcome** — if your case study gets merged, you'll be credited as a contributor.

---

## 📬 Contact & Community

- **Author:** Cristian Tala Sánchez
  - Exit founder, angel investor, startup mentor
  - Blog: [cristiantala.com](https://cristiantala.com)
  - LinkedIn: [linkedin.com/in/ctala](https://linkedin.com/in/ctala)
  - Twitter: [@naitus](https://twitter.com/naitus)

- **Community:** Join the discussion
  - OpenClaw Discord: [discord.com/invite/clawd](https://discord.com/invite/clawd)
  - Submit case studies: [Open an issue](https://github.com/ctala/openclaw-production-guide/issues/new)

---

## 📄 License

MIT License — feel free to use, adapt, and share. Attribution appreciated.

---

## 🙏 Acknowledgments

- **OpenClaw Team** — for building an incredible agent framework
- **Community Contributors** — for sharing real-world patterns and case studies
- **Early Readers** — for feedback that shaped this guide

---

**Last Updated:** 2026-02-18  
**Version:** 1.0.0  
**Production Runtime:** 60+ days, 38 files indexed, 99 active tasks, 12 automated workflows
