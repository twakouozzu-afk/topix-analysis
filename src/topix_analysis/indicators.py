"""TOPIXの基本指標。入力はいずれも共通形式の DataFrame。"""

from __future__ import annotations

import math

import pandas as pd

TRADING_DAYS_PER_YEAR = 245  # 東証の年間営業日数の目安


def daily_returns(df: pd.DataFrame) -> pd.Series:
    """終値の前日比騰落率(0.01 = 1%)。"""
    return df.set_index("date")["close"].pct_change()


def moving_average(df: pd.DataFrame, window: int) -> pd.Series:
    """終値の単純移動平均。"""
    return df.set_index("date")["close"].rolling(window).mean()


def volatility(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """日次騰落率の移動標準偏差を年率換算した変動率。"""
    return daily_returns(df).rolling(window).std() * math.sqrt(TRADING_DAYS_PER_YEAR)


def drawdown(df: pd.DataFrame) -> pd.Series:
    """終値のそれまでの最高値からの下落率(0 以下)。"""
    close = df.set_index("date")["close"]
    return close / close.cummax() - 1


def summary(df: pd.DataFrame) -> dict:
    """期間全体の要約。"""
    if df.empty:
        raise ValueError("データがありません")
    first, last = df.iloc[0], df.iloc[-1]
    returns = daily_returns(df).dropna()
    dd = drawdown(df)
    return {
        "start": first["date"].date(),
        "end": last["date"].date(),
        "days": len(df),
        "first_close": float(first["close"]),
        "last_close": float(last["close"]),
        "total_return": float(last["close"] / first["close"] - 1),
        "annualized_volatility": (
            float(returns.std() * math.sqrt(TRADING_DAYS_PER_YEAR))
            if len(returns) > 1 else float("nan")
        ),
        "max_drawdown": float(dd.min()),
        "max_drawdown_date": dd.idxmin().date(),
    }
