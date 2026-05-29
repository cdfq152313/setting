#!/usr/bin/env python3
"""Replace Ren'Py translation lines by line number.

Input format from stdin:
    行號: 文本

Examples:
    7: MC "我想我會先讀一下從教練那裡得到的書。"
    13: MC "讓我看看。第一章..."
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

REPLACEMENT_RE = re.compile(r"^\s*(\d+)\s*:\s?(.*)$")


@dataclass
class Replacement:
    line_no: int
    text: str


def parse_stdin_replacements(stdin_text: str) -> List[Replacement]:
    replacements: List[Replacement] = []

    for idx, raw in enumerate(stdin_text.splitlines(), start=1):
        line = raw.rstrip("\r")
        if not line.strip():
            continue

        m = REPLACEMENT_RE.match(line)
        if not m:
            raise ValueError(f"Invalid input format at stdin line {idx}: {raw}")

        line_no = int(m.group(1))
        text = m.group(2)
        replacements.append(Replacement(line_no=line_no, text=text))

    return replacements


def choose_target_file(file_arg: str) -> Path:
    p = Path(file_arg)
    if not p.exists() or not p.is_file() or p.suffix != ".rpy":
        raise FileNotFoundError(f"Target file not found or not .rpy: {p}")
    return p


def apply_replacements(path: Path, replacements: List[Replacement]) -> int:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    if not lines:
        return 0

    by_line: Dict[int, str] = {}
    for rep in replacements:
        if rep.line_no in by_line:
            raise ValueError(f"Duplicate line number in input: {rep.line_no}")
        by_line[rep.line_no] = rep.text

    changed = 0
    for line_no, text in by_line.items():
        if line_no < 1 or line_no > len(lines):
            raise ValueError(
                f"Line number out of range for {path}: {line_no} (1..{len(lines)})"
            )

        idx = line_no - 1
        original = lines[idx]
        ending = "\n" if original.endswith("\n") else ""
        body = original[:-1] if ending else original
        stripped = body.strip()

        # Basic guard: avoid writing onto blank lines by mistake.
        if not stripped:
            raise ValueError(f"Refuse to replace blank line at {path}:{line_no}.")

        # Avoid breaking block structure or metadata comments.
        if stripped.startswith("#"):
            raise ValueError(f"Refuse to replace comment line at {path}:{line_no}.")
        if body.startswith("translate"):
            raise ValueError(
                f"Refuse to replace translate header line at {path}:{line_no}."
            )

        indent = body[: len(body) - len(body.lstrip())]
        new_body = f"{indent}{text}"

        new_line = new_body + ending
        if new_line != original:
            lines[idx] = new_line
            changed += 1

    path.write_text("".join(lines), encoding="utf-8")
    return changed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replace translation lines in a Ren'Py .rpy file using 'line: text' input from stdin."
    )
    parser.add_argument(
        "file",
        help="Target .rpy file path.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    stdin_text = sys.stdin.read()
    if not stdin_text.strip():
        print("No input received on stdin.", file=sys.stderr)
        return 2

    try:
        replacements = parse_stdin_replacements(stdin_text)
        target_file = choose_target_file(args.file)
        changed = apply_replacements(target_file, replacements)
    except (FileNotFoundError, ValueError, UnicodeDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Updated {changed} line(s) in {target_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
