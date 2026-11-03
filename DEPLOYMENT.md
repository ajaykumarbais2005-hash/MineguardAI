# MineGuard AI deployment

This guide covers the existing React/Vite frontend and FastAPI backend. Compose builds two containers; the AI/OCR features currently use the backend's demo implementations. `ai-service/` contains library modules, not a separately runnable API, so Compose does not invent an AI service.

## Prerequisites

- Docker Engine with Docker Compose v2 (`docker compose`).
- Git and PowerShell for the commands below.
- For a production deployment, a Linux host or Docker-capable server, a DNS name, and a TLS-terminating reverse proxy.

## Environment setup

From the repository root, copy the example without replacing any existing `.env`:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Compose reads the root `.env` for variable substitution. The backend `.env` used during direct local development is not copied into either image. Production must not use the example signing key or development mode. Generate a unique signing key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set these values in the root `.env` before production startup:

```dotenv
ENVIRONMENT=production
JWT_SECRET=<unique value generated above>
CORS_ORIGINS=https://your-frontend.example.com
VITE_API_URL=/api
DATABASE_URL=sqlite:////app/data/mineguard.db
FRONTEND_PORT=5173
```

Keep the `.env` private and untracked. Do not put backend secrets in `VITE_*` variables. Production configuration validation rejects short/development JWT secrets and non-HTTPS CORS origins. If the frontend is served at another origin, set that exact HTTPS origin in `CORS_ORIGINS`.

The SQLite database and uploaded files are stored together in the named Docker volume `mineguardai-data`, mounted at `/app/data`. The configured container paths are `/app/data/mineguard.db` and `/app/data/uploads`. The named volume is independent of the containers and survives normal rebuilds, restarts, and `docker compose down`.

### Optional migration of existing local data

The application currently uses `backend/mineguard.db` and `backend/data/uploads` for a typical direct local run. Back up these files first. Only perform this one-time import when the Docker volume is new/empty; never copy over a volume that already contains deployment data.

```powershell
docker compose build backend
docker compose create backend
docker compose cp .\backend\mineguard.db backend:/app/data/mineguard.db
if (Test-Path .\backend\data\uploads) { docker compose cp .\backend\data\uploads\. backend:/app/data/uploads/ }
docker compose run --rm --no-deps --user 0 backend chown -R 10001:10001 /app/data
```

Then continue with the normal startup command. These copy commands do not remove or alter the source files. If the source database is in a different location, identify and back it up before using `docker compose cp`.

## Build and start

From the repository root:

```powershell
docker compose build
docker compose up -d
docker compose ps
```

The backend runs Uvicorn without development reload, initializes tables idempotently at container startup, and uses the existing seed function (which adds demo records only in development/test). It runs as UID 10001. The frontend is built with `VITE_API_URL=/api` and served by non-root Nginx on container port 8080. Nginx forwards `/api/*` to the backend using the Compose service name `backend`; API requests therefore do not depend on container `localhost` or expose backend secrets to Vite.

Only the frontend is published, bound by default to `127.0.0.1:5173`. Open the UI at `http://localhost:5173`; FastAPI docs and health are proxied at `http://localhost:5173/docs` and `http://localhost:5173/health`. Put a TLS reverse proxy in front of this loopback-bound port for a public deployment. Configure TLS, trusted forwarded headers, and HSTS at that proxy. Do not expose the container backend port directly to the public internet.

## Health and logs

```powershell
docker compose ps
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
Invoke-RestMethod http://localhost:5173/health
Invoke-WebRequest http://localhost:5173/healthz
Invoke-WebRequest http://localhost:5173/docs
```

Compose checks the backend `/health` endpoint and the frontend Nginx `/healthz` endpoint. Container application logs go to stdout/stderr. The backend health endpoint reports service configuration; it is not a full database integrity or external-dependency monitor.

## Stop and restart

```powershell
docker compose stop
docker compose start
```

To remove stopped containers and their Compose network while retaining application data:

```powershell
docker compose down
```

Do **not** use `docker compose down -v` for routine shutdown; that removes the persistent database/upload volume.

## Database and upload persistence

Check the persistent volume:

```powershell
docker volume inspect mineguardai-data
```

