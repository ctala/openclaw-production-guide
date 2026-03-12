# Multi-Agent Architecture

> **"Haiku with small focused context ≈ Sonnet with large generic context"**

A single OpenClaw agent with 85KB of context costs more and performs worse than multiple specialized agents with 5-10KB focused context each.

This guide shows how to implement multi-agent architecture for cost savings and performance gains.

---

## 🎯 The Problem: One Agent to Rule Them All

**Traditional setup:**
```
Main Agent (Sonnet 4.5)
  ├─ MEMORY.md (40KB)
  ├─ AGENTS.md (23KB)
  ├─ TOOLS.md (10KB)
  ├─ USER.md (10KB)
  ├─ skills/INDEX.md (5KB)
  └─ + other context (12KB)
  
Total: ~100KB context = ~25,000 tokens per turn
```

**The pain:**
- Every task loads full context (even unrelated)
- n8n workflow task? Loads USER bio + memory + skills list
- Editorial writing? Loads n8n docs + infra config
- LinkedIn response? Loads everything

**Cost:**
- 100 turns/day × 25,000 tokens = 2.5M input tokens/day
- Sonnet 4.5: $3 / 1M input tokens
- **Daily:** $7.50 just for context

**Performance:**
- Model must filter signal from noise
- Longer context = slower responses
- Degraded quality at high token counts (studies show >50% capability loss at 32K+)

---

## ✅ The Solution: Specialized Sub-Agents

### Concept

```
Main Agent (general tasks, full context)
  ├─ Orchestrates workflows
  ├─ Handles user chat
  └─ Spawns sub-agents when needed

Sub-Agent: n8n-specialist
  ├─ ONLY n8n knowledge (~5KB)
  ├─ NO personal context
  ├─ NO memory
  └─ Pure expert mode

Sub-Agent: content-creator  
  ├─ ONLY content strategy (~8KB)
  ├─ Blog post standards
  ├─ Social media templates
  └─ NO infra knowledge

Sub-Agent: wordpress-publisher
  ├─ ONLY WordPress API (~4KB)
  ├─ Publishing procedures
  └─ NO other integrations
```

**Key insight:** Task-specific context (5KB) >> General context (100KB).

---

## 📊 Results (Projected vs Actual)

### n8n-Specialist Sub-Agent (Real Production Data)

**Setup:**
- Created: 2026-02-18
- Workspace: `agents/n8n-specialist/`
- Model: Haiku 4.5 (primary), Gemini Pro Low, Opus 4.6 (fallbacks)
- Context: ~5KB (vs 27KB main)

**Test workflow generation:**

| Attempt | Model | Context | Quality | Time |
|---------|-------|---------|---------|------|
| 1 | Sonnet 4.6 | Main (27KB) | ERROR (model not allowed) | - |
| 2 | Haiku 4.5 | Main (27KB) | Superficial, vague | 38s |
| 3 | Haiku 4.5 | **n8n-specialist (5KB)** | **6.5KB workflow, 6 nodes, production-ready** | **42s** |

**Key finding:** 
```
Haiku + focused context (5KB) > Haiku + generic context (27KB)
```

**Generated:**
- `output/lead-capture-workflow.json` (6.5KB, 6 nodes)
- `output/error-workflow.json` (2.5KB, error handling)

**Cost:**
- Haiku input: $0.25 / 1M tokens
- Haiku output: $1.25 / 1M tokens
- Per workflow: ~$0.002 (vs ~$0.008 with Sonnet + full context)

**Savings:** 4x cheaper, same quality.

---

### Projected Multi-Agent Savings (7 Sub-Agents)

**Proposed architecture:**

