# Infrastructure Lessons from Production

> Hard-won lessons from running OpenClaw on a VPS with WordPress on multiple hosting providers. All from real incidents.

---

## Overview

Infrastructure issues don't follow a schedule. This document captures the actual incidents, root causes, and fixes from running `clawdbot.service` on srv1301687 and managing WordPress sites across three hosting providers.

**Timeline of incidents covered:**
- Mar 5, 2026: Hostinger filesystem read-only remount
- Mar 9, 2026: `clawdbot.service` disabled silently
- Ongoing: SSH access hell across WPMU DEV, Rocket.net, Hostinger

---

## 1. Hostinger Filesystem Crisis (March 5, 2026)

### What Happened

At approximately 14:30 Chile time, OpenClaw stopped being able to write to disk. All file operations — saving memory, updating MEMORY.md, writing daily logs — failed with:

```
Error: EROFS: read-only file system, open '~/openclaw-workspace/memory/2026-03-05.md'
```

The service was still running. Session responses worked. But nothing could be written.

### Root Cause

Hostinger VPS filesystem was remounted as read-only by the kernel after detecting I/O errors on the underlying storage. This is a Linux kernel self-protection mechanism — when disk errors are detected, the filesystem switches to read-only to prevent data corruption.

```bash
# Confirm the issue:
mount | grep " / "
# Output: /dev/vda1 on / type ext4 (ro,relatime)  ← 'ro' = read-only
```

### Temporary Fix (Emergency)

```bash
# Remount filesystem as read-write
sudo mount -o remount,rw /

# Verify:
mount | grep " / "
# Output: /dev/vda1 on / type ext4 (rw,relatime)  ← 'rw' = read-write
```

**⚠️ This is a temporary fix.** The kernel switched to read-only for a reason. This fix reverts until the next I/O error or reboot.

### Permanent Investigation

```bash
# Check kernel logs for I/O errors
dmesg | grep -i "error\|fail\|corrupt" | tail -50

# Check filesystem errors
sudo fsck -n /dev/vda1  # -n = dry run, no actual changes

# Check SMART data (disk health)
sudo smartctl -a /dev/vda1
```

**What we found:** Multiple I/O read errors on the virtual disk. Root cause was a host-side storage issue on Hostinger's infrastructure (not our fault). Hostinger support resolved within 24 hours after ticket submission.

### Monitoring Recommendation

Add a filesystem health check to the nightly cron:

```bash
#!/bin/bash
# fs-health-check.sh

MOUNT_STATUS=$(mount | grep " / " | grep -c "rw")

if [ "$MOUNT_STATUS" -eq 0 ]; then
    # Filesystem is read-only — alert immediately
    curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" \
      -d "text=🚨 CRITICAL: Filesystem is READ-ONLY. Run: sudo mount -o remount,rw /"
fi
```

Run every 5 minutes. Alert is worth the cost.

---

## 2. `clawdbot.service` Disabled Silently (March 9, 2026)

### What Happened

OpenClaw heartbeats stopped at approximately 08:15. No error, no alert — just silence. By 10:30 (2+ hours later), it was noticed manually.

Investigation:

```bash
systemctl status clawdbot.service
# Output: 
# ● clawdbot.service - OpenClaw Agent
#    Loaded: loaded (/etc/systemd/system/clawdbot.service; disabled; vendor preset: enabled)
#    Active: inactive (dead)
```

**The service was disabled.** Not failed — disabled. `enabled → disabled` change.

### Root Cause

A system package update ran via `unattended-upgrades` and rebooted the server. After reboot, the service was `disabled` — meaning it was listed in systemd but not configured to start on boot.

The initial setup had been done with:
```bash
systemctl start clawdbot.service  # starts now
# Missing: systemctl enable clawdbot.service  # start on boot
```

The service ran, but wasn't enabled for automatic restart. First reboot = silent death.

### Fix

```bash
# Enable service to start on boot
sudo systemctl enable clawdbot.service

# Start it now
sudo systemctl start clawdbot.service

# Verify
sudo systemctl status clawdbot.service
# Should show: enabled, active (running)
```

### Full Service Check Command

```bash
# Complete status check
systemctl is-enabled clawdbot.service  # Should output: enabled
systemctl is-active clawdbot.service   # Should output: active
systemctl show clawdbot.service --property=ExecStart  # Shows startup command
```

### Monitoring Recommendation

Add heartbeat verification: if no heartbeat in 60 minutes → alert. This catches service failures before 2+ hours of silence.

```
# n8n workflow: check last heartbeat timestamp in NocoDB
# If now() - last_heartbeat > 60min → Telegram alert
```

