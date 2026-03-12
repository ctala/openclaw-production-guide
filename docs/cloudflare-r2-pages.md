# Cloudflare R2 + Pages as CDN and Hosting

> Zero-cost CDN and hosting using Cloudflare's free tier. Production-ready for assets, landings, and tools.

---

## Overview

Cloudflare R2 + Pages replace traditional CDN + hosting setups at $0/month for most use cases. This guide covers production setup based on running `assets.cristiantala.com` and `lp.cristiantala.com`.

**What this solves:**
- Hosting static assets (images, documents, tools) without S3/EC2 costs
- Deploying landing pages without WordPress overhead
- Serving files globally with CDN performance at free tier

---

## 1. R2 Setup

### Create Bucket

1. Cloudflare Dashboard → R2 → Create Bucket
2. Name: `assets-cristiantala` (use DNS-safe names)
3. Location: auto (or closest to your primary audience)
4. Default encryption: enabled

### Enable Public Access

R2 buckets are private by default. Two options:

**Option A: Custom domain (recommended)**
```
R2 Bucket Settings → Public Access → Connect Domain
Domain: assets.cristiantala.com
```

Creates a Cloudflare-managed public access point. Files at `assets.cristiantala.com/path/file` are publicly accessible.

**Option B: r2.dev subdomain (development)**
```
Enable R2.dev subdomain in bucket settings
URL: https://pub-[hash].r2.dev
```
Use for development. Don't use r2.dev for production (no cache control, no custom headers).

### Directory Structure

```
assets.cristiantala.com/
├── social/
│   ├── linkedin/          ← LinkedIn post images
│   ├── instagram/         ← Instagram post images
│   └── twitter/           ← Twitter card images
├── blog/
│   ├── cristiantala/      ← cristiantala.com featured images
│   └── ecosistema/        ← ecosistemastartup.com images
├── podcast/               ← Episode artwork, audio (if needed)
├── documents/
│   ├── tools/             ← Markdown to Skool converter, etc.
│   └── cheatsheets/       ← Lead magnet downloads
└── tools/
    └── *.zip              ← WordPress plugin zips
```

---

## 2. Upload Script

**Location:** `~/clawd/scripts/upload-to-r2.sh`

```bash
#!/bin/bash
# upload-to-r2.sh - Upload file to R2 and return CDN URL
# Usage: bash upload-to-r2.sh <file> <destination-path>
# Example: bash upload-to-r2.sh avatar.webp social/linkedin/

set -e

FILE="$1"
DEST_PATH="$2"
BUCKET="assets-cristiantala"
CDN_BASE="https://assets.cristiantala.com"

if [ -z "$FILE" ] || [ -z "$DEST_PATH" ]; then
  echo "Usage: $0 <file> <destination-path>"
  exit 1
fi

FILENAME=$(basename "$FILE")

# Upload via wrangler (Cloudflare CLI)
wrangler r2 object put "${BUCKET}/${DEST_PATH}${FILENAME}" \
  --file "$FILE" \
  --remote

echo ""
echo "✅ Uploaded: ${CDN_BASE}/${DEST_PATH}${FILENAME}"
```

**Prerequisites:**
```bash
npm install -g wrangler
wrangler login  # Authenticates with Cloudflare account
```

**Usage:**
```bash
bash ~/clawd/scripts/upload-to-r2.sh post-image.jpg blog/cristiantala/
# Output: https://assets.cristiantala.com/blog/cristiantala/post-image.jpg

bash ~/clawd/scripts/upload-to-r2.sh lean-ctas-v2.1.0.zip tools/
# Output: https://assets.cristiantala.com/tools/lean-ctas-v2.1.0.zip
```

### Alternative: wrangler direct

```bash
# Direct wrangler upload (no script)
wrangler r2 object put assets-cristiantala/social/linkedin/image.jpg \
  --file ./image.jpg \
  --remote

# List bucket contents
wrangler r2 object list assets-cristiantala --remote

# Delete object
wrangler r2 object delete assets-cristiantala/social/linkedin/old-image.jpg --remote
```

---

## 3. Cloudflare Pages Deployment

### Initial Setup

1. Cloudflare Dashboard → Pages → Create Application
2. Connect to GitHub → Select repository (`ctala/landings-tala`)
3. Build settings:
   - Framework preset: None (static HTML)
   - Build command: (empty — no build step for pure HTML)
   - Build output directory: `/` (root)
4. Deploy

### Deploy on Push (Automatic)

After initial setup, every `git push` to `main` triggers deployment:

```
git add .
git commit -m "Update hero copy"
git push origin main
# → Cloudflare Pages detects push → builds → deploys
# → Live at lp.cristiantala.com in ~30 seconds
```

### Branch Previews

Non-main branches create preview URLs automatically:

```bash
git checkout -b feature/new-cta
# Edit files...
git push origin feature/new-cta
# → Preview URL: https://feature-new-cta.landings-tala.pages.dev
```

Use for: copy testing, design reviews, stakeholder feedback before production merge.

---

## 4. Custom Domains + DNS

### Setup Custom Domain on Pages

1. Pages Project → Custom Domains → Set up a custom domain
2. Enter: `lp.cristiantala.com`
3. Cloudflare adds CNAME automatically (since DNS is managed in same account)

### DNS Records Created Automatically

```
CNAME lp → landings-tala.pages.dev (proxied)
```

**Important:** Domain must be on Cloudflare DNS for automatic SSL. External DNS requires manual CNAME + certificate verification.

### Subdomain Strategy

