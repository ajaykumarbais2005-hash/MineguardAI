# Phase 26 – Docker and Production Deployment Report

## Initial deployment readiness audit

- The project is an existing React/Vite/TypeScript frontend and FastAPI/SQLAlchemy backend. No application rebuild or API/business-logic changes were required.
- SQLite is the configured default (`sqlite:///./mineguard.db` for local runs); uploads use a configurable directory. The existing initializer calls `create_all` and an idempotent seed function. Production mode skips demo seeding.
- FastAPI already provides `/health`, API docs, and environment validation for production JWT secrets and HTTPS CORS origins.
- The frontend used a development-host API URL by default; a Vite build-time API value is needed in a container.
- The prior Compose file had no Dockerfiles, published the Vite development server, and referenced an `ai-service` build despite no runnable API/Dockerfile in `ai-service/`. AI/OCR functionality currently runs in backend demo mode.
- A backend `.env` exists. Its values were not inspected, changed, or copied into the Docker build context.
- Docker and Docker Compose are available; both images and the Compose deployment were built and exercised.

## Architecture implemented

- **Backend:** Python 3.12 slim image, runtime-only requirements, non-root UID 10001, Uvicorn without reload, container stdout/stderr logs, and idempotent table initialization on startup.
- **Frontend:** multi-stage Node 22 build and Nginx 1.28 Alpine runtime, running as the Nginx non-root user. Vite receives `/api` as a public build-time path; no secret is passed to the frontend.
- **Networking:** Nginx proxies `/api/*` to the Compose backend service name. It also proxies health and docs endpoints. Only the frontend port is published, bound to loopback by default; the backend port is internal to the Compose network.
- **Persistence:** SQLite and uploads share the named `mineguardai-data` volume at `/app/data`. Normal rebuilds, restarts, and `docker compose down` retain it.
- **AI/OCR:** no AI container was added because the repository has no runnable standalone AI service. Existing backend demo modes remain available.

## Files created

- `backend/.dockerignore`
- `backend/Dockerfile`
- `backend/requirements-dev.txt`
- `frontend/.dockerignore`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `DEPLOYMENT.md`
- `PHASE_26_REPORT.md`
- `frontend/src/pages/SettingsPage.tsx`

## Files modified

- `.env.example`
- `.gitignore`
- `README.md`
- `backend/requirements.txt`
- `docker-compose.yml`

## Security and operations improvements

- Backend test-only dependencies are separated from runtime requirements.
- `.env`, databases, uploads, tests, `node_modules`, and build output are excluded from image contexts.
- Containers use non-root users, read-only root filesystems, temporary writable filesystems, dropped Linux capabilities, and `no-new-privileges`.
- Compose uses a named data volume, restart policies, backend/frontend health checks, and dependency readiness.
- Nginx supports client-side route fallback, hashed-asset caching, security headers, API proxying, and the backend's 10 MiB upload size with multipart overhead.
- Production secret, CORS, TLS/reverse proxy, database, backup/restore, migration, and troubleshooting instructions are in `DEPLOYMENT.md`.
- The existing `.env` was not changed. `.env.example` contains placeholders, not actual secrets.

## Verification results

- Backend tests (`python -m pytest -q` from `backend/`): **77 passed**.
- Frontend production build with `VITE_API_URL=/api`: **passed**. Route-level lazy loading reduced the main JavaScript bundle from about 533 kB to about 301 kB; no large-chunk warning is emitted.
- Frontend lint (`npm.cmd run lint`): **passed**.
- Docker Compose YAML parsed successfully with the available Python YAML parser.
- `git diff --check`: **passed**.
- The built frontend bundle contains the `/api` production base path.

## Container and deployment status

Docker Compose build and local container smoke checks:

- Backend Docker image build: **passed**.
- Frontend Docker image build: **passed**.
- `docker compose build`: **passed** for both images.
- Container health: **verified healthy** for the backend and frontend with `docker compose ps`.
- Frontend login and authenticated route rendering through the Compose-served Nginx frontend: **verified**.
- Responsive navigation and horizontal overflow: **checked on mobile and desktop**.
- Full database persistence, API docs through Nginx, and upload persistence across container recreation: **not separately tested**.
- Public/cloud deployment: **not performed**.

Both Docker images were successfully built with `docker compose build`; this does not replace a public/cloud deployment or a full persistence/restore drill.

## Known limitations and manual steps

- Follow `DEPLOYMENT.md` to create the private root `.env`, generate a unique production JWT secret, and configure HTTPS origins before production use.
- If existing local records are required, back up and follow the documented one-time import into a new/empty volume before normal startup. Do not copy over an existing deployment volume.
- Production initialization intentionally skips demo accounts; a fresh production database requires secure role/user provisioning. No bootstrap-admin command exists.
- SQLite is for a single backend instance; multi-instance deployments need an approved database migration and driver.
- TLS termination, public DNS, firewalling, and deployment to a cloud/provider remain operator tasks.

## Completion status

**Phase 26 configuration and documentation are implemented. Backend tests passed (77); frontend build and lint passed; both Docker images built; local container health and frontend login/routes were verified. No public deployment is claimed.**
