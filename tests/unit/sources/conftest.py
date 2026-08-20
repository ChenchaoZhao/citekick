"""Shared fixtures for per-source strategy unit tests: mock the http interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

CallRecord = tuple[str, dict[str, Any] | None, dict[str, str] | None, Any]


@pytest.fixture
def client() -> httpx.AsyncClient:
    """An AsyncClient the strategies can hold; never used (http is mocked)."""
    return httpx.AsyncClient()


@pytest.fixture
def mock_fetch(monkeypatch: pytest.MonkeyPatch) -> Callable[..., list[CallRecord]]:
    """Patch a strategy module's fetch_json/fetch_text and record every call.

    The recorded list lets tests assert the url, params, headers, and cache that
    each strategy passes to the http interface. `payload` may be a plain value
    or a callable taking (url, params) so multi-call strategies (e.g. PubMed)
    can return different payloads per request.
    """

    calls: list[CallRecord] = []

    def install(module: Any, func_name: str, payload: Any) -> list[CallRecord]:
        async def fake(
            _client: httpx.AsyncClient,
            url: str,
            *,
            params: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            cache: Any = None,
        ) -> Any:
            calls.append((url, params, headers, cache))
            return payload(url, params) if callable(payload) else payload

        monkeypatch.setattr(module, func_name, fake)
        return calls

    return install
