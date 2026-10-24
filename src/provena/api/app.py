"""FastAPI application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI

from provena import __version__
from provena.api.errors import register_error_handlers
from provena.api.health import router as health_router
from provena.api.middleware import RequestContextMiddleware
from provena.config import Settings, get_settings
from provena.logs import configure_logging
from provena.probes import HttpProbe, Probe

log = logging.getLogger("provena")


def default_probes(settings: Settings) -> list[Probe]:
    headers = {}
    if settings.qdrant_api_key:
        headers["api-key"] = settings.qdrant_api_key.get_secret_value()
    qdrant = HttpProbe(
        "qdrant",
        f"{str(settings.qdrant_url).rstrip('/')}/readyz",
        timeout_s=settings.probe_timeout_s,
        headers=headers,
    )
    return [qdrant]


def create_app(settings: Settings | None = None, probes: Sequence[Probe] | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_format)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        log.info("Provena %s starting (env=%s)", __version__, settings.env)
        yield
        log.info("Provena shutting down")

    app = FastAPI(
        title="Provena",
        version=__version__,
        summary="Evidence-first agentic RAG",
        lifespan=lifespan,
        # Interactive docs stay off in production.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    app.state.settings = settings
    app.state.probes = list(probes) if probes is not None else default_probes(settings)

    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    app.include_router(health_router)
    return app
