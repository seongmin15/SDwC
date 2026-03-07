# Deployment — React

> This skill defines deployment rules for the **sdwc-web** service.
> Target: **kubernetes** | Build tool: **vite**

---

## 1. Build & Package

```bash
npm run build               # vite build → dist/
npm run preview             # preview production build locally
```

**Rules:**
- Always commit the lock file (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`).
- Use `--frozen-lockfile` (or `npm ci`) in CI to ensure reproducible builds.
- Check bundle size in CI — flag increases over 10%.

---

## 2. Container

**Dockerfile (multi-stage build):**

```dockerfile
# Build stage
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage — serve static files
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**nginx.conf (SPA routing):**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**.dockerignore:**

```
node_modules
.git
.env*
dist/
```

### Infrastructure as Code

**Tool: **

- IaC files location: [sdwc-platform](https://github.com/seongmin15/sdwc-platform) repo `manifests/sdwc/` directory.
- Never hardcode environment-specific values.
- All infra changes go through PR review.

---

## 3. Environment Configuration

- **dev**: Local development with Vite dev server — Hot reload, proxied API requests to local sdwc-api
- **production**: Static files served via nginx container in k3s — Built assets served by nginx, API requests routed via k3s ingress

**Environment variables:**

```bash
# .env.local (dev only, not committed)
VITE_API_URL=http://localhost:8000
VITE_APP_ENV=development
```

**Rules:**
- Prefix all env vars with `VITE_` (or framework equivalent) to expose to client.
- Never put secrets in client-side env vars — they are visible in the bundle.
- Build-time injection only. Use `import.meta.env.VITE_*` to access.
- Per-environment values are set in the deployment platform, not in `.env` files.
- **Secrets management: env_file** — for server-side secrets only (SSR, BFF).

---

## 4. CI/CD Pipeline

**Tool: GitHub Actions**
**Stages: lint -> typecheck -> format -> test -> build -> push to ghcr**

Standard pipeline steps (`.github/workflows/ci-sdwc-web.yml`):

```
Job: check (on PR and push to main)
1. Checkout code
2. Setup Node 20
3. npm ci
4. npm run lint
5. npm run typecheck
6. npm run format:check
7. npm test
8. npm run build

Job: docker (on push to main only, after check passes)
1. Setup Docker Buildx
2. Login to GHCR
3. Build + push image (tags: sha-<7char>, latest)
```

**Triggers:** PR to main + push to main, path-filtered to `sdwc-web/**`

**Rules:**
- Pipeline must pass before merge.
- Tag container images with git commit SHA (short, 7 chars).
- Concurrency: cancel-in-progress per ref.
**CD Tool: argocd**
**Strategy: gitops**

**Container registry: ghcr**

---

## 5. Performance Budget

| Metric | Target |
|--------|--------|
| Initial bundle (gzip) | < 200 KB |
| Largest Contentful Paint | < 2.5s |
| First Input Delay | < 100ms |

**Rules:**
- Analyze bundle with `npx vite-bundle-visualizer` (or equivalent).
- Lazy-load routes and heavy components.
- Tree-shake unused library exports.

---

## 6. Operational Commands

```bash
# Run locally
npm run dev                    # dev server with HMR

# Build and preview
npm run build && npm run preview

# Analyze bundle
npx vite-bundle-visualizer

# Check types
tsc --noEmit
```