---

## 3. SSH Access Across Hosting Providers

### The Problem

Three different WordPress hosts, three different SSH configurations. Nothing is standardized.

### WPMU DEV (ecosistemastartup.com)

**SSH host format:** NOT the domain. Uses a temporary host URL.

```bash
# WRONG - doesn't work
ssh user@ecosistemastartup.com

# CORRECT - uses WPMU DEV's temporary host
ssh user@esup.tempurl.host -p [port-from-panel]
```

**Finding the host:**
1. WPMU DEV Hub → Sites → ecosistemastartup.com → SSH/SFTP
2. Look for "SSH Address" — it will be something like `esup.tempurl.host:22`
3. This address can change if you reset SSH credentials

**IP whitelisting:**
- Required: Go to SSH settings → Whitelist IP
- Must whitelist the VPS IP (not your laptop)
- For agent automation: whitelist srv1301687's IP

**Key file:**
```bash
ssh -i ~/.ssh/wpmu_key user@esup.tempurl.host -p 22
```

### Rocket.net (cristiantala.com)

**SSH host format:** The server IP or custom SSH host (not the domain).

```bash
# From Rocket.net dashboard → SSH/SFTP settings
ssh cristiantala@[server-ip] -p 22
```

**IP whitelisting:**
- Rocket.net requires IP whitelist for SSH (security by default)
- Whitelist: Dashboard → Security → SSH Whitelist → Add IP
- Add srv1301687's IP for automated access

**SFTP (alternative to SSH):**
```bash
lftp sftp://user:[password]@[server-ip]:22
# Or
scp -i ~/.ssh/rocket_key file.php user@[server-ip]:/htdocs/wp-content/plugins/lean-ctas/
```

### Hostinger

**SSH port:** 65002 (non-standard)

```bash
# Standard port 22 DOESN'T work
ssh user@srv1301687.hstgr.cloud -p 65002

# Or with SSH config:
# Host hostinger-vps
#   HostName srv1301687.hstgr.cloud
#   Port 65002
#   User clawd-user
#   IdentityFile ~/.ssh/hostinger_key
```

### SSH Config File (Recommended Setup)

Maintain `~/.ssh/config` for all providers:

```
# ~/.ssh/config

Host vps-main
  HostName srv1301687.hstgr.cloud
  Port 65002
  User clawd-user
  IdentityFile ~/.ssh/hostinger_key
  ServerAliveInterval 60

Host cristiantala-rocket
  HostName [server-ip-from-rocket]
  Port 22
  User cristiantala
  IdentityFile ~/.ssh/rocket_key
  ServerAliveInterval 60

Host ecosistema-wpmu
  HostName esup.tempurl.host
  Port 22
  User [wpmu-user]
  IdentityFile ~/.ssh/wpmu_key
  ServerAliveInterval 60
```

**Benefits:**
- `ssh vps-main` instead of remembering port + key + host
- `scp file.php cristiantala-rocket:/htdocs/plugins/` for simple deploys
- `ServerAliveInterval` prevents SSH timeouts during long operations

---

## 4. PHP Version Mismatches

### The Problem

WordPress hosting increasingly runs PHP 8.x for web requests, but WP-CLI often defaults to the system PHP which may be 7.4.

```bash
$ wp --info
PHP binary: /usr/bin/php
PHP version: 7.4.33

# But the site runs 8.3!
```

Running WP-CLI with wrong PHP version causes:
- Plugin activation failures (PHP 8.x syntax in plugins)
- Database migration errors
- Inconsistent behavior between CLI and web

### Fix: Specify PHP Path Explicitly

```bash
# Method 1: Explicit PHP binary
/usr/local/php83/bin/php $(which wp) plugin activate lean-ctas

# Method 2: WP-CLI config file (per-site)
# Create: /path/to/site/wp-cli.yml
php: /usr/local/php83/bin/php

# Method 3: Shell alias
alias wp83='/usr/local/php83/bin/php /usr/local/bin/wp'
wp83 plugin list
```

### Finding the Correct PHP Binary

```bash
# List available PHP versions
ls /usr/local/php*/bin/php 2>/dev/null
ls /usr/bin/php* 2>/dev/null

# Check which PHP the web server uses
grep -r "php_version" /etc/apache2/ 2>/dev/null
grep -r "php" /etc/nginx/conf.d/ 2>/dev/null

# On cPanel/WPMU DEV:
# Check the Site PHP version in the control panel
# Match that version for WP-CLI
```

### Hostinger Specific

