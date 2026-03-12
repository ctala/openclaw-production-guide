# Production Patterns

> **The boring stuff that keeps things running.** Multi-channel routing, error handling, cron vs heartbeat, sub-agent orchestration, content affiliate strategy.

---

## 1. Multi-Channel Routing

### Architecture Overview

One OpenClaw instance, multiple channels:

```
OpenClaw Gateway
  ├── Telegram (main)
  │     ├── Topic 322: LinkedIn responses
  │     ├── Topic 27: Skool approvals
  │     ├── Topic 6011: UI/UX agent
  │     ├── Topic 6012: Growth agent
  │     └── Topic 6013: Campaign agent
  ├── Discord
  │     ├── #general
  │     └── #automations
  └── WebChat (dashboard)
```

### Binding Configuration

Route specific channels to specific agents or workflows:

```json
{
  "bindings": [
    {
      "agentId": "main",
      "match": {
        "channel": "telegram",
        "peer": { "kind": "private" }
      }
    },
    {
      "agentId": "skool-manager",
      "match": {
        "channel": "telegram",
        "peer": { "kind": "group", "id": "-1003817338035:topic:27" }
      }
    },
    {
      "agentId": "growth-hacker",
      "match": {
        "channel": "telegram",
        "peer": { "kind": "group", "id": "-1003817338035:topic:6012" }
      }
    }
  ]
}
```

### Telegram Topics as Agent Interfaces

Each specialized agent gets a dedicated Telegram topic. This is the most practical multi-agent UI pattern discovered in production:

**Benefits:**
- User writes directly to the specialist, no routing overhead
- Conversation history per topic = context for that agent
- Human can ignore topics they don't care about
- Clean audit trail per domain

**Topic naming convention:**
- `🤖 [Agent Name]` for specialist agents
- `🔔 Alerts` for error notifications
- `📊 Reports` for async outputs

---

## 2. Error Handling

### Graceful Degradation

**Principle:** A failure in one workflow should never crash the main session or block unrelated workflows.

```
# Good pattern
try:
  result = call_external_api()
  process(result)
except ApiError as e:
  log_error(e)
  notify_telegram("⚠️ API call failed: {e}. Skipping this run.")
  return  # Don't cascade
```

In OpenClaw terms: always have a "if this fails, do X instead" path. Silence is not a valid failure mode.

### Error Notification Strategy

**Immediate alert (Telegram):**
- Cron failures
- External API 5xx errors
- Data integrity issues (e.g., NocoDB write failed)

**Log only (review weekly):**
- Transient 429 rate limits (auto-retried)
- Minor quality issues (model output needs editing)
- Non-critical integrations (social media scheduling failed → retry tomorrow)

**Silent (ignorable):**
- Heartbeat `HEARTBEAT_OK` responses
- Cache misses (normal, just slower)

### Retry Logic

For external API calls, implement exponential backoff:

```bash
# n8n workflow pattern
{
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000,  // 5s, 10s, 20s
  "continueOnFail": true     // log error, don't crash workflow
}
```

For OpenClaw crons that fail: n8n handles retry. If cron fails 3 times consecutively → alert to Telegram.

---

## 3. Cron vs Heartbeat

This distinction matters more than it seems.

### Heartbeats

**What they are:** Background checks running every N minutes while the main session is active.

**What they do:** "Is there anything that needs attention right now?" → usually `HEARTBEAT_OK`.

**Model:** Groq Llama 3.3 70B (boolean check, no reasoning needed, 88ms)

**When they escalate:** Spawn a Sonnet sub-agent for actual action.

**Cost:** ~$0.14/month at 30-minute intervals.

```
HEARTBEAT cycle:
  Groq checks HEARTBEAT.md
  → Nothing urgent: "HEARTBEAT_OK" (88ms, $0.0001)
  → Action needed: spawn Sonnet session to handle it ($0.015)
```

### Crons

**What they are:** Scheduled jobs with a specific mission, running at a fixed time.

**What they do:** Execute a complete workflow — analyze tasks, generate a report, send a newsletter.

**Model:** Task-specific (Opus for analysis, Sonnet for editorial, Groq for simple checks)

**Session:** Always isolated (never main session)

**Examples from production:**

| Cron | Schedule | Model | Mission |
|------|----------|-------|---------|
| Task optimizer | Daily 5:00 AM | Opus 4.6 | Analyze 130+ tasks, update priorities, atomize blockers |
| Skool check | Daily 8:00 AM, 4:00 PM | Sonnet 4.6 | Draft responses for new community posts |
| SEO report | Monday 1:00 AM | Opus 4.6 | Serpstat gap analysis, NocoDB update |
| Newsletter draft | Sunday 8:00 PM | Sonnet 4.6 | Generate weekly content batch |
| Memory optimization | Daily 3:00 AM | Haiku 4.5 | Archive old MEMORY.md entries |

### The Rule

```
Heartbeat = "Should I act?" (Groq, cheap, frequent)
Cron      = "Execute this mission" (right model, isolated, scheduled)
```

Don't use heartbeats for execution. Don't use crons for polling. They're different tools.

---

## 4. Sub-Agent Orchestration

### When to Spawn a Sub-Agent

