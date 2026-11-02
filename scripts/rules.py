#!/usr/bin/env python3
"""Locate numbered capabilities and read complete sections or owning files."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys

try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit('Install dependencies first: python -m pip install -r requirements.txt')

ROOT = Path(__file__).resolve().parents[1]
MD = MarkdownIt('commonmark')
RULE_ID = re.compile(r'^([A-Z]{2,12}-\d{2})\s+(.+)$')


class RuleError(ValueError):
    """Invalid or ambiguous capability definition."""


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    path: str
    start_line: int
    end_line: int
    text: str


def runtime_markdown(root: Path) -> list[Path]:
    """Read source or installed runtime resources, never maintenance fixtures."""
    paths: set[Path] = set()
    for folder in ("shared", "skills", "roles", "references"):
        directory = root / folder
        if directory.is_dir():
            paths.update(directory.rglob("*.md"))
    entry = root / "SKILL.md"
    if entry.is_file():
        paths.add(entry)
    return sorted(paths)


def collect(root: Path) -> dict[str, Rule]:
    shared = root / 'shared'
    if not shared.is_dir():
        raise RuleError(f'Missing capability directory: {shared}')
    result: dict[str, Rule] = {}
    owners: dict[str, str] = {}
    for path in runtime_markdown(root):
        text = path.read_text(encoding='utf-8')
        lines = text.splitlines()
        tokens = MD.parse(text)
        headings = [(int(t.tag[1:]), t.map[0], tokens[i + 1].content)
                    for i, t in enumerate(tokens)
                    if t.type == 'heading_open' and t.map is not None]
        html = [t.content for t in tokens if t.type == 'html_block']
        html += [child.content for t in tokens for child in (t.children or [])
                 if child.type == 'html_inline']
        anchors = [anchor for part in html
                   for anchor in re.findall(r'<a\s+id="([^"]+)"\s*>', part)]
        relative = path.relative_to(root).as_posix()
        for pos, (level, start, heading) in enumerate(headings):
            match = RULE_ID.fullmatch(heading) if level == 2 else None
            if not match:
                continue
            ident, title = match.groups()
            marker = start - 1
            while marker >= 0 and not lines[marker].strip():
                marker -= 1
            anchor = f'<a id="{ident.lower()}"></a>'
            if marker < 0 or lines[marker].strip() != anchor:
                raise RuleError(f'{relative}:{start + 1}: missing anchor for {ident}')
            if anchors.count(ident.lower()) != 1:
                raise RuleError(f'{relative}: anchor is not unique: {ident}')
            if ident in result:
                raise RuleError(f'Duplicate ID: {ident} in {relative} and {result[ident].path}')
            prefix = ident.split('-')[0]
            if prefix in owners and owners[prefix] != relative:
                raise RuleError(f'Prefix {prefix} has more than one owner: {owners[prefix]}, {relative}')
            owners[prefix] = relative
            end = len(lines)
            for next_level, next_start, next_heading in headings[pos + 1:]:
                if next_level <= level:
                    end = next_start
                    previous = next_start - 1
                    while previous >= 0 and not lines[previous].strip():
                        previous -= 1
                    next_match = RULE_ID.fullmatch(next_heading)
                    if next_match and previous >= 0 and lines[previous].strip() == f'<a id="{next_match[1].lower()}"></a>':
                        end = previous
                    break
            while end > start and not lines[end - 1].strip():
                end -= 1
            result[ident] = Rule(ident, title, relative, marker + 1, end,
                                 '\n'.join(lines[marker:end]) + '\n')
    if not result:
        raise RuleError('No numbered capabilities found.')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ids', nargs='*', help='Exact IDs, e.g. CONTENT-03 ORG-05')
    parser.add_argument('--list', action='store_true', help='List all IDs and locations')
    parser.add_argument('--file', action='store_true', help='Read owning files in full; use on first load')
    parser.add_argument('--json', action='store_true', help='Output locations and content as JSON')
    args = parser.parse_args()
    if args.list and (args.ids or args.file):
        parser.error('--list cannot be combined with IDs or --file')
    if not args.list and not args.ids:
        parser.error('Provide IDs or --list')
    try:
        registry = collect(ROOT)
        if args.list:
            items = [{k: v for k, v in asdict(rule).items() if k != 'text'}
                     for rule in registry.values()]
        else:
            requested = list(dict.fromkeys(ident.upper() for ident in args.ids))
            unknown = [ident for ident in requested if ident not in registry]
            if unknown:
                raise RuleError(f'Unknown ID(s): {", ".join(unknown)}; use --list to find a capability.')
            selected = [registry[ident] for ident in requested]
            if args.file:
                items = []
                for relative in dict.fromkeys(rule.path for rule in selected):
                    text = (ROOT / relative).read_text(encoding='utf-8')
                    items.append({'path': relative, 'start_line': 1,
                                  'end_line': len(text.splitlines()), 'text': text})
            else:
                items = [asdict(rule) for rule in selected]
        if args.json:
            print(json.dumps(items, ensure_ascii=False, indent=2))
        else:
            for item in items:
                label = f"{item.get('id', '')} {item.get('title', '')}".strip()
                print(f"{label + ' | ' if label else ''}{item['path']}:{item['start_line']}-{item['end_line']}")
                if 'text' in item:
                    print(item['text'])
        return 0
    except (RuleError, OSError, UnicodeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
