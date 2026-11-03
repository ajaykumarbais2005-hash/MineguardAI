# MineGuard AI

MineGuard AI is a foundation for an AI-based smart governance and compliance monitoring system for coal mines. It is being developed for SIH 2026 problem statement SIH26024 by Team REBEL TITANS, MITS Gwalior.

## Phase 1 status

Phase 1 provides the initial development foundation:

- React, Vite, and TypeScript frontend
- FastAPI backend
- SQLite-ready configuration with PostgreSQL-compatible settings
- CORS and environment-based configuration
- `GET /health` service endpoint
- AI and OCR demo-mode configuration boundaries
- Docker Compose development configuration
- SQLAlchemy models, relationships, and deterministic demo seed data
- Authenticated operations shell with a responsive, demo-data dashboard

The completed foundation includes database models, authentication/RBAC, the responsive operations shell, the dashboard, and the mine-management module. Later phases will add the remaining governance workflows, AI integrations, reporting, and audit views.

The dashboard presents API-derived operational KPIs, compliance and risk trends, inspections, alerts, and activity. Seeded development records and simulated AI/IoT values are identified as demo data.

The Mine Management module is available at `/mines` after sign-in. It supports authenticated list/search/filter/sort, manager-restricted create/update/delete, detail statistics, operating zones, and safe deletion checks for related records.

The Compliance module is available at `/compliance` after sign-in. It provides live requirement listing, search and status filtering, compliance summary counts, and safety-officer/admin updates backed by the protected `/compliance` API.

The Inspections module is available at `/inspections` after sign-in. It supports protected inspection listing and status filters, mine/zone validation, checklist records, findings, remarks, evidence references, submission timestamps, and role-restricted workflow updates through the `/inspections` API.

The Violations module is available at `/violations` after sign-in. It provides severity/status filters, summary counts, violation recording, reference validation, ownership/status updates, evidence references, and audit-backed workflow changes through the protected `/violations` API.

The Corrective Actions module is available at `/corrective-actions` after sign-in. It links CAPA records to violations, responsible users, and contractors, supports priority/deadline/evidence fields, status transitions through verification, closure timestamps, summaries, and audit-backed updates.

The Contractors module is available at `/contractors` after sign-in. It provides partner search/status filtering, compliance and risk summaries, workforce counts, worker roster visibility, worker registration APIs, and role-based contractor management.

The Alerts module is available at `/alerts` after sign-in. It provides live alert listing, severity/status filters, unread and critical summaries, acknowledgment ownership, resolution transitions, and audit-backed status changes.

The Audit Trail module is available at `/audit-trail` for administrators and auditors. It provides searchable action/entity filters, event summaries, actor attribution, entity IDs, source IP, timestamps, and protected read-only access through `/audit`.

The AI Monitoring module is available at `/ai-monitoring` after sign-in. It provides a clearly labeled PPE `DEMO_SIMULATION` flow with person, helmet, vest, missing-helmet, and missing-vest detections, confidence, severity, camera context, persisted AI events, and an explicit limitation notice. No trained production model is claimed.

## Development setup

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Backend

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`. Verify it with:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

The health response reports the configured environment, database boundary, AI mode, OCR mode, and timestamp.

For a development login, initialize the database with `python -m app.init_db` and use `admin@mineguard.ai` with password `admin123`. This seeded account is for local development only; change or disable demo credentials before any shared or production deployment. Seeding is idempotent and does not reset passwords in an existing database.

### Database initialization

From the `backend` directory, create all tables and load the Phase 2 demo dataset with:

```powershell
python -m app.init_db
```

The seed is idempotent. It creates six roles/users, five mines, mine zones, inspections, compliance requirements, violations, corrective actions, contractors, AI/risk events, IoT readings, alerts, documents/OCR results, GIS assets, and audit logs.

## Environment configuration

Copy `.env.example` to `.env` and update values for local deployment. Secrets must remain in environment variables and must not be committed.

Important development defaults:

- Database: SQLite
- AI mode: `DEMO_SIMULATION`
- OCR mode: `DEMO`
- Upload directory: `data/uploads`

## Docker

Production-oriented Dockerfiles and Compose configuration are provided. See [DEPLOYMENT.md](./DEPLOYMENT.md) for environment setup, persistence, container commands, backups, and HTTPS deployment guidance.

## Testing

Phase 2 database tests can be run from the `backend` directory with:

```powershell
python -m pytest -q
```

Broader integration checks will be added in later phases.

## Known limitations

No user authentication, database models, mine workflows, trained AI model, OCR engine integration, IoT hardware integration, or production deployment setup is included yet. Simulated AI, sensor, and OCR modes will be explicitly labelled when implemented.
