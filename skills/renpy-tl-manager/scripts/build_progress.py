#!/usr/bin/env python3
"""Build a Ren'Py translation progress file from one or more scan paths."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Set


def expand_paths(items: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for item in items:
        path = Path(item)
        if not path.exists():
            print(f"SKIP {path}: path does not exist", file=sys.stderr)
            continue
        if path.is_file() and path.suffix == ".rpy":
            files.append(path.resolve())
            continue
        if path.is_dir():
            for child in sorted(path.rglob("*.rpy")):
                files.append(child.resolve())
    return files


def make_progress_entries(files: Sequence[Path], project_root: Path) -> List[str]:
    entries: Set[str] = set()
    for file_path in files:
        try:
            rel_path = file_path.relative_to(project_root)
        except ValueError:
            print(
                f"SKIP {file_path}: not under project root {project_root}",
                file=sys.stderr,
            )
            continue
        entries.add(rel_path.as_posix())
    return sorted(entries)


def write_progress(output_path: Path, entries: Sequence[str]) -> None:
    lines = ["# Translation Progress", ""]
    lines.extend(f"- [ ] {entry}" for entry in entries)
    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan .rpy files and write a Translation Progress markdown file."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to scan for .rpy files.",
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Base directory used to generate relative paths in progress.md.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output path. Defaults to <project-root>/progress.md.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"Invalid project root: {project_root}", file=sys.stderr)
        return 2

    files = expand_paths(args.paths)
    if not files:
        print("No .rpy files found in the provided paths.", file=sys.stderr)
        return 2

    entries = make_progress_entries(files, project_root)
    if not entries:
        print("No .rpy files remained after filtering by project root.", file=sys.stderr)
        return 2

    output_path = (
        Path(args.output).resolve()
        if args.output is not None
        else project_root / "progress.md"
    )
    write_progress(output_path, entries)
    print(f"Wrote {len(entries)} progress item(s) to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
