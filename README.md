# OpenClaw Production Guide

> **Real-world optimization from a founder who sold his tech startup and now mentors others in tech and automation**

Running OpenClaw in production is different from running it as a toy project. This guide shares hard-earned lessons from **45+ files indexed, 130+ active tasks, 20+ automated workflows, and countless hours optimizing costs without sacrificing quality.**

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

**Before optimization (Jan 2026):**
- ~$90/month (Sonnet everywhere)
- Context: 85KB bootstrap (21,400 tokens)
- Embeddings disabled (batch API blocking)
- Manual task management
- Single monolithic agent

**After optimization (Feb 2026):**
- ~$45/month (50% reduction) 🎯
- Context: 27KB bootstrap (6,472 tokens, -69.8%)
- Embeddings active (382 chunks, 0 failures, Batch API enabled)
- Automated task prioritization (Opus 4.6 cron @ 05:30 AM)
- Multi-agent architecture (n8n-specialist operational)
- Model routing based on task complexity

**Key insights:**
1. **Context optimization = biggest win** — $135/month savings from memory archival alone
2. **Strategic model selection > blanket downgrading** — Haiku failed 67% of tasks
3. **Multi-agent architecture** — Haiku + 5KB context ≈ Sonnet + 27KB context (4x cheaper)
4. **Heartbeats → Nano** — 95% cost reduction for background checks

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
- **Model Selection Strategy** — Mistral Large default, Sonnet auto-upgrade, why Haiku failed 67% of tasks
- **Embeddings Optimization** — OpenAI Batch API + debounce + lazy indexing
- **Heartbeat Efficiency** — Groq for background checks (95% cost reduction)
- **Cron Strategy** — Isolated sessions with task-specific models

### 3. [Performance Tuning](docs/03-performance-tuning.md)
- **Session Management** — Context limits, compaction, memory flush
- **Tool Call Efficiency** — Output TTL, context limit overrides
- **Memory Search** — When to use, how to structure
- **Anti-Patterns** — Common pitfalls that burn tokens

### 4. [Production Patterns](docs/04-production-patterns.md)
- **Multi-Channel Routing** — Telegram Topics, Discord channels, email
- **Subagent Orchestration** — When to spawn, orchestrator model selection
- **Error Handling** — Graceful degradation, retry logic
- **Monitoring** — What to track (costs, latency, failure rates)

### 5. [Memory Optimization](docs/05-memory-optimization.md) 🆕
- **Context Bloat Analysis** — MEMORY.md = 48% of bootstrap (40KB/85KB)
- **Layered Memory Architecture** — Working memory vs Archive
- **Automated Archival** — Nightly optimization skill
- **Real Results** — 21,400 → 6,500 tokens (-69.8%), $135/month savings

### 6. [Multi-Agent Architecture](docs/06-multi-agent-architecture.md)
- **Specialized Sub-Agents** — n8n-specialist, content-creator, wordpress-publisher
- **Context Efficiency** — 5KB focused > 27KB generic
- **Cost Savings** — Haiku + small context ≈ Sonnet + large context (4x cheaper)
- **Real Results** — n8n-specialist operational, production-ready workflows

### New in v1.2.0:
- **[Multi-Agent Patterns](docs/multi-agent-patterns.md) 🆕** — Agent Identity pattern, orchestration, anti-patterns
- **[Cloudflare R2 + Pages](docs/cloudflare-r2-pages.md) 🆕** — CDN and hosting at $0/month
- **[Memory Management](docs/memory-management.md) 🆕** — Daily logs, archives, size targets, nightly optimization
- **[Infrastructure Lessons](docs/infrastructure-lessons.md) 🆕** — SSH hell, filesystem crisis, PHP mismatches

### 7. [Real-World Cases](cases/)
- [Case 1: Skool Community Automation](cases/01-skool-automation.md) — 93.75% accuracy, inline buttons workflow
- [Case 2: LinkedIn Response System](cases/02-linkedin-responses.md) — Unipile API + Mistral Large 2512
- [Case 3: Newsletter Sync (Listmonk)](cases/03-newsletter-sync.md) — 1,923 subscribers, $348/year saved
- [Case 4: SEO Weekly Reports](cases/04-seo-weekly-reports.md) — Serpstat API + NocoDB tracking
- [Case 5: Why Haiku Failed](cases/05-why-haiku-failed.md) — Real task analysis, honest assessment
- [Case 6: Task Management (NocoDB)](cases/06-task-management-nocodb.md) — 99 active tasks, daily AI optimization
- [Case 7: Infrastructure (Docker + Caddy)](cases/07-infrastructure-docker-caddy.md) — 8 services, wildcard SSL, $552/year saved
- [Case 8: n8n Workflow Automation](cases/08-n8n-workflow-automation.md) — 20+ workflows, 15 hours/week saved
- [Case 9: Skool Member Validation](cases/09-skool-member-validation.md) — LinkedIn identity verification, "Sky is the limit"
- **[Case 10: Multi-Agent Orchestration](cases/10-multi-agent-orchestration.md) 🆕** — Spawnable sub-agents, 8-hour strategy → 30 min
- **[Case 11: WordPress Plugin Pipeline](cases/11-wordpress-plugin-pipeline.md) 🆕** — Dev to deploy across multiple hosts, $0/month
- **[Case 12: LinkedIn Posting Party](cases/12-linkedin-posting-party.md) 🆕** — Real-time tracking for 12 participants, algorithm insights
- **[Case 13: Cloudflare Pages Landings](cases/13-cloudflare-pages-landings.md) 🆕** — Static pages, 97 Lighthouse, $0/month hosting

