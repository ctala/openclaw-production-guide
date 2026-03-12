# Case 11: WordPress Plugin Development and Deployment Pipeline

> **From local dev to live on two sites (and WordPress.org pending): how to build and ship WP plugins without SSH nightmares**

**Problem:** Building a WordPress plugin is easy. Deploying it across multiple hosting providers—each with different SSH configs, PHP versions, and security restrictions—is a production operations challenge.

**Solution:** Standardized pipeline: local dev → GitHub versioning → R2 CDN distribution → SFTP/REST API deployment → WP-CLI configuration.

**Result:** Two production plugins (Lean Redirects + Lean CTAs) deployed to two sites, WordPress.org submission in progress, $0 deployment cost.

---

## 🎯 The Problem: Multi-Host Deployment Chaos

**Context:** cristiantala.com (Rocket.net) + ecosistemastartup.com (WPMU DEV) — two WordPress sites on different hosting providers.

**Pain points:**
1. **SSH access varies wildly** — WPMU DEV uses custom temporary hosts (`esup.tempurl.host`), Rocket.net requires IP whitelisting for SSH
2. **PHP version mismatches** — WP-CLI defaults to PHP 7.4, but the web server runs 8.3 — plugins must specify PHP path explicitly
3. **Plugin function name collisions** — `get_settings()` conflicts with WordPress core functions
4. **Distribution friction** — Sending a zip file over email/Slack to install manually = unsustainable
5. **WordPress.org submission** — Requires DNS verification, ABSPATH guards, Plugin Check tool compliance

**The goal:** Build once, deploy anywhere, with a reproducible pipeline.

---

## ✅ The Solution: Standardized Plugin Pipeline

### Pipeline Overview

```
1. Develop locally
   ~/openclaw-workspace/lean-ctas/
   ~/openclaw-workspace/lean-redirects/
   ↓
2. Version with GitHub tags
   git tag v2.1.0 && git push origin v2.1.0
   ↓
3. Build zip + upload to R2 CDN
   assets.cristiantala.com/tools/lean-ctas-v2.1.0.zip
   ↓
4. Deploy (method depends on host)
   ├── Rocket.net: SFTP (IP whitelisted)
   ├── WPMU DEV: REST API (wp-json/wp/v2/plugins)
   └── Any host: wp-admin Upload Plugin (from CDN URL)
   ↓
5. Configure via WP REST API
   POST /wp-json/lean-ctas/v1/settings
   ↓
6. WordPress.org submission
   svn commit → plugin directory
```

---

## 🔧 Tech Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Local dev | `~/openclaw-workspace/lean-ctas/` | PHP + standard WP plugin structure |
| Version control | GitHub (`ctala/lean-ctas`, `ctala/lean-redirects`) | Tags = releases |
| Distribution | Cloudflare R2 (`assets.cristiantala.com/tools/`) | CDN-hosted zips, free tier |
| Deployment (SSH) | SFTP via `lftp` or `scp` | Rocket.net (IP whitelisted) |
| Deployment (API) | WP REST API `wp-json/wp/v2/plugins` | WPMU DEV fallback |
| WP management | WP-CLI | Config, activation, plugin management |
| Quality check | Plugin Check (PCP) | WordPress.org submission compliance |
| Directory | WordPress.org SVN | Public distribution |

---

## 📋 The Two Plugins Built

### Plugin 1: Lean Redirects

**Purpose:** Simple 301/302 redirect manager without the bloat of Redirection or Yoast.

**Why build it?** Every major redirect plugin has 50+ features. We needed: source URL → destination URL → status code. That's it.

**Features:**
- Admin table: source → destination → status code → active toggle
- Custom DB table for performance (no options table bloat)
- REST API endpoint for programmatic management
- Import/export CSV

**Plugin header:**
```php
/**
 * Plugin Name: Lean Redirects
 * Description: Lightweight redirect manager. Just source → destination → status code.
 * Version: 1.0.0
 * Author: Cristian Tala
 * License: GPL v2 or later
 */

if ( ! defined( 'ABSPATH' ) ) exit; // CRITICAL: Security guard
```

### Plugin 2: Lean CTAs

**Purpose:** Dynamic calls-to-action per post category, with custom colors and tracking.

**Why build it?** cristiantala.com has 5 content pillars (Tech, Startups, Business, AI, Personal) — each needs different CTAs. Existing solutions are either too complex or require specific page builders.

**Features:**
- Admin panel: assign CTA per category (title, text, button, URL, color)
- Automatic injection after paragraph 3 + end of post
- REST API for programmatic config (colors, text per category)
- WP-CLI support for bulk configuration
- Analytics tracking (click count per CTA)

