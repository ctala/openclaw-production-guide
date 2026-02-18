# Case 3: Newsletter Sync (Listmonk)

**Status:** ✅ Production (90 days)  
**Subscribers:** 1,923 (personal list)  
**Campaigns Sent:** 45+ automated  
**Open Rate:** 32% avg (industry avg: 21%)  
**Time Saved:** ~2 hours/week

---

## The Problem

Email newsletters are **high-value** for founder-led brands:
- Direct channel (no algorithm)
- High engagement (if done right)
- Owned audience (not rented from platforms)

**But they're time-intensive:**
- Write content (1-2 hours)
- Format for email (30 min)
- Schedule in ESP (15 min)
- Track performance (15 min)
- **Total: 2-3 hours per newsletter**

**Previous setup:**
- MailerLite (SaaS, $29/month for >1,000 subs)
- Manual scheduling
- Separate tracking in spreadsheets

---

## The Solution

**Self-hosted Listmonk + OpenClaw automation:**

1. **Migration** — Moved from MailerLite to self-hosted Listmonk
2. **Automation** — OpenClaw creates campaigns from blog posts
3. **Scheduling** — Native Listmonk scheduling (not cron-based)
4. **Tracking** — NocoDB table syncs campaign stats
5. **Distribution** — Newsletter content repurposed for social (Late API)

---

## Tech Stack

### Listmonk (Self-Hosted)
- **URL:** listmonk.nyx.cristiantala.com
- **Instance:** Docker on VPS srv1301687
- **Database:** PostgreSQL (same server)
- **Cost:** $0/month (self-hosted, included in VPS)

**Why self-hosted vs SaaS?**
- MailerLite: $29/month for 1,923 subs
- Listmonk: $0/month (one-time setup)
- **Annual savings: $348/year**

### OpenClaw Integration
- **Skill:** `skills/listmonk-api/`
- **Credentials:** `.config/credentials.json`
- **API Endpoints:**
  - `POST /api/campaigns` — Create campaign
  - `PUT /api/campaigns/{id}` — Update (schedule, send)
  - `GET /api/campaigns` — List campaigns
  - `GET /api/campaigns/{id}` — Stats (opens, clicks)

### Workflow
```
Blog Post (WordPress)
  ↓
OpenClaw detects new post
  ↓
Extract title, excerpt, URL
  ↓
Generate email version (Sonnet)
  ↓
Create Listmonk campaign
  ↓
Schedule for next day 9 AM
  ↓
Track in NocoDB Newsletter Tracker
  ↓
Repurpose for social (Late API)
```

---

## File Structure

```
skills/listmonk-api/
├── .config/
│   └── credentials.json        # API key, base URL
├── scripts/
│   ├── create-campaign.py      # Create from blog post
│   ├── schedule-campaign.py    # Set send time
│   ├── get-stats.py            # Pull campaign metrics
│   └── sync-to-nocodb.py       # Update Newsletter Tracker table
└── templates/
    └── blog-to-email.html      # Email template
```

---

## Automation Flow

### 1. Trigger: New Blog Post
When WordPress post is published:
```bash
# n8n webhook triggers OpenClaw
openclaw session send "New blog post: [POST_URL]"
```

### 2. Extract Content
```python
# OpenClaw uses web_fetch to pull post
post_data = web_fetch(post_url)

# Extract metadata
title = post_data['title']
excerpt = post_data['excerpt']
featured_image = post_data['featured_image']
```

### 3. Generate Email Version
**Model:** Sonnet (quality matters for editorial)

**Prompt:**
```
Convert this blog post to an engaging email newsletter.

Blog post: [TITLE + CONTENT]

Requirements:
- Personal tone (from Cristian)
- Hook in first 2 lines
- 3-4 short paragraphs max
- CTA: Read full post
- Subject line (compelling, not clickbait)

Format: Plain text email (no heavy HTML)
```

### 4. Create Listmonk Campaign
```python
import requests

campaign_data = {
    "name": f"Newsletter: {title}",
    "subject": generated_subject,
    "body": email_html,  # From template
    "lists": [1],  # List ID for personal subscribers
    "type": "regular",
    "content_type": "html",
    "send_at": "2026-02-19T09:00:00Z"  # Next day 9 AM
}

response = requests.post(
    "https://listmonk.nyx.cristiantala.com/api/campaigns",
    json=campaign_data,
    auth=("username", "password")
)
```

### 5. Track in NocoDB
**Table:** Newsletter Tracker (`mdnqorwk1v9cwkl`)

**Fields:**
- Name (newsletter title)
- Newsletter (which list)
- Week (YYYY-Wxx)
- Status (Draft/Scheduled/Sent)
- Scheduled For (datetime)
- Sent At (datetime)
- Subscribers (int)
- Opens (int)
- Open Rate (%)
- Clicks (int)
- Click Rate (%)
- Listmonk ID (campaign ID)
- Subject (email subject line)

```python
nocodb.create_record(
    table_id="mdnqorwk1v9cwkl",
    data={
        "Name": title,
        "Newsletter": "Personal",
        "Status": "Scheduled",
        "Scheduled For": "2026-02-19 09:00",
        "Listmonk ID": campaign_id,
        "Subject": subject_line
    }
)
```

