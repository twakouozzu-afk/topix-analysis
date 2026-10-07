import pytest

from topix_analysis.sources.jquants import JQuantsClient, JQuantsError, parse_topix_records


class FakeResponse:
    def __init__(self, body, status_code=200):
        self._body = body
        self.status_code = status_code
        self.text = str(body)

    def json(self):
        return self._body


class FakeSession:
    """J-Quants の代わりに決まった応答を順番に返す。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": dict(params), "headers": headers})
        return self.responses.pop(0)


PAGE1 = {
    "data": [
        {"Date": "2024-01-05", "O": 2380.0, "H": 2400.0, "L": 2370.0, "C": 2390.5},
        {"Date": "2024-01-04", "O": 2350.0, "H": 2385.0, "L": 2340.0, "C": 2380.0},
    ],
    "pagination_key": "next.page.",
}
PAGE2 = {"data": [{"Date": "2024-01-09", "O": 2391.0, "H": 2420.0, "L": 2388.0, "C": 2415.25}]}


def test_fetch_topix_follows_pagination_and_sends_api_key():
    session = FakeSession([FakeResponse(PAGE1), FakeResponse(PAGE2)])
    client = JQuantsClient("dummy-key", session=session)

    df = client.fetch_topix("2024-01-01", "2024-01-31")

    assert list(df.columns) == ["date", "open", "high", "low", "close"]
    assert df["date"].dt.strftime("%Y-%m-%d").tolist() == ["2024-01-04", "2024-01-05", "2024-01-09"]
    assert df["close"].tolist() == [2380.0, 2390.5, 2415.25]

    assert len(session.calls) == 2
    first, second = session.calls
    assert first["url"] == "https://api.jquants.com/v2/indices/bars/daily/topix"
    assert first["headers"] == {"x-api-key": "dummy-key"}
    assert first["params"] == {"from": "2024-01-01", "to": "2024-01-31"}
    assert second["params"]["pagination_key"] == "next.page."


def test_api_key_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("JQUANTS_API_KEY", "env-key")
    session = FakeSession([FakeResponse({"data": []})])

    df = JQuantsClient(session=session).fetch_topix()

    assert df.empty
    assert session.calls[0]["headers"] == {"x-api-key": "env-key"}
    assert session.calls[0]["params"] == {}


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("JQUANTS_API_KEY", raising=False)
    with pytest.raises(JQuantsError, match="JQUANTS_API_KEY"):
        JQuantsClient()


def test_http_error_raises():
    session = FakeSession([FakeResponse({"message": "Invalid API key"}, status_code=403)])
    with pytest.raises(JQuantsError, match="HTTP 403"):
        JQuantsClient("bad", session=session).fetch_topix()


def test_parse_empty_records():
    df = parse_topix_records([])
    assert df.empty
    assert list(df.columns) == ["date", "open", "high", "low", "close"]
