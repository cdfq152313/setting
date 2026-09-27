#!/usr/bin/env python3
"""Merge the marked work range from a validated draft into its source file."""

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from draft_manifest import (  # pyright: ignore[reportImplicitRelativeImport]
    DraftManifest,
    load_manifest,
)
from translation_units import (  # pyright: ignore[reportImplicitRelativeImport]
    DRAFT_WORK_BEGIN,
    DRAFT_WORK_END,
    line_without_ending,
)


@dataclass(frozen=True)
class MergeRequest:
    """Inputs needed to describe a merge before writing any file."""

    project_root: Path
    draft_file: Path
    manifest_file: Path


@dataclass(frozen=True)
class MergeDescription:
    """The exact source-file replacement described by a draft."""

    source_file: Path
    draft_file: Path
    manifest_file: Path
    source_lines: tuple[str, ...]
    merged_lines: tuple[str, ...]
    work_lines: tuple[str, ...]
    work_start: int
    work_end: int


def find_marker_lines(lines: Sequence[str], marker: str) -> tuple[int, ...]:
    expected = f"# {marker}"
    return tuple(
        index
        for index, line in enumerate(lines)
        if line_without_ending(line).strip() == expected
    )


def resolve_source_file(
    manifest: DraftManifest,
    project_root: Path,
) -> Path:
    return (project_root / manifest.translation_file).resolve()


def validate_manifest_paths(
    request: MergeRequest,
    manifest: DraftManifest,
) -> None:
    expected_draft = (request.project_root / manifest.draft_file).resolve()
    if expected_draft != request.draft_file:
        message = (
            "The draft path does not match manifest draft_file: "
            + f"{request.draft_file} != {expected_draft}."
        )
        raise ValueError(message)


def describe_merge(request: MergeRequest) -> MergeDescription:
    manifest = load_manifest(request.manifest_file)
    validate_manifest_paths(request, manifest)
    source_file = resolve_source_file(manifest, request.project_root)
    source_lines = tuple(
        source_file.read_text(encoding="utf-8").splitlines(keepends=True)
    )
    draft_lines = tuple(
        request.draft_file.read_text(encoding="utf-8").splitlines(keepends=True)
    )

    begin_lines = find_marker_lines(draft_lines, DRAFT_WORK_BEGIN)
    end_lines = find_marker_lines(draft_lines, DRAFT_WORK_END)
    if len(begin_lines) != 1 or len(end_lines) != 1:
        raise ValueError("Draft must contain exactly one work-begin and work-end.")
    begin_line = begin_lines[0]
    end_line = end_lines[0]
    if begin_line >= end_line:
        raise ValueError("Draft work-begin must appear before work-end.")

    outer = manifest.translation_file_lines
    work = manifest.work_lines
    if outer.end > len(source_lines):
        raise ValueError(
            "Manifest translation_file_lines extends beyond the source file."
        )
    if work.start < outer.start or work.end > outer.end:
        raise ValueError("Manifest work range is outside the draft range.")
    expected_outer = source_lines[outer.start - 1 : outer.end]
    work_offset = work.start - outer.start
    work_end_offset = work.end - outer.start + 1
    expected_prefix = expected_outer[:work_offset]
    expected_suffix = expected_outer[work_end_offset:]
    actual_prefix = draft_lines[:begin_line]
    actual_suffix = draft_lines[end_line + 1 :]
    if tuple(expected_prefix) != tuple(actual_prefix):
        raise ValueError("Draft content before work-begin differs from source.")
    if tuple(expected_suffix) != tuple(actual_suffix):
        raise ValueError("Draft content after work-end differs from source.")

    work_lines = tuple(draft_lines[begin_line + 1 : end_line])
    expected_work = tuple(source_lines[work.start - 1 : work.end])
    if len(work_lines) != len(expected_work):
        raise ValueError("Draft work range changed its physical line count.")

    merged_lines = (
        *source_lines[: work.start - 1],
        *work_lines,
        *source_lines[work.end :],
    )
    return MergeDescription(
        source_file=source_file,
        draft_file=request.draft_file,
        manifest_file=request.manifest_file,
        source_lines=source_lines,
        merged_lines=tuple(merged_lines),
        work_lines=work_lines,
        work_start=work.start,
        work_end=work.end,
    )


def apply_merge(description: MergeDescription) -> None:
    _ = description.source_file.write_text(
        "".join(description.merged_lines),
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge a Ren'Py draft work range into its source file."
    )
    _ = parser.add_argument("draft", help="Draft .rpy file.")
    _ = parser.add_argument("--manifest", required=True, help="Draft manifest JSON.")
    _ = parser.add_argument(
        "--project-root",
        required=True,
        help="Project root used to resolve translation_file.",
    )
    _ = parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the merge to the source file. Without this flag, only preview.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = Path(cast(str, args.project_root)).resolve()
    draft_file = Path(cast(str, args.draft)).resolve()
    manifest_file = Path(cast(str, args.manifest)).resolve()
    request = MergeRequest(
        project_root=project_root,
        draft_file=draft_file,
        manifest_file=manifest_file,
    )

    try:
        description = describe_merge(request)
    except (OSError, UnicodeDecodeError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if cast(bool, args.apply):
        apply_merge(description)
        message = (
            f"Merged lines {description.work_start}-{description.work_end} "
            + f"into {description.source_file}"
        )
        print(message)
    else:
        message = (
            f"Merge preview: lines {description.work_start}-"
            + f"{description.work_end} into {description.source_file}"
        )
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
