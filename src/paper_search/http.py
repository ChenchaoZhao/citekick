"""HTTP helpers: retries, backoff, and a small on-disk JSON response cache."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

_RETRIES: int = 3
_RETRY_BACKOFF_MAX_SECONDS: float = 10.0
DEFAULT_CACHE_TTL_SECONDS: int = 7 * 24 * 60 * 60
_DEFAULT_CACHE_DIR: Path = Path.home() / ".cache" / "paper-search"
_RETRIABLE_STATUS_CODES: frozenset[int] = frozenset({408, 429, 500, 502, 503, 504})


def _should_retry(exception: BaseException) -> bool:
    if isinstance(exception, httpx.TransportError):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in _RETRIABLE_STATUS_CODES
    return False


@retry(
    stop=stop_after_attempt(_RETRIES),
    wait=wait_exponential(multiplier=1.0, max=_RETRY_BACKOFF_MAX_SECONDS),
    retry=retry_if_exception(_should_retry),
    reraise=True,
)
async def _get(
    client: httpx.AsyncClient,
    url: str,
    params: dict[str, Any] | None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    response = await client.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response


class ResponseCache:
    """Tiny on-disk JSON cache keyed by request URL and params."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    ) -> None:
        self._cache_dir = cache_dir or _DEFAULT_CACHE_DIR
        self._ttl_seconds = ttl_seconds

    def get(self, url: str, params: dict[str, Any] | None) -> Any | None:
        path = self._path_for(url, params)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if time.time() - payload["cached_at"] > self._ttl_seconds:
            return None
        return payload["data"]

    def set(self, url: str, params: dict[str, Any] | None, data: Any) -> None:
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {"cached_at": time.time(), "data": data}
            self._path_for(url, params).write_text(json.dumps(payload))
        except OSError:
            return

    def _path_for(self, url: str, params: dict[str, Any] | None) -> Path:
        return self._cache_dir / f"{_cache_key(url, params)}.json"


def _cache_key(url: str, params: dict[str, Any] | None) -> str:
    payload = json.dumps({"url": url, "params": params}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


async def fetch_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    cache: ResponseCache | None = None,
) -> Any:
    """GET a URL, retrying transient failures, and return parsed JSON.

    ``headers`` are never part of the cache key: responses are identical
    regardless of an API key, so keyed and keyless calls share one entry.
    """
    if cache is not None:
        cached = cache.get(url, params)
        if cached is not None:
            return cached
    data = (await _get(client, url, params=params, headers=headers)).json()
    if cache is not None:
        cache.set(url, params, data)
    return data


async def fetch_text(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    cache: ResponseCache | None = None,
) -> str:
    """GET a URL, retrying transient failures, and return the response text.

    ``headers`` are never part of the cache key: responses are identical
    regardless of an API key, so keyed and keyless calls share one entry.
    """
    if cache is not None:
        cached = cache.get(url, params)
        if cached is not None:
            return cached
    text = (await _get(client, url, params=params, headers=headers)).text
    if cache is not None:
        cache.set(url, params, text)
    return text
