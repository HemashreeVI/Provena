from __future__ import annotations

import httpx
import pytest


async def test_generates_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    assert len(response.headers["X-Request-ID"]) == 32


async def test_echoes_valid_caller_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "trace-123"})
    assert response.headers["X-Request-ID"] == "trace-123"


@pytest.mark.parametrize("bad", ["has spaces", "x" * 129, "semi;colon"])
async def test_replaces_unsafe_request_id(client: httpx.AsyncClient, bad: str) -> None:
    response = await client.get("/health", headers={"X-Request-ID": bad})
    assert response.headers["X-Request-ID"] != bad
    assert len(response.headers["X-Request-ID"]) == 32
