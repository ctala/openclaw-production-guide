# Multi-Agent Architecture Patterns

> Production patterns for spawnable specialized sub-agents in OpenClaw

---

## Overview

Multi-agent orchestration in OpenClaw allows a main agent to spawn specialized sub-agents for focused tasks. This document covers patterns learned from production use starting February 2026.

**Core principle:** Specialized agents with focused context outperform a generalist agent with full context — for both quality and cost.

---

## 1. Agent Identity Pattern

### The Evolution: Docs → Agent Identities

**v1 skills (documentation only):**
```markdown
# SKILL.md - Late API
Use this skill to schedule posts on social media.
API endpoint: https://api.late.app/v1/posts
Authentication: Bearer token in .config/credentials.json
```

**v2 skills (spawnable agent identity):**
```markdown
# SKILL.md - Growth Hacker Agent

## Agent Identity
You are **Alex**, a growth hacker with 8 years scaling B2B SaaS.
Mental model: everything is a funnel, every problem is a conversion problem.
Your superpower: ICE scoring (Impact × Confidence × Ease) applied to all decisions.

## Workflow Integration
- Output to Telegram Topic 6012 (Growth)
- Format outputs as: problem → ICE table → recommended sequence
- NEVER execute externally — DRAFT for human approval only
- Tag main agent when synthesis is ready

## Decision Framework
For every analysis, follow: Identify → Measure → Experiment → Learn
For every recommendation, provide ICE score and reasoning
Prioritize high-ICE experiments over intuitive ones
```

**Why the three sections are mandatory:**
- **Agent Identity** — Establishes domain expertise, voice, mental model. Without it, you get Claude playing a role. With it, you get consistent specialist output.
- **Workflow Integration** — Defines communication channels, output format, execution boundaries. Prevents chaos when multiple agents are active.
- **Decision Framework** — Provides structured reasoning for domain-specific decisions. Ensures consistency across sessions.

---

## 2. Spawnable Sub-Agents via `sessions_spawn`

### Basic Pattern

```python
# Main agent spawning a specialized sub-agent
sessions_spawn(
    skill="growth-hacker",
    task="Analyze LinkedIn cheatsheet lead magnet launch. ICE score top 5 experiments.",
    output_channel="telegram:topic:6012",
    model="claude-sonnet-4-6",
    context_limit="5KB"  # Focused context, not full workspace
)
```

### Context Strategy

| Agent Type | Context Size | Rationale |
|------------|-------------|-----------|
| Growth Hacker | 5-8KB | Needs campaign data + skill identity only |
| Campaign Builder | 5-10KB | Needs brand voice + audience data |
| UI Designer | 3-5KB | Needs target URL + WCAG rules |
| Orchestrator | Full workspace | Needs everything to make decisions |

**Key insight:** A sub-agent with 5KB of focused context + Sonnet ≈ main agent with 27KB + Sonnet in quality. But sub-agent is 4x cheaper because it processes far fewer tokens.

### Isolation Rules

