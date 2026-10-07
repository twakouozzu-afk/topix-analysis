"""コマンドラインの入口。

    python -m topix_analysis fetch --from 2024-01-01 --to 2024-12-31
    python -m topix_analysis import-csv samples/topix_sample.csv
    python -m topix_analysis summary
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from topix_analysis import indicators, storage
from topix_analysis.sources import JQuantsClient, JQuantsError, read_price_csv


def _save(df, out: Path) -> None:
    if out.exists():
        df = storage.merge_prices(storage.load_prices(out), df)
    storage.save_prices(df, out)
    print(f"{out} に保存しました({len(df)} 日分)")


def _cmd_fetch(args) -> int:
    try:
        df = JQuantsClient().fetch_topix(args.start, args.end)
    except JQuantsError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1
    print(f"J-Quants から {len(df)} 日分を取得しました")
    _save(df, args.out)
    return 0


def _cmd_import_csv(args) -> int:
    df = read_price_csv(args.path)
    print(f"{args.path} から {len(df)} 日分を読み込みました")
    _save(df, args.out)
    return 0


def _cmd_summary(args) -> int:
    s = indicators.summary(storage.load_prices(args.path))
    print(f"期間        : {s['start']} 〜 {s['end']}({s['days']} 日)")
    print(f"終値        : {s['first_close']:,.2f} → {s['last_close']:,.2f}")
    print(f"騰落率      : {s['total_return']:+.2%}")
    print(f"変動率(年率): {s['annualized_volatility']:.2%}")
    print(f"最大下落率  : {s['max_drawdown']:.2%}({s['max_drawdown_date']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="topix_analysis", description="TOPIX分析ツール")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fetch", help="J-Quants からTOPIXを取得して保存する")
    p.add_argument("--from", dest="start", help="開始日 (例: 2024-01-01)")
    p.add_argument("--to", dest="end", help="終了日 (例: 2024-12-31)")
    p.add_argument("--out", type=Path, default=storage.DEFAULT_PATH, help="保存先CSV")
    p.set_defaults(func=_cmd_fetch)

    p = sub.add_parser("import-csv", help="手元のCSVを読み込んで保存する")
    p.add_argument("path", type=Path, help="読み込むCSV")
    p.add_argument("--out", type=Path, default=storage.DEFAULT_PATH, help="保存先CSV")
    p.set_defaults(func=_cmd_import_csv)

    p = sub.add_parser("summary", help="保存済みデータの要約を表示する")
    p.add_argument("path", type=Path, nargs="?", default=storage.DEFAULT_PATH)
    p.set_defaults(func=_cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
