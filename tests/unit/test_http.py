"""Unit tests for http.py helpers: client.get interface, retry predicate, and cache."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx
import pytest

from paper_search.http import (
    DEFAULT_CACHE_TTL_SECONDS,
    ResponseCache,
    _get,
    _should_retry,
    fetch_json,
    fetch_text,
)

URL = "https://api.example.com/search"
PARAMS = {"query": "sampling"}


class _ClientStub:
    """Async get() interface stub: records calls and returns a canned response or error."""

    def __init__(self, response: httpx.Response | None = None, error: BaseException | None = None) -> None:
        self._response = response
        self._error = error
        self.calls: list[tuple[str, dict[str, Any] | None, dict[str, str] | None]] = []

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        self.calls.append((url, params, headers))
        if self._error is not None:
            raise self._error
        return self._response


def _run(awaitable: Any) -> Any:
    return asyncio.run(awaitable)


def test_get_issues_request_with_params() -> None:
    request = httpx.Request("GET", URL)
    response = httpx.Response(200, json={"ok": True}, request=request)
    client = _ClientStub(response=response)

    got = _run(_get(client, URL, PARAMS))

    assert client.calls == [(URL, PARAMS, None)]
    assert got is response


def test_get_forwards_headers() -> None:
    request = httpx.Request("GET", URL)
    response = httpx.Response(200, json={"ok": True}, request=request)
    client = _ClientStub(response=response)
    headers = {"x-api-key": "secret"}

    got = _run(_get(client, URL, PARAMS, headers=headers))

    assert client.calls == [(URL, PARAMS, headers)]
    assert got is response


def test_get_raises_for_error_status() -> None:
    request = httpx.Request("GET", URL)
    response = httpx.Response(404, request=request)
    client = _ClientStub(response=response)

    with pytest.raises(httpx.HTTPStatusError):
        _run(_get(client, URL, PARAMS))


@pytest.mark.parametrize(
    "error",
    [
        httpx.ConnectError("down"),
        httpx.TimeoutException("slow"),
    ],
)
def test_should_retry_true_for_transport_errors(error: BaseException) -> None:
    assert _should_retry(error)


def test_should_retry_true_for_retriable_status() -> None:
    request = httpx.Request("GET", URL)
    error = httpx.HTTPStatusError("boom", request=request, response=httpx.Response(429, request=request))
    assert _should_retry(error)


def test_should_retry_false_for_permanent_status() -> None:
    request = httpx.Request("GET", URL)
    error = httpx.HTTPStatusError("boom", request=request, response=httpx.Response(404, request=request))
    assert not _should_retry(error)


def test_should_retry_false_for_other_exceptions() -> None:
    assert not _should_retry(ValueError("nope"))


def test_fetch_json_returns_parsed_body() -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, json={"items": [1]}, request=request))

    data = _run(fetch_json(client, URL, params=PARAMS))

    assert data == {"items": [1]}
    assert client.calls == [(URL, PARAMS, None)]


def test_fetch_json_forwards_headers() -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, json={"items": [1]}, request=request))
    headers = {"x-api-key": "secret"}

    data = _run(fetch_json(client, URL, params=PARAMS, headers=headers))

    assert data == {"items": [1]}
    assert client.calls == [(URL, PARAMS, headers)]


def test_fetch_text_returns_raw_body() -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, text="<feed/>", request=request))

    text = _run(fetch_text(client, URL, params=PARAMS))

    assert text == "<feed/>"


def test_fetch_text_forwards_headers() -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, text="<feed/>", request=request))
    headers = {"x-api-key": "secret"}

    text = _run(fetch_text(client, URL, params=PARAMS, headers=headers))

    assert text == "<feed/>"
    assert client.calls == [(URL, PARAMS, headers)]


def test_fetch_json_uses_cache_on_second_call(tmp_path) -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, json={"items": [1]}, request=request))
    cache = ResponseCache(cache_dir=tmp_path)

    first = _run(fetch_json(client, URL, params=PARAMS, cache=cache))
    second = _run(fetch_json(client, URL, params=PARAMS, cache=cache))

    assert first == second == {"items": [1]}
    assert len(client.calls) == 1


def test_fetch_json_cache_key_excludes_headers(tmp_path) -> None:
    request = httpx.Request("GET", URL)
    client = _ClientStub(response=httpx.Response(200, json={"items": [1]}, request=request))
    cache = ResponseCache(cache_dir=tmp_path)
    headers = {"x-api-key": "secret"}

    first = _run(fetch_json(client, URL, params=PARAMS, headers=headers, cache=cache))
    second = _run(fetch_json(client, URL, params=PARAMS, cache=cache))

    assert first == second == {"items": [1]}
    assert len(client.calls) == 1
    payload = json.loads(next(tmp_path.iterdir()).read_text())
    assert "secret" not in json.dumps(payload)


def test_cache_roundtrip_with_default_ttl(tmp_path) -> None:
    cache = ResponseCache(cache_dir=tmp_path)
    assert cache.get(URL, PARAMS) is None

    cache.set(URL, PARAMS, {"n": 1})

    assert cache.get(URL, PARAMS) == {"n": 1}


def test_cache_expires_after_ttl(tmp_path) -> None:
    cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=1)
    cache.set(URL, PARAMS, {"n": 1})
    payload_path = next(tmp_path.iterdir())
    payload = json.loads(payload_path.read_text())
    payload["cached_at"] = time.time() - DEFAULT_CACHE_TTL_SECONDS - 1
    payload_path.write_text(json.dumps(payload))

    assert cache.get(URL, PARAMS) is None


def test_cache_ignores_corrupt_file(tmp_path) -> None:
    cache = ResponseCache(cache_dir=tmp_path)
    cache.set(URL, PARAMS, {"n": 1})
    next(tmp_path.iterdir()).write_text("not json")

    assert cache.get(URL, PARAMS) is None


def test_cache_set_creates_nested_directory(tmp_path) -> None:
    cache = ResponseCache(cache_dir=tmp_path / "missing" / "nested")

    cache.set(URL, PARAMS, {"n": 1})

    assert cache.get(URL, PARAMS) == {"n": 1}