```bash
# Hostinger PHP paths
/usr/local/php74/bin/php  # 7.4
/usr/local/php80/bin/php  # 8.0
/usr/local/php81/bin/php  # 8.1
/usr/local/php82/bin/php  # 8.2
/usr/local/php83/bin/php  # 8.3 (recommended for new sites)
```

---

## 5. WP-CLI Across Hosting Environments

### Common WP-CLI Commands for Plugin Management

```bash
# Check plugin status
wp plugin status lean-ctas

# Activate/deactivate
wp plugin activate lean-ctas
wp plugin deactivate lean-ctas

# Update plugin
wp plugin update lean-ctas

# Install from URL (R2 CDN zip)
wp plugin install https://assets.cristiantala.com/tools/lean-ctas-v2.1.0.zip --activate

# List all plugins with version
wp plugin list --format=table

# Check if plugin is network-activated (multisite)
wp plugin get lean-ctas --format=json
```

### REST API as WP-CLI Fallback

When WP-CLI isn't available or SSH is blocked:

```bash
# Install plugin from URL
curl -X POST https://cristiantala.com/wp-json/wp/v2/plugins \
  -H "Authorization: Basic $(echo -n 'user:app-password' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"slug": "lean-ctas", "status": "active"}'

# List installed plugins
curl -X GET https://cristiantala.com/wp-json/wp/v2/plugins \
  -H "Authorization: Basic $(echo -n 'user:app-password' | base64)"

# Get plugin info
curl -X GET "https://cristiantala.com/wp-json/wp/v2/plugins/lean-ctas" \
  -H "Authorization: Basic $(echo -n 'user:app-password' | base64)"
```

**Prerequisite:** Application Passwords must be enabled (WP 5.6+, Settings → Users → Application Passwords).

---

## 6. Monitoring Recommendations

### What to Monitor (Priority Order)

| Check | Frequency | Alert Threshold | Method |
|-------|-----------|-----------------|--------|
| `clawdbot.service` status | Every 5 min | Not running | `systemctl is-active` + Telegram |
| Filesystem read/write | Every 5 min | Read-only | `mount | grep rw` |
| Disk space | Every 30 min | >80% full | `df -h` |
| OpenClaw heartbeat | Every 15 min | >30 min silence | n8n check last heartbeat |
| WordPress site availability | Every 10 min | HTTP != 200 | curl check |
| Memory/CPU | Every 60 min | >90% sustained | `top` snapshot |

### Minimal Monitoring Setup

```bash
#!/bin/bash
# health-check.sh — Run via cron every 5 minutes

TELEGRAM_TOKEN="..."
CHAT_ID="..."

send_alert() {
    curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" \
      -d "text=🚨 $1"
}

# Check clawdbot service
if ! systemctl is-active --quiet clawdbot.service; then
    send_alert "clawdbot.service is NOT running! Check: systemctl status clawdbot.service"
fi

# Check filesystem is writable
if ! touch /tmp/fs-write-test 2>/dev/null; then
    send_alert "Filesystem appears READ-ONLY! Run: sudo mount -o remount,rw /"
fi
rm -f /tmp/fs-write-test

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 85 ]; then
    send_alert "Disk usage at ${DISK_USAGE}%! Clean up space."
fi
```

Add to cron:
```
*/5 * * * * ~/openclaw-workspace/scripts/health-check.sh
```

---

## 7. Quick Reference

### Emergency Commands

```bash
# Fix read-only filesystem
sudo mount -o remount,rw /

# Restart OpenClaw service
sudo systemctl restart clawdbot.service

# Enable service to start on boot (RUN THIS AFTER INITIAL SETUP)
sudo systemctl enable clawdbot.service

# Check service logs
journalctl -u clawdbot.service -n 100 --no-pager

# Check all disk errors since boot
dmesg | grep -iE "error|fail|corrupt" | tail -30
```

### Service Management Checklist (After Initial Setup)

- [ ] `systemctl enable clawdbot.service` (survive reboots!)
- [ ] `systemctl start clawdbot.service`
- [ ] `systemctl is-enabled clawdbot.service` → should show `enabled`
- [ ] Test reboot: `sudo reboot`, then check service is running
- [ ] Set up monitoring cron for service health

---

## Related Resources

- [Case 7: Infrastructure (Docker + Caddy)](../cases/07-infrastructure-docker-caddy.md) — Server setup
- [Case 11: WordPress Plugin Pipeline](../cases/11-wordpress-plugin-pipeline.md) — SSH per-provider details
- [docs/memory-management.md](memory-management.md) — Memory flush after incidents

---

*Last updated: 2026-03-12 | Version: 1.2.0*