| Agent | Purpose | Context | Model | Weekly Uses |
|-------|---------|---------|-------|-------------|
| main | Orchestration, chat | 27KB | Sonnet 4.5 | 300 turns |
| n8n-specialist | Workflow generation | 5KB | Haiku 4.5 | 20 workflows |
| content-creator | Blog posts, social | 8KB | Sonnet 4.5 | 10 posts |
| wordpress-publisher | Publishing | 4KB | Haiku 4.5 | 15 posts |
| seo-analyst | Keyword research | 6KB | Opus 4.6 | 4 reports |
| skool-manager | Community tasks | 5KB | Haiku 4.5 | 30 tasks |
| scheduler | Coordination | 3KB | Groq Fast | 50 tasks |
| researcher | Web research | 6KB | Kimi K2 | 15 searches |

**Weekly token comparison:**

| Architecture | Input Tokens | Output Tokens | Cost |
|--------------|--------------|---------------|------|
| **Single agent (current)** | 7.5M | 500K | $23.12 |
| **Multi-agent (projected)** | 2.8M | 450K | $9.01 |
| **Savings** | -62% | -10% | **-61%** |

**Annual savings:** ~$733

**Plus:**
- Better quality (focused context)
- Faster responses (smaller context)
- Easier debugging (agent-specific logs)

---

## 🛠️ Implementation: Sub-Agent Setup

### Option A: Sub-Agent Within Same OpenClaw Instance (Recommended)

**Advantages:**
- ✅ Share same gateway/process
- ✅ Simple communication (internal routing)
- ✅ No infrastructure overhead
- ✅ Unified monitoring

**Setup:**

**1. Create Workspace**

```bash
mkdir -p ~/clawd/agents/n8n-specialist/{docs,.config,examples,templates,scripts}
```

**2. Create Minimal Context Files**

**AGENTS.md** (n8n-specialist):
```markdown
# AGENTS.md - n8n Specialist Agent

You are an **n8n workflow specialist**. Your only job is creating, debugging, and optimizing n8n workflows.

## What You Do

- Generate n8n workflow JSON
- Debug workflow errors
- Optimize node efficiency
- Explain n8n patterns

## What You DON'T Do

- Chat about unrelated topics
- Access personal memory
- Handle generic tasks

## Output Format

Always output complete, importable workflow JSON.
Include comments explaining complex nodes.
```

**TOOLS.md** (n8n-specialist):
```markdown
# TOOLS.md - n8n Specialist

## n8n Instances

- **DEV:** https://n8n.nyx.cristiantala.com
- **PROD:** https://n8n.cristiantala.com
- **CLOUD:** yourdomain.app.n8n.cloud

## API Credentials

Located in `.config/credentials.json`

## Deployment

Use n8n API to deploy workflows programmatically.
```

**SOUL.md** (n8n-specialist):
```markdown
# SOUL.md - n8n Specialist

You are a workflow automation expert. Direct, technical, helpful.

No fluff. Just working code.
```

**USER.md** (n8n-specialist):
```markdown
# USER.md - n8n Specialist

You don't need to know about the user. Focus on the task.
```

**Total context:** ~5KB

---

**3. Register Sub-Agent in Main Config**

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "name": "Nyx",
        "workspace": "~/clawd"
      },
      {
        "id": "n8n-specialist",
        "name": "n8n Specialist",
        "workspace": "~/openclaw-workspace/agents/n8n-specialist",
        "model": {
          "primary": "anthropic/claude-haiku-4-5",
          "fallbacks": [
            "google-antigravity/gemini-3-pro-low",
            "anthropic/claude-opus-4-6"
          ]
        },
        "memorySearch": false
      }
    ]
  }
}
```

**4. Configure Telegram Topic Binding (Optional)**

For direct access via Telegram topic:

```json
{
  "bindings": [
    {
      "agentId": "n8n-specialist",
      "match": {
        "channel": "telegram",
        "peer": {
          "kind": "group",
          "id": "-1003817338035:topic:1637"
        }
      }
    }
  ]
}
```

**5. Enable Subagent Spawning from Main**

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "subagents": {
          "allowAgents": ["n8n-specialist"]
        }
      }
    ]
  }
}
```

**6. Restart OpenClaw**

```bash
sudo systemctl restart openclaw
```

