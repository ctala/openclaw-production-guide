# Model Selection: The Nuance Nobody Talks About

**TL;DR:** "Just use Haiku" is oversimplified advice. The right model depends on your workload. This guide helps you choose.

---

## The Common Advice

Search for "OpenClaw cost optimization" and you'll find:

> "Use Haiku for everything, it's 3x cheaper and 80% as good. Save 50-70% on costs!"

**This advice is:**
- ✅ True for some workloads
- ❌ Wrong for others
- ⚠️ Dangerous if applied blindly

---

## The Reality: Workload Matters

I spent 3.5 hours researching how to cut my costs by 58%. Recommendation: use Haiku as primary model.

Then I tested it on 48 hours of real production work.

**Result:** Only 25% of my tasks were viable with Haiku while maintaining quality standards.

Why? Because my workload is **knowledge-intensive**, not **task-intensive**.

---

## Task-Intensive vs Knowledge-Intensive

### Task-Intensive Workload

**Characteristics:**
- Executing scripts
- Making API calls
- File operations
- Parsing structured data
- Simple decision-making
- Repetitive operations

**Examples:**
- "Run this Python script and report the output"
- "Check if file X exists, if not create it"
- "Call the Stripe API and parse the response"
- "Upload these 5 files to CDN"

**Haiku performance:** ✅ Excellent (95%+ success rate)

**Cost savings:** 60-70% vs Sonnet

### Knowledge-Intensive Workload

**Characteristics:**
- Deep research
- Strategic analysis
- Long-form content creation
- System architecture decisions
- Nuanced communication
- Learning from context

**Examples:**
- "Research embedding optimizations and recommend a strategy"
- "Generate a 18,000-word course maintaining consistency"
- "Analyze why our LinkedIn engagement dropped and suggest fixes"
- "Design an automation system for community management"

**Haiku performance:** ⚠️ Inconsistent (20-50% acceptable quality)

**Cost savings:** Not worth the quality degradation

---

## Real-World Test: 12 Tasks from 48 Hours

I analyzed 12 actual tasks from production use. Here's what I found:

### ✅ Haiku Worked (3 tasks, 25%)

**1. Sync NocoDB**
- **Task:** Execute Python scripts, parse JSON output
- **Complexity:** Low
- **Haiku result:** ✅ Perfect

**2. Disable Cron**
- **Task:** Update cron config, verify changes
- **Complexity:** Low
- **Haiku result:** ✅ Perfect

**3. Upload to CDN**
- **Task:** Run bash scripts, check HTTP status
- **Complexity:** Low
- **Haiku result:** ✅ Perfect

### ⚠️ Haiku Borderline (3 tasks, 25%)

**4. Create Markdown Viewer**
- **Task:** Design HTML viewer, implement security, write docs
- **Complexity:** Medium
- **Haiku result:** ⚠️ Would work, but less elegant

**5. Config Patch**
- **Task:** Apply embeddings configuration
- **Complexity:** Medium
- **Haiku result:** ⚠️ Would work, might miss edge cases

**6. Update Cron Message**
- **Task:** Rewrite cron payload to exclude Asana
- **Complexity:** Medium (requires context understanding)
- **Haiku result:** ⚠️ Would work, but less nuanced

### ❌ Sonnet/Opus Needed (6 tasks, 50%)

**7. Embeddings Research (3.5 hours)**
- **Task:** Research optimization across 7 areas, analyze 15+ sources
- **Complexity:** Very High
- **Haiku result:** ❌ Would miss connections, superficial analysis

**8. YouTube Naming Research**
- **Task:** Multi-source research, strategic analysis, cultural nuance
- **Complexity:** High
- **Haiku result:** ❌ Missing strategic depth, no cultural understanding

**9. Course Content (18,500 words)**
- **Task:** Generate 8 modules, maintain consistency, pedagogical structure
- **Complexity:** Very High
- **Haiku result:** ❌ Loses coherence at scale

