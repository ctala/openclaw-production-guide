# Case 10: Multi-Agent Orchestration with Specialized Sub-Agents

> **From single all-rounder to expert team: how spawnable sub-agents cut 8-hour strategy sessions to 30 minutes**

**Problem:** A single agent trying to be growth hacker, copywriter, and UX auditor simultaneously produces mediocre results across all three.

**Solution:** Specialized sub-agents spawned via OpenClaw's `sessions_spawn`, each with a dedicated identity, skill set, and Telegram Topic for bidirectional communication.

**Result:** 5 growth strategy documents + 3 LinkedIn posts + 5 email sequences + landing page copy — produced in parallel in ~30 minutes, with human approval before anything goes live.

---

## 🎯 The Problem: Jack of All Trades, Master of None

**Initial state:** Main agent (Nyx) handling everything — content, growth analysis, UX audits, campaign execution.

**Pain points:**
- Switching context between "growth hacker mode" and "copywriter mode" within the same session burns tokens
- Generic outputs: neither deep growth analysis nor compelling copy — just average
- Sequential work: growth analysis THEN copy THEN UX audit = hours elapsed
- Skills were just API docs, no real "identity" or reasoning framework per domain

**Real example of the failure mode:**
```
User: "Analyze my funnel AND write 3 LinkedIn posts AND audit my landing page"
Agent: [writes a 3,000-token response that's mediocre on all three]
```

**What was needed:** Parallel expert execution with cross-synthesis at the end.

---

## ✅ The Solution: Spawnable Specialized Sub-Agents

### Architecture Overview

```
Main Agent (Nyx/Opus) — Orchestrator
  ├── [parallel spawn]
  │   ├── Growth Hacker Sub-Agent (Sonnet)
  │   │   ├── Reads: skills/growth-hacker/SKILL.md
  │   │   ├── Outputs to: Telegram Topic 6012
  │   │   └── Speciality: ICE scoring, funnel analysis, viral loops
  │   │
  │   ├── Campaign Builder Sub-Agent (Sonnet)
  │   │   ├── Reads: skills/campaign-builder/SKILL.md
  │   │   ├── Outputs to: Telegram Topic 6013
  │   │   └── Speciality: email sequences, social posts, landing copy
  │   │
  │   └── UI Designer Sub-Agent (Sonnet)
  │       ├── Reads: skills/ui-designer/SKILL.md
  │       ├── Outputs to: Telegram Topic 6011
  │       └── Speciality: Lighthouse audits, accessibility, UX reviews
  │
  └── [synthesis] Main Agent cross-references all three outputs
      └── Human approves → Main Agent implements
```

### The Key Evolution: Skills as Agent Identities

**Before (v1):** Skills were API documentation
```markdown
# SKILL.md - Late API
Use this to schedule posts. API endpoint: ...
```

**After (v2):** Skills as spawnable agent identities
```markdown
# SKILL.md - Growth Hacker Agent

## Agent Identity
You are **Alex**, a growth hacker with 8 years experience scaling B2B SaaS from 0 to 100K users.
Your mental model: everything is a funnel, every problem is a conversion problem.

## Workflow Integration
- Always output ICE-scored experiments
- Tag Telegram Topic 6012 when reporting
- NEVER execute externally (no posting, no sending) — DRAFT only

## Decision Framework
For every analysis: Identify → Measure → Experiment → Learn
ICE Score = (Impact × Confidence × Ease) / 3
```

**Why this matters:** The agent doesn't just know APIs — it knows *how to think* as that specialist.

---

## 🔧 Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Orchestrator | OpenClaw main session (Opus 4.6) | Spawns agents, synthesizes results |
| Sub-agents | OpenClaw sessions (Sonnet 4.5) | Domain-specific execution |
| Communication | Telegram Topics (6011, 6012, 6013) | Bidirectional agent ↔ human |
| Skills | `~/clawd/skills/*/SKILL.md` | Agent identity + workflow + decision framework |
| Task tracking | NocoDB | Track what each agent produced |

---

## 📋 Workflow: End-to-End Orchestration

### Step 1: Orchestrator Receives Request

```
User: "We're launching a lead magnet (LinkedIn cheatsheets). 
       Plan the growth strategy, write the email sequence, 
       and audit the landing page."
```

Main agent (Opus) analyzes complexity → decides multi-agent execution is needed.

### Step 2: Parallel Spawn

```
// Main agent spawns all three simultaneously
[sessions_spawn: growth-hacker] → "Analyze launch strategy for LinkedIn cheatsheet lead magnet. 
                                    Use ICE scoring. Output to Topic 6012."

[sessions_spawn: campaign-builder] → "Write 5-email welcome sequence for LinkedIn cheatsheet 
                                       subscribers. Output draft to Topic 6013."

[sessions_spawn: ui-designer] → "Audit https://lp.cristiantala.com/linkedin-cheatsheets/ 
                                  for Lighthouse, WCAG, and conversion. Output to Topic 6011."
```

