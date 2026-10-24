from __future__ import annotations

import pytest
from pydantic import ValidationError

from provena.config import Environment, LogFormat, Settings


def make(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def test_defaults() -> None:
    s = make()
    assert s.env is Environment.DEVELOPMENT
    assert str(s.qdrant_url) == "http://localhost:6333/"
    assert not s.is_production


def test_reads_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVENA_PORT", "9001")
    monkeypatch.setenv("PROVENA_LOG_FORMAT", "json")
    s = make()
    assert s.port == 9001
    assert s.log_format is LogFormat.JSON


def test_production_requires_json_logs() -> None:
    with pytest.raises(ValidationError, match="json"):
        make(env="production", log_format="console")
    assert make(env="production", log_format="json").is_production


@pytest.mark.parametrize(
    ("field", "value"), [("port", 0), ("log_level", "LOUD"), ("probe_timeout_s", 0)]
)
def test_rejects_invalid_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        make(**{field: value})


def test_api_key_is_not_leaked_in_repr() -> None:
    assert "hunter2" not in repr(make(qdrant_api_key="hunter2"))