**10. LinkedIn Strategy Framework**
- **Task:** Research, template creation, A/B hypothesis
- **Complexity:** High
- **Haiku result:** ❌ Missing strategic thinking

**11. Skool Automation System**
- **Task:** Design end-to-end system, multiple integrations, error handling
- **Complexity:** Very High
- **Haiku result:** ❌ Would miss edge cases, poor architecture

**12. Daily Task Optimization (Opus)**
- **Task:** Analyze 150K+ tokens context, correlate projects, prioritize
- **Complexity:** Very High (+ context limit)
- **Haiku result:** ❌ Not enough context window

---

## The Model Hierarchy

Based on real-world testing:

### Haiku (cheapest, fastest)

**Use for:**
- ✅ Script execution
- ✅ File operations
- ✅ Simple API calls
- ✅ Parsing structured data
- ✅ Heartbeats / health checks
- ✅ Repetitive tasks with clear patterns

**Cost:** ~$0.25 per 1M input tokens

**When it fails:**
- ❌ Tasks requiring deep analysis
- ❌ Long-form content
- ❌ Strategic decisions
- ❌ Nuanced communication

### Sonnet (balanced)

**Use for:**
- ✅ Most production work
- ✅ Content creation (<5K words)
- ✅ Code generation
- ✅ Research (moderate depth)
- ✅ Multi-step workflows
- ✅ System design

**Cost:** ~$3 per 1M input tokens (3x Haiku)

**When it fails:**
- ❌ Extremely long content (>10K words)
- ❌ Very deep research (>3 hours)
- ❌ Architectural decisions requiring 200K context

### Opus (most capable, slowest)

**Use for:**
- ✅ Deep research
- ✅ Long-form content (10K+ words)
- ✅ Complex analysis (150K+ context needed)
- ✅ Architectural decisions
- ✅ When quality is non-negotiable

**Cost:** ~$15 per 1M input tokens (5x Sonnet, 15x Haiku)

**When it fails:**
- ❌ Simple tasks (overkill + expensive)
- ❌ Time-sensitive (slower than Sonnet)

---

## Decision Framework

### Ask These Questions

**1. Is the output quality critical?**
- Yes → Sonnet or Opus
- No → Try Haiku first

**2. Is the task repetitive/well-defined?**
- Yes → Haiku
- No → Sonnet+

**3. Does it require >5K words of output?**
- Yes → Sonnet or Opus
- No → Haiku might work

**4. Does it need deep analysis or research?**
- Yes → Sonnet or Opus
- No → Haiku

**5. Does it require >100K context?**
- Yes → Opus
- No → Sonnet or Haiku

**6. Will re-work cost more than using a better model?**
- Yes → Use Sonnet/Opus
- No → Try Haiku

---

## My Configuration

