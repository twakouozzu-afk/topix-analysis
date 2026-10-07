import math

import pytest

from topix_analysis import indicators


def test_daily_returns(prices):
    r = indicators.daily_returns(prices)
    assert math.isnan(r.iloc[0])
    assert r.iloc[1:].tolist() == pytest.approx([-0.1, 0.0555555, 0.1578947], rel=1e-5)


def test_moving_average(prices):
    ma = indicators.moving_average(prices, 2)
    assert ma.iloc[1:].tolist() == pytest.approx([104.5, 101.75, 112.75])


def test_drawdown(prices):
    dd = indicators.drawdown(prices)
    assert dd.tolist() == pytest.approx([0.0, -0.1, -0.05, 0.0])


def test_summary(prices):
    s = indicators.summary(prices)
    assert s["days"] == 4
    assert s["total_return"] == pytest.approx(0.1)
    assert s["max_drawdown"] == pytest.approx(-0.1)
    assert str(s["max_drawdown_date"]) == "2024-01-05"
    assert s["annualized_volatility"] > 0


def test_volatility_window(prices):
    vol = indicators.volatility(prices, window=2)
    assert vol.isna().sum() == 2
