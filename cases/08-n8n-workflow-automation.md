# Case 8: n8n Workflow Automation

**Status:** ✅ Production (12+ months)  
**Instances:** 3 (dev, prod, cloud)  
**Workflows Active:** 20+  
**Monthly Executions:** 8,000+  
**Cost:** $0/month (self-hosted dev/prod), $20/month (cloud)  
**Time Saved:** ~15 hours/week

---

## The Problem

Founders juggle **100+ repetitive tasks** that could be automated:
- Social media cross-posting (blog → LinkedIn, Twitter, Instagram)
- Webhook routing (Stripe → NocoDB, Circle → Skool migration)
- Data syncing (WordPress → Listmonk → Late API)
- Notification triggers (new comment → Telegram, new sale → email)
- Content workflows (generate image → publish post → track engagement)

**Manual execution:**
- Time-consuming (30 min to publish 1 blog post across 5 platforms)
- Error-prone (forget to tag, use wrong image, miss CTA)
- Inconsistent (do it when you remember, skip when busy)

**Zapier/Make.com:**
- Expensive ($29-99/month for meaningful limits)
- Limited logic (can't handle complex branching)
- Vendor lock-in (can't inspect code or self-host)

---

## The Solution

**n8n self-hosted + cloud hybrid:**

1. **Dev Instance** — Local testing (n8n.nyx.cristiantala.com)
2. **Prod Instance** — Critical workflows (n8n.cristiantala.com)
3. **Cloud Instance** — Webhooks from external services (n8n.cloud)
4. **OpenClaw Integration** — n8n triggers OpenClaw, OpenClaw calls n8n APIs
5. **Skill-Based Patterns** — Reusable sub-workflows (replicate-api, wordpress-api, late-api)

---

## Tech Stack

### n8n Instances

| Instance | URL | Purpose | Hosting | Cost |
|----------|-----|---------|---------|------|
| **Dev** | n8n.nyx.cristiantala.com | Testing, staging workflows | Docker (VPS srv1301687) | $0 |
| **Prod** | n8n.cristiantala.com | Production workflows | Docker (VPS srv1301687) | $0 |
| **Cloud** | cristiantala.app.n8n.cloud | External webhooks, mobile app triggers | n8n Cloud (managed) | $20/month |

**Why 3 instances?**
- **Dev:** Break things safely without affecting production
- **Prod:** Reliable execution for business-critical workflows
- **Cloud:** External services (Stripe, Zapier webhooks) need public endpoints with uptime SLA

### OpenClaw Integration

**n8n calls OpenClaw:**
```javascript
// n8n HTTP Request node
POST https://openclaw-gateway-url/api/session/send
{
  "message": "New blog post published: {{$json.title}}",
  "sessionKey": "main"
}
```

**OpenClaw calls n8n:**
```python
# From OpenClaw skill (e.g., replicate-api)
import requests

n8n_webhook_url = "https://n8n.cristiantala.com/webhook/trigger-image-gen"
response = requests.post(n8n_webhook_url, json={
    "prompt": "Synthwave cyberpunk landscape",
    "style": "featured",
    "format": "jpg"
})
```

---

## Key Workflows

### 1. Blog Post Multi-Channel Distribution

**Trigger:** WordPress post published

**Flow:**
```
WordPress Webhook
  ↓
Extract post data (title, excerpt, featured image, URL)
  ↓
IF featured image exists:
  ├─ Yes → Use it
  └─ No → Generate with Replicate API (Synthwave style)
  ↓
Create LinkedIn post (Late API)
  ├─ Text: Excerpt + CTA
  └─ Image: Featured image
  ↓
Create Twitter thread (Late API)
  ├─ Text: Title + 3 key points
  └─ Image: Featured image
  ↓
Create newsletter (Listmonk)
  ├─ Subject: Post title
  └─ Body: Excerpt + "Read more" link
  ↓
Track in NocoDB (Content Calendar table)
  ├─ Platform: LinkedIn, Twitter, Newsletter
  └─ Status: Scheduled
  ↓
Notify Telegram: "Post distributed to 3 channels ✅"
```

**Execution time:** 30-45 seconds  
**Manual equivalent:** 30-45 minutes

---

### 2. Skool → Asana Task Sync (Pre-Migration)

**Trigger:** New Skool post (via webhook)

**Flow:**
```
Skool Webhook (new post)
  ↓
Extract post data (author, title, content, URL)
  ↓
IF author != Cristian Tala:
  ↓
  Create Asana task
    ├─ Title: "Skool: Respond to {{author}}"
    ├─ Description: {{content}}
    ├─ Project: Community Engagement
    └─ Due: Today + 1 day
  ↓
  Notify Telegram Topic 27: "New Skool post from {{author}}"
```

**Status:** Deprecated after Skool automation (now handled by OpenClaw Apify actor)

---

### 3. Stripe → NocoDB Revenue Tracking

**Trigger:** Stripe webhook (successful payment)

**Flow:**
```
Stripe Webhook (charge.succeeded)
  ↓
Extract payment data (amount, customer, product)
  ↓
Create NocoDB record (Revenue Tracker table)
  ├─ Amount: {{amount / 100}} USD
  ├─ Customer: {{customer_email}}
  ├─ Product: {{product_name}}
  ├─ Date: {{created_timestamp}}
  └─ Source: Stripe
  ↓
IF amount > 100 USD:
  ↓
  Notify Telegram: "🎉 New sale: ${{amount}} from {{customer_email}}"
```

**Frequency:** ~10-20 executions/month

---

### 4. Late API → Listmonk Subscriber Sync

**Trigger:** Cron (daily 2 AM)

**Flow:**
```
Fetch Late API scheduled posts (next 7 days)
  ↓
FOR EACH post:
  ├─ Extract post data (platform, content, scheduled_at)
  ├─ IF platform == "newsletter":
      ├─ Check if Listmonk campaign exists (by Late ID)
      ├─ IF not exists:
          └─ Create Listmonk campaign
              ├─ Subject: {{post_content.subject}}
              ├─ Body: {{post_content.body}}
              ├─ Lists: [1] (personal subscribers)
              └─ Schedule: {{scheduled_at}}
      └─ Update NocoDB (Newsletter Tracker)
```

**Purpose:** Sync Late API scheduling with Listmonk campaigns

---

### 5. SEO Indexing Automation

**Trigger:** New WordPress post published

**Flow:**
```
WordPress Webhook
  ↓
Extract post URL
  ↓
Submit to IndexNow
  ├─ Endpoint: https://api.indexnow.org/indexnow
  ├─ Key: dc2ebb5760ac4dcd9c71c030fea11768
  ├─ URL: {{post_url}}
  ↓
Submit to Google Search Console
  ├─ Endpoint: https://searchconsole.googleapis.com/v1/urlInspection
  ├─ Auth: Service Account (n8n-prod-service-account)
  ├─ URL: {{post_url}}
  ↓
Wait 48 hours (delay node)
  ↓
Check indexing status (Google Search Console API)
  ↓
IF not indexed after 48h:
  ↓
  Notify Telegram: "⚠️ Post not indexed: {{post_url}}"
```

**Status:** Partially blocked (Google Search Console API needs Owner permissions)

---

## Critical Lessons

### 1. **Self-Hosted Dev + Cloud Prod = Best of Both Worlds**

**All self-hosted:**
- ✅ Free
- ❌ Public webhooks break (VPS IP changes, firewall issues)
- ❌ No uptime SLA

**All cloud:**
- ✅ Reliable webhooks
- ✅ Uptime SLA
- ❌ $99/month for >10K executions

**Hybrid (self-hosted dev + cloud prod):**
- ✅ Test locally, deploy to cloud
- ✅ Cloud only for external webhooks (Stripe, etc.)
- ✅ Self-hosted for internal workflows (80% of workflows)
- **Cost:** $20/month (vs $99/month all-cloud)

---

### 2. **n8n Code Nodes = Unlimited Flexibility**

**Function Node (JavaScript):**
```javascript
// Transform WordPress post to LinkedIn format
const post = $input.item.json;

const linkedinPost = {
  text: `${post.title}\n\n${post.excerpt}\n\nLee más: ${post.url}`,
  image_url: post.featured_image,
  scheduled_at: new Date(Date.now() + 86400000).toISOString() // Tomorrow
};

return { json: linkedinPost };
```

**When to use:**
- Data transformation (WordPress → LinkedIn format)
- Complex logic (if X and Y, then Z)
- API payload construction

**When NOT to use:**
- Simple field mapping (use Set node)
- API calls (use HTTP Request node)

---

### 3. **Error Handling = Production-Ready Workflows**

**Bad workflow:**
```
Trigger → API Call → Done
```

**If API fails:** Workflow stops, no notification, no retry.

**Production workflow:**
```
Trigger
  ↓
TRY:
  ├─ API Call
  └─ Success → Log to NocoDB
CATCH:
  ├─ Log error
  ├─ Retry 3x (exponential backoff)
  └─ IF still fails:
      └─ Notify Telegram: "Workflow failed: {{error_message}}"
```

**Implementation:** Use Error Trigger node + retry logic.

---

### 4. **Sub-Workflows = Reusable Patterns**

**Problem:** "Generate Synthwave image" logic duplicated in 5 workflows.

**Solution:** Create sub-workflow:

**Main workflow:**
```
Trigger
  ↓
Call sub-workflow: "generate-synthwave-image"
  ├─ Input: prompt, style, format
  └─ Output: image_url
  ↓
Use image_url in Late API post
```

**Sub-workflow: "generate-synthwave-image"**
```
Webhook Trigger (internal)
  ↓
Replicate API (synthwave model)
  ↓
Poll for completion (max 60s)
  ↓
Download image
  ↓
Upload to CDN (assets.nyx.cristiantala.com)
  ↓
Return CDN URL
```

**Benefits:**
- DRY (Don't Repeat Yourself)
- Update logic in 1 place
- Easier debugging

---

### 5. **Execution Limits = Monitor Before You Hit Them**

**n8n Cloud limits (Starter plan):**
- 2,500 executions/month
- Overage: $1 per 500 executions

**My usage:**
- Month 1: 8,000 executions → $11 overage fees
- **Problem:** Didn't realize how many executions I was burning

**Solution:**
1. Self-host high-frequency workflows (daily crons → dev instance)
2. Keep cloud for low-frequency, high-reliability webhooks (Stripe, etc.)
3. Monitor via n8n dashboard (set alert at 80% quota)

**Result:** $20/month (no overages) vs $32/month before.

---

## OpenClaw ↔ n8n Integration Patterns

### Pattern 1: n8n Triggers OpenClaw

**Use case:** External event needs AI processing

**Example:** Stripe payment → notify OpenClaw → generate thank-you email

```javascript
// n8n HTTP Request node
POST https://gateway.openclaw.local/api/session/send
{
  "message": "New customer: {{$json.customer_email}}. Generate personalized thank-you email.",
  "sessionKey": "main"
}
```

---

### Pattern 2: OpenClaw Calls n8n Webhook

**Use case:** OpenClaw needs external API orchestration

**Example:** OpenClaw generates image → n8n uploads to CDN

```python
# OpenClaw skill
import requests

webhook_url = "https://n8n.cristiantala.com/webhook/upload-to-cdn"
response = requests.post(webhook_url, json={
    "image_data": base64_image,
    "filename": "synthwave-featured.jpg"
})

cdn_url = response.json()['cdn_url']
```

---

### Pattern 3: n8n as Middleware

**Use case:** Complex API workflow with multiple steps

**Example:** Blog post → generate image → publish to 3 platforms → track

```
OpenClaw: "Publish blog post X"
  ↓
OpenClaw calls n8n webhook: /webhook/publish-blog-post
  ↓
n8n orchestrates:
  ├─ Generate image (Replicate API)
  ├─ Publish LinkedIn (Late API)
  ├─ Publish Twitter (Late API)
  ├─ Create newsletter (Listmonk)
  ├─ Track in NocoDB
  └─ Return summary to OpenClaw
  ↓
OpenClaw announces: "Post published to 3 platforms ✅"
```

---

## Results

**Stats (12 months):**
- Workflows active: 20+
- Monthly executions: 8,000+ (avg)
- Execution success rate: 97.2%
- Failed workflows: 224 (mostly API rate limits, handled by retry logic)

**Time saved:**
- Blog post distribution: 30 min → 30 sec (60x faster)
- SEO indexing: 15 min → 0 min (fully automated)
- Revenue tracking: 10 min/week → 0 min (Stripe webhook)
- Social scheduling: 2 hours/week → 0 min (automated)
- **Total saved: ~15 hours/week**

---

## Cost Breakdown

| Instance | Hosting | Monthly Cost |
|----------|---------|--------------|
| Dev (n8n.nyx.cristiantala.com) | Self-hosted (Docker on VPS) | $0 |
| Prod (n8n.cristiantala.com) | Self-hosted (Docker on VPS) | $0 |
| Cloud (cristiantala.app.n8n.cloud) | n8n Cloud Starter | $20 |
| **Total** | | **$20/month** |

**vs Zapier equivalent:**
- 8,000 tasks/month on Zapier: $99/month (Team plan)
- **Savings:** $79/month = $948/year

**vs Make.com equivalent:**
- 10,000 operations/month: $79/month (Pro plan)
- **Savings:** $59/month = $708/year

---

## Workflow Examples (Code Snippets)

### Synthwave Image Generation

**n8n workflow JSON snippet:**
```json
{
  "nodes": [
    {
      "name": "Replicate API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.replicate.com/v1/predictions",
        "method": "POST",
        "authentication": "headerAuth",
        "headerParameters": {
          "parameters": [
            {
              "name": "Authorization",
              "value": "Token {{$credentials.replicateApi.apiKey}}"
            }
          ]
        },
        "jsonBody": {
          "version": "{{$json.model_version}}",
          "input": {
            "prompt": "{{$json.prompt}} synthwave cyberpunk neon",
            "width": 1216,
            "height": 640,
            "num_outputs": 1
          }
        }
      }
    },
    {
      "name": "Poll Completion",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 30,
        "unit": "seconds"
      }
    },
    {
      "name": "Download Image",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$json.output[0]}}",
        "method": "GET",
        "responseFormat": "file"
      }
    }
  ]
}
```

---

### Late API Scheduling

**n8n Function node:**
```javascript
// Input: WordPress post data
const post = $input.item.json;

// Calculate publish time (tomorrow 9 AM Santiago time)
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
tomorrow.setHours(9, 0, 0, 0);

const lateApiPayload = {
  accountId: "697a4c1177637c5c857ca4b4", // Tala LinkedIn
  scheduledAt: tomorrow.toISOString(),
  post: {
    text: `${post.title}\n\n${post.excerpt}\n\nLee más: ${post.link}`,
    media: [
      {
        url: post.featured_image,
        type: "image"
      }
    ]
  }
};

return { json: lateApiPayload };
```

---

## Next Steps

1. **Workflow library** — Document all 20+ workflows with screenshots
2. **Version control** — Export workflows to git (backup + collaboration)
3. **Monitoring dashboard** — Track execution success rate, failure patterns
4. **Community templates** — Share workflows for common use cases

---

## Takeaway

**n8n isn't just "no-code Zapier"—it's a programmable automation platform.**

Self-hosting saved $79-99/month. Code nodes enabled complex logic Zapier can't handle. OpenClaw integration turned workflows into intelligent agents.

**The result:** 15 hours/week saved, $948/year cost reduction, infinite flexibility.