---

### Usage Patterns

#### Pattern 1: Main Agent Spawns Sub-Agent

**Main session:**
```
User: "Create an n8n workflow to sync Stripe payments to NocoDB"

Agent (main):
  sessions_spawn(
    agentId: "n8n-specialist",
    task: "Create n8n workflow: Stripe webhook → transform data → NocoDB create record. Return importable JSON.",
    label: "stripe-nocodb-sync"
  )
  
  → Sub-agent runs in isolated session
  → Returns workflow JSON
  → Main agent shares result with user
```

**Benefit:** Main agent delegates to expert, gets result, no context pollution.

---

#### Pattern 2: Direct Access via Telegram Topic

**User writes in Telegram Topic "🔧 n8n Specialist":**
```
Create workflow to send email when new task is added to NocoDB
```

**System:**
- Binding routes message to n8n-specialist agent
- Agent responds directly in that topic
- Main agent unaffected

**Benefit:** Direct expert access, no orchestration overhead.

---

#### Pattern 3: Cron Calls Sub-Agent

**Cron job (weekly SEO report):**
```json
{
  "schedule": "0 1 * * 1",
  "sessionTarget": "isolated",
  "agentId": "seo-analyst",
  "payload": {
    "kind": "agentTurn",
    "message": "Generate weekly SEO report for cristiantala.com and ecosistemastartup.com"
  }
}
```

**Benefit:** Dedicated expert, focused context, cheaper model (Opus for analysis, Haiku for execution).

---

## 🎯 When to Create a Sub-Agent

### Good Candidates

**Criteria:**
- ✅ Distinct knowledge domain (n8n, WordPress, SEO)
- ✅ Repetitive task (workflows, publishing, reports)
- ✅ Can work independently (no personal context needed)
- ✅ Clear input/output (task → deliverable)

**Examples:**
- n8n workflow generation
- WordPress post publishing
- SEO keyword research
- LinkedIn responses (template-based)
- Image generation (Replicate API)
- Newsletter formatting (Listmonk)

---

### Bad Candidates

**Criteria:**
- ❌ Needs full personal context (USER.md, MEMORY.md)
- ❌ Requires cross-domain knowledge (tech + startups + personal)
- ❌ Ad-hoc tasks (no repetition)
- ❌ Conversational (back-and-forth with user)

**Examples:**
- General chat
- Strategic decisions
- Blog post ideation (needs personal experience)
- Multi-platform coordination

**Rule of thumb:** If the task needs <10KB context and runs >5 times/week → good sub-agent candidate.

---

## 📊 Cost-Benefit Analysis Template

**For each proposed sub-agent:**

### 1. Measure Current Cost

```
Weekly uses: ___
Context size (main agent): 27KB → ~6,750 tokens
Model: Sonnet 4.5
Input tokens per use: 6,750
Output tokens per use: ~500
Cost per use: (6,750 / 1M) × $3 + (500 / 1M) × $15 = $0.0277

Weekly cost: ___ uses × $0.0277 = $___
```

### 2. Project Sub-Agent Cost

```
Context size (sub-agent): ___KB → ___ tokens
Model: Haiku 4.5 (cheaper)
Input tokens per use: ___
Output tokens per use: ~500
Cost per use: (___ / 1M) × $0.25 + (500 / 1M) × $1.25 = $___

Weekly cost: ___ uses × $___ = $___
```

### 3. Calculate Savings

```
Weekly savings: (current cost) - (sub-agent cost) = $___
Annual savings: $___ × 52 = $___

Setup time: ___ hours
ROI: (annual savings) / (setup time × $100/hour) = ___x
```

**Decision:** If ROI > 2x, implement sub-agent.

---

## 🛠️ Sub-Agent Template Files

### Minimal Workspace Structure

