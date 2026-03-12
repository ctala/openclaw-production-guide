# Changelog - OpenClaw Production Guide

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.0] - 2026-03-12

### Fixed

**Broken internal links (9 total):**
- `docs/01-introduction.md`: `../cases/` → individual case file links
- `docs/01-introduction.md`: `../configs/` → `../configs/README.md`
- `docs/01-introduction.md`: `../scripts/` → `../scripts/cost-calculator.py`
- `configs/README.md`: `../01-cost-optimization/embeddings.md` → `../docs/05-memory-optimization.md`
- `configs/README.md`: `../01-cost-optimization/heartbeats.md` → `../docs/02-cost-optimization.md`
- `configs/README.md`: `../01-cost-optimization/context-management.md` → `../docs/03-performance-tuning.md`
- `configs/README.md`: `../CONTRIBUTING.md` (non-existent) → removed
- `configs/README.md`: `../06-community/faq.md` (non-existent) → removed

**Model version updates:**
- `claude-sonnet-4-5` → `claude-sonnet-4-6` across all files
- `claude-opus-4-5` → `claude-opus-4-6` where applicable
- Files updated: `docs/multi-agent-patterns.md`, `configs/model-routing.json`, `configs/model-routing-rules.json`, `configs/README.md`, `cases/10-multi-agent-orchestration.md`, `CHANGELOG.md`

**Internal path generalization:**
- `/home/moltbot/clawd/` → `~/openclaw-workspace/` in all public-facing docs
- `User moltbot` → `User clawd-user` in SSH config examples

### Added

**Missing documentation (3 files):**
- `docs/02-cost-optimization.md` — Full cost optimization guide
  - Model selection strategy (Mistral Large default, Sonnet auto-upgrade, Opus for analysis)
  - Embedding optimization (Batch API, debounce, lazy indexing, cost breakdown)
  - Heartbeat optimization (Groq, 95% cost reduction, escalation pattern)
  - Context management (layered architecture, pruning config)
  - Cron optimization (isolated sessions, model-per-cron table)
  - Real numbers: $90/month → $45/month with breakdown of savings sources

- `docs/03-performance-tuning.md` — Performance tuning guide
  - Memory search configuration (`minScore` tuning, Batch API, production numbers)
  - Session management (context limits, compaction config, memory flush protocol)
  - Tool call efficiency (output TTL, context limit overrides per tool)
  - Anti-patterns (5 documented: reading files every turn, full context for specialized tasks, tight poll loops, sub-agent with full context, storing payloads in MEMORY.md)
  - Response time reference table across 6 models/providers
  - Monitoring dashboard (NocoDB metrics table)

- `docs/04-production-patterns.md` — Production patterns guide
  - Multi-channel routing (Telegram Topics, Discord, WebChat binding config)
  - Error handling (graceful degradation, alert strategy, retry logic)
  - Cron vs heartbeat distinction (clear definitions, model per role, cost comparison)
  - Sub-agent orchestration (when to spawn, execution boundary enforcement)
  - Affiliate link strategy (active programs, insertion rules, n8n automation)
  - Monitoring (cost metrics, quality metrics, `clawdbot.service` lesson)

**Orchestrator model selection section:**
- Added to `docs/multi-agent-patterns.md` and `docs/06-multi-agent-architecture.md`
- Full benchmark: 10 models across 6 providers (Anthropic, Google, OpenAI, Mistral, OpenRouter, Groq)
- Key data: Sonnet 4.6 recommended default (8.5/10, $1.20/month), Gemini 2.5 Pro tier-2 (8.0/10, $0.80/month), Opus 4.6 for complexity (9.5/10, $2.40/month)
- Haiku explicitly disqualified (4.0/10, routes only, cannot synthesize)
- Side-by-side output example: Haiku pastes reports, Sonnet detects conflicts and adjusts plan
- Anti-pattern documented: $0.25/month saved with Haiku = 50% quality loss, not worth it

### Changed

**Default model narrative:**
- Updated throughout docs to reflect actual production setup: Mistral Large 2512 as default (not Haiku)
- Auto-upgrade logic documented: Mistral → Sonnet for editorial/community; Mistral → Opus for analysis
- Case 5 ("Why Haiku Failed") preserved as historical lesson — still accurate and relevant

**configs/model-routing.json:**
- `primary` updated to `mistral/mistral-large-2512`
- Heartbeat updated to `groq/groq-llama`
- Fallbacks: Sonnet 4.6, Haiku 4.5

