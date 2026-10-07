"""価格データの共通形式への整形。"""

from __future__ import annotations

import pandas as pd

from topix_analysis import PRICE_COLUMNS


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """共通形式(date, open, high, low, close)に整え、日付順に並べる。

    同じ日付が複数ある場合は後の行を残す。終値が欠けた行は捨てる。
    """
    missing = [c for c in PRICE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"必要な列がありません: {', '.join(missing)}")

    out = df[PRICE_COLUMNS].copy()
    out["date"] = pd.to_datetime(out["date"])
    for col in PRICE_COLUMNS[1:]:
        out[col] = pd.to_numeric(out[col], errors="coerce").astype(float)

    out = out.dropna(subset=["date", "close"])
    out = out.drop_duplicates(subset="date", keep="last")
    return out.sort_values("date").reset_index(drop=True)