Sub-agents should be isolated from:
- Workspace secrets (API keys they don't need)
- Unrelated conversation history
- Cross-domain context (growth hacker doesn't need infrastructure data)

Sub-agents should have access to:
- Their skill's SKILL.md
- Relevant data files (specific to their task)
- Communication channels (their Telegram Topic)

---

## 3. Dedicated Telegram Topics for Agent Communication

### Topic Architecture

Each specialized agent gets its own Telegram Topic for bidirectional communication:

```
Main Chat (general)
  ├── Topic 6011: UI/UX → UI Designer sub-agent
  ├── Topic 6012: Growth → Growth Hacker sub-agent
  ├── Topic 6013: Campaigns → Campaign Builder sub-agent
  └── Topic 322: LinkedIn → LinkedIn Response agent
```

### Why Dedicated Topics Work

1. **Signal vs noise:** Scrolling one feed with outputs from 3 agents = chaos. Dedicated topics = organized by specialty.
2. **Conversation continuity:** Follow-up questions to a specific agent go to its Topic. The agent reads its Topic history and maintains context.
3. **Human filtering:** Humans can ignore Topics they don't care about in a given session.
4. **Audit trail:** All outputs from "the growth hacker" are in one place, chronologically.

### Bidirectional Usage

```
Human → Topic 6012: "What's the ICE score for Pinterest vs LinkedIn for this campaign?"
↓
Growth Hacker reads Topic 6012, sees question in context
↓
Growth Hacker → Topic 6012: "ICE Analysis: LinkedIn 8.0 vs Pinterest 3.5..."
↓
Human reads response, approves or asks follow-up
```

---

## 4. Orchestration: Parallel Execution + Cross-Synthesis

### The Orchestration Pattern

```
Main Agent (Opus) receives complex request
  ↓
Decompose into domain-specific subtasks
  ↓
[PARALLEL] Spawn all sub-agents simultaneously
  ├── Growth Hacker: strategy analysis
  ├── Campaign Builder: execution assets
  └── UI Designer: delivery channel validation
  ↓
[WAIT] All sub-agents complete (8-12 minutes)
  ↓
[SYNTHESIS] Main agent reads all Topic outputs
  ↓
Cross-reference: Do growth strategy and copy align?
Identify dependencies: Which UI issues block launch?
Generate unified plan
  ↓
Present synthesis to human
  ↓
Human approves components
  ↓
Main agent implements approved items
```

### When to Use Parallel vs Sequential

**Use parallel when:**
- Subtasks are independent (growth analysis doesn't block copy writing)
- All subtasks are needed before synthesis
- Time savings matter (parallel saves 60-75% wall clock time)

**Use sequential when:**
- Subtask B depends on Subtask A's output
- One agent reviews another's work (UI Designer reviewing Campaign Builder's landing copy)
- Resource constraints (rate limits, context limits)

### Cross-Synthesis Best Practices

The orchestrator's synthesis must:
1. **Identify alignment** — Do all agents agree on approach? Flag conflicts.
2. **Identify blockers** — What must be fixed before others proceed?
3. **Establish priority order** — What's the logical sequence for implementation?
4. **Flag for human decision** — What requires judgment that should not be automated?

---

## 5. Model Selection Per Agent Role

### Decision Matrix

| Role | Model | Provider | Reasoning |
|------|-------|----------|-----------|
| **Orchestrator (default)** | Sonnet 4.6 | Anthropic | Best cost/quality for synthesis — detects conflicts, cross-references, adjusts plan |
| **Orchestrator (alt)** | Gemini 2.5 Pro | Google | Same tier, $0.40/month cheaper, good provider diversity |
| **Orchestrator (3+ agents / strategic)** | Opus 4.6 | Anthropic | Deepest reasoning for complex cross-agent synthesis |
| **Domain specialist** | Sonnet 4.6 | Anthropic | Deep domain analysis with quality output |
| **Simple data tasks** | Haiku 4.5 | Anthropic | Mechanical operations within a sub-agent (fetch, format, extract) |
| **Heartbeats** | Groq Llama 3.3 70B | Groq | Boolean checks, no reasoning needed — 88ms, near-free |

---

## 5a. Orchestrator Model Selection (Production Data)

> **Key insight:** Orchestration ≠ Execution. Cheap models can route tasks. They cannot synthesize them.

This section covers production data from 20+ orchestrated runs comparing orchestrator models directly.

### What "Orchestration" Actually Requires

Executing tasks is easy. Orchestration means:
- **Deciding** which agents to spawn (and in what order)
- **Detecting conflicts** between specialist outputs
- **Cross-referencing** data that specialists produced independently
- **Adjusting** the final plan when Growth Hacker's timeline doesn't match Campaign Builder's deliverables
- **Presenting** a coherent synthesis — not a dump of 3 reports

A cheap model can paste outputs together. Only a capable model can synthesize them.

---

### Production Benchmark (20 Orchestrations, 3 Sub-Agents Each)

All models tested on identical 3-agent runs (Growth Hacker + Campaign Builder + UI Designer). Scored on conflict detection, cross-referencing, synthesis coherence, and plan quality.

| Model | Provider | Quality | Cost/Call | Speed | 20x/Month | Verdict |
|-------|----------|---------|-----------|-------|-----------|---------|
| **Opus 4.6** | Anthropic | 9.5/10 | $0.075 | 15–25s | $2.40 | Best synthesis; use for 3+ agents or strategic decisions |
| **Sonnet 4.6** | Anthropic | 8.5/10 | $0.015 | 5–8s | **$1.20** ✅ | **RECOMMENDED default** — best cost/quality ratio |
| **Gemini 2.5 Pro** | Google | 8.0/10 | $0.010 | 3–5s | $0.80 | Strong alternative to Sonnet; good synthesis at lower cost |
| **GPT-4.1** | OpenAI | 8.0/10 | $0.020 | 4–6s | $1.60 | Solid but pricier than Sonnet for same quality tier |
| **Qwen 3.5 397B** | OpenRouter | 7.5/10 | $0.003 | 4–8s | $0.24 | Budget option; decent synthesis, occasional shallow outputs |
| **Mistral Large 2512** | Mistral | 7.0/10 | $0.004 | 2–3s | $0.32 | OK for simple 2-agent sequential; weak multi-agent synthesis |
| **GPT-4.1-mini** | OpenAI | 6.0/10 | $0.004 | 2–3s | $0.32 | Weak synthesis; similar tier to Mistral but less consistent |
| **DeepSeek V3** | OpenRouter | 6.5/10 | $0.002 | 3–5s | $0.16 | Budget-friendly; fails on complex multi-dependency chains |
| **Haiku 4.5** | Anthropic | 4.0/10 | $0.0025 | 1–2s | $0.95 | ⚠️ Routes only — cannot synthesize. Not recommended. |
| **Groq Llama 3.3 70B** | Groq | 3.0/10 | $0.0001 | 88ms | $0.01 | ❌ Speed-only. Too shallow for orchestration decisions. |

*\*20 orchestrations/month*

**Recommended default: Sonnet 4.6** (Anthropic) — best cost/quality ratio at $1.20/month.  
**Tier 2 alternative: Gemini 2.5 Pro** — same quality bracket as Sonnet at $0.40/month less.  
**Upgrade to Opus 4.6** when: 3+ agents in parallel, or strategic decisions are at stake.  
**Important: Mistral Large is an excellent daily default model** — but do not confuse this with orchestration capability. At 7/10 synthesis quality it works for simple 2-agent chains; it breaks down in multi-dependency scenarios.

---

### The $0.01/Call Difference That Costs You 50% Quality

The gap between Haiku and Sonnet as orchestrators is $0.0125/call. That's about **$0.25/month** saved if you run 20 orchestrations.

What you lose: **50% synthesis quality.**

#### Haiku Orchestrator Output (actual example)

```
Here's what each agent said:

Growth Hacker: [paste of full report]
Campaign Builder: [paste of full report]
UI Designer: [paste of full report]

Let me know if you have questions.
```

No conflicts detected. No dependencies identified. No actionable plan. Three reports stapled together.

#### Sonnet Orchestrator Output (same inputs)

```
Synthesis from 3 specialist agents:

Growth Hacker recommended LinkedIn-first (ICE: 8.0) with a launch Tuesday 10AM.
Campaign Builder built assets for a Friday launch.
→ Timing conflict: adjusting to Tuesday. Notifying Campaign Builder to reformat.

UI Designer flagged 2 critical WCAG issues on the landing page — these block the campaign.
→ Blocking issue: resolving before proceeding.

Recommended sequence:
1. Fix WCAG issues (blocking) — UI Designer on standby
2. Update assets for Tuesday timeline — Campaign Builder
3. Launch Tuesday 10AM — Growth Hacker strategy approved

Requires human decision: Should we delay or run parallel WCAG fix + campaign prep?
```

**That's the difference.** One pastes. One synthesizes.

---

### When to Use Each Orchestrator Model

**Sonnet 4.6 — RECOMMENDED default (Anthropic)**
- 2–3 specialist agents, any domain
- Workflow orchestration (content → publish → schedule)
- Conflict detection between specialist outputs
- Standard business decisions with no major strategic stakes
- Cost: $1.20/month at 20 orchestrations ✅

**Gemini 2.5 Pro — Tier 2 alternative (Google)**
- Same quality bracket as Sonnet (8.0/10 vs 8.5/10)
- Slightly lower cost ($0.80/month vs $1.20/month at 20 orchestrations)
- Good cross-referencing; slightly weaker on subtle conflicts
- Use if you're already in the Google ecosystem or want provider diversity
- Cost: $0.80/month ✅

**Opus 4.6 — Upgrade for complexity (Anthropic)**
- 3+ agents in parallel with interdependencies
- Strategic decisions (go/no-go, investment thesis, product direction)
- Conflicts that require nuanced multi-factor judgment
- Synthesis where missing a dependency = significant rework
- Cost: $2.40/month at 20 orchestrations (extra $1.20 is worth it here)

**GPT-4.1 — Solid but not the sweet spot (OpenAI)**
- Comparable quality to Sonnet (8.0/10)
- More expensive ($1.60/month vs $1.20/month for Sonnet)
- No clear advantage over Sonnet for orchestration specifically
- Reasonable if you're already paying for OpenAI and want one fewer provider

**Qwen 3.5 397B — Budget option (OpenRouter)**
- Decent synthesis for the price (7.5/10, $0.24/month)
- Occasional shallow outputs on complex dependency chains
- Worth testing if cost is a hard constraint and you have simple workflows

**Mistral Large 2512 — Simple 2-agent routing only (Mistral)**
- Sequential 2-agent chains where no synthesis is needed (A produces → B processes)
- Example: content-creator → wordpress-publisher (no conflict possible)
- Breaks down in multi-agent scenarios requiring conflict detection
- **Important:** Mistral Large is an excellent daily default model for chat and standard tasks. This limitation is specific to multi-agent orchestration.
- Cost: $0.32/month ✅ (only when truly no synthesis required)

**GPT-4.1-mini / DeepSeek V3 — Not recommended for orchestration**
- Weak synthesis (6.0/10 and 6.5/10 respectively)
- Similar price bracket to Mistral Large but less consistent
- DeepSeek fails on complex dependency chains

**Haiku 4.5 / Groq — Do not use as orchestrators**
Routes only. Cannot synthesize. Haiku at $0.95/month costs almost as much as Sonnet at $1.20/month for 50% quality loss. Groq is 88ms and 3/10 — speed-only, not reasoning.

---

### Why Not Haiku for Sub-Agents Either?

Sub-agents do specialized deep work that requires:
- Domain reasoning (ICE scoring, WCAG compliance checks)
- Quality output (copy that converts, audits that are actionable)
- Consistent application of frameworks

Haiku tested on sub-agent tasks showed:
- Growth analysis: Superficial ICE scores without real reasoning
- Copy generation: Generic output without brand voice
- UX audits: Checklist items without prioritization

**Conclusion:** Sub-agent quality = Sonnet minimum. Orchestrator = Sonnet default, Opus for complexity.

---

## 6. Anti-Patterns

### Anti-Pattern 1: Sub-Agents That Execute Externally

```
# WRONG
[sessions_spawn: campaign-builder] → "Write email sequence AND schedule in Listmonk"

# RIGHT
[sessions_spawn: campaign-builder] → "Write email sequence draft, output to Topic 6013"
# Then: Human approves → Main agent schedules
```

**Why:** Sub-agents have limited context. They don't know:
- Is the Listmonk account in a grace period?
- Is there a conflicting campaign scheduled?
- Has the list warmed up enough for this send volume?

Only the main agent with full workspace context can safely execute externally.

### Anti-Pattern 2: Skill Overload

```
# WRONG: One skill tries to do everything
## SKILL.md - Marketing Agent
You do: SEO, PPC, email marketing, social media, PR, content, analytics, CRO...
```

```
# RIGHT: Focused skills with clear boundaries
## SKILL.md - Campaign Builder
You do: email sequences, social post copy, landing page copy
You don't do: strategy (that's Growth Hacker), audits (that's UI Designer)
```

Unfocused agents produce mediocre outputs. The specialist beats the generalist every time.

### Anti-Pattern 3: No Synthesis Step

Spawning 3 agents and dumping their outputs on the human = information overload. The orchestrator must synthesize:
- What's aligned
- What conflicts
- What's the recommended sequence
- What requires human judgment

### Anti-Pattern 4: No Execution Boundaries

Sub-agents without clear "you DRAFT, you don't execute" instructions will confidently execute wrong things. This is not a model failure — it's a prompt failure. Always specify execution boundaries in the skill's Workflow Integration section.

---

## 7. Skills as Docs vs Skills as Agents

### Comparison

| Aspect | Skills as Docs | Skills as Agents |
|--------|----------------|------------------|
| Purpose | Reference for main agent | Spawnable specialist identity |
| Context | How to use an API | Who the agent is + how it thinks |
| Output | Main agent uses info | Sub-agent produces direct output |
| Reusability | Every session reads it | Spawn when specific task arises |
| Quality | Depends on main agent's generalism | Expert output from specialist context |
| Cost | Tokens in main context | Separate session (cheaper) |

### When to Use Each

**Skills as docs:** Tool documentation, API references, configuration guides, workflow instructions. Read by main agent and incorporated into its reasoning.

**Skills as agents:** When you need deep domain expertise, parallel execution, or specialist output quality. The skill becomes an agent identity, spawned in isolated sessions.

**The decision rule:** If you find yourself giving the main agent 10+ lines of domain-specific instructions for a specialized task — that task should become a sub-agent skill.

---

## 8. Production Checklist

Before deploying a multi-agent workflow:

- [ ] Each skill has Agent Identity, Workflow Integration, Decision Framework sections
- [ ] Dedicated Telegram Topics assigned to each agent
- [ ] Main agent has "read all Topics" in synthesis step
- [ ] Sub-agent execution boundaries explicitly stated ("DRAFT only")
- [ ] Human approval gate before any external execution
- [ ] Orchestrator model: Sonnet 4.6 (default) or Opus 4.6 (3+ agents / strategic decisions)
- [ ] Sub-agent model: Sonnet minimum
- [ ] Sub-agent context: focused (not full workspace)
- [ ] Test with low-stakes task before production use

---

## Related Resources

- [Case 10: Multi-Agent Orchestration](../cases/10-multi-agent-orchestration.md) — Production case study
- [docs/06-multi-agent-architecture.md](06-multi-agent-architecture.md) — Architecture deep dive
- [configs/model-routing-rules.json](../configs/model-routing-rules.json) — Model selection rules

---

*Last updated: 2026-03-12 | Version: 1.2.0*