**configs/model-routing-rules.json:**
- Version: 1.2.0 → 1.3.0
- `orchestration` rule: model updated to `sonnet` (default), `opus` as upgrade
- Added full `benchmark` block with 10-model production data across all providers
- `model_versions.sonnet` updated to `claude-sonnet-4-6`

**configs/README.md:**
- Broken links replaced with valid paths
- Model routing "What it does" section updated to reflect Mistral Large default + Groq heartbeats
- `config.patch` example updated to show Mistral Large as primary
- CONTRIBUTING.md and FAQ references removed (files don't exist)

**README.md:**
- Version: 1.2.0 → 1.3.0
- Tech Stack models updated to current setup
- TOC descriptions updated for cost optimization and production patterns
- Added v1.3.0 "What's New" section

**Production checklist in multi-agent-patterns.md:**
- Orchestrator rule updated: Sonnet 4.6 default, Opus for 3+ agents / strategic decisions

### Technical Notes

**Why the default model change matters:**
Haiku as default was the initial recommendation in v1.0.0, based on cost theory. After 90 days of production use, only 25–33% of actual tasks are viable with Haiku. Mistral Large 2512 at $0.004/call handles 70%+ of tasks with good quality. The remaining 30% get auto-upgraded to Sonnet or Opus based on task type. This is the actual setup, documented accurately.

**Orchestrator model benchmark methodology:**
20 identical 3-agent orchestration runs (Growth Hacker + Campaign Builder + UI Designer) per model. Scored by: conflict detection (0-10), cross-referencing (0-10), synthesis coherence (0-10), actionable plan quality (0-10). Averaged to produce quality score. Cost calculated at actual API pricing. Speed measured wall clock from orchestration start to synthesis complete.

---

## [1.2.0] - 2026-03-12

### Added

**Case Studies (4 new):**
- `cases/10-multi-agent-orchestration.md` — Spawnable specialized sub-agents
  - Growth Hacker, Campaign Builder, UI Designer agents
  - Agent Identity pattern: identity + workflow + decision framework
  - Parallel execution (8-hour strategy → 30 min automated)
  - Dedicated Telegram Topics per agent (bidirectional)
  - Model selection: Sonnet for sub-agents, Opus for orchestration
  - Anti-pattern documented: don't let sub-agents execute externally
  - Cost: ~$0.15-0.30 per orchestrated run

- `cases/11-wordpress-plugin-pipeline.md` — Plugin development and deployment
  - Two plugins built: Lean Redirects + Lean CTAs
  - R2 CDN for zip distribution
  - SSH config per provider (WPMU DEV, Rocket.net, Hostinger)
  - WP-CLI PHP version mismatch fixes
  - REST API fallback when SSH blocked
  - WordPress.org submission process (DNS verification)
  - Cost: $0/month

- `cases/12-linkedin-posting-party.md` — Real-time engagement tracking
  - Google Sheets as live dashboard
  - Unipile API + browser fallback for 2nd-degree connections
  - LinkedIn Algorithm Q1 2026 data (van der Blom 1.8M posts)
  - 15+ word comments = 2.5x weight
  - Links in body = -60% distribution
  - First comment strategy for links
  - Cost: $0/month

- `cases/13-cloudflare-pages-landings.md` — Static landing pages
  - GitHub → Cloudflare Pages pipeline
  - R2 for assets
  - Lighthouse: 81 → 97 Performance, 76 → 95 Accessibility
  - robots.txt fixing 507 errors
  - _headers for cache control
  - WCAG compliance details
  - Cost: $0/month vs $12-27/month WordPress

**Documentation (4 new):**
- `docs/multi-agent-patterns.md` — Architecture patterns reference
  - Agent Identity pattern (3 mandatory sections)
  - Spawnable sub-agents via sessions_spawn
  - Dedicated Telegram Topics for agent communication
  - Orchestration: parallel execution + cross-synthesis
  - Skills as docs vs skills as agents comparison
  - Anti-patterns documented

- `docs/cloudflare-r2-pages.md` — CDN and hosting guide
  - R2 bucket setup and custom domains
  - Upload script (scripts/upload-to-r2.sh)
  - Pages deployment from GitHub
  - Cache headers configuration
  - Cost comparison vs S3 (R2 wins on egress)
  - CORS troubleshooting

- `docs/memory-management.md` — Long-running agent memory
  - Three-layer architecture: working → daily → archive
  - Size targets: MEMORY.md ≤4KB, AGENTS.md ≤4KB, TOOLS.md ≤10KB
  - Memory flush pre-compaction
  - Nightly optimization cron (3 AM)
  - Reference validation script
  - Embeddings configuration

- `docs/infrastructure-lessons.md` — Production incidents and fixes
  - Hostinger filesystem read-only crisis (Mar 5)
  - clawdbot.service disabled silently (Mar 9)
  - SSH access per provider (WPMU DEV, Rocket.net, Hostinger)
  - PHP version mismatches (CLI vs web)
  - WP-CLI across environments
  - Monitoring recommendations

### Changed

**configs/model-routing-rules.json:**
- Updated model versions: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5
- Added `sub_agent_specialist` routing rule (Sonnet, focused context)
- Added `orchestration` routing rule (Opus, synthesis decisions)
- Added model_versions reference block
- Updated test coverage: 99 → 130+ tasks

**README.md:**
- Version: 1.1.0 → 1.2.0
- Stats: 38 files → 45+, 99 tasks → 130+, 12 workflows → 20+
- Added 4 new cases to Table of Contents
- Added "New in v1.2.0" documentation section
- Added "What's New in v1.2.0" summary section
- Updated last update date

### Technical Insights

**LinkedIn Algorithm Q1 2026 (van der Blom study, 1.8M posts):**
- Native video: +69% distribution
- Image: +11%, Carousel PDF: +7%
- Links in body: -60% distribution
- Reply within 1h: +35% visibility
- Comments 15+ words: 2.5x weight
- Depth Score = (Dwell Time ×2) + (Comment Quality ×15) + (Saves ×5) - Bounce Rate

**Multi-Agent Architecture Evolution:**
- Skills evolved from API docs to agent identities
- Three mandatory sections: Agent Identity, Workflow Integration, Decision Framework
- Sub-agents with 5KB focused context ≈ main agent quality at 4x less cost
- Anti-pattern: sub-agents must DRAFT, not execute externally

**Infrastructure Learnings:**
- `systemctl enable` is not optional (service survives reboots)
- Filesystem read-only = kernel self-protection, `mount -o remount,rw /` is temporary fix
- SSH access varies wildly: WPMU DEV temporary hosts, Rocket.net IP whitelist, Hostinger port 65002
- WP-CLI PHP version ≠ web PHP version — always specify path

---

## [1.1.0] - 2026-02-19

### Added

**Documentation:**
- `docs/05-memory-optimization.md` - Complete guide to context optimization
  - Context bloat analysis (MEMORY.md = 48% of bootstrap)
  - Layered memory architecture (Working → Archive → Daily logs)
  - Automated archival via nightly-optimization skill
  - Real results: 85KB → 27KB (-69.8%), $135/month savings
  - Quick wins checklist (~70 min implementation)
  
- `docs/06-multi-agent-architecture.md` - Multi-agent patterns and implementation
  - Specialized sub-agents concept
  - n8n-specialist case study (operational in production)
  - Context efficiency analysis: 5KB focused > 27KB generic
  - Cost comparison: Haiku + small context ≈ Sonnet + large context (4x cheaper)
  - 7 sub-agents proposed with ROI calculations
  - Step-by-step setup guide
  
- `cases/09-skool-member-validation.md` - LinkedIn identity verification system
  - Unique approach: DM validation (not just profile scraping)
  - Complete architecture: Zapier → n8n → NocoDB → Unipile → Apify
  - Scoring system (100 pts: 30 Skool + 70 LinkedIn)
  - Anti-fraud detection and edge case handling
  - NocoDB schema and workflow documentation
  - Competitive advantage analysis ("Sky is the limit")
  - Cost breakdown (~$1-2/month)

### Changed

**README.md:**
- Updated production results: $90/month → $45/month (50% reduction)
- Added context optimization stats (21,400 → 6,472 tokens)
- Expanded key insights section (4 principles)
- Added Memory Optimization to Table of Contents
- Added Multi-Agent Architecture to Table of Contents
- Updated Case Studies list (9 total)
- Bumped version to 1.1.0
- Updated last update date to 2026-02-19

### Improved

- Documentation structure (6 core docs + 9 case studies)
- Cost optimization coverage (context + models + architecture)
- Real-world examples with production data
- Technical depth while maintaining accessibility

---

## [1.0.0] - 2026-02-18

### Added

**Initial Release:**

**Core Documentation:**
- `docs/01-introduction.md` - Overview and setup context
- `docs/02-cost-optimization.md` - Model selection, embeddings, heartbeats
- `docs/03-performance-tuning.md` - Session management, tool efficiency
- `docs/04-production-patterns.md` - Multi-channel routing, error handling

**Case Studies:**
- `cases/01-skool-automation.md` - Community engagement automation (93.75% accuracy)
- `cases/02-linkedin-responses.md` - Unipile API + Mistral Large 2512
- `cases/03-newsletter-sync.md` - Listmonk self-hosted ($348/year saved)
- `cases/04-seo-weekly-reports.md` - Serpstat API + NocoDB tracking
- `cases/05-why-haiku-failed.md` - Real task analysis (67% failure rate)
- `cases/06-task-management-nocodb.md` - 99 active tasks, daily AI optimization
- `cases/07-infrastructure-docker-caddy.md` - 8 services, wildcard SSL ($552/year saved)
- `cases/08-n8n-workflow-automation.md` - 20+ workflows (15 hours/week saved)

**Configs & Scripts:**
- `configs/embeddings-optimized.json` - OpenAI Batch API setup
- `configs/model-routing-rules.json` - Task-based model selection
- `configs/heartbeat-templates.md` - Efficient heartbeat patterns
- `configs/cron-examples.json` - Production cron jobs
- `scripts/enable-optimized-embeddings.sh` - One-click embeddings setup
- `scripts/cost-calculator.py` - Monthly cost projection
- `scripts/analyze-task-complexity.py` - Model selection helper

**Infrastructure:**
- `README.md` - Main documentation index
- `LICENSE` - MIT License
- `.gitignore` - Standard exclusions

### Results (v1.0.0)

**Cost Optimization:**
- Before: ~$90/month (Sonnet everywhere)
- After: ~$70/month (22% reduction)
- Embeddings: 382 chunks indexed, 0 failures
- Task management: Automated (Opus 4.6 @ 05:30 AM)

**Production Stats:**
- Runtime: 60+ days
- Files indexed: 38
- Active tasks: 99
- Automated workflows: 12

---

## Future Roadmap

### Planned for v1.3.0

**Documentation:**
- Disaster recovery and backup strategies
- Scale-up patterns (100+ workflows, 1000+ tasks)
- Advanced sub-agent patterns (recursive orchestration)

**Case Studies:**
- Image generation workflows (Replicate API)
- Cross-platform content distribution
- Analytics dashboard (metrics aggregation)
- Voice memo transcription pipeline

**Tools:**
- Interactive cost calculator (web UI)
- Workflow library (importable templates)
- Performance benchmarking suite
- Agent identity template generator

### Planned for v2.0.0

**Major Updates:**
- Complete rewrite with updated OpenClaw APIs
- Docker Compose quick-start
- Terraform/IaC templates for VPS setup
- Video tutorials and walkthroughs
- Community contribution guidelines

---

## Release Notes

### v1.2.0 Summary

**What's New:**
- Multi-agent orchestration with spawnable sub-agents (4 new case studies)
- Infrastructure lessons from production incidents (filesystem crisis, SSH hell)
- LinkedIn Algorithm Q1 2026 data (van der Blom 1.8M post study)
- Cloudflare R2 + Pages for $0/month CDN and hosting

**Who Should Upgrade:**
- Anyone building multi-agent workflows
- Users deploying across multiple hosting providers
- LinkedIn power users (posting parties, engagement groups)
- Cost-conscious operators (landing pages on static vs WordPress)

**Breaking Changes:** None

**Migration:** No action required, all additions are new content

---

### v1.1.0 Summary

**What's New:**
- Memory optimization guide (biggest cost saver: -$135/month)
- Multi-agent architecture patterns (4x cost reduction demonstrated)
- Skool member validation (unique LinkedIn identity verification)

**Who Should Upgrade:**
- Anyone running OpenClaw with context >50KB
- Users considering cost optimization
- Teams building multi-agent systems
- Community managers needing member validation

**Breaking Changes:** None

**Migration:** No action required, all additions are new content

---

### v1.0.0 Summary

**Initial public release** of production-tested OpenClaw optimization guide.

Based on 60+ days running OpenClaw in production for:
- Content automation (blog, social, newsletter)
- Community engagement (Skool, LinkedIn, Discord)
- Business operations (task management, SEO, revenue tracking)

Covers real-world cost optimization (22% reduction), performance tuning, and 8 complete case studies with configs.

---

## Links

- **Repository:** https://github.com/ctala/openclaw-production-guide
- **Author Blog:** https://cristiantala.com
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Community:** https://discord.com/invite/clawd

---

## Contributing

See case studies and configs for contribution examples. PRs welcome for:
- New case studies (your production OpenClaw setup)
- Additional configs (tested patterns)
- Corrections and improvements

---

**Maintained by:** Cristian Tala Sánchez (@ctala)  
**License:** MIT