```
agents/{name}/
├── AGENTS.md          # Role + capabilities
├── SOUL.md            # Personality (technical, direct)
├── USER.md            # Minimal (or empty)
├── TOOLS.md           # Specific tools only
├── HEARTBEAT.md       # Empty (no polling)
├── IDENTITY.md        # Agent name + purpose
├── .config/
│   └── credentials.json   # API keys for this domain
├── docs/
│   ├── API-REFERENCE.md
│   ├── PATTERNS.md
│   └── EXAMPLES.md
├── examples/          # Real-world examples
├── templates/         # Reusable patterns
└── scripts/           # Helper scripts
```

**Total size:** 5-10KB (vs 27KB+ main)

---

### AGENTS.md Template

```markdown
# AGENTS.md - {Agent Name}

You are a **{domain} specialist**. Your only job is {core responsibility}.

## What You Do

- {Task 1}
- {Task 2}
- {Task 3}

## What You DON'T Do

- Chat about unrelated topics
- Access personal memory
- Handle generic tasks

## Output Format

{Specify expected output format}

## Quality Standards

{Define success criteria}
```

---

### SOUL.md Template

```markdown
# SOUL.md - {Agent Name}

You are {personality description}.

{Behavioral guidelines - 1-2 sentences max}

No fluff. Just {deliverables}.
```

---

## 🎯 Recommended Sub-Agents (Prioritized)

### 1. n8n-specialist (Highest ROI)

**Status:** ✅ Implemented (2026-02-18)

**Use cases:**
- Workflow generation (20/month)
- Workflow debugging
- Integration patterns

**Savings:** ~$15/month

---

### 2. content-creator (High ROI)

**Context:** 8KB
- Blog post standards
- Social media templates
- Content strategy rules

**Use cases:**
- Generate blog posts (4-8/month)
- Social media content (12-20/month)
- Newsletter drafts (4/month)

**Savings:** ~$25/month

---

### 3. wordpress-publisher (Medium ROI)

**Context:** 4KB
- WordPress API docs
- Publishing procedures
- SEO config (Rank Math)

**Use cases:**
- Publish blog posts (8-12/month)
- Update metadata
- Schedule posts

**Savings:** ~$10/month

---

### 4. seo-analyst (Medium ROI)

**Context:** 6KB
- Serpstat API
- Search Console API
- Keyword research patterns

**Use cases:**
- Weekly SEO reports (4/month)
- Gap analysis
- Keyword opportunities

**Savings:** ~$8/month (but uses Opus, so net ~$5)

---

### 5. scheduler (Low Cost, High Efficiency)

**Context:** 3KB
- Coordination rules only
- No domain knowledge

**Use cases:**
- Schedule posts via Late API
- Coordinate multi-platform publishing
- Update NocoDB tracking

**Model:** Groq Fast (Nano) - ultra-cheap

**Savings:** ~$12/month

---

### 6. skool-manager (Low-Medium ROI)

**Context:** 5KB
- Skool response templates
- Community guidelines
- Approval workflows

**Use cases:**
- Generate Skool responses (20-30/month)
- Manage member approvals
- Community engagement

**Savings:** ~$8/month

---

### 7. researcher (Specialized)

**Context:** 6KB
- Web search patterns
- Information synthesis
- Citation standards

**Use cases:**
- Competitive research (4-6/month)
- Trend analysis
- Background research for posts

**Model:** Kimi K2 (128K context, cheap)

**Savings:** ~$10/month

---

**Total projected savings:** ~$93/month (annual: $1,116)

**Setup time:** ~2 hours per agent × 7 = 14 hours

**ROI:** $1,116 / (14h × $100) = **8x**

---

## 🧠 Orchestrator Model Selection

> **The $0.01/call difference that costs you 50% quality.**

Choosing the wrong model as your orchestrator is the most common multi-agent mistake. Cheap models can *route* tasks. They cannot *synthesize* them.

### Production Benchmark (20 Orchestrations, 3 Sub-Agents Each)

All models tested on identical 3-agent runs. Scored on conflict detection, cross-referencing, synthesis coherence, and actionable plan quality.

