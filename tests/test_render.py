"""渲染层测试。"""

import unittest

from fractionops.model import build_worksheet, format_fraction
from fractionops.render import render_worksheet


class RenderTest(unittest.TestCase):
    def test_skeleton(self):
        html = render_worksheet(build_worksheet(3, seed=1))
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', html)

    def test_item_count(self):
        html = render_worksheet(build_worksheet(6, seed=1))
        self.assertEqual(html.count('class="item"'), 6)

    def test_question_appears(self):
        items = build_worksheet(1, seed=2)
        html = render_worksheet(items)
        self.assertIn(format_fraction(items[0].left), html)
        self.assertIn(items[0].op, html)

    def test_answers_hidden(self):
        html = render_worksheet(build_worksheet(2, seed=3))
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        items = build_worksheet(2, seed=3)
        html = render_worksheet(items, include_answers=True)
        self.assertIn("参考答案", html)
        for item in items:
            self.assertIn(item.answer_text, html)

    def test_title_escaped(self):
        html = render_worksheet([], title="<分数> & 练习")
        self.assertIn("&lt;分数&gt; &amp; 练习", html)

    def test_empty(self):
        self.assertIn("暂无题目", render_worksheet([]))

    def test_a4_style(self):
        html = render_worksheet(build_worksheet(1, seed=4))
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)

    def test_total_count(self):
        html = render_worksheet(build_worksheet(4, seed=5))
        self.assertIn("共 4 题", html)


if __name__ == "__main__":
    unittest.main()
