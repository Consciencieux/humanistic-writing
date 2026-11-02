#!/usr/bin/env python3
"""Validate the source repository, build optional skills, or archive the sources."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit, urlunsplit
import zipfile

try:
    from markdown_it import MarkdownIt
    import yaml
except ImportError:
    raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt")

import rules

ROOT = Path(__file__).resolve().parents[1]
NAME = "humanistic-writing"
ENTRIES = {
    "combined": Path("SKILL.md"),
    "guide": Path("skills/humanistic-writing-guide/SKILL.md"),
    "audit": Path("skills/humanistic-writing-audit/SKILL.md"),
}
NAMES = {"combined": NAME, "guide": NAME + "-guide", "audit": NAME + "-audit"}
SKIP = {".git", "dist", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".DS_Store"}
MD = MarkdownIt("commonmark")
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


class RepositoryError(ValueError):
    """An invalid entry, resource or output path was found."""


def source_files(root: Path):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP or part.startswith("._") for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"} or relative.parts[:2] == ("evals", "runs"):
            continue
        if path.is_symlink():
            raise RepositoryError(f"Symbolic links are not packaged: {relative}")
        if path.is_file():
            yield path


def version(root: Path) -> str:
    value = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", value):
        raise RepositoryError("VERSION must contain a semantic version, e.g. 0.1.0")
    return value


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8-sig")
    match = FRONT.match(text)
    if not match:
        raise RepositoryError(f"{path}: missing YAML frontmatter")
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise RepositoryError(f"{path}: invalid YAML: {error}") from error
    if not isinstance(data, dict):
        raise RepositoryError(f"{path}: frontmatter must be a mapping")
    return data, text[match.end():]


def check_entry(path: Path, expected_name: str) -> None:
    data, body = frontmatter(path)
    name = data.get("name")
    if name != expected_name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(name)) or len(name) > 64:
        raise RepositoryError(f"{path}: invalid name, expected {expected_name!r}")
    description = data.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        raise RepositoryError(f"{path}: description must contain 1–1024 characters")
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()):
        raise RepositoryError(f"{path}: metadata keys and values must be strings")
    if not body.strip():
        raise RepositoryError(f"{path}: missing instructions")


def link_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for token in MD.parse(text):
        for child in token.children or []:
            attribute = "href" if child.type == "link_open" else "src" if child.type == "image" else None
            if attribute:
                value = child.attrGet(attribute)
                if value:
                    targets.add(value)
    return targets


def resolve_local(root: Path, source: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None
    target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()
    if not target.is_relative_to(root.resolve()):
        raise RepositoryError(f"{source.relative_to(root)}: link escapes the repository: {href}")
    return target


def check_links(root: Path) -> None:
    for source in source_files(root):
        if source.suffix != ".md":
            continue
        for href in link_targets(source.read_text(encoding="utf-8")):
            target = resolve_local(root, source, href)
            if target is None:
                continue
            if not target.exists():
                raise RepositoryError(f"{source.relative_to(root)}: missing link target: {href}")
            # This repository uses explicit anchors when a fragment is needed.
            fragment = unquote(urlsplit(href).fragment)
            if fragment and target.is_file():
                anchors = re.findall(r'<(?:a|h[1-6])\b[^>]*\bid=[\"\']([^\"\']+)[\"\']', target.read_text(encoding="utf-8"))
                if fragment not in anchors:
                    raise RepositoryError(f"{source.relative_to(root)}: missing explicit anchor: {href}")


BASELINE = ("shared/core.md", "shared/protocols/context.md")


def check_capabilities(root: Path, entries: list[Path]) -> dict[str, rules.Rule]:
    try:
        registry = rules.collect(root)
    except rules.RuleError as error:
        raise RepositoryError(str(error)) from error
    index = root / "shared/INDEX.md"
    indexed = {resolve_local(root, index, href)
               for href in link_targets(index.read_text(encoding="utf-8"))}
    shared = (root / "shared").resolve()
    for rule in registry.values():
        owner = (root / rule.path).resolve()
        if owner.is_relative_to(shared) and owner not in indexed:
            raise RepositoryError(f"Missing capability owner in index: {rule.path}")
    sources = sorted(set(rules.runtime_markdown(root)) | set(entries))
    graph: dict[Path, set[Path]] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        linked = {target for href in link_targets(text)
                  if (target := resolve_local(root, source, href)) is not None}
        graph[source.resolve()] = linked
        if source.resolve().is_relative_to(shared):
            for target in linked:
                relative = target.relative_to(root.resolve())
                if relative.parts[0] in {"skills", "roles", "references"} or relative == Path("SKILL.md"):
                    raise RepositoryError(
                        f"{source.relative_to(root)}: shared resource depends on a role: {relative}")
        for ident in re.findall(r"\b[A-Z]{2,12}-\d{2}\b", text):
            if ident not in registry:
                raise RepositoryError(f"{source.relative_to(root)}: unknown rule ID: {ident}")
            owner = (root / registry[ident].path).resolve()
            if source.resolve().is_relative_to(shared) and not owner.is_relative_to(shared):
                raise RepositoryError(
                    f"{source.relative_to(root)}: shared resource depends on a role ID: {ident}")
    for entry in entries:
        linked = graph[entry.resolve()]
        for required in BASELINE:
            if (root / required).resolve() not in linked:
                raise RepositoryError(f"{entry.relative_to(root)}: missing baseline pointer: {required}")
    # Follow actual links rather than maintaining a second method registry.
    reached: set[Path] = set()
    pending = [entry.resolve() for entry in entries]
    while pending:
        source = pending.pop()
        if source in reached:
            continue
        reached.add(source)
        pending.extend(graph.get(source, set()) - reached)
    for rule in registry.values():
        if (root / rule.path).resolve() not in reached:
            raise RepositoryError(f"Unreachable runtime resource: {rule.path}")
    return registry


def check_source(root: Path) -> None:
    version(root)
    for kind, entry in ENTRIES.items():
        check_entry(root / entry, NAMES[kind])
    for required in ("LICENSE", "README.md", "shared/core.md", "requirements.txt", "scripts/text_stats.py", "scripts/rules.py", "shared/INDEX.md", "evals/cases.json"):
        if not (root / required).is_file():
            raise RepositoryError(f"Missing required source: {required}")
    check_links(root)
    registry = check_capabilities(root, [root / p for p in ENTRIES.values()])
    cases = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RepositoryError("Evaluation case IDs must be unique")
    for case in cases:
        for ident in case.get("rules", []):
            if ident not in registry:
                raise RepositoryError(f"Evaluation {case['id']}: unknown rule ID {ident}")
        if case.get("entry") not in {p.as_posix() for p in ENTRIES.values()}:
            raise RepositoryError(f"Evaluation {case['id']}: unknown entry")
        for relative in case.get("fixtures", []):
            if not (root / relative).is_file():
                raise RepositoryError(f"Evaluation {case['id']}: missing fixture {relative}")


def mapping_for(root: Path, kind: str) -> dict[Path, Path]:
    """Package shared resources and only the selected roles' own methods."""
    mapping = {root / ENTRIES[kind]: Path("SKILL.md")}
    roles = ("guide", "audit") if kind == "combined" else (kind,)
    for role in roles:
        entry = root / ENTRIES[role]
        if kind == "combined":
            mapping[entry] = Path("roles") / f"{role}.md"
        reference_root = entry.parent / "references"
        destination = Path("roles") / role if kind == "combined" else Path("references")
        for source in source_files(reference_root):
            mapping[source] = destination / source.relative_to(reference_root)
    for folder in ("shared", "assets"):
        for source in source_files(root / folder):
            mapping[source] = source.relative_to(root)
    for relative in ("LICENSE", "VERSION", "requirements.txt", "scripts/text_stats.py", "scripts/rules.py"):
        mapping[root / relative] = Path(relative)
    return {key.resolve(): value for key, value in mapping.items()}