Here's what I actually use in production:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": [
          "anthropic/claude-opus-4-6",
          "anthropic/claude-haiku-4-5"
        ]
      },
      "heartbeat": {
        "model": "anthropic/claude-haiku-4-5"
      }
    }
  }
}
```

**Breakdown:**
- **Main work:** Sonnet (quality/cost balance)
- **Heartbeats:** Haiku (perfect for checks)
- **Fallback:** Opus (when Sonnet isn't enough)
- **Subagents:** Sonnet (real work, needs quality)

---

## Cost Analysis: My Case

### If I Used Haiku for Everything

**Estimated savings:** 60-70% (~$50/mo)

**Quality impact:**
- ❌ Research: Superficial, missing connections
- ❌ Content: Loses coherence at scale
- ❌ Strategy: Missing nuance
- ❌ Architecture: Poor decisions

**Re-work cost:**
- 2-3 hours/week fixing Haiku output
- @ $100/hour opportunity cost = $800-1200/month

**Net result:** Lose money by "saving" money

### What I Actually Did

**Primary:** Sonnet (maintained)  
**Heartbeats:** Haiku (switched from Sonnet)  
**Embeddings:** Optimized (Batch API)  
**Context:** Pruned (400K → 100K)

**Savings:** $15/month (17%)  
**Quality:** Maintained  
**Re-work:** Zero

**ROI:** Positive (no opportunity cost)

---

## When Haiku Makes Sense

**Haiku works great if your workload is:**

1. **Automation-heavy**
   - Running scripts
   - API orchestration
   - File management
   - Data parsing

2. **Well-defined tasks**
   - Clear inputs/outputs
   - Repetitive patterns
   - Simple decision trees

3. **Low stakes**
   - Mistakes are cheap to fix
   - Quality bar is "good enough"
   - No complex reasoning needed

**Examples:**
- Home automation
- File organization
- Data extraction
- Simple chatbots
- Health checks

**For these use cases, Haiku is perfect. Use it.**

---

## When Haiku Doesn't Make Sense

**Haiku struggles if your workload is:**

1. **Knowledge work**
   - Research
   - Analysis
   - Strategy
   - Writing

2. **High quality bar**
   - Published content
   - Client deliverables
   - Business decisions
   - Architectural design

3. **Complex reasoning**
   - Multi-step analysis
   - Nuanced decisions
   - Long-form coherence
   - Strategic thinking

**Examples:**
- Business operations
- Content creation
- Investment analysis
- System architecture
- Mentoring/advice

**For these use cases, pay for Sonnet/Opus. It's worth it.**

---

## The Honest Recommendation

**Don't ask:** "Should I use Haiku or Sonnet?"

**Ask instead:**
1. "What's my workload composition?"
2. "What's my quality bar?"
3. "What's the cost of re-work?"

Then choose models per use case:

| Use Case | Model | Why |
|----------|-------|-----|
| Heartbeats | Haiku | Perfect fit |
| Scripts | Haiku | Perfect fit |
| API calls | Haiku | Perfect fit |
| Short content | Sonnet | Quality matters |
| Research | Sonnet/Opus | Depth required |
| Long-form | Opus | Coherence at scale |
| Architecture | Opus | Context + quality |

**Optimize where it makes sense. Maintain quality where it matters.**

---

## Testing Methodology

**Want to test this yourself?**

1. **Track your tasks for 48 hours**
   - What did you ask OpenClaw to do?
   - How complex was each task?
   - What was the output quality bar?

2. **Categorize tasks**
   - Low complexity (scripts, APIs)
   - Medium (content, code)
   - High (research, architecture)

3. **Test Haiku on low-complexity tasks**
   - Did it work?
   - Any issues?
   - Quality acceptable?

4. **Calculate savings**
   - Tokens saved on viable tasks
   - Cost reduction
   - Re-work time avoided

5. **Make informed decision**
   - Not based on advice
   - Based on YOUR data

---

## Common Mistakes

### Mistake #1: Blindly Following Advice

❌ "Someone said use Haiku, so I switched everything"

✅ "Let me test Haiku on my actual workload first"

### Mistake #2: Optimizing Too Early

❌ "I just started, let me optimize costs"

✅ "Let me understand my usage pattern first, then optimize"

### Mistake #3: Ignoring Opportunity Cost

❌ "I saved $50/month using Haiku!"

✅ "I saved $50/month but spent 10 hours fixing output. Net: -$950"

### Mistake #4: All-or-Nothing

❌ "Haiku for everything or Sonnet for everything"

✅ "Haiku for heartbeats, Sonnet for main work, Opus for deep dives"

---

## Next Steps

1. **Implement cheap heartbeats** — [Heartbeats guide →](heartbeats.md)
2. **Read real-world analysis** — [Why Haiku failed →](../04-real-world-cases/why-haiku-failed.md)
3. **Optimize context** — [Context management →](context-management.md)

---

**Bottom line:** Model selection is not a religion. It's a trade-off. Understand your workload, test with your data, make informed decisions.

**The goal is not minimum cost. The goal is maximum value.**
