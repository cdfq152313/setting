#!/usr/bin/env python3
"""Extract likely untranslated Ren'Py lines and print plain text.

Output format:
- 行號: 待翻譯文字
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

TRANSLATE_BLOCK_RE = re.compile(r"^\s*translate\s+\w+\s+([^\s:]+)\s*:\s*$")
SOURCE_LOC_COMMENT_RE = re.compile(r"^\s*#\s+.+:\d+\s*$")
OLD_RE = re.compile(r'^\s*old\s+"((?:[^"\\]|\\.)*)"\s*$')
NEW_RE = re.compile(r'^\s*new\s+"((?:[^"\\]|\\.)*)"\s*(#.*)?$')
QUOTED_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def extract_quoted_text(line: str) -> Optional[str]:
    m = QUOTED_RE.search(line)
    if not m:
        return None
    return m.group(1)


def find_next_nonempty(lines: Sequence[str], start: int, stop: int) -> Optional[int]:
    i = start
    while i < stop:
        if lines[i].strip():
            return i
        i += 1
    return None


def collect_translate_block_ranges(lines: Sequence[str]) -> List[Tuple[int, int, str]]:
    starts: List[Tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = TRANSLATE_BLOCK_RE.match(line)
        if m:
            starts.append((i, m.group(1)))

    ranges: List[Tuple[int, int, str]] = []
    for idx, (start, label) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        ranges.append((start, end, label))

    return ranges


def parse_dialogue_block(
    lines: Sequence[str], start: int, end: int
) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []

    source_lines: List[str] = []
    target_lines: List[Tuple[int, str]] = []

    for i in range(start + 1, end):
        stripped = lines[i].strip()
        if not stripped:
            continue

        if stripped.startswith("#"):
            if SOURCE_LOC_COMMENT_RE.match(stripped):
                continue
            source_lines.append(stripped[1:].strip())
            continue

        target_lines.append((i + 1, stripped))

    for source_line, (line_no, target_line) in zip(source_lines, target_lines):
        if source_line == target_line:
            out.append((line_no, target_line))

    return out


def parse_strings_block(
    lines: Sequence[str], start: int, end: int
) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    i = start + 1

    while i < end:
        stripped = lines[i].strip()

        if not stripped:
            i += 1
            continue

        old_m = OLD_RE.match(lines[i])
        if not old_m:
            i += 1
            continue

        source_text = old_m.group(1)
        j = find_next_nonempty(lines, i + 1, end)
        if j is None:
            break

        new_m = NEW_RE.match(lines[j])
        if not new_m:
            i = j + 1
            continue

        target_text = new_m.group(1)
        trailing_comment = new_m.group(2) or ""
        if source_text == target_text and not trailing_comment.strip():
            out.append((j + 1, lines[j].strip()))

        i = j + 1

    return out


def parse_file(path: Path) -> List[Tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: List[Tuple[int, str]] = []

    for start, end, label in collect_translate_block_ranges(lines):
        if label == "strings":
            out.extend(parse_strings_block(lines, start, end))
        else:
            out.extend(parse_dialogue_block(lines, start, end))

    return out


def expand_paths(items: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for item in items:
        p = Path(item)
        if not p.exists():
            continue
        if p.is_file() and p.suffix == ".rpy":
            files.append(p)
            continue
        if p.is_dir():
            files.extend(sorted(p.rglob("*.rpy")))
    return files


def run(paths: Sequence[str], out_file: Optional[str], limit: Optional[int]) -> int:
    files = expand_paths(paths)
    if not files:
        print("No .rpy files found in the provided paths.", file=sys.stderr)
        return 2

    rows: List[Tuple[int, str]] = []
    for path in files:
        try:
            rows.extend(parse_file(path))
        except UnicodeDecodeError:
            print(f"SKIP {path}: not valid UTF-8", file=sys.stderr)

    if limit is not None:
        rows = rows[:limit]

    output = sys.stdout if out_file is None else open(out_file, "w", encoding="utf-8")
    try:
        for line_no, text in rows:
            output.write(f"{line_no}: {text}\n")
    finally:
        if out_file is not None:
            output.close()

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract untranslated Ren'Py texts as 'line: text'."
    )
    parser.add_argument(
        "paths", nargs="+", help="Files or directories to scan for .rpy files."
    )
    parser.add_argument(
        "-o", "--out", help="Optional output CSV file path. Defaults to stdout."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of output rows.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be >= 0")
    return run(args.paths, args.out, args.limit)


if __name__ == "__main__":
    sys.exit(main())
