"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    OPS,
    FractionError,
    apply_operation,
    build_worksheet,
    format_answer,
    parse_fraction,
)
from .render import render_worksheet


def parse_ops(text: str) -> List[str]:
    """把 +,- 或 + - 这样的写法拆成运算符列表。"""
    cleaned = text.replace("+", " + ").replace("*", " * ").replace("/", " / ")
    parts = [part for part in cleaned.replace(",", " ").split() if part]
    if not parts:
        raise FractionError("请至少给出一种运算符")
    for part in parts:
        if part not in OPS:
            raise FractionError("不支持的运算符：%s" % part)
    return parts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fractionops",
        description="分数四则运算：计算、约分与可打印 A4 练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    calc_parser = subparsers.add_parser("calc", help="计算两个分数")
    calc_parser.add_argument("left", help="左操作数，例如 3/4 或 1 1/2")
    calc_parser.add_argument("op", choices=OPS, help="运算符")
    calc_parser.add_argument("right", help="右操作数")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=20, help="题目数量，默认 20")
    sheet_parser.add_argument("--ops", default="+,-", help="运算符集合，默认 +,-")
    sheet_parser.add_argument("--max-den", type=int, default=12, help="最大分母，默认 12")
    sheet_parser.add_argument("--negative", action="store_true", help="允许减法出现负数")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="分数四则运算练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案页")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "calc":
            result = apply_operation(
                parse_fraction(args.left), args.op, parse_fraction(args.right)
            )
            print("%s %s %s = %s" % (args.left.strip(), args.op, args.right.strip(), format_answer(result)))
            return 0
        ops = parse_ops(args.ops)
        items = build_worksheet(
            args.count, ops, args.seed, args.max_den, allow_negative=args.negative
        )
        _write_output(
            render_worksheet(items, args.title, include_answers=args.answers),
            args.output,
        )
        return 0
    except FractionError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