The backend's startup initializer uses SQLAlchemy `create_all` and the existing idempotent seed function; it does not drop tables or delete existing records. In production, demo seeding is disabled. A fresh production database therefore needs users/roles provisioned through an approved, secure administrative process before login; the application does not currently provide a production bootstrap-admin command.

SQLite is appropriate for a single backend instance with this local persistent volume. Do not scale multiple backend containers against the same SQLite file. For multi-instance/high-availability production, plan a reviewed migration to a managed PostgreSQL database, including a supported SQLAlchemy driver, schema/data migration, backups, and restore testing. This phase does not migrate the database.

## Backup and restore

Stop the backend first to make a consistent SQLite backup. The following backs up the database and uploaded files together:

```powershell
New-Item -ItemType Directory -Force .\backups | Out-Null
$backupDirectory = (Resolve-Path .\backups).Path
docker compose stop backend
docker run --rm --mount type=volume,source=mineguardai-data,target=/data --mount "type=bind,source=$backupDirectory,target=/backup" alpine:3.22 sh -c "tar -czf /backup/mineguard-data.tar.gz -C /data ."
docker compose start backend
```

Copy the archive off-host and protect it as sensitive operational data. To restore, first stop the application and make a separate backup of the current volume. Then restore the selected archive into the volume:

```powershell
$backupDirectory = (Resolve-Path .\backups).Path
docker compose down
docker run --rm --mount type=volume,source=mineguardai-data,target=/data --mount "type=bind,source=$backupDirectory,target=/backup" alpine:3.22 sh -c "tar -xzf /backup/mineguard-data.tar.gz -C /data && chown -R 10001:10001 /data"
docker compose up -d
```

Restoring overlays the volume contents. Verify the archive and preserve a separate copy of the pre-restore data before doing so.

## Updating the application

After obtaining the desired source revision:

```powershell
git pull
docker compose build
docker compose up -d
docker compose ps
```

The named data volume is not removed by these commands.

## Security and production recommendations

- Terminate HTTPS at a maintained reverse proxy, redirect HTTP to HTTPS, and set HSTS there.
- Restrict host/firewall access to the loopback frontend port; publish it only through the trusted proxy.
- Keep `.env`, backups, and Docker daemon access restricted. Rotate the JWT secret through a planned deployment; doing so invalidates existing tokens.
- Use a unique production JWT secret and exact HTTPS origins. The frontend API URL is a build-time public path, not a secret.
- Keep SQLite and uploads in the persistent volume; monitor disk usage and implement encrypted, tested off-host backups.
- Use a least-privilege host, regular base-image rebuilds, vulnerability monitoring, log retention, and a reverse-proxy request-size limit consistent with the backend's 10 MiB upload cap (Nginx allows 12 MiB for multipart overhead).
- The Docker images run non-root, drop Linux capabilities, use read-only container filesystems with temporary writable `/tmp`, and avoid copying `.env`, local databases, uploads, tests, or `node_modules` into images.
- The browser stores JWTs in memory rather than HttpOnly cookies; this limits persistence but does not protect against active same-origin script execution. Review the security limitations in [SECURITY.md](./SECURITY.md).

## Troubleshooting

- **Docker command unavailable:** Install/start Docker Desktop or Docker Engine with the Compose v2 plugin, then confirm `docker --version` and `docker compose version`.
- **Frontend cannot reach API:** Check `docker compose ps` and backend health. Confirm the build argument is `/api`; rebuild the frontend after changing `VITE_API_URL`.
- **Backend exits during startup:** Inspect `docker compose logs backend`. Production requires a unique 32-byte JWT secret and HTTPS CORS origin. Check that the volume is writable by UID 10001 and that `DATABASE_URL` points to `/app/data`.
- **Uploads return 413:** The default Nginx proxy limit is 12 MiB while the application accepts files up to 10 MiB. Keep proxy limits aligned.
- **Login unavailable on a new production database:** Production intentionally skips demo account seeding. Provision roles and accounts using a secure, reviewed operational process; do not enable demo mode to create production credentials.
- **API docs fail to load:** Use the proxied `/docs` URL and confirm `/openapi.json` is reachable through the frontend container.
- **A database or upload is missing after recreation:** Confirm `mineguardai-data` is mounted and has not been explicitly removed. Restore from a known-good backup if needed.

## Deployment status

These files configure local/container deployment. They do not publish or deploy the service to a cloud provider or public domain.
