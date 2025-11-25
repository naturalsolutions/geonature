import pytest

from geonature.utils import utilsmails
from geonature.utils.utilsmails import send_mail


class _FailingSMTPContext:
    def __enter__(self):
        raise AssertionError("SMTP path should not be used when provider=graph")

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def test_send_mail_via_graph(monkeypatch, app):
    calls = []

    def fake_post(url, data=None, headers=None, json=None, timeout=None):
        if "oauth2/v2.0/token" in url:
            return _FakeResponse({"access_token": "token-abc"}, 200)
        if "sendMail" in url:
            calls.append({"url": url, "headers": headers, "json": json})
            return _FakeResponse({}, 202)
        raise AssertionError(f"Unexpected URL {url}")

    monkeypatch.setattr(utilsmails.requests, "post", fake_post)
    monkeypatch.setattr(utilsmails.MAIL, "connect", lambda *a, **k: _FailingSMTPContext())

    app.config["MAIL_CONFIG"] = {
        "PROVIDER": "graph",
        "GRAPH_TENANT_ID": "tenant-id",
        "GRAPH_CLIENT_ID": "client-id",
        "GRAPH_CLIENT_SECRET": "client-secret",
        "GRAPH_SCOPE": "https://graph.microsoft.com/.default",
        "GRAPH_SENDER": "sender@example.com",
    }

    with app.app_context():
        send_mail(["User <user@example.com>", "other@example.com"], "Subject", "<p>Body</p>")

    assert len(calls) == 1
    payload = calls[0]["json"]
    assert payload["message"]["subject"] == "Subject"
    assert len(payload["message"]["toRecipients"]) == 2
    assert payload["message"]["toRecipients"][0]["emailAddress"]["name"] == "User"
    assert calls[0]["headers"].get("Authorization", "").startswith("Bearer token-abc")
