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
    model="claude-sonnet-4-5",
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

| Role | Model | Reasoning |
|------|-------|-----------|
| Orchestrator | claude-opus-4-6 | Complex multi-factor reasoning: which agents to spawn, how to synthesize, what's priority |
| Domain specialist | claude-sonnet-4-5 | Deep domain analysis with quality output |
| Simple data tasks | claude-haiku-4-5 | Mechanical operations within a sub-agent (fetch, format, extract) |
| Heartbeats | groq-fast | Boolean checks don't need reasoning |

### Why Not Haiku for Sub-Agents?

Sub-agents do specialized deep work that requires:
- Domain reasoning (ICE scoring, WCAG compliance checks)
- Quality output (copy that converts, audits that are actionable)
- Consistent application of frameworks

Haiku tested on sub-agent tasks showed:
- Growth analysis: Superficial ICE scores without real reasoning
- Copy generation: Generic output without brand voice
- UX audits: Checklist items without prioritization

**Conclusion:** Sub-agent quality = Sonnet minimum.

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
- [ ] Orchestrator model: Opus (not Sonnet)
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
