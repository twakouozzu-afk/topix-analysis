import pandas as pd

from topix_analysis.storage import load_prices, merge_prices, save_prices


def test_save_and_load_roundtrip(tmp_path, prices):
    path = save_prices(prices, tmp_path / "sub" / "topix.csv")
    pd.testing.assert_frame_equal(load_prices(path), prices)


def test_merge_overwrites_same_date(prices):
    update = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-10", "2024-01-11"]),
         "open": [1.0, 2.0], "high": [1.0, 2.0], "low": [1.0, 2.0], "close": [1.0, 2.0]}
    )
    merged = merge_prices(prices, update)
    assert len(merged) == 5
    assert merged.set_index("date").loc["2024-01-10", "close"] == 1.0
