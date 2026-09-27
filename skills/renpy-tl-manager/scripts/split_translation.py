#!/usr/bin/env python3
"""Create a draft translation fragment and its manifest."""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from draft_manifest import (  # pyright: ignore[reportImplicitRelativeImport]
    DraftManifest,
    LineRange,
)
from translation_units import (  # pyright: ignore[reportImplicitRelativeImport]
    DRAFT_WORK_BEGIN,
    DRAFT_WORK_END,
    ParsedTranslationFile,
    TranslationUnit,
    parse_file,
)


@dataclass(frozen=True)
class SplitRequest:
    """Pure description of one split request before any output is written."""

    project_root: Path
    translation_file: Path
    draft_root: Path
    context_units: int
    work_units: int


@dataclass(frozen=True)
class SplitDescription:
    """All derived data needed to write one draft and one manifest."""

    draft_path: Path
    manifest_path: Path
    draft_lines: tuple[str, ...]
    manifest: DraftManifest
    context_units: tuple[TranslationUnit, ...]
    work_units: tuple[TranslationUnit, ...]


@dataclass(frozen=True)
class CliOptions:
    """Typed command-line values used to build a split request."""

    file: str
    project_root: str
    context_units: int
    work_units: int
    draft_root: str | None


def leading_whitespace(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return "\n"


def marker_line(marker: str, reference_line: str) -> str:
    return (
        f"{leading_whitespace(reference_line)}# {marker}"
        f"{line_ending(reference_line)}"
    )


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def load_active_manifests(
    draft_root: Path,
    translation_file: str,
) -> tuple[Path, ...]:
    active: list[Path] = []
    if not draft_root.exists():
        return ()

    for manifest_path in sorted(draft_root.rglob("*.json")):
        try:
            raw_manifest = cast(
                object,
                json.loads(manifest_path.read_text(encoding="utf-8")),
            )
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw_manifest, dict):
            continue
        manifest = cast(dict[str, object], raw_manifest)
        if manifest.get("translation_file") == translation_file:
            active.append(manifest_path)
    return tuple(active)


def choose_units(
    parsed: ParsedTranslationFile,
    context_count: int,
    work_count: int,
) -> tuple[tuple[TranslationUnit, ...], tuple[TranslationUnit, ...]]:
    first_untranslated = next(
        (idx for idx, unit in enumerate(parsed.units) if unit.untranslated),
        None,
    )
    if first_untranslated is None:
        raise ValueError("The translation file has no untranslated units.")

    context: list[TranslationUnit] = []
    idx = first_untranslated - 1
    while idx >= 0 and len(context) < context_count:
        unit = parsed.units[idx]
        if unit.untranslated or not unit.is_structurally_valid:
            break
        context.append(unit)
        idx -= 1
    context.reverse()

    work: list[TranslationUnit] = []
    idx = first_untranslated
    while idx < len(parsed.units) and len(work) < work_count:
        unit = parsed.units[idx]
        if not unit.is_structurally_valid:
            error_detail = "; ".join(unit.errors)
            error_message = (
                f"Cannot split around malformed unit at lines {unit.start}-"
                f"{unit.end}: {error_detail}"
            )
            raise ValueError(error_message)
        if not unit.untranslated:
            error_detail = (
                "The requested work range is not contiguous: "
                f"unit {unit.start}-{unit.end} is already translated before "
                f"{work_count} untranslated unit(s) were selected."
            )
            raise ValueError(
                error_detail
            )
        work.append(unit)
        idx += 1

    if not work:
        raise ValueError("No untranslated units were selected.")

    return tuple(context), tuple(work)


def span_start(unit: TranslationUnit) -> int:
    return min(unit.start, unit.block_start)


def build_draft(
    parsed: ParsedTranslationFile,
    context: Sequence[TranslationUnit],
    work: Sequence[TranslationUnit],
) -> tuple[tuple[str, ...], int, int]:
    selected = [*context, *work]
    source_start = span_start(selected[0])
    source_end = work[-1].end
    source_lines = list(parsed.lines[source_start - 1 : source_end])

    work_start = work[0].start - source_start
    work_end = work[-1].end - source_start + 1
    begin_marker = marker_line(
        DRAFT_WORK_BEGIN,
        source_lines[work_start],
    )
    end_marker = marker_line(
        DRAFT_WORK_END,
        source_lines[work_end - 1],
    )

    draft_lines = [
        *source_lines[:work_start],
        begin_marker,
        *source_lines[work_start:work_end],
        end_marker,
        *source_lines[work_end:],
    ]
    return tuple(draft_lines), source_start, source_end


