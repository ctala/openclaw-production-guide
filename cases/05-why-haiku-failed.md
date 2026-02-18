# Case 5: Why Haiku Failed (And Why That's OK)

**TL;DR:** After analyzing 99 real production tasks, only 25-33% could use Haiku without quality loss. The "just use Haiku everywhere" advice doesn't survive contact with real workflows.

---

## The Hypothesis

**Common wisdom:** "Haiku is 20x cheaper than Sonnet, so use it for everything except the most complex tasks."

**My assumption:** "I bet 80% of my tasks could run on Haiku, saving $600+/year."

**Reality:** 67-75% of my tasks degraded significantly with Haiku. Actual realistic savings: **$180/year** (not $624/year).

---

## The Test

I analyzed **99 active tasks** in my production NocoDB instance across these categories:

### Task Breakdown

| Category | Count | % of Total |
|----------|-------|------------|
| Content creation (blog, social, newsletter) | 28 | 28% |
| Skool community engagement | 15 | 15% |
| LinkedIn responses | 12 | 12% |
| Task optimization & prioritization | 10 | 10% |
| SEO research & gap analysis | 8 | 8% |
| Course content creation | 7 | 7% |
| API integrations & debugging | 6 | 6% |
| Strategic planning | 5 | 5% |
| General automation | 4 | 4% |
| Misc (email drafts, research, etc.) | 4 | 4% |

**Question:** Which of these can Haiku handle without degrading quality?

---

## The Results

### ✅ Tasks Haiku Handled Well (25-33%)

**1. Simple Data Fetching**
- Pull latest posts from API
- Extract structured data (JSON → CSV)
- Basic filtering/sorting

**Example:** "Fetch last 10 blog posts from WordPress API and output as JSON"

**Haiku result:** ✅ Perfect. No thinking required, just API call + format.

---

**2. Straightforward Code Edits**
- Fix typo in Python script
- Update config value
- Add simple validation check

**Example:** "Update scripts/index-url.py to use new API key variable"

**Haiku result:** ✅ Works fine. Code is clear, change is obvious.

---

**3. Factual Lookups**
- Check file existence
- Read specific config value
- Look up API endpoint

**Example:** "What's the current Listmonk API endpoint in credentials.json?"

**Haiku result:** ✅ Fast and accurate.

---

**4. Template Population**
- Fill in email template with variables
- Generate simple social post from outline
- Create changelog entry

**Example:** "Use this template to create a changelog entry for version 2.1.3"

**Haiku result:** ✅ Perfect for mechanical tasks.

---

### ❌ Tasks Haiku Failed (67-75%)

**1. Editorial Content (Blog Posts, Newsletters)**

**Task:** "Write blog post: 'Why OpenClaw Beats Mental Notes for Startup Founders'"

**Sonnet result:** 
- Personal tone, specific examples from real experience
- Nuanced points (e.g., "mental notes work...until they don't")
- Natural storytelling flow
- Founder credibility shines through

**Haiku result:**
- Generic startup blog voice
- Obvious AI writing patterns
- No personality or founder voice
- Reads like content mill output

**Quality gap:** 40-50% worse (subjective but noticeable)

**Verdict:** ❌ Not acceptable for public-facing content with founder's name on it.

---

**2. Community Engagement (Skool, LinkedIn)**

**Task:** Respond to Skool member's question about fundraising timelines

**Sonnet result:**
- Direct, empathetic, based on real exit experience
- Specific advice ("focus on revenue, not valuation")
- Asks follow-up question to continue conversation

**Haiku result:**
- Generic startup advice ("it depends on many factors")
- No personal experience referenced
- Feels like ChatGPT default mode

**Quality gap:** Members would notice immediately (destroys trust)

**Verdict:** ❌ Community engagement is relationship-building, not content generation.

---

**3. Task Prioritization & Strategic Thinking**

**Task:** Daily cron analyzing 99 NocoDB tasks, identifying blockers, suggesting atomization

