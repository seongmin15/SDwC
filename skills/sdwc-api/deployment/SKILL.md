# Deployment — FastAPI

> This skill defines deployment rules for the **sdwc-api** service.
> Target: **kubernetes** | Build tool: **poetry**

---

## 1. Build & Package

```bash
poetry install              # install dependencies
poetry lock                 # update lock file (commit poetry.lock)
poetry export -f requirements.txt -o requirements.txt  # for Docker
```

**Rules:**
- Always commit `poetry.lock`.
- Pin major versions in `pyproject.toml` (e.g., `fastapi = "^0.110"`).
- Use `poetry add --group dev` for test/lint dependencies.

---

## 2. Container

**Dockerfile (multi-stage build):**

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.{service_name}.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore:**

```
__pycache__
*.pyc
.git
.env
tests/
.venv/
```

**Rules:**
- Always use multi-stage builds to minimize image size.
- Never copy `.env` files into the image. Inject environment variables at runtime.
- Use `--no-cache-dir` in pip install to reduce layer size.

### Infrastructure as Code

**Tool: **

- IaC files location: [sdwc-platform](https://github.com/seongmin15/sdwc-platform) repo `manifests/sdwc/` directory.
- Never hardcode environment-specific values — use variables/parameters.
- All infra changes go through the same PR review process as code.

---

## 3. Environment Configuration

- **dev**: Local development and testing — Runs directly via uvicorn, no container
- **production**: k3s cluster on Windows WSL2 — Containerized, served behind k3s Traefik ingress

**Configuration management:**

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

**Rules:**
- All config via environment variables. Never hardcode secrets or URLs.
- Use `.env` for local development only. Never commit `.env` files.
- Each environment loads its own variables (via deployment platform, not files).
- **Secrets management: env_file** — fetch secrets from this source in production.

---

## 4. CI/CD Pipeline

**Tool: GitHub Actions**
**Stages: lint -> typecheck -> test -> build -> push to ghcr**

Standard pipeline steps for this service (`.github/workflows/ci-sdwc-api.yml`):

```
Job: check (on PR and push to main)
1. Checkout code
2. Setup Python 3.12
3. Install Poetry 2.1.1
4. poetry install
5. ruff check src/
6. mypy src/
7. pytest --tb=short

Job: docker (on push to main only, after check passes)
1. Setup Docker Buildx
2. Login to GHCR
3. Build + push image (tags: sha-<7char>, latest)
```

**Triggers:** PR to main + push to main, path-filtered to `sdwc-api/**` and `.sdwc/**`

**Rules:**
- Pipeline must pass before merge.
- Container image tag uses git commit SHA (short, 7 chars) for traceability.
- Concurrency: cancel-in-progress per ref.
**CD Tool: argocd**
**Strategy: gitops**

**Container registry: ghcr**

---

## 5. Health Check & Readiness

```python
# routers/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Liveness probe — app is running."""
    return {"status": "ok"}

@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    """Readiness probe — app can serve traffic."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Not ready")
```

**Rules:**
- `/health` — no dependencies, always fast. Used for liveness.
- `/ready` — checks DB and critical dependencies. Used for readiness.
- Both endpoints are public (no auth required).

---

## 6. Operational Commands

```bash
# Run locally
uvicorn src.{service_name}.main:app --reload --port 8000

# Database migration
alembic upgrade head          # apply all migrations
alembic revision --autogenerate -m "description"  # create migration

# Logs (container)
docker logs -f {container_name}

# Shell access (container)
docker exec -it {container_name} /bin/bash
```
