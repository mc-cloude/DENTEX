"""Async bridge between FastAPI endpoints and CrewAI runtime.

This module encapsulates guarded routing logic so the API gateway simply
passes tasks to named agents while the orchestrator handles policy
pre-checks, guardian flows, and audit trails.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    crew_config_path: str = "ai/crewai_config.yaml"
    guardian_first: bool = True
    require_consent_scopes: tuple[str, ...] = ("ai:coach",)


@dataclass
class DSRJob:
    job_id: str
    user_id: str
    status: str = "pending"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class AgentOrchestrator:
    """In-memory orchestrator with CrewAI bridging hooks."""

    def __init__(self, config: OrchestratorConfig | None = None) -> None:
        self._config = config or OrchestratorConfig()
        self._jobs: Dict[str, DSRJob] = {}
        self._lock = asyncio.Lock()
        logger.debug("Orchestrator initialized with %s", self._config)

    async def dispatch(self, endpoint: str, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_guardian(task_payload)
        logger.info("Dispatching task endpoint=%s", endpoint)
        # Instead of invoking CrewAI synchronously we simulate with async stub.
        await asyncio.sleep(0.01)
        return {
            "endpoint": endpoint,
            "echo": task_payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _ensure_guardian(self, task_payload: Dict[str, Any]) -> None:
        if not self._config.guardian_first:
            return
        user = task_payload.get("user", {})
        scopes = set(user.get("scopes", []))
        missing = [scope for scope in self._config.require_consent_scopes if scope not in scopes]
        if missing:
            logger.warning("Guardian pre-check failed missing_scopes=%s", missing)
            raise PermissionError(f"Missing consent scopes: {','.join(missing)}")
        logger.debug("Guardian pre-check passed for user=%s", user.get("user_id"))

    async def start_dsr_job(self, user, payload: Dict[str, Any]) -> str:
        async with self._lock:
            job_id = str(uuid.uuid4())
            job = DSRJob(job_id=job_id, user_id=user.user_id)
            self._jobs[job_id] = job
            logger.info("Started DSR job job_id=%s user=%s", job_id, user.user_id)
            asyncio.create_task(self._simulate_dsr(job_id))
            return job_id

    async def get_dsr_status(self, job_id: str) -> Dict[str, Any]:
        job = self._jobs.get(job_id)
        if not job:
            return {"job_id": job_id, "status": "unknown"}
        return {
            "job_id": job.job_id,
            "status": job.status,
            "started_at": job.started_at.isoformat(),
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        }

    async def _simulate_dsr(self, job_id: str) -> None:
        await asyncio.sleep(0.05)
        async with self._lock:
            job = self._jobs[job_id]
            job.status = "completed"
            job.finished_at = datetime.now(timezone.utc)
            logger.info("Completed DSR job job_id=%s", job_id)