**Sonnet result:**
- Detects nuance ("this task is blocked because X depends on Y")
- Suggests intelligent splits ("divide 'Create course' into 8 modules")
- Understands business context (revenue-generating tasks = higher priority)

**Haiku result:**
- Mechanical prioritization (just sorts by due date)
- Misses implicit blockers
- Suggests overly granular splits (e.g., "Research X" → 5 tasks of 30 min each)

**Quality gap:** Strategic decisions need context, not just pattern matching

**Verdict:** ❌ Task optimization IS the job—can't compromise here.

---

**4. SEO Research & Gap Analysis**

**Task:** Weekly SEO report comparing cristiantala.com vs ecosistemastartup.com, identifying content gaps

**Sonnet result:**
- Identifies thematic gaps ("You rank for 'pitch deck' but not 'investor deck'")
- Suggests strategic content ("Your exit story gives you E-E-A-T for fundraising topics")
- Prioritizes by search volume + relevance

**Haiku result:**
- Lists keywords mechanically
- No strategic insight
- Misses thematic connections

**Quality gap:** SEO without strategy = wasted effort

**Verdict:** ❌ Need intelligence, not just data processing.

---

**5. API Debugging & Complex Scripting**

**Task:** "Fix LinkedIn API integration—getting 403 errors on comment posting"

**Sonnet result:**
- Debugs systematically (checks auth, headers, payload structure)
- Reads API docs, compares to current implementation
- Identifies root cause (missing `X-AWS-WAF-Token` header)

**Haiku result:**
- Generic debugging steps ("check your API key")
- Doesn't read docs deeply
- Suggests trial-and-error instead of root cause analysis

**Quality gap:** Wastes time with surface-level fixes

**Verdict:** ❌ Debugging needs reasoning, not scripts.

---

## Why the 80/20 Assumption Was Wrong

**My error:** I assumed tasks were evenly distributed between "simple" and "complex."

**Reality:** 
- Production work skews heavily toward **nuanced, context-dependent tasks**
- The simple stuff (data fetching, file operations) was already automated
- What's left = the work that *needs* intelligence

**Analogy:**
- Hiring a junior dev to "just handle the easy stuff" sounds great...
- ...until you realize the easy stuff is already handled by scripts
- What remains = decisions, debugging, strategy

---

## The Honest Cost-Benefit Analysis

### Original Projection (Optimistic)
- **Assumption:** 80% tasks → Haiku (20x cheaper)
- **Projected savings:** $624/year

### Realistic Assessment (After Testing)
- **Reality:** 25-33% tasks → Haiku
- **Actual savings:** $180/year

**Breakdown:**

| Task Type | % of Tasks | Can Use Haiku? | Monthly Cost (Sonnet) | Monthly Cost (Haiku) | Savings |
|-----------|------------|----------------|------------------------|----------------------|---------|
| Editorial content | 28% | ❌ No | $18 | — | $0 |
| Community engagement | 15% | ❌ No | $12 | — | $0 |
| LinkedIn responses | 12% | ❌ No | $8 | — | $0 |
| Task optimization | 10% | ❌ No | $6 | — | $0 |
| SEO research | 8% | ❌ No | $5 | — | $0 |
| Course content | 7% | ❌ No | $4 | — | $0 |
| API debugging | 6% | ❌ No | $4 | — | $0 |
| Strategic planning | 5% | ❌ No | $3 | — | $0 |
| Simple fetching | 5% | ✅ Yes | $3 | $0.15 | $2.85/mo |
| Template population | 4% | ✅ Yes | $2 | $0.10 | $1.90/mo |
| **Total** | **100%** | **9%** | **$65/mo** | **$60/mo** | **~$5/mo** |

**Annual savings:** $5/mo × 12 = **$60/year** (for main session tasks)

**Heartbeat optimization:** Switching to Nano = additional **$120/year**

**Total realistic savings:** **$180/year** (not $624)

---

## Where Haiku DOES Work

### ✅ Heartbeats (95% Cost Reduction)
Polling every 30 minutes with Sonnet = $45/month.