All three start working in parallel. Wall clock time: ~8 minutes for full execution.

### Step 3: Sub-Agent Execution

**Growth Hacker (Alex) outputs:**
```markdown
## ICE-Scored Experiments for LinkedIn Cheatsheet Launch

| Experiment | Impact | Confidence | Ease | ICE Score |
|------------|--------|------------|------|-----------|
| LinkedIn posting party | 9 | 8 | 7 | 8.0 |
| Email to existing 1,923 subscribers | 8 | 9 | 9 | 8.7 |
| Skool community announcement | 7 | 8 | 9 | 8.0 |
| LinkedIn story + link | 6 | 6 | 8 | 6.7 |

**Viral Loop Identified:** Download cheatsheet → "Share with your network" CTA in email → new signups

**Funnel Analysis:**
- Top of funnel: LinkedIn post (organic, posting party)
- Landing page: lp.cristiantala.com/linkedin-cheatsheets/
- Capture: Listmonk form
- Activation: 5-email welcome sequence
- Viral loop: share CTA in email 3
```

**Campaign Builder (Cam) outputs:**
```markdown
## 5-Email Welcome Sequence: LinkedIn Cheatsheets

Email 1 (Immediate): "Your cheatsheets are here + how to use them"
Email 2 (Day 2): "The LinkedIn algorithm change nobody talks about"  
Email 3 (Day 4): "How 12 people grew together (posting party invite)"
Email 4 (Day 7): "Advanced move: the Depth Score formula"
Email 5 (Day 14): "What's next (tease next lead magnet)"
```

**UI Designer (Ui) outputs:**
```markdown
## Landing Page Audit: lp.cristiantala.com/linkedin-cheatsheets/

Lighthouse:
- Performance: 81 → 95+ (after optimization)
- Accessibility: 76 → 95+
- SEO: 100

Issues found:
- [CRITICAL] Avatar image: 400x400 27KB → should be 96x96 1.6KB WebP
- [CRITICAL] Missing robots.txt → 507 Lighthouse errors
- [HIGH] No cache headers for static assets
- [MEDIUM] Contrast ratio fails WCAG AA on 3 elements
- [LOW] Missing focus-visible states on 2 CTAs
```

### Step 4: Cross-Synthesis

Main agent reads all three outputs and synthesizes:

```markdown
## Synthesis: LinkedIn Cheatsheet Launch Plan

Growth strategy (Alex) + Campaign (Cam) are aligned:
- Posting party is priority #1 experiment (ICE 8.0) — Cam wrote email 3 about it ✓
- Email sequence timing matches funnel stages ✓

UI blockers (Ui) that must be fixed BEFORE launch:
- robots.txt (blocks 507 errors, 1 min fix)
- Avatar optimization (performance impact, 10 min fix)

Recommended launch sequence:
1. Fix UI issues [today, 15 min]
2. Schedule email sequence in Listmonk [today]
3. Post in LinkedIn + tag Posting Party group [launch day]
4. Send email 1 immediately on first signup
```

### Step 5: Human Approval

Human reviews all three outputs in their respective Telegram Topics + synthesis. Approves what to implement.

### Step 6: Implementation

Main agent implements approved items (UI fixes, Listmonk setup, etc.). Sub-agents did NOT execute anything externally — they only drafted.

---

## 🧠 Critical Lessons

### 1. Skills Must Have Three Sections to Work as Agent Identities

```markdown
## Agent Identity     ← WHO this agent is (name, background, mental model)
## Workflow Integration ← HOW it communicates (Telegram Topics, output format)
## Decision Framework   ← HOW it thinks (ICE scoring, checklists, frameworks)
```

Without all three, you get a helpful assistant. With all three, you get an expert.

### 2. Parallel Is Better Than Sequential

**Sequential (before):** Growth → Copy → UX = 45+ minutes wall clock
**Parallel (after):** All three simultaneously = 8-12 minutes wall clock

The bottleneck shifts from agent compute to human review.

### 3. Dedicated Telegram Topics = Organized Chaos

Each agent has its own Topic. This means:
- Human can follow one agent's thread without noise from others
- Agent can be asked follow-up questions in its Topic
- Outputs are naturally organized by specialty
- History is preserved per domain

```
Topic 6011: UI/UX → @NyxBot posts UX audits, human asks follow-ups
Topic 6012: Growth → @NyxBot posts growth analysis, human asks follow-ups  
Topic 6013: Campaigns → @NyxBot posts copy drafts, human reviews
```

Bidirectional: the agent posts results AND receives clarification requests in the same Topic.