def rewrite_links(text: str, source: Path, destination: Path,
                  mapping: dict[Path, Path], root: Path) -> str:
    """Rebase this repository's inline links, preserving fenced code samples.

    Reference-style local links are rejected by the build if rebasing is needed;
    maintenance prose uses inline links so source and packaged paths stay clear.
    """
    replacements: dict[str, str] = {}
    for href in link_targets(text):
        target = resolve_local(root, source, href)
        if target is None:
            continue
        if target not in mapping:
            raise RepositoryError(f"{source.relative_to(root)}: runtime dependency is not included: {href}")
        parsed = urlsplit(href)
        relative = Path(os.path.relpath(mapping[target], destination.parent)).as_posix()
        replacements[href] = urlunsplit(("", "", relative, parsed.query, parsed.fragment))
    lines = text.splitlines(keepends=True)
    fenced_lines: set[int] = set()
    for token in MD.parse(text):
        if token.type in {"fence", "code_block"} and token.map:
            fenced_lines.update(range(*token.map))
    changed: set[str] = set()
    for index, line in enumerate(lines):
        if index in fenced_lines:
            continue
        # Inline code spans are not dependencies and must remain unchanged.
        parts = re.split(r"(`+[^`]*`+)", line)
        for pos in range(0, len(parts), 2):
            for old, new in replacements.items():
                pattern = re.compile(r"(?<=\]\()" + re.escape(old) + r"(?=\))")
                parts[pos], count = pattern.subn(lambda _: new, parts[pos])
                if count:
                    changed.add(old)
        lines[index] = "".join(parts)
    unresolved = {old for old, new in replacements.items() if old != new and old not in changed}
    if unresolved:
        raise RepositoryError(f"{source.relative_to(root)}: use inline links for package dependencies: {sorted(unresolved)}")
    return "".join(lines)


