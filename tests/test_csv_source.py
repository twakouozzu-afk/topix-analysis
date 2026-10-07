import pytest

from topix_analysis.sources.csv_source import read_price_csv


def test_read_sample_csv(sample_csv):
    df = read_price_csv(sample_csv)
    assert list(df.columns) == ["date", "open", "high", "low", "close"]
    assert len(df) == 60
    assert df["date"].is_monotonic_increasing


def test_read_japanese_shift_jis_csv(tmp_path):
    path = tmp_path / "topix_sjis.csv"
    path.write_text(
        "日付,始値,高値,安値,終値\n"
        "2024/01/05,\"2,380.00\",\"2,400.00\",\"2,370.00\",\"2,390.50\"\n"
        "2024/01/04,\"2,350.00\",\"2,385.00\",\"2,340.00\",\"2,380.00\"\n",
        encoding="cp932",
    )
    df = read_price_csv(path)
    assert df["date"].dt.strftime("%Y-%m-%d").tolist() == ["2024-01-04", "2024-01-05"]
    assert df["close"].tolist() == [2380.0, 2390.5]


def test_read_jquants_style_columns(tmp_path):
    path = tmp_path / "jq.csv"
    path.write_text("Date,O,H,L,C\n2024-01-04,1,2,0.5,1.5\n", encoding="utf-8")
    assert read_price_csv(path)["close"].tolist() == [1.5]


def test_missing_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("Date,Open,High,Low\n2024-01-04,1,2,0.5\n", encoding="utf-8")
    with pytest.raises(ValueError, match="close"):
        read_price_csv(path)
