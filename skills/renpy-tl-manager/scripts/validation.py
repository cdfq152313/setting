#!/usr/bin/env python3
"""Validate Ren'Py translation drafts and complete translation files."""

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from draft_manifest import (  # pyright: ignore[reportImplicitRelativeImport]
    DraftManifest,
    load_manifest,
)
from translation_units import (  # pyright: ignore[reportImplicitRelativeImport]
    DRAFT_WORK_BEGIN,
    DRAFT_WORK_END,
    ParsedTranslationFile,
    TranslationUnit,
    is_blank,
    is_full_line_comment,
    is_source_location_comment,
    line_without_ending,
    parse_file,
)

TOKEN_RE = re.compile(
    r"\{[^{}\n]*\}|\[[^\[\]\n]+\]|%\([^)]*\)[a-zA-Z]"
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    line: int | None
    message: str
    owner: str


@dataclass(frozen=True)
class ValidationResult:
    path: str
    mode: str
    untranslated: tuple[ValidationIssue, ...] = ()
    structural: tuple[ValidationIssue, ...] = ()
    protected_changes: tuple[ValidationIssue, ...] = ()
    token_changes: tuple[ValidationIssue, ...] = ()

    @property
    def has_errors(self) -> bool:
        return any(
            (
                self.untranslated,
                self.structural,
                self.protected_changes,
                self.token_changes,
            )
        )

    @property
    def next_action(self) -> str:
        if self.structural or self.protected_changes:
            return "manager_fix_structure"
        if self.untranslated or self.token_changes:
            return "worker_continue"
        if self.mode == "worker":
            return "worker_done"
        return "merge_ready" if self.mode == "draft" else "mark_complete"


@dataclass(frozen=True)
class ValidationOptions:
    path: Path
    manifest: Path | None
    project_root: Path | None
    output_format: str
    max_details: int


def issue(
    code: str,
    line: int | None,
    message: str,
    owner: str,
) -> ValidationIssue:
    return ValidationIssue(code=code, line=line, message=message, owner=owner)


def token_counter(texts: Sequence[str]) -> Counter[str]:
    tokens: list[str] = []
    for text in texts:
        tokens.extend(TOKEN_RE.findall(text))
    return Counter(tokens)


def units_in_range(
    parsed: ParsedTranslationFile,
    start: int,
    end: int,
) -> tuple[TranslationUnit, ...]:
    return tuple(
        unit
        for unit in parsed.units
        if unit.start >= start and unit.end <= end
    )


def find_marker_lines(lines: Sequence[str], marker: str) -> tuple[int, ...]:
    expected = f"# {marker}"
    return tuple(
        index
        for index, line in enumerate(lines)
        if line_without_ending(line).strip() == expected
    )


def validate_units(
    parsed: ParsedTranslationFile,
    line_offset: int = 0,
) -> tuple[
    tuple[ValidationIssue, ...],
    tuple[ValidationIssue, ...],
    tuple[ValidationIssue, ...],
]:
    untranslated: list[ValidationIssue] = []
    structural: list[ValidationIssue] = []
    token_changes: list[ValidationIssue] = []
    for unit in parsed.units:
        line = line_offset + unit.start
        if unit.errors:
            structural.append(
                issue(
                    "malformed_unit",
                    line,
                    f"{unit.kind} unit {unit.start}-{unit.end}: "
                    + "; ".join(unit.errors),
                    "manager",
                )
            )
        if unit.untranslated:
            untranslated.append(
                issue(
                    "untranslated",
                    line,
                    f"Untranslated {unit.kind} unit at lines "
                    + f"{unit.start}-{unit.end}.",
                    "worker",
                )
            )
        if token_counter(unit.source_texts) != token_counter(unit.target_texts):
            token_changes.append(
                issue(
                    "placeholder_mismatch",
                    line,
                    "Ren'Py tags or placeholders differ in unit "
                    + f"{unit.start}-{unit.end}.",
                    "worker",
                )
            )
    return tuple(untranslated), tuple(structural), tuple(token_changes)


def compare_line_ranges(
    expected: Sequence[str],
    actual: Sequence[str],
    first_line: int,
    code: str,
    message: str,
) -> tuple[ValidationIssue, ...]:
    if tuple(expected) == tuple(actual):
        return ()
    issues: list[ValidationIssue] = []
    for offset, (before, after) in enumerate(zip(expected, actual)):
        if before != after:
            issues.append(issue(code, first_line + offset, message, "manager"))
    if len(expected) != len(actual):
        issues.append(
            issue(
                "line_count_changed",
                first_line,
                f"Expected {len(expected)} lines but received {len(actual)}.",
                "manager",
            )
        )
    return tuple(issues)


def validate_draft(
    draft_path: Path,
    manifest: DraftManifest,
    project_root: Path,
) -> ValidationResult:
    draft = parse_file(draft_path)
    source_path = project_root / manifest.translation_file
    source = parse_file(source_path)
    draft_lines = draft.lines
    source_lines = source.lines
    structural: list[ValidationIssue] = []
    protected_changes: list[ValidationIssue] = []

    begin_lines = find_marker_lines(draft_lines, DRAFT_WORK_BEGIN)
    end_lines = find_marker_lines(draft_lines, DRAFT_WORK_END)
    if len(begin_lines) != 1:
        structural.append(
            issue(
                "work_begin_count",
                None,
                f"Expected one work-begin marker, found {len(begin_lines)}.",
                "manager",
            )
        )
    if len(end_lines) != 1:
        structural.append(
            issue(
                "work_end_count",
                None,
                f"Expected one work-end marker, found {len(end_lines)}.",
                "manager",
            )
        )

    if len(begin_lines) == 1 and len(end_lines) == 1:
        begin_line = begin_lines[0]
        end_line = end_lines[0]
        if begin_line >= end_line:
            structural.append(
                issue(
                    "work_marker_order",
                    begin_line + 1,
                    "work-begin must appear before work-end.",
                    "manager",
                )
            )
        else:
            outer = manifest.translation_file_lines
            work = manifest.work_lines
            if outer.end > len(source_lines):
                structural.append(
                    issue(
                        "draft_range_outside_source",
                        outer.end,
                        "Manifest draft range extends beyond the source file.",
                        "manager",
                    )
                )
            elif work.start < outer.start or work.end > outer.end:
                structural.append(
                    issue(
                        "work_range_outside_draft",
                        None,
                        "Manifest work range is outside the draft range.",
                        "manager",
                    )
                )
            else:
                expected_outer = source_lines[outer.start - 1 : outer.end]
                work_offset = work.start - outer.start
                work_end_offset = work.end - outer.start + 1
                expected_prefix = expected_outer[:work_offset]
                expected_suffix = expected_outer[work_end_offset:]
                actual_prefix = draft_lines[:begin_line]
                actual_suffix = draft_lines[end_line + 1 :]
                protected_changes.extend(
                    compare_line_ranges(
                        expected_prefix,
                        actual_prefix,
                        outer.start,
                        "context_changed",
                        "Content outside the work range was changed.",
                    )
                )
                protected_changes.extend(
                    compare_line_ranges(
                        expected_suffix,
                        actual_suffix,
                        work.end + 1,
                        "context_changed",
                        "Content outside the work range was changed.",
                    )
                )

                expected_work = source_lines[work.start - 1 : work.end]
                actual_work = draft_lines[begin_line + 1 : end_line]
                protected_changes.extend(
                    compare_protected_work_lines(
                        expected_work,
                        actual_work,
                        work.start,
                    )
                )

                compare_unit_structure(
                    source,
                    draft,
                    outer.start,
                    outer.end,
                    structural,
                )

    untranslated, unit_structural, token_changes = validate_units(draft)
    structural.extend(unit_structural)
    return ValidationResult(
        path=str(draft_path),
        mode="draft",
        untranslated=untranslated,
        structural=tuple(structural),
        protected_changes=tuple(protected_changes),
        token_changes=token_changes,
    )


def compare_protected_work_lines(
    expected: Sequence[str],
    actual: Sequence[str],
    first_line: int,
) -> tuple[ValidationIssue, ...]:
    if len(expected) != len(actual):
        return (
            issue(
                "work_line_count_changed",
                first_line,
                "Worker changed the number of physical lines in the work range.",
                "manager",
            ),
        )

    issues: list[ValidationIssue] = []
    for offset, (before, after) in enumerate(zip(expected, actual)):
        before_body = line_without_ending(before)
        after_body = line_without_ending(after)
        if before_body == after_body:
            continue
        before_stripped = before_body.strip()
        if (
            is_blank(before)
            or is_full_line_comment(before)
            or is_source_location_comment(before)
            or before_stripped.startswith(("translate ", "old "))
        ):
            issues.append(
                issue(
                    "protected_work_line_changed",
                    first_line + offset,
                    "A source comment, header, or structural line in the work "
                    + "range was changed.",
                    "manager",
                )
            )
            continue
        if before_body[: len(before_body) - len(before_body.lstrip())] != after_body[
            : len(after_body) - len(after_body.lstrip())
        ]:
            issues.append(
                issue(
                    "indent_changed",
                    first_line + offset,
                    "Translation indentation was changed.",
                    "manager",
                )
            )
    return tuple(issues)


def compare_unit_structure(
    source: ParsedTranslationFile,
    draft: ParsedTranslationFile,
    outer_start: int,
    outer_end: int,
    structural: list[ValidationIssue],
) -> None:
    source_units = units_in_range(source, outer_start, outer_end)
    draft_units = draft.units
    if len(source_units) != len(draft_units):
        structural.append(
            issue(
                "unit_count_changed",
                outer_start,
                f"Expected {len(source_units)} translation units but found "
                + f"{len(draft_units)} in the draft.",
                "manager",
            )
        )
        return

    for source_unit, draft_unit in zip(source_units, draft_units):
        if (
            source_unit.kind != draft_unit.kind
            or source_unit.language != draft_unit.language
            or source_unit.label != draft_unit.label
            or source_unit.source_texts != draft_unit.source_texts
        ):
            structural.append(
                issue(
                    "unit_identity_changed",
                    source_unit.start,
                    "Translation unit identity or source text changed.",
                    "manager",
                )
            )
            continue
        # Target text changes are permitted inside the work range. Changes
        # outside that range are caught by the raw prefix/suffix comparisons.


def validate_file(path: Path) -> ValidationResult:
    parsed = parse_file(path)
    untranslated, structural, token_changes = validate_units(parsed)
    markers = tuple(
        index + 1
        for index, line in enumerate(parsed.lines)
        if "renpy-tl-draft:" in line
    )
    if markers:
        structural = structural + (
            issue(
                "draft_marker_in_source",
                markers[0],
                "Draft-only work markers must not be merged into the source file.",
                "manager",
            ),
        )
    return ValidationResult(
        path=str(path),
        mode="file",
        untranslated=untranslated,
        structural=structural,
        token_changes=token_changes,
    )


def validate_worker_draft(path: Path) -> ValidationResult:
    parsed = parse_file(path)
    structural: list[ValidationIssue] = []
    begin_lines = find_marker_lines(parsed.lines, DRAFT_WORK_BEGIN)
    end_lines = find_marker_lines(parsed.lines, DRAFT_WORK_END)
    if len(begin_lines) != 1:
        structural.append(
            issue(
                "work_begin_count",
                None,
                f"Expected one work-begin marker, found {len(begin_lines)}.",
                "manager",
            )
        )
    if len(end_lines) != 1:
        structural.append(
            issue(
                "work_end_count",
                None,
                f"Expected one work-end marker, found {len(end_lines)}.",
                "manager",
            )
        )
    if (
        len(begin_lines) == 1
        and len(end_lines) == 1
        and begin_lines[0] >= end_lines[0]
    ):
        structural.append(
            issue(
                "work_marker_order",
                begin_lines[0] + 1,
                "work-begin must appear before work-end.",
                "manager",
            )
        )
    untranslated, unit_structural, token_changes = validate_units(parsed)
    structural.extend(unit_structural)
    return ValidationResult(
        path=str(path),
        mode="worker",
        untranslated=untranslated,
        structural=tuple(structural),
        token_changes=token_changes,
    )


def render_text(result: ValidationResult, max_details: int) -> str:
    lines = [
        f"{'FAIL' if result.has_errors else 'OK'} {result.path}",
        f"NEXT_ACTION={result.next_action}",
        (
            f"SUMMARY untranslated={len(result.untranslated)} "
            f"structural={len(result.structural)} "
            f"protected_changes={len(result.protected_changes)} "
            f"token_changes={len(result.token_changes)}"
        ),
    ]
    all_issues = (
        ("untranslated", result.untranslated),
        ("structural", result.structural),
        ("protected_changes", result.protected_changes),
        ("token_changes", result.token_changes),
    )
    for name, issues in all_issues:
        for current in issues[:max_details]:
            line = f" line={current.line}" if current.line is not None else ""
            lines.append(f"{name}{line} {current.message}")
        if len(issues) > max_details:
            lines.append(f"{name} ...")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Ren'Py translation draft or complete file."
    )
    _ = parser.add_argument("path", help="Draft or translation .rpy file.")
    _ = parser.add_argument(
        "--manifest",
        help="Manifest JSON for draft validation. Omit for whole-file validation.",
    )
    _ = parser.add_argument(
        "--worker",
        action="store_true",
        help="Validate only the draft, without reading its original file.",
    )
    _ = parser.add_argument(
        "--project-root",
        help="Project root used to resolve manifest translation_file.",
    )
    _ = parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="Output format.",
    )
    _ = parser.add_argument(
        "--max-details",
        type=int,
        default=10,
        help="Maximum issues to print per group in text output.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = Path(cast(str, args.path)).resolve()
    manifest_arg = cast(str | None, args.manifest)
    project_root_arg = cast(str | None, args.project_root)
    worker_only = cast(bool, args.worker)
    output_format = cast(str, args.output_format)
    max_details = cast(int, args.max_details)
    if max_details < 0:
        _ = parser.error("--max-details must be >= 0")
    if not path.is_file() or path.suffix != ".rpy":
        print(f"Target file not found or not .rpy: {path}", file=sys.stderr)
        return 2

    options = ValidationOptions(
        path=path,
        manifest=Path(manifest_arg).resolve() if manifest_arg else None,
        project_root=Path(project_root_arg).resolve()
        if project_root_arg
        else None,
        output_format=output_format,
        max_details=max_details,
    )

    try:
        if worker_only:
            if options.manifest is not None or options.project_root is not None:
                raise ValueError("--worker cannot be combined with draft options.")
            result = validate_worker_draft(options.path)
        elif options.manifest is None:
            if options.project_root is not None:
                raise ValueError("--project-root requires --manifest.")
            result = validate_file(options.path)
        else:
            if options.project_root is None:
                raise ValueError("--project-root is required with --manifest.")
            manifest = load_manifest(options.manifest)
            result = validate_draft(options.path, manifest, options.project_root)
    except (
        OSError,
        UnicodeDecodeError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if options.output_format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_text(result, options.max_details))
    return 1 if result.has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
