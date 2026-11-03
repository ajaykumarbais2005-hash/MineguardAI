# MineGuard AI Security

## Security architecture

The React client calls the FastAPI backend over HTTP(S). The API uses SQLAlchemy ORM queries and Pydantic request/response models; the existing relational schema is unchanged. Database credentials, signing keys, and deployment settings belong in environment configuration, never frontend variables or source-controlled `.env` files.

## Authentication and JWTs

Passwords are hashed with bcrypt through Passlib. Login returns a signed bearer access token with `sub`, `iat`, and `exp` claims. The API validates the signature, configured algorithm, required claims, and expiry, then loads the user and checks that the account is active. Authentication errors do not distinguish unknown, inactive, or incorrect-password accounts.

The browser keeps the access token in memory and attaches it to API requests in the `Authorization` header. Tokens are not persisted to browser storage; a page reload therefore requires signing in again. A `401` response clears the in-memory token and authentication state. Logout clears the client token and records the action; access tokens remain usable until expiry because the API does not maintain a revocation list.

## RBAC

Backend dependencies enforce role access for protected endpoints. The existing role names are `ADMIN`, `MINE_MANAGER`, `SAFETY_OFFICER`, `INSPECTOR`, `CONTRACTOR`, and `AUDITOR`. The client hides restricted navigation and redirects from restricted pages, but frontend checks are only a usability layer; backend authorization remains authoritative.

## Environment variables

Copy `.env.example` to a local `.env` and replace placeholder values. The backend reads its working-directory `.env`; Docker Compose reads variable substitutions from its Compose environment (for example, the root `.env` or exported variables). Do not commit `.env` files.

- `ENVIRONMENT`: use `development` locally and `production` for deployment.
- `JWT_SECRET`: production requires a unique secret of at least 32 bytes; the development fallback is rejected in production.
- `JWT_ALGORITHM`: currently defaults to `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: positive lifetime in minutes.
- `DATABASE_URL`: SQLAlchemy database URL. SQLite is the development default.
- `CORS_ORIGINS`: comma-separated explicit origins; wildcard origins are rejected. Production origins must use HTTPS.
- `UPLOAD_DIRECTORY`: private server-side upload directory.
- `AI_SERVICE_URL`, `AI_MODE`, and `OCR_MODE`: AI/OCR service configuration.

The production server must be started with `ENVIRONMENT=production`, a production signing key, and the intended HTTPS frontend origins. When setting variables for Compose, do not place secrets in `VITE_*` variables. Fresh production database initialization does not seed demo data; existing databases are not modified or purged.

## File uploads and OCR

Document uploads accept `.pdf`, `.png`, `.jpg`, `.jpeg`, and `.txt`, enforce an approximately 10 MiB limit, validate declared MIME type and file signatures/text encoding, and generate random storage names. Client filenames are reduced to a safe basename; returned `file_path` values expose only the stored basename. Uploads are stored under the configured backend directory and are never served as executable web content. OCR remains in the existing demo-processing flow.

The multipart parser may spool an incoming request before application-level size checks; deployments should also impose request-body limits at the reverse proxy or ingress.

## Security headers

The API sets `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy`. A restrictive CSP is added to API responses and omitted from Swagger/OpenAPI pages for compatibility. HSTS is sent only for HTTPS requests in production. TLS termination and trusted proxy configuration must be correctly configured by the deployment.

## Audit logging

Authentication success/failure, logout, missing/invalid credentials, inactive-account access, and RBAC denials are written to the existing `AuditLog` table. Existing sensitive mutations continue to use their audit records. Audit entries exclude passwords, bearer tokens, and signing secrets. Configure access controls and retention for the audit database in production.

## Security tests

From `backend`, run:

```powershell
python -m pytest -q
```

From `frontend`, run:

```powershell
npm.cmd run build
npm.cmd run lint
npm.cmd audit --omit=dev
```

## Development limitations and deployment recommendations

- Demo seed users and demo data are available only in development/test environments. Do not reuse the development database or demo credentials in production; existing records are deliberately not deleted by this phase.
- Access tokens are held in memory, not HttpOnly cookies. This reduces persistence and exposure to browser storage theft but does not protect a token from active same-origin script execution.
- Login rate limiting, MFA, token revocation, and password reset workflows are not implemented. Add appropriate controls before production use.
- Use HTTPS end-to-end or a correctly configured trusted TLS-terminating proxy, a least-privilege database account, encrypted backups, private upload storage, request-size limits, dependency monitoring, and audit-log retention.
- Current AI/OCR demo modes are not production-grade data processing controls.