### 8. [Ready-to-Use Configs](configs/)
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
- **Models:** Mistral Large 2512 (default), Sonnet 4.6 (editorial + community), Opus 4.6 (crons + analysis), Groq (heartbeats), Haiku 4.5 (simple mechanical tasks only)
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

## 📄 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** — Version history and release notes
- **README.md** — This file (main index)
- **docs/** — Deep-dive guides
- **cases/** — Real-world case studies
- **configs/** — Ready-to-use configurations
- **scripts/** — Helper scripts and tools

---

## 📄 License

MIT License — feel free to use, adapt, and share. Attribution appreciated.

---

## 🙏 Acknowledgments

- **OpenClaw Team** — for building an incredible agent framework
- **Community Contributors** — for sharing real-world patterns and case studies
- **Early Readers** — for feedback that shaped this guide

---

## 🆕 What's New in v1.3.0 (March 2026)

### Fixes & Updates
- **Fixed 9 broken internal links** across docs and configs
- **Updated model names:** Sonnet 4.5 → 4.6, Opus 4.5 → 4.6 everywhere
- **Default model is now Mistral Large 2512** (not Haiku) — reflects actual production setup
- **Created 3 missing docs:** `02-cost-optimization.md`, `03-performance-tuning.md`, `04-production-patterns.md`
- **Genericized internal paths** (removed server-specific paths for public consumption)
- **Expanded orchestrator model benchmark** to 10 models across 5 providers (Anthropic, Google, OpenAI, Mistral, OpenRouter, Groq)
- **Added ORCHESTRATOR MODEL SELECTION section** to multi-agent docs with full cost/quality data

### Key New Insight: Orchestrator Model Matters
Sonnet 4.6 is the recommended default orchestrator (8.5/10, $1.20/month). Gemini 2.5 Pro is a strong tier-2 alternative ($0.80/month). Haiku at 4/10 cannot synthesize multi-agent outputs — it only routes. The $0.25/month saved is not worth the 50% quality loss.

---

## 🆕 What's New in v1.2.0 (March 2026)

### New Case Studies
- **Multi-Agent Orchestration** — Turn 8-hour strategy sessions into 30-minute parallel agent execution
- **WordPress Plugin Pipeline** — Build once, deploy anywhere (WPMU DEV, Rocket.net, WordPress.org)
- **LinkedIn Posting Party** — Real-time tracking for engagement groups with algorithm insights
- **Cloudflare Pages Landings** — Kill WordPress for landing pages, get 97 Lighthouse score at $0/month

### New Documentation
- **Multi-Agent Patterns** — Agent Identity pattern, orchestration best practices, anti-patterns
- **Cloudflare R2 + Pages** — CDN and hosting setup, cache headers, CORS troubleshooting
- **Memory Management** — Size targets, nightly optimization, reference validation
- **Infrastructure Lessons** — Filesystem crisis recovery, SSH per-provider, PHP version hell

### Key Learnings
- LinkedIn Algorithm Q1 2026: -60% distribution for body links, +69% for native video, 15+ word comments = 2.5x weight
- Skills evolved from API docs to spawnable agent identities (Agent Identity + Workflow Integration + Decision Framework)
- Unipile API returns 0 for 2nd-degree connections — browser fallback required
- `clawdbot.service` must be `enabled` (not just `started`) to survive reboots

---

**Last Updated:** 2026-03-12  
**Version:** 1.3.0  
**Production Runtime:** 90+ days, 45+ files indexed, 130+ active tasks, 20+ automated workflows  
**Recent Additions:**
- Multi-Agent Orchestration case (4 new cases total)
- Memory Management + Infrastructure Lessons docs
- LinkedIn Algorithm Q1 2026 data (van der Blom 1.8M post study)
- Model routing for sub-agents and orchestration
