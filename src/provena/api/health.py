"""Liveness (`/health`) and readiness (`/ready`) endpoints."""

from __future__ import annotations

import asyncio
from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from provena import __version__
from provena.probes import Probe

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = __version__


class CheckResult(BaseModel):
    ok: bool
    latency_ms: float
    detail: str | None = None


class ReadyResponse(BaseModel):
    status: Literal["ready", "degraded"]
    checks: dict[str, CheckResult]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """The process is up. Never touches dependencies, so it is safe for liveness checks."""
    return HealthResponse()


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request, response: Response) -> ReadyResponse:
    """All dependencies answer. Returns 503 if any probe fails."""
    probes: list[Probe] = request.app.state.probes
    results = await asyncio.gather(*(probe.check() for probe in probes))
    all_ok = all(r.ok for r in results)
    if not all_ok:
        response.status_code = 503
    return ReadyResponse(
        status="ready" if all_ok else "degraded",
        checks={
            r.name: CheckResult(ok=r.ok, latency_ms=r.latency_ms, detail=r.detail) for r in results
        },
    )