**Category → CTA mapping:**
```json
{
  "434": { "title": "¿Automatizando tu negocio?", "color": "#00ff88", "cta": "Únete a la comunidad" },
  "916": { "title": "¿Lanzando una startup?", "color": "#ff6600", "cta": "Habla con Cristian" },
  "1204": { "title": "¿Escalando tu empresa?", "color": "#0066ff", "cta": "Ver inversiones" },
  "1205": { "title": "¿Implementando IA?", "color": "#cc00ff", "cta": "Explorar automatización" },
  "116":  { "title": "Conectemos", "color": "#ff0066", "cta": "Escríbeme en LinkedIn" }
}
```

---

## 🧠 Critical Lessons

### Lesson 1: NEVER Use Unprefixed Function Names

**The bug that cost 2 hours:**

```php
// WRONG - collides with WordPress core
function get_settings() {
    return get_option('lean_ctas_settings', []);
}

// ERROR: PHP Fatal error - Cannot redeclare get_settings()
// WordPress has its own get_settings() in wp-admin/includes/misc.php
```

**The fix:**
```php
// CORRECT - always prefix with plugin name
function lean_ctas_get_settings() {
    return get_option('lean_ctas_settings', []);
}

// Also applies to: classes, hooks, constants, REST routes
add_action('rest_api_init', 'lean_ctas_register_routes');
define('LEAN_CTAS_VERSION', '2.1.0');
```

**Rule:** Every function, class, constant, and hook in a WordPress plugin must be prefixed. No exceptions.

### Lesson 2: ABSPATH Guard Is Not Optional

```php
<?php
// FIRST LINE of every PHP file (after opening tag)
if ( ! defined( 'ABSPATH' ) ) {
    exit; // Prevent direct file access
}
```

Without this, any PHP file in your plugin can be accessed directly via URL, bypassing WordPress's security layer. WordPress.org submission will reject your plugin without it.

### Lesson 3: WP-CLI PHP Version Mismatch Will Break Deployments

**The problem:**
```bash
$ wp plugin activate lean-ctas
Error: This script requires a minimum PHP version of 8.0. You are running PHP 7.4.

# But the site runs PHP 8.3 in the browser. What?
```

**Root cause:** WP-CLI on shared hosting often uses the system PHP (7.4), not the web PHP (8.3).

**Fix:**
```bash
# Specify PHP binary explicitly
$ /usr/local/php83/bin/php $(which wp) plugin activate lean-ctas

# Or set in wp-cli.yml
php: /usr/local/php83/bin/php
```

**Lesson:** Always check `wp --info` output and compare `php_binary` with the server's web PHP version. If they differ, use explicit PHP path in all WP-CLI commands.

### Lesson 4: SSH Access Varies Wildly by Host

**Rocket.net:**
- SSH enabled by default
- Requires IP whitelisting (server-side setting in dashboard)
- Port: 22 (standard)
- Works with standard `ssh user@host -p 22`
- **Gotcha:** Your VPS IP must be whitelisted — not your laptop IP

**WPMU DEV:**
- SSH host is a temporary URL (not the domain): `esup.tempurl.host`
- Port may be non-standard (check hosting panel)
- IP whitelisting also required
- The temporary host changes if you reset SSH credentials

**Hostinger:**
- Standard SSH, port 65002 (non-standard)
- IP whitelisting in hPanel

**Lesson:** Never hardcode SSH hosts. Keep a config file:
```bash
# ~/.ssh/config
Host cristiantala-rocket
  HostName [whitelisted-ip-or-host]
  User [username]
  Port 22
  IdentityFile ~/.ssh/rocket_key

Host ecosistema-wpmu
  HostName esup.tempurl.host
  User [username]
  Port [port-from-panel]
  IdentityFile ~/.ssh/wpmu_key
```

### Lesson 5: REST API as Fallback When SSH Is Blocked

When SSH is unavailable (IP not whitelisted, blocked by firewall), WP REST API can install plugins:

```bash
# Install plugin from URL via REST API (WordPress 5.5+)
curl -X POST https://site.com/wp-json/wp/v2/plugins \
  -H "Authorization: Basic $(echo -n 'user:app-password' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"slug": "lean-ctas", "status": "active"}'

# For custom plugins (not in directory), upload zip:
curl -X POST https://site.com/wp-json/wp/v2/plugins \
  -H "Authorization: Basic $(echo -n 'user:app-password' | base64)" \
  -F "file=@lean-ctas-v2.1.0.zip"
```

**Prerequisite:** Application Passwords enabled (Settings → Users → Application Passwords in WP 5.6+).

### Lesson 6: Run Plugin Check (PCP) Before WordPress.org Submission

**Plugin Check** is an official WordPress tool that catches issues before submission:

