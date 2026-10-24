from __future__ import annotations

import httpx

from provena import __version__
from provena.api.app import create_app
from provena.config import Settings
from tests.conftest import FakeProbe


async def test_health_reports_ok_and_version(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


async def test_ready_when_all_probes_pass(client: httpx.AsyncClient) -> None:
    response = await client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"]["qdrant"]["ok"] is True


async def test_ready_is_503_when_a_probe_fails(settings: Settings) -> None:
    app = create_app(settings, probes=[FakeProbe("qdrant", ok=False, detail="ConnectError")])
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"]["qdrant"]["detail"] == "ConnectError"