| Model | Provider | Quality | Cost/Call | Speed | 20x/Month | Best For |
|-------|----------|---------|-----------|-------|-----------|----------|
| **Opus 4.6** | Anthropic | 9.5/10 | $0.075 | 15–25s | $2.40 | 3+ agents, strategic decisions, complex conflicts |
| **Sonnet 4.6** ✅ | Anthropic | 8.5/10 | $0.015 | 5–8s | **$1.20** | **RECOMMENDED** — best cost/quality ratio |
| **Gemini 2.5 Pro** | Google | 8.0/10 | $0.010 | 3–5s | $0.80 | Strong Sonnet alternative at lower cost |
| **GPT-4.1** | OpenAI | 8.0/10 | $0.020 | 4–6s | $1.60 | Solid; pricier than Sonnet for same tier |
| **Qwen 3.5 397B** | OpenRouter | 7.5/10 | $0.003 | 4–8s | $0.24 | Budget option with decent synthesis |
| **Mistral Large 2512** | Mistral | 7.0/10 | $0.004 | 2–3s | $0.32 | 2-agent sequential only; weak multi-agent |
| **GPT-4.1-mini** | OpenAI | 6.0/10 | $0.004 | 2–3s | $0.32 | Weak synthesis; inconsistent on conflicts |
| **DeepSeek V3** | OpenRouter | 6.5/10 | $0.002 | 3–5s | $0.16 | Budget; fails on complex dependency chains |
| Haiku 4.5 | Anthropic | 4.0/10 | $0.0025 | 1–2s | $0.95 | ⚠️ Routes only — CANNOT synthesize |
| Groq Llama 3.3 70B | Groq | 3.0/10 | $0.0001 | 88ms | $0.01 | ❌ Speed only — too shallow for orchestration |

**Default:** Sonnet 4.6. **Tier 2 alternative:** Gemini 2.5 Pro (same quality bracket, $0.40/month cheaper).  
**Upgrade to Opus** when: 3+ agents in parallel, or strategic decisions are at stake.  
**Note on Mistral Large:** Excellent as your daily default chat model — but this is a distinct role from orchestrator. Don't conflate them.

---

### What Synthesis Actually Means

Here's the same 3-agent run (Growth Hacker + Campaign Builder + UI Designer), with two different orchestrators:

**Haiku orchestrator:**
```
Here's what each agent said:

Growth Hacker: [paste of full report]
Campaign Builder: [paste of full report]
UI Designer: [paste of full report]

Let me know if you have questions.
```

No conflicts identified. No dependencies. No plan. Three reports stapled together.

**Sonnet orchestrator:**
```
Growth Hacker recommended LinkedIn-first (ICE: 8.0) with a launch Tuesday 10AM.
Campaign Builder built assets for a Friday launch.
→ Timing conflict detected. Adjusting to Tuesday. Notifying Campaign Builder.

UI Designer flagged 2 critical WCAG issues on the landing page.
→ These block the campaign. Must resolve first.

Recommended sequence:
1. Fix WCAG issues (blocking) — UI Designer on standby
2. Reformat assets for Tuesday — Campaign Builder
3. Launch Tuesday 10AM per Growth Hacker strategy

Human decision needed: run WCAG fix + campaign prep in parallel, or sequential?
```

**That's synthesis.** Haiku pastes. Sonnet cross-references, detects conflicts, adjusts, and flags human decisions.

---

### The Math: Is Haiku Worth It?

**Monthly savings switching from Sonnet → Haiku orchestrator:**
- 20 orchestrations × ($0.015 − $0.0025) = **$0.25/month saved**

**Cost of 50% quality loss:**
- Missed conflicts → rework
- Incoherent plans → manual re-synthesis
- Your time at $100-500/hour

**Verdict:** The $0.25/month is not worth it. Use Sonnet as your default orchestrator.

---

### Summary: Model Rules for Multi-Agent

