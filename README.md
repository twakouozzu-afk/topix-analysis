TOPIX分析用リポジトリ

## できること

- J-Quants API(JPX公式)から TOPIX の日次四本値(始値・高値・安値・終値)を取得
- 手元の CSV(英語/日本語の列名、UTF-8/Shift_JIS)の取り込み
- 取得データの保存(`data/topix.csv`、Git には含めません)
- 基本指標:騰落率、移動平均、変動率(年率)、最大下落率

## 準備

```bash
pip install -r requirements-dev.txt
pip install -e .
```

J-Quants から取得する場合は、ダッシュボードで発行した API キーを環境変数に設定します。
API キーはリポジトリに保存しないでください。

```bash
export JQUANTS_API_KEY="発行したAPIキー"
```

## 使い方

```bash
# J-Quants から取得して data/topix.csv に保存(既存データには追記)
python -m topix_analysis fetch --from 2024-01-01 --to 2024-12-31

# 手元の CSV を取り込む(サンプルは架空の値です)
python -m topix_analysis import-csv samples/topix_sample.csv

# 保存済みデータの要約を表示
python -m topix_analysis summary
```

## テスト

```bash
python -m pytest
```

テストはサンプルデータと J-Quants の模擬応答を使うため、ネット接続や API キーは不要です。

## 構成

```
src/topix_analysis/
├─ sources/jquants.py     J-Quants API(V2)からの取得
├─ sources/csv_source.py  CSV の取り込み
├─ prices.py              共通形式(date, open, high, low, close)への整形
├─ storage.py             CSV での保存・読み込み・追記
├─ indicators.py          基本指標
└─ cli.py                 コマンドの入口
```
