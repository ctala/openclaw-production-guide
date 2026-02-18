# Case 7: Infrastructure (Docker + Caddy)

**Status:** ✅ Production (6+ months)  
**Uptime:** 99.8% (6 months avg)  
**Services Running:** 8+ containerized apps  
**SSL Certs:** Wildcard auto-renewal (Let's Encrypt)  
**Cost:** $12/month (VPS only)

---

## The Problem

Running multiple services in production requires:
- **Isolation** — Service A crash shouldn't kill Service B
- **SSL/TLS** — All services need HTTPS (Let's Encrypt)
- **Reverse Proxy** — Route domains to correct service
- **Easy Deployment** — Ship updates without downtime
- **Resource Efficiency** — Run 8+ services on 1 VPS

**Traditional approach:**
- Manual nginx config (30+ min per service)
- Separate SSL certs per domain (renewal hell)
- Services installed directly on host (dependency conflicts)
- No rollback mechanism (break it = rebuild server)

**Result:** Deployment friction → services don't get shipped.

---

## The Solution

**Docker + Caddy = Zero-config reverse proxy with auto-SSL:**

1. **Docker** — All services containerized (isolation + portability)
2. **Caddy** — Reverse proxy with automatic HTTPS (no manual config)
3. **Wildcard SSL** — One cert for `*.nyx.cristiantala.com`
4. **Cloudflare DNS** — DNS challenge for wildcard cert verification
5. **Docker Compose** — Declarative service orchestration

---

## Tech Stack

### VPS (srv1301687)
- **Provider:** Hostinger (could be any VPS provider)
- **Specs:** 4 CPU, 8 GB RAM, 200 GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Cost:** $12/month

### Docker
- **Purpose:** Service containerization
- **Version:** 24.x (Docker Engine)
- **Networking:** Bridge network (containers communicate internally)

### Caddy
- **Purpose:** Reverse proxy + SSL termination
- **Version:** 2.x
- **SSL:** Automatic Let's Encrypt via Cloudflare DNS challenge
- **Config:** `Caddyfile` (simple, declarative)

### Cloudflare
- **Purpose:** DNS management + DNS challenge for wildcard SSL
- **API Token:** Required for DNS-01 challenge (wildcard certs)

---

## Services Running

| Service | Container | Domain | Purpose |
|---------|-----------|--------|---------|
| n8n (dev) | `n8n-dev` | n8n.nyx.cristiantala.com | Workflow automation (staging) |
| Listmonk | `listmonk` | listmonk.nyx.cristiantala.com | Self-hosted newsletter platform |
| Excalidraw | `excalidraw` | draw.cristiantala.com | Diagram tool |
| NocoDB | `nocodb` | (internal) | Task/content management |
| PostgreSQL | `postgres` | (internal) | Database for Listmonk + NocoDB |
| OpenClaw | (host) | (webhook endpoints) | AI agent runtime |
| Markdown Viewer | (static) | assets.nyx.cristiantala.com/md/ | Temp document viewer |
| CDN Assets | (static) | assets.nyx.cristiantala.com | Public CDN for images/media |

**Total:** 8 services, 1 VPS, $12/month.

---

## Architecture

```
Internet
  ↓
Cloudflare DNS (*.nyx.cristiantala.com → VPS IP)
  ↓
Caddy (reverse proxy on VPS:443)
  ↓
  ├─ n8n.nyx.cristiantala.com → Docker container n8n-dev:5678
  ├─ listmonk.nyx.cristiantala.com → Docker container listmonk:9000
  ├─ draw.cristiantala.com → Docker container excalidraw:80
  └─ assets.nyx.cristiantala.com → Static files /var/www/assets/
  
PostgreSQL (Docker internal network)
  ↑
  ├─ Listmonk connects via docker network
  └─ NocoDB connects via docker network
```

---

## Caddy Configuration

**File:** `/etc/caddy/Caddyfile`

```caddyfile
# Global options
{
    email cristian@cristiantala.com
    
    # Cloudflare DNS challenge for wildcard certs
    acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}

# n8n (dev environment)
n8n.nyx.cristiantala.com {
    reverse_proxy localhost:5678
    
    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000;"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
    }
}

# Listmonk
listmonk.nyx.cristiantala.com {
    reverse_proxy localhost:9000
}

# Excalidraw
draw.cristiantala.com {
    reverse_proxy localhost:8080
}

# Assets CDN (public)
assets.nyx.cristiantala.com {
    root * /var/www/assets
    file_server browse
    
    # CORS for public assets
    header Access-Control-Allow-Origin "*"
}

# Wildcard catch-all for *.nyx.cristiantala.com
*.nyx.cristiantala.com {
    respond "Service not configured" 404
}
```

**Key features:**
- **Auto HTTPS:** Caddy requests Let's Encrypt certs automatically
- **Wildcard cert:** One cert covers all `*.nyx.cristiantala.com` subdomains
- **Zero manual renewal:** Caddy renews certs 30 days before expiry
- **Hot reload:** `caddy reload` applies config changes without downtime

---

## Docker Compose Setup

**File:** `/home/moltbot/docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL (shared database)
  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: listmonk
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

  # Listmonk
  listmonk:
    image: listmonk/listmonk:latest
    container_name: listmonk
    restart: always
    ports:
      - "9000:9000"
    depends_on:
      - postgres
    environment:
      LISTMONK_app__address: "0.0.0.0:9000"
      LISTMONK_db__host: postgres
      LISTMONK_db__port: 5432
      LISTMONK_db__user: ${POSTGRES_USER}
      LISTMONK_db__password: ${POSTGRES_PASSWORD}
      LISTMONK_db__database: listmonk
    networks:
      - internal

  # n8n (dev)
  n8n-dev:
    image: n8nio/n8n:latest
    container_name: n8n-dev
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.nyx.cristiantala.com
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.nyx.cristiantala.com/
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - internal

  # Excalidraw
  excalidraw:
    image: excalidraw/excalidraw:latest
    container_name: excalidraw
    restart: always
    ports:
      - "8080:80"
    networks:
      - internal

  # NocoDB
  nocodb:
    image: nocodb/nocodb:latest
    container_name: nocodb
    restart: always
    ports:
      - "8081:8080"
    depends_on:
      - postgres
    environment:
      NC_DB: "pg://postgres:5432?u=${POSTGRES_USER}&p=${POSTGRES_PASSWORD}&d=nocodb"
    volumes:
      - nocodb_data:/usr/app/data
    networks:
      - internal

volumes:
  postgres_data:
  n8n_data:
  nocodb_data:

networks:
  internal:
    driver: bridge
```

**Start all services:**
```bash
cd /home/moltbot/docker
docker-compose up -d
```

**Stop all services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f listmonk
```

---

## SSL Certificate Setup

### Wildcard Certificate via DNS Challenge

**Why DNS challenge?**
- HTTP challenge requires port 80 open (blocked in some VPS configs)
- DNS challenge works from anywhere
- Enables wildcard certs (`*.nyx.cristiantala.com`)

**Cloudflare API Token:**
1. Cloudflare Dashboard → API Tokens
2. Create Token → Edit Zone DNS
3. Permissions: `Zone:DNS:Edit`
4. Zone Resources: `Include:Specific zone:cristiantala.com`
5. Copy token → Set as env var

**Set token:**
```bash
export CLOUDFLARE_API_TOKEN="your_token_here"

# Make persistent
echo 'export CLOUDFLARE_API_TOKEN="your_token_here"' >> ~/.bashrc
```

**Caddy requests cert automatically:**
```bash
# First request to n8n.nyx.cristiantala.com triggers:
# 1. Caddy detects no cert exists
# 2. Requests wildcard cert from Let's Encrypt
# 3. Let's Encrypt asks for DNS TXT record proof
# 4. Caddy creates TXT record via Cloudflare API
# 5. Let's Encrypt verifies, issues cert
# 6. Caddy stores cert, serves HTTPS

# Total time: 30-60 seconds
# Manual steps: 0
```

---

## Critical Lessons

### 1. **Caddy > nginx for Small Teams**
**nginx:**
- Manual SSL cert config
- Separate certbot setup
- Cron for renewals
- Config syntax hell (`location` blocks, regex)

**Caddy:**
- SSL automatic (zero config)
- Renewal automatic (built-in)
- Config syntax: dead simple (domain → reverse_proxy)

**Setup time:**
- nginx + certbot: 30-60 min per service
- Caddy: 2 min per service

**Winner:** Caddy (unless you need nginx-specific features).

---

### 2. **Docker Networking = No Port Conflicts**
Before Docker:
- Service A needs port 5000
- Service B also needs port 5000
- **Conflict:** Can't run both

With Docker:
- Service A: `ports: "5000:5000"` (host 5000 → container 5000)
- Service B: `ports: "5001:5000"` (host 5001 → container 5000)
- Both run simultaneously, no conflict

**Bonus:** Internal communication via service name (e.g., `postgres:5432`).

---

### 3. **Wildcard Certs = One Cert, Infinite Subdomains**
Without wildcard:
- `n8n.nyx.cristiantala.com` → cert 1
- `listmonk.nyx.cristiantala.com` → cert 2
- `draw.cristiantala.com` → cert 3
- **Total:** 3 certs, 3 renewals

With wildcard:
- `*.nyx.cristiantala.com` → 1 cert
- Covers all subdomains
- **Total:** 1 cert, 1 renewal

**Savings:** 0 manual renewals (Caddy handles it).

---

### 4. **Environment Variables > Hardcoded Secrets**
**Bad:**
```yaml
environment:
  POSTGRES_PASSWORD: "my_secret_password"
```

**Good:**
```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

**Load from `.env`:**
```bash
# docker/.env
POSTGRES_USER=listmonk
POSTGRES_PASSWORD=super_secret_password
CLOUDFLARE_API_TOKEN=abc123
```

```bash
docker-compose --env-file .env up -d
```

**Why:** Secrets don't leak in git commits or logs.

---

### 5. **Resource Limits = Prevent Runaway Containers**
**Problem:** One container (e.g., n8n) consumes all RAM → kills other services.

**Solution:** Set resource limits in `docker-compose.yml`:
```yaml
services:
  n8n-dev:
    image: n8nio/n8n
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.5'
        reservations:
          memory: 512M
          cpus: '0.5'
```

**Result:** n8n maxes out at 2 GB RAM, 1.5 CPUs. Other services remain stable.

---

## Deployment Workflow

### Adding a New Service

**Example:** Add Plausible Analytics

**1. Update `docker-compose.yml`:**
```yaml
  plausible:
    image: plausible/analytics:latest
    container_name: plausible
    restart: always
    ports:
      - "8082:8000"
    environment:
      BASE_URL: https://analytics.nyx.cristiantala.com
      SECRET_KEY_BASE: ${PLAUSIBLE_SECRET}
    networks:
      - internal
```

**2. Update `Caddyfile`:**
```caddyfile
analytics.nyx.cristiantala.com {
    reverse_proxy localhost:8082
}
```

**3. Deploy:**
```bash
# Start container
docker-compose up -d plausible

# Reload Caddy (zero downtime)
caddy reload --config /etc/caddy/Caddyfile

# Verify
curl https://analytics.nyx.cristiantala.com
```

**Total time:** 5 minutes.

---

### Updating a Service

**Example:** Update n8n to latest version

```bash
# Pull latest image
docker-compose pull n8n-dev

# Restart with new image
docker-compose up -d n8n-dev

# Old container stops, new starts
# Downtime: <10 seconds
```

---

### Rollback

**If new version breaks:**
```bash
# Check available images
docker images | grep n8n

# Run specific version
docker run -d --name n8n-dev-rollback \
  -p 5678:5678 \
  n8nio/n8n:0.228.0  # Previous version

# Update Caddy to point to rollback container
# Edit Caddyfile, change port if needed
caddy reload
```

---

## Monitoring

### Health Checks
```bash
# Check all containers
docker ps

# Check resource usage
docker stats

# Check logs for errors
docker-compose logs --tail=100 | grep -i error
```

### Uptime Monitoring
- **Tool:** UptimeRobot (free tier)
- **Monitors:** All public services (n8n, listmonk, draw, assets)
- **Alert:** Telegram if >5 min downtime

### Disk Usage
```bash
# Check Docker disk usage
docker system df

# Clean old images/containers
docker system prune -a
```

---

## Results

**Stats (6 months):**
- Uptime: 99.8% (VPS reboot 1x for kernel update)
- Services running: 8
- SSL cert renewals: 12 (all automatic, 0 manual)
- Deployment time per service: 5 min avg
- New service additions: 5 (Listmonk, NocoDB, Excalidraw, Markdown Viewer, Assets CDN)

**Time savings:**
- Before (manual nginx + certbot): 45 min per service deployment
- After (Docker + Caddy): 5 min per service
- **Savings: 40 min per deployment**
- **Total saved (5 deployments): 3.3 hours**

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| VPS (Hostinger, 4 CPU, 8 GB RAM) | $12/month |
| Domain (cristiantala.com) | $12/year ($1/month) |
| Cloudflare (DNS + API) | $0/month (free tier) |
| Let's Encrypt SSL | $0/month (free) |
| Docker | $0 (open source) |
| Caddy | $0 (open source) |
| **Total** | **~$13/month** |

**vs SaaS equivalent:**
- n8n Cloud: $20/month
- Managed Listmonk: $29/month
- NocoDB Cloud: $10/month
- **Total SaaS:** $59/month

**Annual savings:** $552/year

---

## Next Steps

1. **Backup automation** — Daily PostgreSQL dumps to S3
2. **Container health monitoring** — Auto-restart on failure
3. **Resource usage alerts** — Notify if any service >80% memory
4. **Multi-server setup** — Split DB to separate VPS (when needed)

---

## Takeaway

**Self-hosting isn't just about cost—it's about control.**

Docker + Caddy gave me:
- ✅ 8 services on 1 VPS ($12/month vs $59/month SaaS)
- ✅ Zero-config SSL (wildcard cert, auto-renewal)
- ✅ 5-minute deployments (vs 45 minutes manual)
- ✅ Rollback capability (docker images = time machine)

**The result:** Ship services fast, run them cheap, sleep well at night.
