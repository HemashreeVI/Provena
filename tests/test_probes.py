from __future__ import annotations

import httpx

from provena.api.app import default_probes
from provena.config import Settings
from provena.probes import HttpProbe


def probe_with(handler: httpx.MockTransport) -> HttpProbe:
    return HttpProbe("svc", "http://svc/readyz", timeout_s=1, transport=handler)


async def test_ok_on_2xx() -> None:
    result = await probe_with(httpx.MockTransport(lambda r: httpx.Response(200))).check()
    assert result.ok
    assert result.detail is None
    assert result.latency_ms >= 0


async def test_fails_on_error_status() -> None:
    result = await probe_with(httpx.MockTransport(lambda r: httpx.Response(503))).check()
    assert not result.ok
    assert result.detail == "HTTP 503"


async def test_fails_on_connection_error() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    result = await probe_with(httpx.MockTransport(refuse)).check()
    assert not result.ok
    assert result.detail == "ConnectError"


def test_default_qdrant_probe_sends_api_key() -> None:
    settings = Settings(qdrant_api_key="k", _env_file=None)
    [probe] = default_probes(settings)
    assert isinstance(probe, HttpProbe)
    assert probe.name == "qdrant"
    assert probe._url == "http://localhost:6333/readyz"
    assert probe._headers == {"api-key": "k"}
