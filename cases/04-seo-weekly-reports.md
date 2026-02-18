# Case 4: SEO Weekly Reports

**Status:** ✅ Production (30 days)  
**Frequency:** Weekly (Mondays 1 AM)  
**Tasks Created:** 21 SEO opportunities  
**Content Gaps Identified:** 190+ keywords  
**Time Saved:** ~3 hours/week

---

## The Problem

SEO requires **continuous optimization**, not one-time setup:
- Keywords shift (new trends, competitors)
- Content gaps emerge (you rank for X, not Y)
- Opportunities get missed (high-volume, low-competition keywords)

**Manual SEO audits:**
- 2-3 hours per week
- Tedious (comparing keyword lists, finding gaps)
- Inconsistent (depends on founder's availability)

**Result:** SEO gets deprioritized → organic traffic stagnates.

---

## The Solution

**Automated weekly SEO reports with actionable tasks:**

1. **Data Pull** — Serpstat API fetches keyword rankings for 2 domains
2. **Gap Analysis** — Compare cristiantala.com vs ecosistemastartup.com
3. **Opportunity Detection** — High-volume keywords where neither site ranks
4. **Task Creation** — NocoDB tasks with priority, search volume, difficulty
5. **Strategic Recommendations** — Leverage E-E-A-T (Experience, Expertise, Authority, Trust)

---

## Tech Stack

### Serpstat API
- **Purpose:** Keyword research, competitor analysis, ranking tracking
- **Plan:** Professional ($69/month, shared with other projects)
- **Endpoints Used:**
  - `/v4/domain_keywords` — All keywords a domain ranks for
  - `/v4/keywords_top` — Top keywords by search volume
  - `/v4/keyword_difficulty` — SEO difficulty score

### NocoDB (Task Management)
- **Table:** Tasks (`mpi5xe87sjlrncl`)
- **Base:** Content & Tasks Manager (`pjs7sxtkkuwmzn8`)
- **Fields:** Title, Description, Priority, Due Date, Status, Value, Tags

### OpenClaw Cron
- **Model:** Opus 4.6 (strategic analysis needs deep reasoning)
- **Schedule:** Mondays 1:00 AM (weekly)
- **Session:** Isolated (doesn't clutter main session history)
- **Delivery:** Announce to Telegram (summary of findings)

---

## Workflow

### 1. Data Collection
```python
import requests

# Fetch keywords for cristiantala.com
cristiantala_kw = serpstat.get_domain_keywords("cristiantala.com")
# Returns: 98 keywords

# Fetch keywords for ecosistemastartup.com
ecosistema_kw = serpstat.get_domain_keywords("ecosistemastartup.com")
# Returns: 92 keywords

# Fetch high-volume startup/tech keywords
target_keywords = serpstat.get_keywords_top(
    query="startup OR pitch OR inversión OR fundraising",
    country="CL",
    limit=500
)
```

### 2. Gap Analysis
```python
# Keywords cristiantala ranks for
ct_keywords = set([kw['keyword'] for kw in cristiantala_kw])

# Keywords ecosistema ranks for
eco_keywords = set([kw['keyword'] for kw in ecosistema_kw])

# Keywords NEITHER ranks for (opportunity)
target_set = set([kw['keyword'] for kw in target_keywords])
gaps = target_set - ct_keywords - eco_keywords

# Filter by search volume (>100/month) and difficulty (<40)
high_value_gaps = [
    kw for kw in gaps 
    if kw['volume'] > 100 and kw['difficulty'] < 40
]
```

### 3. Strategic Prioritization
**Model:** Opus 4.6

**Prompt:**
```
You are analyzing SEO opportunities for Cristian Tala (cristiantala.com).

Context:
- Sold tech startup (fintech)
- 30+ angel investments
- Mentor in tech and automation
- Blog focus: Tech, AI, Startups, Automation

Keyword gaps found: [LIST]

For each keyword, analyze:
1. Relevance to Cristian's expertise (1-10)
2. E-E-A-T advantage (does his experience give unfair advantage?)
3. Content angle (what unique perspective can he bring?)
4. Priority (P0/P1/P2/P3)

Return top 10 opportunities with:
- Keyword
- Search volume
- Difficulty
- Recommended angle
- Priority
- Estimated traffic potential
```

**Output example:**
```json
{
  "keyword": "pitch deck template",
  "volume": 3600,
  "difficulty": 35,
  "angle": "Share actual pitch deck from successful exit + investor feedback",
  "priority": "P1",
  "traffic_potential": "500-800 visits/month",
  "eeat_advantage": "Real exit experience + 30+ investments = credibility others lack"
}
```

### 4. Task Creation (NocoDB)
For each opportunity:
```python
nocodb.create_record(
    table_id="mpi5xe87sjlrncl",  # Tasks table
    data={
        "Title": f"SEO: Write '{keyword}' post",
        "Description": f"""
Keyword: {keyword}
Search volume: {volume}/month
Difficulty: {difficulty}
Angle: {recommended_angle}

E-E-A-T advantage: {eeat_advantage}

Estimated traffic: {traffic_potential}
        """,
        "Priority": priority,  # P0/P1/P2/P3
        "Status": "Backlog",
        "Tags": ["SEO", "Content", "Blog"],
        "Value": calculate_value(volume, difficulty),  # 1-10 scale
        "Due Date": None  # Will be prioritized by daily task optimization cron
    }
)
```

### 5. Report Generation
**Markdown report saved to:**
```
content-strategy/keyword-research/weekly-YYYY-MM-DD.md
```

**Structure:**
```markdown
# SEO Weekly Report — 2026-02-16

## Summary
- **cristiantala.com:** 98 keywords ranking
- **ecosistemastartup.com:** 92 keywords ranking
- **Content gaps found:** 47 high-value keywords
- **Tasks created:** 7 (P1: 3, P2: 4)

## Top Opportunities

### 1. "pitch deck template" (3.6K/mo, Difficulty 35)
**Angle:** Share actual pitch deck from exit + investor feedback  
**E-E-A-T:** Real exit + 30+ investments = unfair advantage  
**Traffic potential:** 500-800/month  
**Priority:** P1

[... more opportunities ...]

## Strategic Recommendations
1. Prioritize exit story content (highest E-E-A-T)
2. Create pillar page: "Startup Fundraising" (link to pitch, investor, valuation posts)
3. Internal linking: Link ecosistema posts to cristiantala (dofollow, pass authority)

## Tasks Created
- [x] SEO: Write "pitch deck template" post (P1, NocoDB #130)
- [x] SEO: Write "product market fit" post (P1, NocoDB #131)
[...]
```

---

## Critical Lessons

### 1. **Opus for Strategy, Not Haiku**
I tested Haiku for SEO analysis.

**Haiku output:**
- Mechanical keyword lists
- No strategic insight
- Missed E-E-A-T connections ("pitch deck" + "exit experience" correlation)

**Opus output:**
- Strategic angles ("Your exit gives you credibility competitors lack")
- Content cluster recommendations
- Priority based on business goals (not just search volume)

**Verdict:** SEO analysis IS strategic thinking. Use Opus.

---

### 2. **E-E-A-T = Unfair Advantage**
Google's algorithm prioritizes **Experience, Expertise, Authority, Trust**.

**For Cristian:**
- Exit experience → Authority on fundraising, exits, scaling
- 30+ investments → Expertise on pitch decks, investor perspectives
- Tech background → Trust on automation, AI, tech stacks

**Insight:** Don't compete on generic keywords. Target keywords where his experience is an unfair advantage.

**Example:**
- ❌ "how to start a startup" (generic, everyone writes this)
- ✅ "how to negotiate exit terms" (requires real experience)

---

### 3. **Content Gaps ≠ Keyword Stuffing**
190 keyword gaps doesn't mean "write 190 posts."

**Better approach:**
1. Group keywords by theme (e.g., "pitch deck", "investor deck", "startup presentation" = 1 pillar post)
2. Create comprehensive content (3,000+ words)
3. Naturally covers 10-20 related keywords

**Result:** 10 pillar posts > 100 thin posts.

---

### 4. **Weekly Cadence = Sustainable**
I tried daily SEO checks → too noisy, no time to act.

Weekly works because:
- Enough time to execute previous week's tasks
- Keywords don't shift daily
- Prevents task backlog explosion

---

### 5. **Automate Data, Not Decisions**
Serpstat API pulls data → automated.

Which keywords to target → human decision (Opus-assisted).

**Anti-pattern:** "Just write about top 10 keywords by volume."

**Reality:** Volume without relevance = wasted effort.

---

## Results

**Stats (30 days, 4 reports):**
- Keywords analyzed: 680
- Content gaps identified: 190
- High-value opportunities: 47
- Tasks created: 21 (P1: 7, P2: 10, P3: 4)
- Tasks completed: 8 (38% completion rate in 30 days)

**SEO impact (early, 30 days):**
- New keywords ranking: 12
- Traffic increase: +8% (too early for statistical significance)
- Blog posts published from gaps: 3

**Time savings:**
- Manual SEO audit: 3 hours/week
- Automated report: 5 min review time
- **Savings: 2h 55min/week = 12 hours/month**

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Serpstat API (Professional plan) | $69/month (shared with other projects) |
| Opus 4.6 (weekly cron) | ~$0.30/week ($1.20/month) |
| NocoDB (self-hosted) | $0/month |
| Storage (keyword reports) | $0 (text files, negligible) |
| **Total** | **~$70/month** |

**ROI:**
- Time saved: 12 hours/month
- At $100/hour value = $1,200 saved
- Cost: $70
- **Net value: $1,130/month**

---

## Sample Output

**Top 3 opportunities from 2026-02-16 report:**

### 1. "pitch deck template" 
- **Volume:** 3,600/month
- **Difficulty:** 35
- **Angle:** Share actual pitch deck from exit + breakdown of investor feedback
- **E-E-A-T:** Real exit + 30+ investments = credibility competitors lack
- **Traffic potential:** 500-800/month
- **Priority:** P1

### 2. "product market fit"
- **Volume:** 390/month
- **Difficulty:** 28
- **Angle:** PMF lessons from Pago Fácil (plugin → 6K companies)
- **E-E-A-T:** Built product from 0 → exit, knows PMF journey firsthand
- **Traffic potential:** 150-250/month
- **Priority:** P1

### 3. "startup equity calculator"
- **Volume:** 720/month
- **Difficulty:** 32
- **Angle:** Interactive calculator + equity mistakes from 30+ investments
- **E-E-A-T:** Investor perspective (sees both sides: founder + investor)
- **Traffic potential:** 300-500/month
- **Priority:** P2 (requires tool development)

---

## Next Steps

1. **Integrate Search Console API** — Currently blocked (403 Forbidden, service account needs Owner permissions)
2. **Rank tracking** — Monitor position changes for target keywords
3. **Competitor analysis** — Track what competitors rank for that we don't
4. **Backlink monitoring** — Identify new link opportunities

---

## Takeaway

**SEO doesn't happen by accident—it happens by system.**

Weekly automated reports turn "I should do SEO" into "here are 7 tasks with clear ROI."

**The result:** Consistent content strategy, no manual research, 12 hours/month saved.
