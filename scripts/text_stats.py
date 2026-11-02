#!/usr/bin/env python3
"""Count visible prose without grading style or changing the input file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt")


HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U000323af]")
WORDS = re.compile(r"[^\W_]+(?:['’\-][^\W_]+)*", re.UNICODE)


def visible_markdown(text: str, stop_before: str | None = None) -> str:
    """Extract visible prose. Code blocks, URLs and raw HTML are not counted.

    Stop only at an exact parsed heading, so a heading-looking line inside a
    fenced code sample cannot truncate the article. Image captions are counted
    through their alternative text. Table contents remain text in CommonMark.
    """
    tokens = MarkdownIt("commonmark").parse(text)
    output: list[str] = []
    for index, token in enumerate(tokens):
        if (
            stop_before
            and token.type == "heading_open"
            and index + 1 < len(tokens)
            and tokens[index + 1].content.strip() == stop_before
        ):
            break
        if token.type != "inline":
            continue
        parts: list[str] = []
        for child in token.children or []:
            if child.type in {"text", "code_inline"}:
                parts.append(child.content)
            elif child.type in {"softbreak", "hardbreak"}:
                parts.append(" ")
            elif child.type == "image":
                parts.append(child.content)
        output.append("".join(parts))
    return "\n".join(output)


def count_text(text: str, *, markdown: bool = True,
               stop_before: str | None = None) -> dict[str, int]:
    visible = visible_markdown(text, stop_before) if markdown else text
    han_count = len(HAN.findall(visible))
    other_groups = len(WORDS.findall(HAN.sub(" ", visible)))
    return {
        "han_characters": han_count,
        "other_letter_number_groups": other_groups,
        "mixed_estimate": han_count + other_groups,
        "non_whitespace_characters": sum(not ch.isspace() for ch in visible),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="UTF-8 Markdown or plain-text file")
    parser.add_argument("--plain", action="store_true", help="Count literal text, including markup")
    parser.add_argument("--stop-before", metavar="HEADING", help="Exclude an exact Markdown heading and all following text")
    parser.add_argument("--json", action="store_true", help="Output named counts as JSON")
    args = parser.parse_args()
    if args.plain and args.stop_before:
        parser.error("--stop-before requires Markdown mode; omit --plain")
    try:
        text = args.file.read_text(encoding="utf-8-sig")
        result = count_text(text, markdown=not args.plain, stop_before=args.stop_before)
    except (OSError, UnicodeError) as error:
        print(f"Cannot read {args.file}: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"汉字：{result['han_characters']}")
        print(f"其他文字/数字词组：{result['other_letter_number_groups']}")
        print(f"混合估计（前两项之和）：{result['mixed_estimate']}")
        print(f"可见非空白字符（含标点）：{result['non_whitespace_characters']}")
        print("统计仅用于篇幅；具体字数按用户或目标平台规定的口径。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