**Solution:** Use Nano model for heartbeats (just checking if action needed).

**Savings:** $40/month = **$480/year**

**Reality check:** This savings alone is bigger than all Haiku task savings combined.

---

### ✅ Simple Data Operations
- Fetching API data
- File operations (read, write, basic edits)
- Template population
- Structured data transformation

**When to use Haiku:**
1. Zero ambiguity in task
2. No quality threshold (it's correct or it's not)
3. No strategic thinking required
4. Output is intermediate (not public-facing)

---

### ✅ Background Checks (Crons)
- "Check if Late API has scheduled posts"
- "Verify Listmonk campaign sent successfully"
- "Download Apify dataset"

**Why it works:** Boolean checks, no nuance.

---

## The Better Optimization Strategy

Instead of "use Haiku everywhere," focus on:

### 1. **Model Routing** (15-20% savings)
Match model to task complexity:
- **Heartbeats:** Nano ($0.0001/call)
- **Simple data ops:** Haiku ($0.0025/call)
- **Editorial:** Sonnet ($0.015/call)
- **Strategic:** Opus ($0.075/call)

**Implementation:** `configs/model-routing-rules.json`

---

### 2. **Optimize Heartbeats First** (50% of potential savings)
Biggest cost = background polling with expensive model.

**Quick win:** Switch heartbeats to Nano → $480/year saved.

**Time to implement:** 10 minutes.

---

### 3. **Batch Simple Tasks** (10% savings)
Instead of:
- Haiku call 1: Fetch posts
- Haiku call 2: Filter posts
- Haiku call 3: Format output

**Do:**
- Single Haiku call: Fetch + filter + format

**Savings:** 67% fewer API calls.

---

### 4. **Cache Aggressively** (5-10% savings)
OpenClaw caches tool outputs with TTL.

**Example:** Fetching WordPress posts every 5 minutes = wasteful.

**Solution:** Set `outputTTL: 3600` (1 hour cache).

**Savings:** 92% fewer API calls.

---

## Lessons Learned

### 1. **Measure Real Tasks, Not Hypothetical Ones**
"I bet 80% could use Haiku" = wishful thinking.

**Better:** Export your actual task list, analyze each one.

---

### 2. **Quality Degradation is Subjective (And That Matters)**
Haiku's blog posts aren't *wrong*—they're just...generic.

For a founder with an exit positioning themselves as a thought leader, generic = death.

**Different context?** Haiku might be fine (e.g., internal docs, drafts for heavy editing).

---

### 3. **The 'Cheap' Model Costs More If You Redo Work**
If Haiku generates a blog post that needs 30 min of manual rewriting...

...you just spent more time ($$) than using Sonnet upfront.

**Hidden cost:** Your time fixing AI output.

---

### 4. **Optimization ≠ Cheapest Model Everywhere**
Real optimization:
- ✅ Right model for right task
- ✅ Cache aggressively
- ✅ Batch when possible
- ✅ Eliminate unnecessary calls

**Not:**
- ❌ Blanket downgrade to Haiku
- ❌ "Set it and forget it"

---

### 5. **Honesty > Hype**
Admitting "Haiku didn't work for 67% of my tasks" is more valuable than claiming "I saved $600/year" (when I didn't).

**Why this matters:** 
- Other founders waste less time testing what won't work
- Credibility > inflated numbers
- Real production insights > theoretical optimization

---

## Takeaway

**Haiku is great for what it's great for:**
- Heartbeats
- Simple data operations
- Template population
- Boolean checks

**Haiku is NOT a drop-in replacement for Sonnet** when:
- Quality threshold exists (editorial, community, client-facing)
- Strategic thinking required (prioritization, gap analysis)
- Context matters (debugging, nuanced responses)

**The real win:** Optimize heartbeats to Nano ($480/year), use Haiku for ~10% of tasks ($60/year).

**Total realistic savings:** $540/year.

**Time to implement:** 2-3 hours.

**ROI:** $180/hour of optimization work.

---

**Honest assessment beats optimistic projection every time.**
