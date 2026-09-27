#!/usr/bin/env python3
"""Build a Ren'Py translation progress file from one or more scan paths."""

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

PROGRESS_ITEM_RE = re.compile(r"^- \[(?P<status>[ xX])\] (?P<path>.+)$")


@dataclass(frozen=True)
class ProgressEntry:
    """One progress item, preserving the existing completion state."""

    path: str
    complete: bool = False


def expand_paths(items: Iterable[str]) -> list[Path]:
    files: list[Path] = []
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


def make_progress_entries(files: Sequence[Path], project_root: Path) -> list[str]:
    entries: set[str] = set()
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


def read_existing_statuses(progress_path: Path) -> dict[str, bool]:
    if not progress_path.is_file():
        return {}

    statuses: dict[str, bool] = {}
    for line in progress_path.read_text(encoding="utf-8").splitlines():
        match = PROGRESS_ITEM_RE.match(line.strip())
        if match is not None:
            statuses[match.group("path")] = match.group("status").lower() == "x"
    return statuses


def make_progress_items(
    paths: Sequence[str],
    existing_statuses: dict[str, bool],
) -> tuple[ProgressEntry, ...]:
    return tuple(
        ProgressEntry(path=path, complete=existing_statuses.get(path, False))
        for path in paths
    )


def write_progress(output_path: Path, entries: Sequence[ProgressEntry]) -> None:
    lines = ["# Translation Progress", ""]
    lines.extend(
        f"- [{'x' if entry.complete else ' '}] {entry.path}"
        for entry in entries
    )
    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _ = output_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan .rpy files and write a Translation Progress markdown file."
    )
    _ = parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to scan for .rpy files.",
    )
    _ = parser.add_argument(
        "--project-root",
        required=True,
        help="Base directory used to generate relative paths in progress.md.",
    )
    _ = parser.add_argument(
        "-o",
        "--output",
        help="Optional output path. Defaults to <project-root>/progress.md.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = Path(cast(str, args.project_root)).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"Invalid project root: {project_root}", file=sys.stderr)
        return 2

    files = expand_paths(cast(list[str], args.paths))
    if not files:
        print("No .rpy files found in the provided paths.", file=sys.stderr)
        return 2

    entries = make_progress_entries(files, project_root)
    if not entries:
        print("No .rpy files remained after filtering by project root.", file=sys.stderr)
        return 2

    output_arg = cast(str | None, args.output)
    output_path = (
        Path(output_arg).resolve()
        if output_arg is not None
        else project_root / "progress.md"
    )
    statuses = read_existing_statuses(output_path)
    progress_items = make_progress_items(entries, statuses)
    write_progress(output_path, progress_items)
    print(f"Wrote {len(progress_items)} progress item(s) to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
