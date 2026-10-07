"""J-Quants API(V2)からTOPIXの日次四本値を取得する。

仕様: https://jpx-jquants.com/en/spec/idx-bars-daily-topix
    GET https://api.jquants.com/v2/indices/bars/daily/topix
    ヘッダー x-api-key にダッシュボードで発行したAPIキーを指定する。
    応答は {"data": [{"Date", "O", "H", "L", "C"}, ...], "pagination_key": ...}
"""

from __future__ import annotations

import os
from datetime import date

import pandas as pd
import requests

from topix_analysis.prices import normalize

BASE_URL = "https://api.jquants.com/v2"
TOPIX_PATH = "/indices/bars/daily/topix"
API_KEY_ENV = "JQUANTS_API_KEY"

# 応答のキー → 共通形式の列名
_FIELD_MAP = {"Date": "date", "O": "open", "H": "high", "L": "low", "C": "close"}


class JQuantsError(RuntimeError):
    """J-Quants API の呼び出しに失敗した。"""


class JQuantsClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = BASE_URL,
        session: requests.Session | None = None,
        timeout: float = 30.0,
    ) -> None:
        api_key = api_key or os.environ.get(API_KEY_ENV)
        if not api_key:
            raise JQuantsError(
                f"APIキーがありません。環境変数 {API_KEY_ENV} に設定してください。"
            )
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch_topix(
        self, start: date | str | None = None, end: date | str | None = None
    ) -> pd.DataFrame:
        """TOPIXの日次四本値を取得する。ページ分割された応答はすべて連結する。"""
        params: dict[str, str] = {}
        if start is not None:
            params["from"] = str(start)
        if end is not None:
            params["to"] = str(end)

        records: list[dict] = []
        while True:
            body = self._get(TOPIX_PATH, params)
            records.extend(body.get("data", []))
            key = body.get("pagination_key")
            if not key:
                break
            params = {**params, "pagination_key": key}

        return parse_topix_records(records)

    def _get(self, path: str, params: dict[str, str]) -> dict:
        try:
            resp = self._session.get(
                self._base_url + path,
                params=params,
                headers={"x-api-key": self._api_key},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise JQuantsError(f"J-Quants への接続に失敗しました: {exc}") from exc
        if resp.status_code != 200:
            raise JQuantsError(
                f"J-Quants がエラーを返しました (HTTP {resp.status_code}): {resp.text[:200]}"
            )
        return resp.json()


def parse_topix_records(records: list[dict]) -> pd.DataFrame:
    """J-Quants の応答レコードを共通形式の DataFrame に変換する。"""
    if not records:
        return normalize(pd.DataFrame(columns=list(_FIELD_MAP.values())))
    return normalize(pd.DataFrame(records).rename(columns=_FIELD_MAP))
