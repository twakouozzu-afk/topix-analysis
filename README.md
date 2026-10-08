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

J-Quants から取得するには、ダッシュボードで発行した API キーが必要です。
API キーはリポジトリ・チャット・GitHub には保存しないでください。

**手元の Mac で使う場合**:キーをキーチェーンに保存し、使うときだけ環境変数に読み込みます。

```bash
# 1回だけ:キーチェーンに保存(入力したキーは画面に表示されません)
security add-generic-password -a "$USER" -s jquants-api-key -w

# 使うたびに:キーチェーンから読み込む
export JQUANTS_API_KEY="$(security find-generic-password -a "$USER" -s jquants-api-key -w)"
```

**Claude Code のクラウド環境で使う場合**:環境設定の **API credentials** に登録します
(Pro / Max プラン)。キーは環境変数に現れず、プロキシが送信時にヘッダーを付けます。

| 項目 | 値 |
|---|---|
| Allowed websites | `api.jquants.com` |
| Custom headers の Name | `x-api-key` |
| Custom headers の Prefix | 空欄(`Bearer` を消す) |
| Custom headers の Value | API キー |

`JQUANTS_API_KEY` が未設定のときは x-api-key ヘッダーを付けずに送信し、プロキシに任せます。

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
