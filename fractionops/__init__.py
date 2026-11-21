"""fractionops：分数四则运算练习。"""

from .model import (
    OP_LABELS,
    OPS,
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
from .render import render_worksheet

__all__ = [
    "OP_LABELS",
    "OPS",
    "FractionError",
    "WorksheetItem",
    "apply_operation",
    "build_worksheet",
    "check_answer",
    "check_op",
    "format_answer",
    "format_fraction",
    "format_mixed",
    "mixed_parts",
    "parse_fraction",
    "render_worksheet",
]

__version__ = "0.1.0"
