"""価格データのCSV保存・読み込み。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from topix_analysis.prices import normalize

DEFAULT_PATH = Path("data/topix.csv")


def save_prices(df: pd.DataFrame, path: str | Path = DEFAULT_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = normalize(df)
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False)
    return path


def load_prices(path: str | Path = DEFAULT_PATH) -> pd.DataFrame:
    return normalize(pd.read_csv(path))


def merge_prices(existing: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """既存データに新しいデータを追加する。同じ日付は新しいデータで上書きする。"""
    return normalize(pd.concat([existing, new], ignore_index=True))
