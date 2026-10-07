from topix_analysis.cli import main
from topix_analysis.storage import load_prices


def test_import_csv_then_summary(tmp_path, sample_csv, capsys):
    out = tmp_path / "topix.csv"
    assert main(["import-csv", str(sample_csv), "--out", str(out)]) == 0
    assert len(load_prices(out)) == 60

    # 同じデータを再度取り込んでも重複しない
    assert main(["import-csv", str(sample_csv), "--out", str(out)]) == 0
    assert len(load_prices(out)) == 60

    assert main(["summary", str(out)]) == 0
    assert "最大下落率" in capsys.readouterr().out


def test_fetch_without_api_key_fails_cleanly(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("JQUANTS_API_KEY", raising=False)
    assert main(["fetch", "--out", str(tmp_path / "x.csv")]) == 1
    assert "JQUANTS_API_KEY" in capsys.readouterr().err
