"""分数解析、四则运算与练习题生成。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, List, Optional, Sequence, Tuple

OPS = ("+", "-", "*", "/")
OP_LABELS = {"+": "加", "-": "减", "*": "乘", "/": "除"}

_MIXED = re.compile(r"^(-?\d+)\s+(\d+)\s*/\s*(\d+)$")
_SIMPLE = re.compile(r"^(-?\d+)\s*/\s*(\d+)$")
_INTEGER = re.compile(r"^(-?\d+)$")


class FractionError(ValueError):
    """分数写法或题目参数不合法。"""


def parse_fraction(text: str) -> Fraction:
    """解析 3/4、1 1/2、-2 这样的写法。"""
    if not isinstance(text, str):
        raise FractionError("分数必须是字符串")
    cleaned = text.strip()
    if not cleaned:
        raise FractionError("分数不能为空")
    mixed = _MIXED.match(cleaned)
    if mixed:
        whole = int(mixed.group(1))
        numerator = int(mixed.group(2))
        denominator = int(mixed.group(3))
        if denominator == 0:
            raise FractionError("分母不能为 0")
        sign = -1 if whole < 0 else 1
        return sign * (abs(whole) + Fraction(numerator, denominator))
    simple = _SIMPLE.match(cleaned)
    if simple:
        numerator = int(simple.group(1))
        denominator = int(simple.group(2))
        if denominator == 0:
            raise FractionError("分母不能为 0")
        return Fraction(numerator, denominator)
    integer = _INTEGER.match(cleaned)
    if integer:
        return Fraction(int(integer.group(1)))
    raise FractionError("无法识别的分数：%s" % text)


def format_fraction(value: Fraction) -> str:
    """化成最简分数，整数不带分母。"""
    if not isinstance(value, Fraction):
        raise FractionError("需要 Fraction 对象")
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


def mixed_parts(value: Fraction) -> Tuple[int, int, int]:
    """返回带分数的整数部分、分子与分母。"""
    if not isinstance(value, Fraction):
        raise FractionError("需要 Fraction 对象")
    sign = -1 if value < 0 else 1
    whole, remainder = divmod(abs(value.numerator), value.denominator)
    return sign * whole, remainder, value.denominator


def format_mixed(value: Fraction) -> str:
    """化成带分数，例如 5/4 -> 1 1/4。"""
    whole, numerator, denominator = mixed_parts(value)
    if numerator == 0:
        return str(whole)
    sign = "-" if value < 0 else ""
    if whole == 0:
        return "%s%d/%d" % (sign, numerator, denominator)
    return "%s%d %d/%d" % (sign, abs(whole), numerator, denominator)


def format_answer(value: Fraction) -> str:
    improper = format_fraction(value)
    mixed = format_mixed(value)
    if mixed != improper:
        return "%s（%s）" % (improper, mixed)
    return improper


def check_op(op: str) -> str:
    if op not in OPS:
        raise FractionError("运算符必须是 +、-、* 或 /，收到 %r" % (op,))
    return op


def apply_operation(left: Fraction, op: str, right: Fraction) -> Fraction:
    check_op(op)
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if right == 0:
        raise FractionError("除数不能为 0")
    return left / right


@dataclass(frozen=True)
class WorksheetItem:
    """一道分数运算题。"""

    left: Fraction
    op: str
    right: Fraction

    def __post_init__(self) -> None:
        if not isinstance(self.left, Fraction) or not isinstance(self.right, Fraction):
            raise FractionError("运算数必须是 Fraction")
        check_op(self.op)
        if self.op == "/" and self.right == 0:
            raise FractionError("除数不能为 0")

    @property
    def answer(self) -> Fraction:
        return apply_operation(self.left, self.op, self.right)

    @property
    def answer_text(self) -> str:
        return format_answer(self.answer)

    @property
    def question(self) -> str:
        return "%s %s %s =" % (
            format_fraction(self.left),
            self.op,
            format_fraction(self.right),
        )


def _proper_fractions(max_denominator: int) -> List[Fraction]:
    values = []
    for denominator in range(2, max_denominator + 1):
        for numerator in range(1, denominator):
            values.append(Fraction(numerator, denominator))
    return values


def build_worksheet(
    count: int,
    ops: Sequence[str] = ("+", "-"),
    seed: Optional[int] = None,
    max_denominator: int = 12,
    allow_negative: bool = False,
) -> List[WorksheetItem]:
    """生成分数四则运算练习题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise FractionError("题目数量必须是正整数")
    if isinstance(max_denominator, bool) or not isinstance(max_denominator, int):
        raise FractionError("最大分母必须是整数")
    if max_denominator < 2:
        raise FractionError("最大分母不能小于 2")
    if not ops:
        raise FractionError("至少需要一种运算符")
    checked_ops = [check_op(op) for op in ops]
    pool = _proper_fractions(max_denominator)
    if len(pool) < 2:
        raise FractionError("可用分数不足")
    rng = random.Random(seed)
    items: List[WorksheetItem] = []
    seen = set()
    attempts = 0
    limit = count * 500 + 500
    while len(items) < count and attempts < limit:
        attempts += 1
        left = rng.choice(pool)
        right = rng.choice(pool)
        op = rng.choice(checked_ops)
        if op == "-" and not allow_negative and left < right:
            left, right = right, left
        if op == "/" and right == 0:
            continue
        key = (left, op, right)
        if key in seen:
            continue
        seen.add(key)
        items.append(WorksheetItem(left, op, right))
    if len(items) < count:
        raise FractionError("可用的不重复题目不足 %d 道" % count)
    return items


def check_answer(item: WorksheetItem, text: str) -> bool:
    """答案必须与标准答案完全相等，允许写成带分数。"""
    try:
        value = parse_fraction(text)
    except FractionError:
        return False
    return value == item.answer
