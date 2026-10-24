from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI

from provena.api.app import create_app
from provena.config import Environment, Settings
from provena.probes import ProbeResult


class FakeProbe:
    def __init__(self, name: str, ok: bool = True, detail: str | None = None) -> None:
        self.name = name
        self._ok = ok
        self._detail = detail

    async def check(self) -> ProbeResult:
        return ProbeResult(self.name, self._ok, 1.0, self._detail)


@pytest.fixture
def settings() -> Settings:
    return Settings(env=Environment.TEST, _env_file=None)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings, probes=[FakeProbe("qdrant")])


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