def output_paths(
    translation_file: Path,
    project_root: Path,
    draft_root: Path,
    source_start: int,
    source_end: int,
) -> tuple[Path, Path]:
    relative = translation_file.resolve().relative_to(project_root.resolve())
    output_dir = draft_root / relative.parent
    stem = f"{relative.stem}.lines-{source_start:05d}-{source_end:05d}"
    return output_dir / f"{stem}.rpy", output_dir / f"{stem}.json"


def describe_split(
    request: SplitRequest,
    parsed: ParsedTranslationFile,
) -> SplitDescription:
    context, work = choose_units(
        parsed,
        context_count=request.context_units,
        work_count=request.work_units,
    )
    draft_lines, source_start, source_end = build_draft(parsed, context, work)
    draft_path, manifest_path = output_paths(
        request.translation_file,
        request.project_root,
        request.draft_root,
        source_start,
        source_end,
    )
    translation_relative = relative_path(
        request.translation_file,
        request.project_root,
    )
    manifest = DraftManifest(
        translation_file=translation_relative,
        translation_file_lines=LineRange(source_start, source_end),
        work_lines=LineRange(work[0].start, work[-1].end),
        draft_file=relative_path(draft_path, request.project_root),
    )
    return SplitDescription(
        draft_path=draft_path,
        manifest_path=manifest_path,
        draft_lines=draft_lines,
        manifest=manifest,
        context_units=context,
        work_units=work,
    )


def write_split(description: SplitDescription) -> None:
    _ = description.draft_path.parent.mkdir(parents=True, exist_ok=True)
    _ = description.draft_path.write_text(
        "".join(description.draft_lines),
        encoding="utf-8",
    )
    _ = description.manifest_path.write_text(
        json.dumps(description.manifest.as_dict(), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a Ren'Py translation draft and JSON manifest."
    )
    _ = parser.add_argument("file", help="Translation .rpy file to split.")
    _ = parser.add_argument(
        "--project-root",
        required=True,
        help="Project root used for relative paths.",
    )
    _ = parser.add_argument(
        "--context-units",
        type=int,
        default=0,
        help="Number of already translated units to include before the work range.",
    )
    _ = parser.add_argument(
        "--work-units",
        type=int,
        required=True,
        help="Number of contiguous untranslated units to include.",
    )
    _ = parser.add_argument(
        "--draft-root",
        help="Draft directory. Defaults to <project-root>/.renpy-tl/drafts.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    options = CliOptions(
        file=cast(str, args.file),
        project_root=cast(str, args.project_root),
        context_units=cast(int, args.context_units),
        work_units=cast(int, args.work_units),
        draft_root=cast(str | None, args.draft_root),
    )

    if options.context_units < 0:
        _ = parser.error("--context-units must be >= 0")
    if options.work_units <= 0:
        _ = parser.error("--work-units must be > 0")

    project_root = Path(options.project_root).resolve()
    translation_file = Path(options.file).resolve()
    draft_root = (
        Path(options.draft_root).resolve()
        if options.draft_root
        else project_root / ".renpy-tl" / "drafts"
    )

    if not project_root.is_dir():
        print(f"Invalid project root: {project_root}", file=sys.stderr)
        return 2
    if not translation_file.is_file() or translation_file.suffix != ".rpy":
        print(
            f"Target file not found or not .rpy: {translation_file}",
            file=sys.stderr,
        )
        return 2
    try:
        translation_relative = relative_path(translation_file, project_root)
    except ValueError:
        print(
            f"Target file is not under project root: {translation_file}",
            file=sys.stderr,
        )
        return 2

    active = load_active_manifests(draft_root, translation_relative)
    if active:
        active_detail = ", ".join(str(path) for path in active)
        active_message = (
            f"Active draft already exists for {translation_relative}: "
            + active_detail
        )
        print(active_message, file=sys.stderr)
        return 2

    try:
        parsed = parse_file(translation_file)
        request = SplitRequest(
            project_root=project_root,
            translation_file=translation_file,
            draft_root=draft_root,
            context_units=options.context_units,
            work_units=options.work_units,
        )
        description = describe_split(request, parsed)
        if description.draft_path.exists() or description.manifest_path.exists():
            output_detail = (
                "Draft output already exists: "
                f"{description.draft_path} or {description.manifest_path}"
            )
            raise ValueError(output_detail)
        write_split(description)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Wrote draft: {description.draft_path}")
    print(f"Wrote manifest: {description.manifest_path}")
    summary = (
        f"Source lines: {description.manifest.translation_file_lines.start}-"
        f"{description.manifest.translation_file_lines.end}; "
        f"work lines: {description.manifest.work_lines.start}-"
        f"{description.manifest.work_lines.end}; "
        f"context units: {len(description.context_units)}; "
        f"work units: {len(description.work_units)}"
    )
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
