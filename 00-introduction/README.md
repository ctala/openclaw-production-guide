# Introduction

## Who I Am

I'm Cristian Tala, founder of a fintech startup that had a successful exit. Since then, I've been:

- **Angel investor** in 30+ startups across Latin America
- **Mentor** at startup accelerators (Startup Chile, others)
- **LP** in 7+ VC funds
- **Technology advisor** helping founders scale operations

I started using OpenClaw to automate repetitive work: community engagement, content creation, research, SEO optimization. What started as "let's try this AI thing" became a critical part of my daily workflow.

## Why This Guide Exists

When I first deployed OpenClaw in production, I made every mistake in the book:

- ❌ Burned $200+ in a month on context accumulation
- ❌ Had conversations freeze for 30 seconds while embeddings indexed
- ❌ Followed "just use Haiku" advice blindly (spoiler: didn't work)
- ❌ Broke production with config changes I didn't understand

After 6 months of iteration, I figured out what actually works. This guide is the resource I wish I had on day one.

## What Makes This Different

There are other OpenClaw optimization guides out there. This one is different because:

1. **Real production case** — Not a toy project. I run OpenClaw for actual business operations that matter.

2. **Nuance over dogma** — "Use Haiku" isn't always right. "Keep Sonnet" isn't always wrong. This guide helps you understand **when**.

3. **Honest about trade-offs** — I tried to cut costs by 58%. Realized I could realistically cut 17%. I explain why.

4. **Evolving** — Pull requests welcome. I update this weekly as I learn new things.

5. **No vendor bias** — I'm not selling anything. Just sharing what works.

## My Production Setup

**What I use OpenClaw for:**

- **Community management:** Automated engagement on Skool (1,000+ interactions/month)
- **LinkedIn presence:** Response system for comments (30+ interactions/week)
- **Content creation:** Blog posts, courses (18K+ words/week), newsletters
- **Research:** Investment analysis, SEO optimization, competitive research
- **Automation:** n8n workflows, WordPress publishing, social media scheduling

**Stack:**
- Self-hosted on VPS (srv1301687)
- Telegram as primary interface (topics for different workflows)
- NocoDB for task management
- Skills: WordPress, Late API, Listmonk, Skool, LinkedIn (via Unipile)

**Models I use:**
- **Main:** Sonnet 4.5 (for quality)
- **Heartbeats:** Haiku 4.5 (for cost)
- **Deep work:** Opus 4.6 (for research/long-form)
- **Subagents:** Sonnet 4.5 (for spawned tasks)

## Results

**Before optimization:**
- Monthly cost: ~$90
- Conversations blocked by embeddings: frequently
- Context window: 400K tokens (way too much)
- Heartbeats: Sonnet ($15/mo just for checks)

**After optimization:**
- Monthly cost: ~$75 (-17% = $180/year savings)
- Conversations blocked: never (async embeddings)
- Context window: 100K tokens (pruned)
- Heartbeats: Haiku ($0.25/mo)

**Why not bigger savings?**

Because my work is research-heavy and strategy-heavy. Downgrading the main model would hurt quality more than the cost savings justify.

This guide explains when to optimize and when to prioritize quality.

## What You'll Learn

1. **Cost optimization** — Where to cut costs safely (and where not to)
2. **Model selection** — Haiku vs Sonnet vs Opus: the honest comparison
3. **Performance** — Embeddings, context, sessions, tools
4. **Production patterns** — Error handling, monitoring, multi-channel
5. **Real cases** — Skool automation, LinkedIn responses, why Haiku failed
6. **Workflows** — Daily optimization, content pipeline, SEO reporting

## Who This Is For

**This guide is for you if:**
- ✅ You're running OpenClaw for business operations (not hobby)
- ✅ Your monthly bill is $50+ and you wonder if that's normal
- ✅ You care about quality but also about cost efficiency
- ✅ You want to understand **why**, not just copy configs

**This guide is NOT for you if:**
- ❌ You just installed OpenClaw yesterday (start with official docs)
- ❌ You only use it for casual chat (optimization won't matter much)
- ❌ You want "one weird trick to cut costs 90%" (doesn't exist)

## How to Use This Guide

1. **Start here** — Read this introduction
2. **Quick wins** — Implement [heartbeat optimization](../01-cost-optimization/heartbeats.md) and [embeddings](../01-cost-optimization/embeddings.md) (10 min total)
3. **Understand nuance** — Read [model selection](../01-cost-optimization/model-selection.md) and [why Haiku failed](../04-real-world-cases/why-haiku-failed.md)
4. **Deep dive** — Explore sections that match your use case
5. **Implement gradually** — Don't change everything at once
6. **Share results** — Contribute your learnings back to the community

## Contributing

Found something that works better? Have a different use case? Spotted an error?

**Pull requests welcome.**

This guide gets better when the community adds their knowledge.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Next:** [My Production Setup →](my-setup.md)