def populate(root: Path, stage: Path, kind: str) -> Path:
    target_root = stage / NAMES[kind]
    mapping = mapping_for(root, kind)
    for source, relative in mapping.items():
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".md":
            text = source.read_text(encoding="utf-8")
            if kind == "combined" and source in {
                (root / ENTRIES["guide"]).resolve(), (root / ENTRIES["audit"]).resolve()
            }:
                _, text = frontmatter(source)
            text = rewrite_links(text, source, relative, mapping, root)
            target.write_text(text, encoding="utf-8")
        else:
            target.write_bytes(source.read_bytes())
    check_entry(target_root / "SKILL.md", NAMES[kind])
    check_links(target_root)
    entries = [target_root / "SKILL.md"] + list((target_root / "roles").glob("*.md"))
    check_capabilities(target_root, entries)
    return target_root


def write_zip(files: list[tuple[Path, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".humanistic-writing-package-", suffix=".zip", dir=output.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, archive_name in files:
                archive.write(path, archive_name)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build(root: Path, output_dir: Path, kinds: list[str]) -> list[Path]:
    check_source(root)
    built: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="humanistic-writing-build-") as temporary:
        stage = Path(temporary)
        for kind in kinds:
            package = populate(root, stage, kind)
            output = output_dir / f"{NAMES[kind]}-v{version(root)}.zip"
            write_zip([(path, f"{package.name}/{path.relative_to(package).as_posix()}")
                       for path in source_files(package)], output)
            built.append(output)
    return built


def archive_source(root: Path, output: Path) -> None:
    check_source(root)
    output = output.resolve()
    entries = [(path, f"{NAME}/{path.relative_to(root).as_posix()}")
               for path in source_files(root) if path.resolve() != output]
    write_zip(entries, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Check entry metadata, resources and local Markdown links")
    package_parser = sub.add_parser("build", help="Build optional installable skill archives")
    package_parser.add_argument("--kind", choices=["all", *ENTRIES], default="all")
    package_parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    source_parser = sub.add_parser("source", help="Archive the complete source repository")
    source_parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            check_source(ROOT)
            print("Source entries, baseline pointers, numbered capabilities and local links are valid.")
        elif args.command == "build":
            kinds = list(ENTRIES) if args.kind == "all" else [args.kind]
            for path in build(ROOT, args.output_dir.resolve(), kinds):
                print(path)
        else:
            output = args.output or ROOT / "dist" / f"{NAME}-source-v{version(ROOT)}.zip"
            archive_source(ROOT, output)
            print(output.resolve())
    except (RepositoryError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