### 4. Anti-Pattern: Don't Let Sub-Agents Execute Externally

**Wrong approach:**
```
[sessions_spawn: campaign-builder] → "Write email sequence AND schedule it in Listmonk"
```

**Right approach:**
```
[sessions_spawn: campaign-builder] → "Write email sequence draft, output to Topic 6013"
// Human approves → Main agent schedules in Listmonk
```

Sub-agents DRAFT. Humans APPROVE. Main agent EXECUTES.

Why: Sub-agents have limited context. They don't know if the account is in a grace period, if the list is warming up, or if there's a conflicting campaign already scheduled. Main agent has full context for safe execution.

### 5. Model Selection: Sonnet for Sub-Agents, Opus for Orchestration

| Role | Model | Reasoning |
|------|-------|-----------|
| Orchestrator | Opus 4.6 | Needs to reason about which agents to spawn, how to synthesize, what's priority |
| Growth Hacker | Sonnet 4.5 | Domain expertise + quality output, doesn't need orchestration depth |
| Campaign Builder | Sonnet 4.5 | Writing quality matters, Haiku produces generic copy |
| UI Designer | Sonnet 4.5 | Technical analysis + actionable recommendations |

**Why not Haiku for sub-agents?** Sub-agents do specialized deep work. Haiku lacks the domain reasoning to produce ICE-scored experiments or WCAG-compliant audit reports. Tested and confirmed: quality drop is significant.

### 6. The Orchestration Pattern That Works

```
Growth Hacker → analyzes opportunity
Campaign Builder → builds execution assets
UI Designer → validates delivery channel
↓ [all parallel]
Main Agent → cross-synthesizes
Human → approves
Main Agent → implements
```

This is not just "spawn three agents." The orchestrator must understand which agents to use, what order to synthesize in, and which outputs are dependencies for others.

---

## 📊 Results

| Metric | Before (Manual) | After (Orchestrated) |
|--------|-----------------|----------------------|
| Time for full strategy + copy + audit | 8-10 hours | 30 min execution + 15 min review |
| Growth docs produced | 0-1 per week | 5 in one session |
| Email sequences per week | 1 (hours of work) | 5 in one session |
| Landing page audits | 0 (never happened) | Automated per launch |
| Human bottleneck | Writing everything | Review + approval only |
| Consistency | Variable | Frameworks applied every time |

**Single session outputs:**
- 5 growth strategy documents (ICE-scored experiments for 5 campaigns)
- 3 LinkedIn posts (drafted and formatted)
- 5 email sequences (150+ emails drafted)
- 1 full landing page audit with prioritized fixes

---

## 💰 Cost Breakdown

| Component | Model | Calls | Cost/Call | Total |
|-----------|-------|-------|-----------|-------|
| Orchestrator (Opus) | claude-opus-4-6 | 1 | $0.075 | $0.075 |
| Growth Hacker (Sonnet) | claude-sonnet-4-6 | 1 | $0.015 | $0.015 |
| Campaign Builder (Sonnet) | claude-sonnet-4-6 | 1 | $0.015 | $0.015 |
| UI Designer (Sonnet) | claude-sonnet-4-6 | 1 | $0.015 | $0.015 |
| Follow-up clarifications | Sonnet | ~2-3 | $0.015 | $0.045 |
| **Total per orchestrated run** | | | | **$0.165–$0.30** |

**Manual equivalent:** 8-10 hours of founder time at $200+/hour = **$1,600–$2,000**

ROI on automation: **5,000–6,000x per session**

---

## 🏁 Takeaway

Multi-agent orchestration isn't about spawning agents for the sake of it. It's about recognizing when a task genuinely requires different mental models operating simultaneously.

The breakthrough came from treating skills not as API docs but as agent identities: give an agent a name, a mental model, a decision framework, and dedicated communication channels — and it stops being "Claude doing marketing" and starts being "Alex the growth hacker."

**If you replicate one thing from this case:** Add `Agent Identity`, `Workflow Integration`, and `Decision Framework` sections to your skills. The quality difference is dramatic.

**One warning:** This pattern requires human-in-the-loop approval before external execution. Sub-agents with limited context will confidently execute wrong things if you let them. Use them to draft and analyze; keep execution in the hands of the fully-contextualized main agent.

---

## 🔗 Related

- [docs/multi-agent-patterns.md](../docs/multi-agent-patterns.md) — Architecture patterns reference
- [Case 6: Task Management (NocoDB)](06-task-management-nocodb.md) — NocoDB integration
- [Case 13: Cloudflare Pages Landings](13-cloudflare-pages-landings.md) — The landing page that got audited here
- [docs/06-multi-agent-architecture.md](../docs/06-multi-agent-architecture.md) — Multi-agent architecture deep dive
