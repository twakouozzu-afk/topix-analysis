"""TOPIX分析用パッケージ。

価格データは共通して次の列を持つ pandas.DataFrame で扱う。
    date (datetime64), open, high, low, close (float)
"""

PRICE_COLUMNS = ["date", "open", "high", "low", "close"]

__version__ = "0.1.0"
