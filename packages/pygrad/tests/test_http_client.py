"""Tests for external API HTTP client helpers."""

from __future__ import annotations

import httpx
import pytest

from pygrad.graphrag.http_client import create_sync_client, post_json_with_retries


def test_create_sync_client_uses_ipv4_local_address() -> None:
    with create_sync_client() as client:
        transport = client._transport
        assert transport._pool._local_address == "0.0.0.0"


def test_post_json_with_retries_recovers_from_transient_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}

    def fake_post(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.ConnectError("[Errno 101] Network is unreachable")
        request = httpx.Request("POST", "https://example.com/embeddings")
        return httpx.Response(200, json={"data": [{"embedding": [0.1, 0.2]}]}, request=request)

    client = httpx.Client()
    monkeypatch.setattr(client, "post", fake_post)
    monkeypatch.setattr("pygrad.graphrag.http_client.time.sleep", lambda _seconds: None)

    response = post_json_with_retries(
        client,
        "https://example.com/embeddings",
        json={"model": "test", "input": "hello"},
        headers={"Authorization": "Bearer test"},
        retries=2,
    )

    assert response.status_code == 200
    assert attempts["count"] == 2

    client.close()


def test_post_json_with_retries_raises_after_exhausting_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("[Errno 101] Network is unreachable")

    client = httpx.Client()
    monkeypatch.setattr(client, "post", fake_post)
    monkeypatch.setattr("pygrad.graphrag.http_client.time.sleep", lambda _seconds: None)

    with pytest.raises(httpx.ConnectError):
        post_json_with_retries(
            client,
            "https://example.com/embeddings",
            json={"model": "test", "input": "hello"},
            headers={"Authorization": "Bearer test"},
            retries=2,
        )

    client.close()
