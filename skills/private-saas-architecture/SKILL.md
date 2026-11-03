---
name: private-saas-architecture
description: Use for building modular private SaaS and admin dashboards.
version: 0.2.0
author: Bagas Cihuy & Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [saas, private-cloud, docker, caddy, laravel, nextjs, security]
---

# Private SaaS Architecture & Engineering Doctrine

Architectural blueprint, security hardening, and deployment governance for private SaaS platforms, client micro-portals, and enterprise dashboards.

## Supporting References
- `references/unabridged-private-saas.md`: Full unabridged architecture doctrine and complete field notes.
- `references/network-proxies-and-tunnels.md`: 27KB detailed guide on Cloudflare tunnels, Caddy reverse proxy, TLS termination, and firewall isolation.
- `references/b2b-edtech-compliance.md`: 21KB specification on multi-tenant RBAC, compliance logs, and autonomous blueprint execution.
- `references/oaas-virtual-backoffice.md`: Outcome-as-a-Service (OaaS) and hybrid virtual back-office workflows.
- `references/white-label-commercial-ai-saas.md`: Multi-tenant dynamic personas, quota isolation, and white-label branding.
- `references/app-shell-hierarchy.md`: Desktop vs mobile navigation and responsive layout hierarchies.
- `references/pm2-integration.md`: Process supervision, auto-restart watchdogs, and cluster health.

---

## 1. Modular "Briefcase" Philosophy (Koper Kerja Digital)
- **Self-Contained Deployment**: Each SaaS product must be encapsulated like a standalone briefcase (`docker-compose.yml`, `.env.example`, isolated DB, and explicit entrypoint).
- **Zero Host Pollution**: Applications must not depend on global host runtime state beyond standard container engines (Docker) and reverse proxy ingress.
- **Port Discipline**: Assign deterministic, collision-free internal port ranges (e.g. 3000-3099 for frontend, 8000-8099 for APIs) bound to `127.0.0.1`. Never expose raw application ports to public `0.0.0.0`.

## 2. Ingress, Proxies & Edge Security
*(Full network specifications in `references/network-proxies-and-tunnels.md`)*
- **Edge Ingress**: Route public web traffic through authenticated Cloudflare Tunnels (`cloudflared`) or hardened Caddy reverse proxy.
- **Host Security**: Block external direct IP hits. Bind internal backend services strictly to `localhost` or Docker bridge network.
- **SSL / TLS**: Automatic zero-maintenance TLS via Let's Encrypt / Cloudflare Edge Certificates. Enforce HTTP Strict Transport Security (HSTS).
- **Public URL Contract**: NEVER output `http://localhost:<port>` to end-users. Always provide the canonical HTTPS domain (e.g. `https://app.jajandigital.web.id`).

## 3. UI/UX Mindset & Anti-Slop Standards
- **Two-Layer Silhouette Architecture**: Background canvas (acromatic 95%, subtle depth) + high-contrast foreground content (WCAG AAA >= 7:1).
- **Anti-AI-Slop**: Forbid generic purple/cyan neon gradients, bloated card shadows, floating badge clutter, and emojis in UI.
- **Micro-Interactions & Morphing**: Integrate 60 FPS in-place state transitions (`cubic-bezier(0.16, 1, 0.3, 1)`). Avoid disruptive full-page reloads.
- **Mobile Ergonomics**: Full-bleed responsive layouts, touch targets >= 44px, bottom clearance for virtual keyboards (`interactive-widget=resizes-content`).

## 4. Backend Hardening & Data Isolation
- **Tenant Isolation**: Isolate tenant data via separate schemas or rigorous tenant-scoped ORM global scopes (`where('tenant_id', $currentTenant->id)`).
- **Zero Raw Password Storage**: Bcrypt / Argon2id hashing with minimum work factor 12.
- **Idempotent Webhooks**: Process webhooks transactionally with HMAC signature verification, UUID idempotency keys, and exponential backoff retry.
- **Durable Audit Trail**: Log administrative changes (`user_id`, `action`, `resource_id`, `timestamp`, `ip_address`, `diff_json`).

## 5. Engineering Empiricism over "ABS"
- **Runtime Proof**: Never declare a feature or deployment complete without verifiable proof (HTTP 200, exit code 0, browser screenshot).
- **Direct Execution**: For bounded tasks, apply direct file patches and single-pass verification. Avoid endless testing paralysis loops.