### 6. Post-Send Stats Update
**Cron:** Daily 12 PM (3 hours after typical send time)

```python
# Fetch campaign stats from Listmonk
stats = listmonk.get_campaign_stats(campaign_id)

# Update NocoDB
nocodb.update_record(
    table_id="mdnqorwk1v9cwkl",
    record_id=nocodb_record_id,
    data={
        "Status": "Sent",
        "Sent At": stats['sent_at'],
        "Subscribers": stats['total'],
        "Opens": stats['opens'],
        "Open Rate": round(stats['opens'] / stats['total'] * 100, 1),
        "Clicks": stats['clicks'],
        "Click Rate": round(stats['clicks'] / stats['total'] * 100, 1)
    }
)
```

---

## Critical Lessons

### 1. **Self-Hosted = One-Time Setup Cost, Infinite Savings**
MailerLite cost for 1,923 subs: $29/month

Listmonk setup:
- 2 hours initial setup (Docker + PostgreSQL)
- $0/month ongoing
- **Payback period: 2 hours vs $29 = ROI in first month**

### 2. **Native Scheduling > Cron-Based Scheduling**
**Wrong approach:**
```bash
# Cron at 9 AM: "Send newsletter via API"
```

**Right approach:**
```python
# Create campaign with scheduled_at timestamp
# Listmonk handles sending at exact time
```

**Why:**
- Exact timing (not dependent on cron intervals)
- Better deliverability (Listmonk optimizes send time per ISP)
- Less failure points (no need for cron → OpenClaw → API chain)

### 3. **Email Subject Lines = Humans Only**
I tried AI-generated subject lines for 10 newsletters.

**Results:**
- AI subjects: 24% open rate
- Human-written subjects: 35% open rate

**Lesson:** Let AI draft the body, but write subject lines yourself.

### 4. **Plain Text > Heavy HTML**
Test results:
- Rich HTML templates: 28% open rate, 15% flagged as spam
- Plain text with light formatting: 34% open rate, 2% spam flags

**Why:** ISPs trust plain text more, readers prefer simple emails from founders.

### 5. **Repurposing = 3x Content ROI**
One blog post becomes:
1. WordPress post (SEO + evergreen)
2. Newsletter (email subscribers)
3. LinkedIn article snippet (Late API)
4. Twitter thread (Late API)
5. Instagram carousel summary (manual, but content ready)

**Time investment:**
- Write blog post: 2 hours
- Repurpose to 5 formats: 30 min (mostly automated)
- **Total reach: 5,000+ people from 2.5 hours work**

---

## Results

**Stats (90 days):**
- Newsletters sent: 45
- Avg subscribers per send: 1,923
- Avg open rate: 32% (industry avg: 21%)
- Avg click rate: 8% (industry avg: 2.5%)
- Total opens: 27,594
- Total clicks: 6,912

**Cost savings:**
- MailerLite cost (90 days): $87
- Listmonk cost (90 days): $0
- **Savings: $87** (annual: $348)

**Time savings:**
- Before: 2-3 hours per newsletter
- After: 30-45 min (mostly approval + subject line)
- **Savings per newsletter: 1.5-2 hours**
- **Monthly savings: 6-8 hours** (assuming 4 newsletters/month)

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Listmonk hosting (self-hosted on VPS) | $0/month |
| Domain (nyx.cristiantala.com) | $0 (wildcard subdomain) |
| SSL cert (Caddy auto-renewal) | $0 (Let's Encrypt) |
| Sonnet API calls (email generation) | ~$0.60/month (4 newsletters × $0.15) |
| NocoDB tracking (self-hosted) | $0/month |
| **Total** | **~$0.60/month** |

**vs MailerLite:** $29/month  
**Annual savings:** $341/year

---

## Template Example

**blog-to-email.html:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px; }
    h1 { font-size: 24px; margin-bottom: 10px; }
    p { line-height: 1.6; margin-bottom: 15px; }
    .cta { background: #0066cc; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>{{TITLE}}</h1>
  
  {{CONTENT}}
  
  <a href="{{POST_URL}}" class="cta">Read the full post →</a>
  
  <p style="color: #666; font-size: 14px; margin-top: 40px;">
    You're receiving this because you signed up for updates from cristiantala.com.<br>
    <a href="{{UNSUBSCRIBE_URL}}">Unsubscribe</a>
  </p>
</body>
</html>
```

---

## Next Steps

1. **A/B test subject lines** — Track which patterns perform best
2. **Segment lists** — Separate tech content vs startup content subscribers
3. **Automated follow-ups** — Send "missed this?" email to non-openers after 48h
4. **Integrate with Skool** — Newsletter → Skool post for community members

---

## Takeaway

**Newsletters don't need expensive SaaS—they need good content and reliable delivery.**

Self-hosting Listmonk saved $348/year with zero compromise on deliverability. Automation saved 6-8 hours/month.

**The result:** More time writing, less time scheduling. Higher engagement, lower costs.
