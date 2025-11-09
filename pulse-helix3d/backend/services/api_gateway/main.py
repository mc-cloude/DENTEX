"""Pulse HELIX3D API Gateway.

This FastAPI application terminates OIDC tokens, enforces OPA policies,
bridges to the CrewAI runtime, and exposes tier-aware wellness APIs.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer

from backend.services.ai_agentic_core.orchestrator import AgentOrchestrator
from backend.shared.opa_client.client import OPAAuthorizer, PolicyDecision
from backend.shared.telemetry.metrics import metrics_router
from backend.shared.utils.auth import (
    AuthenticatedUser,
    OAuthUser,
    build_opa_input,
    decode_jwt,
)
from backend.shared.utils.errors import ErrorResponse
from backend.services.fitness.router import router as fitness_router
from backend.services.nutrition.router import router as nutrition_router
from backend.services.clinical.router import router as clinical_router
from backend.services.labs.router import router as labs_router
from backend.services.community.router import router as community_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Pulse HELIX3D Gateway", version="1.0.0-RC3")
app.include_router(metrics_router)
app.include_router(fitness_router)
app.include_router(nutrition_router)
app.include_router(clinical_router)
app.include_router(labs_router)
app.include_router(community_router)

oauth_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/auth/authorize",
    tokenUrl="/auth/exchange",
    scopes={
        "ai:coach": "Access the AI coaching endpoints",
        "ai:telemed": "Clinical telemedicine access",
    },
)

OPA_URL = os.getenv("OPA_URL", "http://opa.pulse.svc.cluster.local:8181")
authorizer = OPAAuthorizer(base_url=OPA_URL)
agent_orchestrator = AgentOrchestrator()


async def require_user(token: str = Depends(oauth_scheme)) -> AuthenticatedUser:
    try:
        raw_user = decode_jwt(token)
    except ValueError as exc:  # pragma: no cover - defensive
        logger.exception("Failed to decode JWT")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return AuthenticatedUser.from_claims(raw_user)


async def opa_guard(request: Request, user: AuthenticatedUser) -> PolicyDecision:
    opa_input = build_opa_input(request, user)
    decision = await authorizer.authorize(route_name=opa_input["route"], payload=opa_input)
    if not decision.allow:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=decision.reason or "Access denied by policy",
        )
    return decision


@app.get("/healthz", tags=["system"])
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/auth/exchange", tags=["auth"], response_model=OAuthUser)
async def exchange_code(payload: Dict[str, Any]) -> OAuthUser:
    """Exchange an OIDC auth code for a gateway-scoped access token."""
    # In production this would call the IdP token endpoint. Here we emulate.
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    logger.info("Issuing simulated token for code %s", code)
    return OAuthUser(
        access_token=str(uuid.uuid4()),
        expires_in=3600,
        token_type="Bearer",
        scope="ai:coach",
    )


@app.get("/me", tags=["profile"])
async def me(user: AuthenticatedUser = Depends(require_user)) -> Dict[str, Any]:
    return {
        "user_id": user.user_id,
        "tier": user.tier,
        "tenant": user.tenant,
        "scopes": user.scopes,
    }


@app.post("/ingest/wearable/{vendor}", tags=["ingest"])
async def ingest_wearable(
    vendor: str,
    payload: Dict[str, Any],
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    if vendor not in {"fitbit", "whoop", "apple"}:
        raise HTTPException(status_code=404, detail="Unsupported wearable vendor")
    logger.info("Ingest payload for %s user=%s", vendor, user.user_id)
    return {
        "ingested": True,
        "vendor": vendor,
        "policy": decision.model_dump(),
        "payload_size": len(payload or {}),
    }


@app.get("/dashboard/summary", tags=["dashboard"])
async def dashboard_summary(
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    return {
        "tier": user.tier,
        "metrics": {
            "hrv_score": 72,
            "sleep_debt_hours": 1.3,
            "strain_index": 0.62,
        },
        "allowed": decision.allow,
    }


@app.get("/dashboard/analytics", tags=["dashboard"])
async def dashboard_analytics(
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    if user.tier == "core":
        raise HTTPException(status_code=403, detail="Analytics gated for tier")
    return {
        "tier": user.tier,
        "hrv_trend": [71, 72, 74, 73],
        "sleep_debt": [2.1, 1.8, 1.3, 1.0],
        "strain": [0.54, 0.58, 0.62, 0.61],
        "policy": decision.model_dump(),
    }


async def _run_agentic(endpoint: str, user: AuthenticatedUser, payload: Dict[str, Any]) -> Dict[str, Any]:
    task_payload = {"user": user.model_dump(), "input": payload}
    return await agent_orchestrator.dispatch(endpoint=endpoint, task_payload=task_payload)


@app.post("/ai/plan", tags=["ai"])
async def ai_plan(
    payload: Dict[str, Any],
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    if "goal" not in payload:
        raise HTTPException(status_code=400, detail="goal is required")
    result = await _run_agentic("planner", user, payload)
    return {"result": result, "policy": decision.model_dump()}


@app.post("/ai/coach", tags=["ai"])
async def ai_coach(
    payload: Dict[str, Any],
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    result = await _run_agentic("coach", user, payload)
    return {"result": result, "policy": decision.model_dump()}


@app.post("/ai/guardian/validate", tags=["ai"])
async def ai_guardian_validate(
    payload: Dict[str, Any],
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    result = await _run_agentic("guardian", user, payload)
    return {"result": result, "policy": decision.model_dump()}


@app.post("/dsr/erase", tags=["privacy"])
async def dsr_erase(
    payload: Dict[str, Any],
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    job_id = await agent_orchestrator.start_dsr_job(user, payload)
    return {"job_id": job_id, "policy": decision.model_dump()}


@app.get("/dsr/status/{job_id}", tags=["privacy"])
async def dsr_status(
    job_id: str,
    user: AuthenticatedUser = Depends(require_user),
    decision: PolicyDecision = Depends(opa_guard),
) -> Dict[str, Any]:
    status_payload = await agent_orchestrator.get_dsr_status(job_id)
    return {"status": status_payload, "policy": decision.model_dump()}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=ErrorResponse.from_exc(exc).model_dump())


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now(tz=timezone.utc)
    response = await call_next(request)
    duration = (datetime.now(tz=timezone.utc) - start).total_seconds()
    logger.info("%s %s completed in %.3fs status=%s", request.method, request.url.path, duration, response.status_code)
    return response


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
