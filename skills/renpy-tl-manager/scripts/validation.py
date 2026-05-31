#!/usr/bin/env python3
"""Validate a Ren'Py translation file after worker edits."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional, Sequence


def load_worker_extract():
    skills_dir = Path(__file__).resolve().parents[2]
    extract_path = skills_dir / "renpy-tl-worker" / "scripts" / "extract.py"
    spec = importlib.util.spec_from_file_location("renpy_tl_worker_extract", extract_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load worker extract.py: {extract_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract = load_worker_extract()

EXPECTED_TRANSLATE_BLOCK_INDENT = 4


@dataclass
class UntranslatedIssue:
    line: int
    text: str
    owner: str = "worker"


@dataclass
class BadIndentIssue:
    line: int
    actual: int
    text: str
    owner: str = "manager"


@dataclass
class CommentChangedIssue:
    line: int
    before: str
    after: str
    owner: str = "manager"


@dataclass
class LineCountChangedIssue:
    before: int
    after: int
    owner: str = "manager"


@dataclass
class ValidationResult:
    path: str
    untranslated: list[UntranslatedIssue] = field(default_factory=list)
    bad_indent: list[BadIndentIssue] = field(default_factory=list)
    comment_changed: list[CommentChangedIssue] = field(default_factory=list)
    line_count_changed: list[LineCountChangedIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(
            (
                self.untranslated,
                self.bad_indent,
                self.comment_changed,
                self.line_count_changed,
            )
        )


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def without_trailing_blank_lines(lines: Sequence[str]) -> Sequence[str]:
    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    return lines[:end]


def load_git_base(path: Path, rev: str) -> list[str]:
    repo_root = subprocess.run(
        ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()
    rel_path = path.resolve().relative_to(Path(repo_root).resolve()).as_posix()
    blob = subprocess.run(
        ["git", "-C", repo_root, "show", f"{rev}:{rel_path}"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    return blob.splitlines()


def count_leading_spaces(line: str) -> int:
    count = 0
    for char in line:
        if char == " ":
            count += 1
            continue
        if char == "\t":
            return -1
        break
    return count


def is_full_line_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def is_source_location_comment(line: str) -> bool:
    return bool(extract.SOURCE_LOC_COMMENT_RE.match(line.strip()))


def collect_untranslated(path: Path) -> list[UntranslatedIssue]:
    return [
        UntranslatedIssue(line=line_no, text=text)
        for line_no, text in extract.parse_file(path)
    ]


def collect_bad_indent(lines: Sequence[str]) -> list[BadIndentIssue]:
    issues: list[BadIndentIssue] = []
    ranges = extract.collect_translate_block_ranges(lines)
    for start, end, _label in ranges:
        for idx in range(start + 1, end):
            line = lines[idx]
            if not line.strip():
                continue
            # Ranges end at the next translate header, so they also include
            # the source-location comment immediately before that header.
            if is_source_location_comment(line):
                continue
            actual = count_leading_spaces(line)
            if actual != EXPECTED_TRANSLATE_BLOCK_INDENT:
                issues.append(
                    BadIndentIssue(
                        line=idx + 1,
                        actual=actual,
                        text=line.strip(),
                    )
                )
    return issues


def collect_comment_changes(
    base_lines: Sequence[str], current_lines: Sequence[str]
) -> list[CommentChangedIssue]:
    issues: list[CommentChangedIssue] = []
    for idx, before in enumerate(base_lines[: len(current_lines)]):
        if not is_full_line_comment(before):
            continue
        after = current_lines[idx]
        if before != after:
            issues.append(
                CommentChangedIssue(line=idx + 1, before=before, after=after)
            )
    return issues


def validate(
    path: Path,
    base_lines: Optional[Sequence[str]],
) -> ValidationResult:
    current_lines = read_lines(path)
    result = ValidationResult(path=str(path))
    result.untranslated = collect_untranslated(path)
    result.bad_indent = collect_bad_indent(current_lines)

    if base_lines is not None:
        normalized_base_lines = without_trailing_blank_lines(base_lines)
        normalized_current_lines = without_trailing_blank_lines(current_lines)
        if len(normalized_base_lines) != len(normalized_current_lines):
            result.line_count_changed.append(
                LineCountChangedIssue(
                    before=len(normalized_base_lines),
                    after=len(normalized_current_lines),
                )
            )
        result.comment_changed = collect_comment_changes(base_lines, current_lines)

    return result


def choose_next_action(result: ValidationResult) -> str:
    structure_errors = (
        result.bad_indent or result.comment_changed or result.line_count_changed
    )
    if structure_errors:
        return "manager_fix_structure"
    if result.untranslated:
        return "worker_continue"
    return "mark_complete"


def render_text(result: ValidationResult, max_details: int) -> str:
    status = "FAIL" if result.has_errors() else "OK"
    lines = [f"{status} {result.path}", f"NEXT_ACTION={choose_next_action(result)}"]
    lines.append(
        "SUMMARY "
        f"untranslated={len(result.untranslated)} "
        f"bad_indent={len(result.bad_indent)} "
        f"comment_changed={len(result.comment_changed)} "
        f"line_count_changed={str(bool(result.line_count_changed)).lower()}"
    )

    def format_lines(issues: Sequence[object]) -> str:
        shown = issues[:max_details]
        line_numbers = [str(issue.line) for issue in shown]
        if len(issues) > len(shown):
            line_numbers.append("...")
        return ",".join(line_numbers)

    def emit_line_group(name: str, issues: Sequence[object]) -> None:
        if not issues:
            return
        lines.append(f"{name} lines={format_lines(issues)}")

    for issue in result.line_count_changed:
        lines.append(f"line_count_changed before={issue.before} after={issue.after}")
    emit_line_group("comment_changed", result.comment_changed)
    emit_line_group("bad_indent", result.bad_indent)
    emit_line_group("untranslated", result.untranslated)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Ren'Py translation file for untranslated text, indentation, and changed comments."
    )
    parser.add_argument("file", help="Target .rpy file to validate.")
    parser.add_argument(
        "--base",
        help="Optional baseline file used to detect changed original comments.",
    )
    parser.add_argument(
        "--git-base",
        help="Optional git revision used as the baseline, for example HEAD.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--max-details",
        type=int,
        default=10,
        help="Maximum issues to print per group in text output.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists() or not path.is_file() or path.suffix != ".rpy":
        print(f"Target file not found or not .rpy: {path}", file=sys.stderr)
        return 2
    if args.base and args.git_base:
        parser.error("Use only one of --base or --git-base.")
    if args.max_details < 0:
        parser.error("--max-details must be >= 0")

    try:
        base_lines: Optional[Sequence[str]] = None
        if args.base:
            base_lines = read_lines(Path(args.base))
        elif args.git_base:
            base_lines = load_git_base(path, args.git_base)

        result = validate(path, base_lines)
    except (
        OSError,
        UnicodeDecodeError,
        subprocess.CalledProcessError,
        ValueError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_text(result, args.max_details))

    return 1 if result.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