```
cristiantala.com      → WordPress (existing)
assets.cristiantala.com → R2 CDN (custom domain on bucket)
lp.cristiantala.com   → Cloudflare Pages (landing pages)
n8n.cristiantala.com  → n8n production
listmonk.nyx.cristiantala.com → Listmonk
```

---

## 5. Cache Headers

### `_headers` File for Pages

Create `_headers` in repo root to control HTTP headers:

```
# _headers (Cloudflare Pages cache control)

# CSS, JS, fonts: 1 year immutable
/style.css
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=31536000, immutable

/*.woff2
  Cache-Control: public, max-age=31536000, immutable

# Images: 1 year immutable (use cache-busting filenames for updates)
/*.webp
  Cache-Control: public, max-age=31536000, immutable

/*.jpg
  Cache-Control: public, max-age=31536000, immutable

/*.png
  Cache-Control: public, max-age=31536000, immutable

# HTML: 5 minutes (frequent content updates)
/*.html
  Cache-Control: public, max-age=300

# API responses: no cache
/api/*
  Cache-Control: no-cache, no-store
```

### Cache Busting Strategy

For immutable assets (1-year cache), use filename versioning:

```html
<!-- Instead of: -->
<link rel="stylesheet" href="style.css">

<!-- Use: -->
<link rel="stylesheet" href="style.css?v=2.1">
<!-- Or filename versioning: -->
<link rel="stylesheet" href="style-v2.1.css">
```

When you update the CSS, change the version → browsers fetch fresh copy.

---

## 6. Cost Comparison

### R2 vs S3

| Feature | Cloudflare R2 | AWS S3 |
|---------|---------------|--------|
| Storage | $0 first 10GB, then $0.015/GB | $0.023/GB |
| Egress (download) | **$0** | $0.09/GB (to internet) |
| PUT requests | $0 first 1M/month | $0.005/1K |
| GET requests | $0 first 10M/month | $0.0004/1K |
| Custom domain | Included | CloudFront extra |

**The killer feature:** R2 charges $0 for egress. S3 charges $0.09/GB for outbound traffic. For a CDN serving images, egress dominates cost. R2 is dramatically cheaper for media-heavy sites.

**Break-even:** R2 is cheaper than S3 at any bandwidth level due to $0 egress.

### Cloudflare Pages vs Traditional Hosting

| Feature | Cloudflare Pages | Traditional Hosting |
|---------|-----------------|---------------------|
| Monthly cost | $0 (free tier) | $5-15/month |
| Builds/month | 500 | N/A |
| Bandwidth | Unlimited | Typically 100GB+ |
| SSL | Automatic | Manual or Let's Encrypt |
| CDN | Global (Cloudflare) | Optional (extra cost) |
| Deploy time | ~30 seconds | 2-10 minutes |
| Preview URLs | Automatic per branch | Manual setup |

**Annual savings vs traditional hosting:** $60-$180/year for simple landing pages.

---

## 7. Use Cases

### Assets (R2)

| Use Case | Path | Example |
|----------|------|---------|
| Blog featured images | `blog/cristiantala/*.jpg` | `assets.cristiantala.com/blog/cristiantala/post-slug.jpg` |
| LinkedIn post images | `social/linkedin/*.jpg` | Synthwave-style graphics |
| Lead magnet PDFs | `documents/cheatsheets/*.pdf` | LinkedIn algorithm cheatsheets |
| WordPress plugin zips | `tools/*.zip` | `lean-ctas-v2.1.0.zip` |
| HTML tools | `documents/tools/*.html` | Markdown-to-Skool converter |

### Landings (Cloudflare Pages)

| Use Case | Path | Description |
|----------|------|-------------|
| Link in Bio | `/` | Central hub for all social profiles |
| Lead magnets | `/linkedin-cheatsheets/` | Download page with email capture |
| Event pages | `/webinar-2026-03/` | Time-limited landing pages |
| Product pages | `/lean-ctas/` | Plugin landing page |

### When NOT to Use Static Pages

- Dynamic content that changes per user (use WordPress or server-rendered)
- Pages with real-time data (use server-side rendering)
- Complex forms with server validation (consider Cloudflare Workers)
- Authentication-gated content (not for static)

---

## 8. Troubleshooting

### CORS Errors on API Calls from Pages

```
Access to fetch at 'https://listmonk.nyx.cristiantala.com/api/subscriptions' 
from origin 'https://lp.cristiantala.com' has been blocked by CORS policy
```

**Fix:** Add to reverse proxy config (Caddy example):
```
header Access-Control-Allow-Origin "https://lp.cristiantala.com"
header Access-Control-Allow-Origin "https://landings-tala.pages.dev"
header Access-Control-Allow-Methods "POST, GET, OPTIONS"
header Access-Control-Allow-Headers "Content-Type"
```

Also add branch preview URL (`*.pages.dev`) for testing.

### Cache Not Updating After Deploy

Cloudflare Pages purges cache automatically on deploy. If changes aren't visible:

```bash
# Manual cache purge via Cloudflare dashboard
# Or via API:
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything":true}'
```

### R2 Object Not Publicly Accessible

Check:
1. Custom domain connected to bucket (not just r2.dev)
2. Cloudflare proxy enabled for the custom domain CNAME
3. No bucket-level access policy blocking public reads

---

## Related Resources

- [Case 13: Cloudflare Pages Landings](../cases/13-cloudflare-pages-landings.md) — Production case study
- [Case 11: WordPress Plugin Pipeline](../cases/11-wordpress-plugin-pipeline.md) — R2 for plugin distribution
- `scripts/upload-to-r2.sh` — Upload helper script

---

*Last updated: 2026-03-12 | Version: 1.2.0*