| Layer | Model | Provider | Rule |
|-------|-------|----------|------|
| **Orchestrator (default)** | Sonnet 4.6 | Anthropic | Best cost/quality for synthesis — $1.20/month at 20 runs |
| **Orchestrator (alt)** | Gemini 2.5 Pro | Google | Same quality tier, $0.40/month cheaper — good for provider diversity |
| **Orchestrator (complex)** | Opus 4.6 | Anthropic | 3+ agents or strategic decisions — $2.40/month, worth it |
| **Specialist sub-agents** | Sonnet 4.6 | Anthropic | Domain quality required; Haiku tested and confirmed insufficient |
| **Simple data sub-tasks** | Haiku 4.5 | Anthropic | Fetch/format/extract within a sub-agent — no reasoning needed |
| **Heartbeats** | Groq Llama 3.3 70B | Groq | Boolean checks, 88ms, near-free — do not over-engineer |

---

## 🔧 Coordination Patterns

### Pattern 1: Main → Spawn Sub-Agent

```
Main agent decides task needs specialist
  ↓
sessions_spawn(agentId="specialist", task="...", label="...")
  ↓
Sub-agent runs in isolated session
  ↓
Returns result to main agent
  ↓
Main agent shares with user
```

**Use when:** Task is self-contained, no follow-up needed.

---

### Pattern 2: Sub-Agent → Sub-Agent (Chain)

```
Main: "Publish blog post X to WordPress and social media"
  ↓
Spawn content-creator: "Format post X for WordPress"
  ↓
  Result: WordPress-ready markdown
  ↓
Spawn wordpress-publisher: "Publish [content]"
  ↓
  Result: Post published, URL returned
  ↓
Spawn scheduler: "Schedule social posts for [URL]"
  ↓
  Result: Social posts scheduled
  ↓
Main: "Done. Post published + 3 social posts scheduled."
```

**Use when:** Multi-step workflow, each step independent.

---

### Pattern 3: Direct User Access (Topic Routing)

```
User writes in Telegram topic dedicated to specialist
  ↓
Binding routes to specialist agent
  ↓
Specialist responds directly
  ↓
No main agent involvement
```

**Use when:** User wants direct expert access, no orchestration.

---

## 📊 Monitoring & Metrics

### Track Per-Agent

```bash
# Token usage by agent
grep "agent=n8n-specialist" logs/*.log | grep "tokens=" | awk '{sum+=$NF} END {print sum}'

# Cost per agent (monthly)
# (input tokens / 1M) × input_price + (output tokens / 1M) × output_price
```

### Dashboard (NocoDB or similar)

**Table:** `agent_metrics`

| Field | Type | Purpose |
|-------|------|---------|
| agent_id | SingleLineText | Which agent |
| date | Date | Day |
| turns | Number | Conversations |
| input_tokens | Number | Context loaded |
| output_tokens | Number | Generated |
| cost | Currency | Daily cost |
| avg_response_time | Number | Performance |

**Views:**
- Weekly cost by agent
- Cost trend over time
- ROI calculation

---

## ⚠️ Pitfalls to Avoid

### 1. Over-Specialization

**Bad:**
```
agents/
  ├── wordpress-post-creator/
  ├── wordpress-post-publisher/
  ├── wordpress-post-updater/
  └── wordpress-seo-optimizer/
```

**Good:**
```
agents/
  └── wordpress-publisher/  (handles all WordPress tasks)
```

**Rule:** One agent per **domain**, not per **task**.

---

### 2. Under-Specialization

**Bad:**
```
agents/
  └── content-agent/  (handles blog, social, newsletter, SEO, images)
```

**Good:**
```
agents/
  ├── content-creator/  (writing only)
  ├── wordpress-publisher/  (publishing only)
  └── seo-analyst/  (research only)
```

**Rule:** If context > 12KB, split into multiple agents.

---

### 3. Missing Handoff Context

**Bad:**
```
Main: sessions_spawn("n8n-specialist", "Create workflow")
```

