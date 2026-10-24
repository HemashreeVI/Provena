from __future__ import annotations

import json
import logging

import pytest

from provena.config import LogFormat
from provena.logs import configure_logging, request_id_var


def test_json_logs_include_request_id_and_extras(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", LogFormat.JSON)
    token = request_id_var.set("req-42")
    try:
        logging.getLogger("provena.test").info("hello %s", "world", extra={"user": "u1"})
    finally:
        request_id_var.reset(token)

    record = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert record["msg"] == "hello world"
    assert record["level"] == "INFO"
    assert record["request_id"] == "req-42"
    assert record["user"] == "u1"


def test_json_logs_include_exceptions(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", LogFormat.JSON)
    try:
        raise ValueError("bad")
    except ValueError:
        logging.getLogger("provena.test").exception("failed")
    record = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert "ValueError: bad" in record["exc"]


def test_console_format_is_plain_text(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("DEBUG", LogFormat.CONSOLE)
    logging.getLogger("provena.test").debug("plain")
    line = capsys.readouterr().out.strip().splitlines()[-1]
    assert "DEBUG" in line
    assert line.endswith("plain")
