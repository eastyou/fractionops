"""模型层测试。"""

import unittest
from fractions import Fraction

from fractionops.model import (
    FractionError,
    WorksheetItem,
    apply_operation,
    build_worksheet,
    check_answer,
    check_op,
    format_answer,
    format_fraction,
    format_mixed,
    mixed_parts,
    parse_fraction,
)


class ParseTest(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(parse_fraction("3/4"), Fraction(3, 4))

    def test_reduces(self):
        self.assertEqual(parse_fraction("6/8"), Fraction(3, 4))

    def test_integer(self):
        self.assertEqual(parse_fraction("5"), Fraction(5, 1))

    def test_negative_integer(self):
        self.assertEqual(parse_fraction("-7"), Fraction(-7, 1))

    def test_negative_fraction(self):
        self.assertEqual(parse_fraction("-3/4"), Fraction(-3, 4))

    def test_mixed(self):
        self.assertEqual(parse_fraction("1 1/2"), Fraction(3, 2))

    def test_negative_mixed(self):
        self.assertEqual(parse_fraction("-1 1/2"), Fraction(-3, 2))

    def test_zero_numerator(self):
        self.assertEqual(parse_fraction("0/5"), Fraction(0, 1))

    def test_spaces(self):
        self.assertEqual(parse_fraction("  2 / 3  "), Fraction(2, 3))

    def test_zero_denominator(self):
        with self.assertRaises(FractionError):
            parse_fraction("1/0")

    def test_mixed_zero_denominator(self):
        with self.assertRaises(FractionError):
            parse_fraction("1 1/0")

    def test_empty(self):
        with self.assertRaises(FractionError):
            parse_fraction("  ")

    def test_garbage(self):
        with self.assertRaises(FractionError):
            parse_fraction("three quarters")

    def test_non_string(self):
        with self.assertRaises(FractionError):
            parse_fraction(0.75)


class FormatTest(unittest.TestCase):
    def test_improper(self):
        self.assertEqual(format_fraction(Fraction(3, 2)), "3/2")

    def test_integer(self):
        self.assertEqual(format_fraction(Fraction(4, 2)), "2")

    def test_mixed(self):
        self.assertEqual(format_mixed(Fraction(5, 4)), "1 1/4")

    def test_mixed_negative(self):
        self.assertEqual(format_mixed(Fraction(-3, 2)), "-1 1/2")

    def test_negative_proper(self):
        self.assertEqual(format_mixed(Fraction(-1, 2)), "-1/2")

    def test_integer_mixed(self):
        self.assertEqual(format_mixed(Fraction(3, 1)), "3")

    def test_parts(self):
        self.assertEqual(mixed_parts(Fraction(7, 4)), (1, 3, 4))

    def test_answer_with_mixed(self):
        self.assertEqual(format_answer(Fraction(5, 4)), "5/4（1 1/4）")

    def test_answer_integer(self):
        self.assertEqual(format_answer(Fraction(2, 1)), "2")


class OperationTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(apply_operation(Fraction(1, 2), "+", Fraction(1, 3)), Fraction(5, 6))

    def test_subtract(self):
        self.assertEqual(apply_operation(Fraction(3, 4), "-", Fraction(1, 4)), Fraction(1, 2))

    def test_subtract_negative(self):
        self.assertEqual(apply_operation(Fraction(1, 4), "-", Fraction(3, 4)), Fraction(-1, 2))

    def test_multiply(self):
        self.assertEqual(apply_operation(Fraction(2, 3), "*", Fraction(3, 4)), Fraction(1, 2))

    def test_divide(self):
        self.assertEqual(apply_operation(Fraction(1, 2), "/", Fraction(3, 4)), Fraction(2, 3))

    def test_divide_by_zero(self):
        with self.assertRaises(FractionError):
            apply_operation(Fraction(1, 2), "/", Fraction(0))

    def test_invalid_operator(self):
        with self.assertRaises(FractionError):
            check_op("%")


class ItemTest(unittest.TestCase):
    def test_question(self):
        item = WorksheetItem(Fraction(3, 4), "+", Fraction(1, 2))
        self.assertEqual(item.question, "3/4 + 1/2 =")
        self.assertEqual(item.answer, Fraction(5, 4))

    def test_answer_text(self):
        item = WorksheetItem(Fraction(1, 2), "*", Fraction(2, 1))
        self.assertEqual(item.answer_text, "1")

    def test_invalid_operand(self):
        with self.assertRaises(FractionError):
            WorksheetItem(0.5, "+", Fraction(1, 2))

    def test_division_by_zero(self):
        with self.assertRaises(FractionError):
            WorksheetItem(Fraction(1, 2), "/", Fraction(0))


class WorksheetTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_worksheet(15, seed=1)), 15)

    def test_unique(self):
        items = build_worksheet(20, seed=2)
        keys = [(item.left, item.op, item.right) for item in items]
        self.assertEqual(len(set(keys)), 20)

    def test_proper_operands(self):
        for item in build_worksheet(10, seed=3):
            self.assertLess(abs(item.left.numerator), item.left.denominator)
            self.assertLess(abs(item.right.numerator), item.right.denominator)

    def test_denominator_bound(self):
        for item in build_worksheet(10, seed=4, max_denominator=6):
            self.assertLessEqual(item.left.denominator, 6)
            self.assertLessEqual(item.right.denominator, 6)

    def test_deterministic(self):
        first = [(i.left, i.op, i.right) for i in build_worksheet(10, seed=5)]
        second = [(i.left, i.op, i.right) for i in build_worksheet(10, seed=5)]
        self.assertEqual(first, second)

    def test_different_seed(self):
        first = [(i.left, i.op, i.right) for i in build_worksheet(10, seed=5)]
        second = [(i.left, i.op, i.right) for i in build_worksheet(10, seed=6)]
        self.assertNotEqual(first, second)

    def test_ops_filter(self):
        items = build_worksheet(10, ops=["*"], seed=7)
        self.assertTrue(all(item.op == "*" for item in items))

    def test_subtraction_non_negative_by_default(self):
        for item in build_worksheet(10, ops=["-"], seed=8):
            self.assertGreaterEqual(item.answer, 0)

    def test_negative_allowed(self):
        items = build_worksheet(30, ops=["-"], seed=9, allow_negative=True)
        self.assertTrue(any(item.answer < 0 for item in items))

    def test_too_many(self):
        with self.assertRaises(FractionError):
            build_worksheet(3, ops=["+"], max_denominator=2)

    def test_zero(self):
        with self.assertRaises(FractionError):
            build_worksheet(0)

    def test_invalid_max_denominator(self):
        with self.assertRaises(FractionError):
            build_worksheet(3, max_denominator=1)

    def test_empty_ops(self):
        with self.assertRaises(FractionError):
            build_worksheet(3, ops=[])


class CheckAnswerTest(unittest.TestCase):
    def setUp(self):
        self.item = WorksheetItem(Fraction(3, 4), "+", Fraction(1, 2))

    def test_improper(self):
        self.assertTrue(check_answer(self.item, "5/4"))

    def test_mixed(self):
        self.assertTrue(check_answer(self.item, "1 1/4"))

    def test_unreduced(self):
        self.assertTrue(check_answer(self.item, "10/8"))

    def test_integer(self):
        item = WorksheetItem(Fraction(1, 2), "+", Fraction(1, 2))
        self.assertTrue(check_answer(item, "1"))

    def test_wrong(self):
        self.assertFalse(check_answer(self.item, "5/3"))

    def test_invalid(self):
        self.assertFalse(check_answer(self.item, "five quarters"))

    def test_empty(self):
        self.assertFalse(check_answer(self.item, " "))


if __name__ == "__main__":
    unittest.main()