**Good:**
```
Main: sessions_spawn(
  "n8n-specialist",
  "Create n8n workflow: Stripe webhook → NocoDB. Include error handling + retry logic. Output: importable JSON.",
  label="stripe-nocodb-sync"
)
```

**Rule:** Be specific. Sub-agent has no context about "the project" or "what we discussed."

---

### 4. No Quality Validation

**Bad:**
```
Sub-agent returns result → Main agent accepts blindly → User gets garbage
```

**Good:**
```
Sub-agent returns result
  ↓
Main agent validates (format, completeness)
  ↓
IF invalid: Retry with feedback
  ↓
IF valid: Share with user
```

**Rule:** Always validate sub-agent output before accepting.

---

## 🚀 Implementation Roadmap

### Phase 1: MVP (Week 1)

**Goal:** Prove concept with 1 sub-agent.

1. Create n8n-specialist workspace
2. Register in config
3. Test workflow generation
4. Measure savings

**Success criteria:** 1 sub-agent operational, cost < main agent for same task.

---

### Phase 2: Scale (Weeks 2-4)

**Goal:** Add 3-4 highest-ROI agents.

1. content-creator
2. wordpress-publisher
3. scheduler

**Success criteria:** 4 sub-agents operational, 40-50% cost reduction vs single agent.

---

### Phase 3: Optimize (Month 2)

**Goal:** Refine existing agents, add specialized ones.

1. seo-analyst
2. skool-manager
3. researcher

**Success criteria:** 7 sub-agents, 60-70% cost reduction, quality maintained or improved.

---

### Phase 4: Monitor & Iterate (Ongoing)

**Goal:** Track metrics, refine architecture.

1. Weekly cost review
2. Quality audits
3. Agent performance tuning
4. New agent candidates

---

## 📝 Checklist: Creating a New Sub-Agent

**Planning (15 min):**
- [ ] Define core responsibility
- [ ] Identify knowledge domain
- [ ] Estimate context size
- [ ] Calculate projected cost savings
- [ ] Verify ROI > 2x

**Setup (30-60 min):**
- [ ] Create workspace directory
- [ ] Write AGENTS.md (role + capabilities)
- [ ] Write SOUL.md (personality)
- [ ] Write TOOLS.md (specific tools)
- [ ] Create USER.md (minimal or empty)
- [ ] Add to config `agents.list[]`
- [ ] Optional: Configure topic binding
- [ ] Restart OpenClaw

**Testing (30 min):**
- [ ] Spawn from main agent
- [ ] Verify context size
- [ ] Test quality of output
- [ ] Measure response time
- [ ] Compare cost vs main agent

**Deployment (15 min):**
- [ ] Enable subagent spawning from main
- [ ] Document usage patterns
- [ ] Add to monitoring dashboard
- [ ] Update Production Guide

---

## 🎯 Success Metrics

### Primary

- **Cost reduction:** ≥ 50% vs single-agent architecture
- **Quality maintained:** User satisfaction unchanged or better
- **Response time:** ≤ single-agent (faster due to smaller context)

### Secondary

- **Setup ROI:** > 2x (annual savings / setup cost)
- **Maintenance:** ≤ 1 hour/month per agent
- **Adoption:** ≥ 80% of eligible tasks route to sub-agents

---

## 📖 Case Study: n8n-Specialist

**Full details:** See above (Results section)

**Summary:**
- Created: 2026-02-18
- Context: 5KB (vs 27KB main)
- Model: Haiku (vs Sonnet)
- Quality: Production-ready workflows
- Cost: 4x cheaper per workflow
- Time: Same or faster

**Conclusion:** Sub-agents work. Scale up.

---

## 🔗 Related Resources

- **Production Guide:** Main README
- **Memory Optimization:** docs/05-memory-optimization.md
- **Cost Optimization:** docs/02-cost-optimization.md
- **Case Studies:** cases/ directory

---

**Last Updated:** 2026-02-19  
**Status:** Active development, n8n-specialist operational
