"""分数练习纸的 HTML 渲染。"""

from __future__ import annotations

import html
from typing import Sequence

from .model import WorksheetItem, format_fraction

STYLE = """
@page { size: A4 portrait; margin: 14mm 12mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1f2933;
  font-size: 11.5pt;
  line-height: 1.5;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 6mm; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm 10mm; }
.item {
  display: flex;
  align-items: baseline;
  gap: 2mm;
  padding: 2mm 0 1.2mm;
  border-bottom: 0.4pt dashed #c7cdd4;
  page-break-inside: avoid;
}
.no { color: #7b8794; min-width: 7mm; text-align: right; }
.expr { flex: 1; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; }
.blank { display: inline-block; min-width: 26mm; border-bottom: 0.8pt solid #1f2933; height: 1.1em; }
.meta { margin-top: 8mm; color: #6b7280; font-size: 9pt; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { columns: 3; column-gap: 8mm; padding-left: 7mm; }
.answers li { margin-bottom: 2.4mm; break-inside: avoid; font-family: "SFMono-Regular", Consolas, monospace; }
.note { color: #6b7280; font-size: 9.5pt; margin-bottom: 5mm; }
@media print { .item, .answers li { break-inside: avoid; } }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "分数四则运算练习",
    include_answers: bool = False,
) -> str:
    """生成 A4 练习页；答案化为最简分数并附带分数形式。"""
    safe_title = _escape(title)
    blocks = []
    for index, item in enumerate(items, start=1):
        blocks.append(
            '<div class="item"><span class="no">%d.</span>'
            '<span class="expr">%s %s %s = <span class="blank"></span></span></div>'
            % (
                index,
                _escape(format_fraction(item.left)),
                _escape(item.op),
                _escape(format_fraction(item.right)),
            )
        )
    body = "".join(blocks) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<div class="grid">%s</div>' % body,
        '<p class="meta">共 %d 题　结果请化成最简分数。</p>' % len(items),
    ]
    if include_answers:
        answers = "".join(
            "<li>%s</li>" % _escape(item.answer_text) for item in items
        )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案</h2>",
                "<ol>%s</ol>" % answers,
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)
