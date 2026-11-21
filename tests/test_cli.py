"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from fractionops.cli import main, parse_ops


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class ParseOpsTest(unittest.TestCase):
    def test_comma(self):
        self.assertEqual(parse_ops("+,-"), ["+", "-"])

    def test_spaces(self):
        self.assertEqual(parse_ops("+ - *"), ["+", "-", "*"])

    def test_single(self):
        self.assertEqual(parse_ops("/"), ["/"])

    def test_empty(self):
        with self.assertRaises(Exception):
            parse_ops(" ")


class CalcCommandTest(unittest.TestCase):
    def test_add(self):
        code, out, _ = run_cli(["calc", "3/4", "+", "1/2"])
        self.assertEqual(code, 0)
        self.assertIn("5/4", out)
        self.assertIn("1 1/4", out)

    def test_subtract(self):
        code, out, _ = run_cli(["calc", "1 1/2", "-", "1/2"])
        self.assertEqual(code, 0)
        self.assertIn("= 1", out)

    def test_multiply(self):
        code, out, _ = run_cli(["calc", "2/3", "*", "3/4"])
        self.assertEqual(code, 0)
        self.assertIn("1/2", out)

    def test_divide(self):
        code, out, _ = run_cli(["calc", "1/2", "/", "1/4"])
        self.assertEqual(code, 0)
        self.assertIn("= 2", out)

    def test_divide_by_zero(self):
        code, _, err = run_cli(["calc", "1/2", "/", "0"])
        self.assertEqual(code, 2)
        self.assertIn("除数不能为 0", err)

    def test_invalid_fraction(self):
        code, _, err = run_cli(["calc", "abc", "+", "1/2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "10", "--seed", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertEqual(html.count('class="item"'), 10)

    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_ops_filter(self):
        code, out, _ = run_cli(["sheet", "--count", "5", "--ops", "*", "--seed", "4"])
        self.assertEqual(code, 0)
        self.assertIn(" * ", out)

    def test_negative_flag(self):
        code, out, _ = run_cli(
            ["sheet", "--count", "10", "--ops", "-", "--negative", "--seed", "5"]
        )
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_too_many(self):
        code, _, err = run_cli(["sheet", "--count", "3", "--ops", "+", "--max-den", "2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        _, second, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        self.assertEqual(first, second)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