**Spawn when:**
- Task needs domain expertise you'd otherwise inject via a 10KB skill context
- Task is parallelizable with other tasks (don't wait, spawn simultaneously)
- Task produces a deliverable that needs human review before action
- You want an isolated token budget for a heavy workflow

**Don't spawn when:**
- Task needs full workspace context (personal history, cross-domain decisions)
- Task is conversational (back-and-forth with user)
- Task runs <5 times per week (setup cost not worth it)

### Orchestration Pattern

```
User: "Run the weekly growth strategy"
  ↓
Main agent (Sonnet 4.6):
  ├── sessions_spawn("growth-hacker", task="ICE score top 5 experiments this week")
  ├── sessions_spawn("campaign-builder", task="Draft assets for top experiment")
  └── sessions_spawn("ui-designer", task="Audit landing page for conversion blockers")
  ↓
  [All run in parallel — ~10 minutes]
  ↓
Main agent reads all Topic outputs
  ↓
Synthesizes: conflicts? dependencies? recommended sequence?
  ↓
Presents unified plan to user
  ↓
User approves → main agent executes
```

### Orchestrator Model

**Default:** Sonnet 4.6 — handles synthesis for 2–3 agents, detects conflicts, produces coherent plans ($1.20/month at 20 orchestrations).

**Upgrade to Opus 4.6** for 3+ agents in parallel or strategic decisions ($2.40/month).

**Do not use Haiku or Groq** as orchestrators — they route but cannot synthesize. See [Multi-Agent Patterns](multi-agent-patterns.md) for full benchmark.

### Execution Boundary (Critical)

Sub-agents **draft**, main agent **executes**. Always.

```
# WRONG: Sub-agent sends email
sessions_spawn("campaign-builder", "Draft AND send the email sequence in Listmonk")

# RIGHT: Sub-agent drafts, human approves, main executes
sessions_spawn("campaign-builder", "Draft the email sequence. Output to Topic 6013.")
→ Human reviews
→ Main agent: "Approved. Scheduling in Listmonk now."
```

Sub-agents have limited context. They don't know if the list is warmed up, if there's a conflicting campaign, or if Listmonk is in a grace period. The main agent does.

---

## 5. Affiliate Link Strategy in Content

### The Pattern

Every piece of content that mentions a tool should include the relevant affiliate link — but naturally, not spammy.

**Active affiliate programs:**

| Platform | Link | Context |
|----------|------|---------|
| Hostinger | `https://hostinger.com?REFERRALCODE=1CRISTIAN62` | Hosting, VPS mentions |
| n8n | `https://n8n.partnerlinks.io/wpqwwllhiznx` | Automation workflow mentions |
| Amazon | Tag: `cristiantal04-20` → `amazon.com/dp/ASIN?tag=cristiantal04-20` | Book or tool recommendations |
| Skool | `https://www.skool.com/cagala-aprende-repite/about` | Community mentions (use `/about` for tracking) |

### When to Insert (and When Not To)

**Insert when:**
- Blog post specifically reviews or recommends the tool
- Tutorial uses the tool step-by-step
- Case study relies on the tool as a core component

**Don't insert when:**
- Brief passing mention in a list
- Comparison article where you're being neutral
- Already used the link 2+ times in the same post

### Automated Link Insertion (n8n Workflow)

An n8n workflow checks every published post for affiliate opportunities:
1. Read published post content
2. Match against affiliate keyword list
3. If link missing → flag for review (not auto-insert — requires editorial judgment)
4. Report weekly: "5 posts missing Hostinger link, 3 missing n8n link"

---

## 6. Monitoring

### What to Monitor

**Costs (weekly review):**
- Total spend vs previous week
- Cost breakdown by agent/model
- Any spikes (usually a rogue cron or accidental Sonnet heartbeat)

**Quality (ongoing):**
- Rejection rate on AI drafts (Skool responses, LinkedIn replies)
- Time spent editing AI output
- User satisfaction signals (community engagement, newsletter open rates)

**Reliability (daily):**
- Cron success/failure rate
- External API health (NocoDB, WordPress, Listmonk, Late API)
- `clawdbot.service` status (must be `enabled`, not just `started`)

### The `clawdbot.service` Lesson

Learned the hard way (March 9, 2026): `systemctl start` runs the service but it dies on reboot. `systemctl enable` makes it survive reboots.

```bash
# The right way
sudo systemctl enable clawdbot.service
sudo systemctl start clawdbot.service

# Verify it's both active AND enabled
systemctl status clawdbot.service
# Look for: "Active: active (running)" AND "enabled;"
```

Set a monthly reminder to verify: `systemctl is-enabled clawdbot.service`

### Alert Thresholds

Configure Telegram alerts when:
- Daily cost > $5 (something is running Sonnet where it shouldn't)
- Cron failure 3x in a row (likely API outage or credential expiry)
- `clawdbot.service` not active (via external health check)
- NocoDB API returns 500 (database issue)

---

## Related Resources

- [Cost Optimization](02-cost-optimization.md) — Model routing, embeddings, heartbeat config
- [Performance Tuning](03-performance-tuning.md) — Context management, tool efficiency
- [Multi-Agent Architecture](06-multi-agent-architecture.md) — Sub-agent setup, coordination
- [Multi-Agent Patterns](multi-agent-patterns.md) — Orchestration patterns, anti-patterns
- [Infrastructure Lessons](infrastructure-lessons.md) — Production incidents, SSH, filesystem recovery
- [Case 1: Skool Automation](../cases/01-skool-automation.md) — Multi-channel approval workflow in practice

---

**Last Updated:** 2026-03-12 | **Version:** 1.3.0