```bash
# Install PCP plugin, then:
wp plugin check lean-ctas

# Common issues caught:
# - Unprefixed function names
# - Missing ABSPATH guards
# - Direct DB queries without wpdb->prepare()
# - Enqueue scripts without version parameter
# - Missing nonce verification in form handlers
# - Incorrect license headers
```

**Our PCP results:**
- 14 warnings on first run
- 0 warnings after fixes
- Submission accepted (pending review queue)

### Lesson 7: R2 as Plugin Distribution Channel

Instead of emailing zips or storing in git:

```bash
# Build zip
cd ~/openclaw-workspace/lean-ctas
zip -r lean-ctas-v2.1.0.zip lean-ctas/ --exclude "*.git*" --exclude "node_modules/*"

# Upload to R2
bash ~/clawd/scripts/upload-to-r2.sh lean-ctas-v2.1.0.zip tools/

# Result: https://assets.cristiantala.com/tools/lean-ctas-v2.1.0.zip
```

**Benefits:**
- Shareable URL (anyone can install from wp-admin → Upload Plugin)
- CDN-delivered (fast download worldwide)
- Versioned (each release has unique URL)
- Free (R2 free tier is generous)
- No GitHub releases setup needed

### Lesson 8: WordPress.org Requires DNS TXT Verification

To prove plugin ownership for WordPress.org, you must add a TXT record:

```
TXT @ "wordpress-plugin-verification=lean-ctas-abc123xyz"
```

This is not documented prominently — it shows up during submission. Cloudflare DNS makes this trivial (add record, propagates in seconds).

---

## 📋 Deployment Checklist

### Before First Deploy
- [ ] All functions prefixed with plugin name
- [ ] ABSPATH guard in every PHP file
- [ ] Plugin Check (PCP) shows 0 errors
- [ ] Version number in plugin header + `define('PLUGIN_VERSION', '...')`
- [ ] `readme.txt` in WordPress.org format (Stable tag, changelog, screenshots)
- [ ] Test on local with PHP 8.3 (not 7.4)

### For Each Release
- [ ] Update version in plugin header + constant
- [ ] Update readme.txt changelog
- [ ] `git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Build zip + upload to R2
- [ ] Deploy via SFTP or REST API (method per host)
- [ ] Verify plugin active via WP-CLI: `wp plugin status lean-ctas`
- [ ] Test core functionality (redirect works, CTA appears)
- [ ] Update SVN (WordPress.org): `svn commit -m "Release vX.Y.Z"`

---

## 📊 Results

| Metric | Result |
|--------|--------|
| Plugins built | 2 (Lean Redirects, Lean CTAs) |
| Sites deployed | 2 (cristiantala.com, ecosistemastartup.com) |
| Development time (each plugin) | 4-6 hours (from scratch) |
| Deployment time (after setup) | < 5 minutes per site |
| WP-CLI issues resolved | 3 (PHP mismatch, function collision, ABSPATH) |
| Plugin Check warnings fixed | 14 → 0 |
| WordPress.org submission | Pending review queue |
| Ongoing cost | $0/month |

**Version history (Lean CTAs):**
- v1.0.0: Basic CTA injection by category
- v1.1.0: Added REST API for config
- v2.0.0: Added analytics (click tracking)
- v2.1.0: WP-CLI support + PCP compliance

---

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| Development time | Sunk cost (learning counts) |
| R2 storage (zips) | ~$0/month (free tier) |
| GitHub (private repo) | $0 (free tier) |
| Hosting (no extra cost) | $0 |
| WordPress.org submission | $0 (free) |
| **Total monthly** | **$0** |

---

## 🏁 Takeaway

Building WordPress plugins is not hard. Deploying them reliably across multiple hosts with different configurations is where most people give up and revert to manual uploads.

The key wins:
1. **Standardize function naming** — prefixed everything, zero collisions
2. **R2 for distribution** — shareable URL beats emailing zips
3. **REST API fallback** — when SSH is blocked, the API works
4. **Plugin Check before submission** — catch issues before WordPress.org reviewers do

The "Lean" naming convention (Lean Redirects, Lean CTAs) reflects the philosophy: one plugin, one job, zero bloat. WordPress core has feature creep. Your plugins shouldn't.

**What's next:** WordPress.org approval → public listing → potential community contributions.

---

## 🔗 Related

- [Case 7: Infrastructure (Docker + Caddy)](07-infrastructure-docker-caddy.md) — Server infrastructure context
- [docs/infrastructure-lessons.md](../docs/infrastructure-lessons.md) — SSH and hosting provider lessons
- [configs/model-routing-rules.json](../configs/model-routing-rules.json) — Code generation uses Sonnet (not Haiku)
