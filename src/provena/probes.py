"""Readiness probes for the services Provena depends on."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True, slots=True)
class ProbeResult:
    name: str
    ok: bool
    latency_ms: float
    detail: str | None = None


class Probe(Protocol):
    name: str

    async def check(self) -> ProbeResult: ...


class HttpProbe:
    """Healthy when a GET to `url` returns a 2xx status within the timeout."""

    def __init__(
        self,
        name: str,
        url: str,
        *,
        timeout_s: float,
        headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.name = name
        self._url = url
        self._timeout_s = timeout_s
        self._headers = headers or {}
        self._transport = transport

    async def check(self) -> ProbeResult:
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_s, transport=self._transport
            ) as client:
                response = await client.get(self._url, headers=self._headers)
            ok = response.is_success
            detail = None if ok else f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            ok, detail = False, type(exc).__name__
        return ProbeResult(self.name, ok, round((time.perf_counter() - start) * 1000, 2), detail)
