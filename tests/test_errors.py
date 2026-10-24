from __future__ import annotations

import httpx
from fastapi import FastAPI


async def test_not_found_uses_error_envelope(client: httpx.AsyncClient) -> None:
    response = await client.get("/nope", headers={"X-Request-ID": "abc"})
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Not Found", "request_id": "abc"}
    }


async def test_validation_error_lists_details(app: FastAPI, client: httpx.AsyncClient) -> None:
    @app.get("/echo")
    async def echo(n: int) -> int:
        return n

    response = await client.get("/echo", params={"n": "not-a-number"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["loc"] == ["query", "n"]


async def test_unhandled_error_hides_internals(app: FastAPI, client: httpx.AsyncClient) -> None:
    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret internals")

    response = await client.get("/boom", headers={"X-Request-ID": "req-1"})
    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "internal_error",
        "message": "Internal server error",
        "request_id": "req-1",
    }
    assert response.headers["X-Request-ID"] == "req-1"
    assert "secret" not in response.text
