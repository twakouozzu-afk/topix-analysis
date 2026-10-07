"""手元のCSVファイルからTOPIXの四本値を読み込む。

英語・日本語・J-Quants 形式の列名と、UTF-8 / Shift_JIS(cp932) の文字コードに対応する。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from topix_analysis.prices import normalize

# 受け付ける列名(小文字・前後空白除去後)→ 共通形式の列名
_ALIASES = {
    "date": "date", "日付": "date", "年月日": "date",
    "open": "open", "o": "open", "始値": "open",
    "high": "high", "h": "high", "高値": "high",
    "low": "low", "l": "low", "安値": "low",
    "close": "close", "c": "close", "終値": "close",
}

_ENCODINGS = ("utf-8-sig", "cp932")


def read_price_csv(path: str | Path) -> pd.DataFrame:
    """CSVを読み込み、共通形式の DataFrame を返す。"""
    last_error: Exception | None = None
    for encoding in _ENCODINGS:
        try:
            raw = pd.read_csv(path, encoding=encoding, thousands=",")
            break
        except UnicodeDecodeError as exc:
            last_error = exc
    else:
        raise ValueError(f"文字コードを判別できません: {path}") from last_error

    renamed = {}
    for col in raw.columns:
        key = _ALIASES.get(str(col).strip().lower())
        if key and key not in renamed.values():
            renamed[col] = key
    return normalize(raw.rename(columns=renamed))
