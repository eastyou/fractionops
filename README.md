# fractionops

[![CI](https://github.com/eastyou/fractionops/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/fractionops/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

分数四则运算工具：支持真分数、假分数与带分数，自动约分，并可生成 A4 练习纸。

## 特性

- 解析 `3/4`、`6/8`、`1 1/2`、`-2` 等写法，自动约分
- 加、减、乘、除四则运算，除数为 0 时明确报错
- 答案同时给出最简假分数与带分数
- 练习纸同页不重复，可限制最大分母、选择运算符
- 减法默认避免负数，也可用 `--negative` 打开
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
fractionops calc "3/4" + "1/2"
fractionops calc "1 1/2" / "1/4"
fractionops sheet --count 20 --ops +,-,* --max-den 12 --seed 5 --answers -o sheet.html
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 20 |
| `--ops` | 运算符集合，例如 `+,-` 或 `*` | `+,-` |
| `--max-den` | 最大分母 | 12 |
| `--negative` | 允许减法结果为负 | 关闭 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加答案页 | 关闭 |

## 示例

```text
$ fractionops calc "3/4" + "1/2"
3/4 + 1/2 = 5/4（1 1/4）
```

[examples/fractionops.html](examples/fractionops.html) 是 20 道加减法练习，带答案页。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
