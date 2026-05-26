"""HTTP client helpers for external embedding and LLM APIs."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

import httpx

# Docker bridge networks often resolve AAAA records but have no IPv6 route.
_IPV4_LOCAL_ADDRESS = "0.0.0.0"
_DEFAULT_TIMEOUT_SEC = 60.0
_DEFAULT_RETRIES = 3
_DEFAULT_RETRY_BACKOFF_SEC = 2.0
_RETRYABLE_EXCEPTIONS = (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)


def create_sync_client(timeout: float = _DEFAULT_TIMEOUT_SEC) -> httpx.Client:
    """Create a sync client that prefers IPv4 for outbound requests."""
    transport = httpx.HTTPTransport(local_address=_IPV4_LOCAL_ADDRESS)
    return httpx.Client(timeout=timeout, transport=transport)


def create_async_client(timeout: float = _DEFAULT_TIMEOUT_SEC) -> httpx.AsyncClient:
    """Create an async client that prefers IPv4 for outbound requests."""
    transport = httpx.AsyncHTTPTransport(local_address=_IPV4_LOCAL_ADDRESS)
    return httpx.AsyncClient(timeout=timeout, transport=transport)


def post_json_with_retries(
    client: httpx.Client,
    url: str,
    *,
    json: Mapping[str, Any],
    headers: Mapping[str, str],
    retries: int = _DEFAULT_RETRIES,
    backoff_sec: float = _DEFAULT_RETRY_BACKOFF_SEC,
) -> httpx.Response:
    """POST JSON and retry transient network failures."""
    last_exc: Exception | None = None
    payload = dict(json)
    request_headers = dict(headers)

    for attempt in range(retries):
        try:
            response = client.post(url, json=payload, headers=request_headers)
            response.raise_for_status()
            return response
        except _RETRYABLE_EXCEPTIONS as exc:
            last_exc = exc
            if attempt + 1 >= retries:
                break
            time.sleep(backoff_sec * (attempt + 1))

    assert last_exc is not None
    raise last_exc
