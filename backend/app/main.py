import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.compliance import router as compliance_router
from app.routers.capa import router as capa_router
from app.routers.contractors import router as contractors_router
from app.routers.alerts import router as alerts_router
from app.routers.audit import router as audit_router
from app.routers.ai import router as ai_router
from app.routers.health import router as health_router
from app.routers.inspections import router as inspections_router
from app.routers.violations import router as violations_router
from app.routers.mines import router as mines_router
from app.routers.risk import router as risk_router
from app.routers.anomaly import router as anomaly_router
from app.routers.documents import router as documents_router
from app.routers.gis import router as gis_router
from app.routers.iot import router as iot_router
from app.routers.reports import router as reports_router
from app.routers.workflow import router as workflow_router

settings = get_settings()
logger = logging.getLogger(__name__)
app = FastAPI(
    title="MineGuard AI API",
    description="Smart governance and compliance monitoring for coal mines.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: RequestResponseEndpoint) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path not in {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    if settings.environment.lower() in {"production", "prod"} and request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled API error at %s (%s)", request.url.path, type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(compliance_router)
app.include_router(capa_router)
app.include_router(contractors_router)
app.include_router(alerts_router)
app.include_router(audit_router)
app.include_router(ai_router)
app.include_router(inspections_router)
app.include_router(violations_router)
app.include_router(mines_router)
app.include_router(risk_router)
app.include_router(anomaly_router)
app.include_router(documents_router)
app.include_router(gis_router)
app.include_router(iot_router)
app.include_router(reports_router)
app.include_router(workflow_router)
