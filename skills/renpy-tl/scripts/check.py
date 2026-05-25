#!/usr/bin/env python3
"""Deterministic Ren'Py translation completion checker.

Checks .rpy translation blocks and reports likely untranslated items with
file/line locations. Designed to avoid false "completed" states.

States:
- pass_translated: target differs from source
- pass_keep_source: target equals source but is allowed to remain unchanged
- fail_untranslated: target equals source and is not allowed
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple

TRANSLATE_BLOCK_RE = re.compile(r"^\s*translate\s+\w+\s+([^\s:]+)\s*:\s*$")
OLD_RE = re.compile(r'^\s*old\s+"((?:[^"\\]|\\.)*)"\s*$')
NEW_RE = re.compile(r'^\s*new\s+"((?:[^"\\]|\\.)*)"\s*$')
QUOTED_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
PUNCT_ONLY_RE = re.compile(
    r"^[\s\.,!?;:'\"`~\-_=+/*\\|()\[\]{}<>@#$%^&*。，！？、；：「」『』（）〔〕【】《》…⋯—]+$"
)
TOKEN_RE = re.compile(r"(\{[^{}]*\}|\[[^\[\]]*\])")
LEADING_TRAILING_PUNCT_RE = re.compile(
    r"^[\s\.,!?;:'\"`~\-_=+/*\\|()\[\]{}<>@#$%^&*。，！？、；：「」『』（）〔〕【】《》…⋯—]+|[\s\.,!?;:'\"`~\-_=+/*\\|()\[\]{}<>@#$%^&*。，！？、；：「」『』（）〔〕【】《》…⋯—]+$"
)


@dataclass
class Unit:
    path: Path
    line: int
    unit_type: str  # dialogue | strings
    source: str
    target: str
    marker: bool


@dataclass
class Result:
    state: str  # pass_translated | pass_keep_source | fail_untranslated
    reason: str


def normalize_text(text: str) -> str:
    text = text.strip()
    text = text.replace("\u3000", " ")
    text = text.replace("\u2026", "...")
    text = re.sub(r"\s+", " ", text)
    return text


def remove_tokens(text: str) -> str:
    return TOKEN_RE.sub("", text)


def strip_wrapping_quotes(text: str) -> str:
    t = text.strip()
    # Handle escaped quote wrappers common in Ren'Py dialogue: \"...\"
    if len(t) >= 4 and t.startswith(r"\"") and t.endswith(r"\""):
        return t[2:-2].strip()
    if len(t) >= 2 and (
        (t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'")
    ):
        return t[1:-1].strip()
    return t


def normalize_name_candidate(text: str) -> str:
    t = normalize_text(remove_tokens(text))
    t = strip_wrapping_quotes(t)
    t = LEADING_TRAILING_PUNCT_RE.sub("", t)
    t = normalize_text(t)
    return t


def is_allowed_keep_source(text: str, proper_nouns: Set[str]) -> Tuple[bool, str]:
    normalized = normalize_text(text)
    if not normalized:
        return True, "empty content"

    without_tokens = normalize_text(remove_tokens(normalized))
    if not without_tokens:
        return True, "token-only content"

    if PUNCT_ONLY_RE.fullmatch(without_tokens):
        return True, "punctuation-only content"

    if proper_nouns:
        candidate = normalize_name_candidate(normalized)
        if candidate and candidate.lower() in proper_nouns:
            return True, "proper noun allowlist"

    return False, "no keep-source allow condition"


def classify_unit(
    source: str, target: str, marker: bool, proper_nouns: Set[str]
) -> Result:
    source_norm = normalize_text(source)
    target_norm = normalize_text(target)

    if source_norm != target_norm:
        return Result("pass_translated", "target differs from source")

    if marker:
        return Result("pass_keep_source", "explicit keep-source marker")

    allowed, reason = is_allowed_keep_source(source_norm, proper_nouns)
    if allowed:
        return Result("pass_keep_source", reason)

    return Result("fail_untranslated", "target equals source without allow condition")


def extract_quoted_text(line: str) -> Optional[str]:
    match = QUOTED_RE.search(line)
    if not match:
        return None
    return match.group(1)


def find_next_nonempty(lines: Sequence[str], start: int, stop: int) -> Optional[int]:
    idx = start
    while idx < stop:
        if lines[idx].strip():
            return idx
        idx += 1
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


def parse_dialogue_units(
    path: Path, lines: Sequence[str], start: int, end: int, marker_key: str
) -> List[Unit]:
    units: List[Unit] = []
    i = start + 1

    while i < end:
        stripped = lines[i].strip()
        if not stripped or not stripped.startswith("#"):
            i += 1
            continue

        source_comment = stripped[1:].strip()
        source_text = extract_quoted_text(source_comment)
        if source_text is None:
            i += 1
            continue

        marker = marker_key in source_comment

        nxt = find_next_nonempty(lines, i + 1, end)
        if nxt is None:
            break

        target_line = lines[nxt].strip()
        if target_line.startswith("#"):
            i += 1
            continue

        target_text = extract_quoted_text(target_line)
        if target_text is None:
            i += 1
            continue

        units.append(
            Unit(
                path=path,
                line=nxt + 1,
                unit_type="dialogue",
                source=source_text,
                target=target_text,
                marker=marker,
            )
        )
        i = nxt + 1

    return units


def parse_strings_units(
    path: Path, lines: Sequence[str], start: int, end: int, marker_key: str
) -> List[Unit]:
    units: List[Unit] = []
    i = start + 1
    pending_marker = False

    while i < end:
        stripped = lines[i].strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("#"):
            if marker_key in stripped:
                pending_marker = True
            i += 1
            continue

        old_m = OLD_RE.match(lines[i])
        if not old_m:
            pending_marker = False
            i += 1
            continue

        source_text = old_m.group(1)
        j = find_next_nonempty(lines, i + 1, end)
        if j is None:
            break

        new_m = NEW_RE.match(lines[j])
        if not new_m:
            pending_marker = False
            i = j + 1
            continue

        target_text = new_m.group(1)
        units.append(
            Unit(
                path=path,
                line=j + 1,
                unit_type="strings",
                source=source_text,
                target=target_text,
                marker=pending_marker,
            )
        )

        pending_marker = False
        i = j + 1

    return units


def parse_file(path: Path, marker_key: str) -> List[Unit]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    units: List[Unit] = []

    for start, end, label in collect_translate_block_ranges(lines):
        if label == "strings":
            units.extend(parse_strings_units(path, lines, start, end, marker_key))
        else:
            units.extend(parse_dialogue_units(path, lines, start, end, marker_key))

    return units


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


def load_proper_nouns(path: Optional[str]) -> Set[str]:
    if not path:
        return set()
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Proper nouns file not found: {p}")

    names: Set[str] = set()
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        normalized = normalize_name_candidate(line).lower()
        if normalized:
            names.add(normalized)
    return names


def run(
    paths: Sequence[str],
    marker_key: str,
    show_keep: bool,
    proper_nouns_file: Optional[str],
    short: bool,
) -> int:
    files = expand_paths(paths)
    if not files:
        print("No .rpy files found in the provided paths.")
        return 2

    try:
        proper_nouns = load_proper_nouns(proper_nouns_file)
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        print(str(exc))
        return 2

    pass_translated = 0
    pass_keep = 0
    fail_untranslated = 0
    total_dialogue = 0
    total_strings = 0

    failures: List[Tuple[Unit, Result]] = []
    keeps: List[Tuple[Unit, Result]] = []

    for path in files:
        try:
            units = parse_file(path, marker_key)
        except UnicodeDecodeError:
            print(f"SKIP {path}: not valid UTF-8")
            continue

        for unit in units:
            if unit.unit_type == "dialogue":
                total_dialogue += 1
            else:
                total_strings += 1

            result = classify_unit(unit.source, unit.target, unit.marker, proper_nouns)

            if result.state == "pass_translated":
                pass_translated += 1
            elif result.state == "pass_keep_source":
                pass_keep += 1
                if show_keep:
                    keeps.append((unit, result))
            else:
                fail_untranslated += 1
                failures.append((unit, result))

    print("Ren'Py Translation Completion Report")
    print(f"files_scanned: {len(files)}")
    print(f"proper_nouns_loaded: {len(proper_nouns)}")
    print(f"dialogue_units: {total_dialogue}")
    print(f"strings_units: {total_strings}")
    print(f"pass_translated: {pass_translated}")
    print(f"pass_keep_source: {pass_keep}")
    print(f"fail_untranslated: {fail_untranslated}")

    if show_keep and keeps:
        print("\nAllowed keep-source items:")
        for unit, result in keeps:
            print(f"KEEP {unit.path}:{unit.line} [{unit.unit_type}] {result.reason}")

    if failures:
        print("\nUntranslated candidates:")
        failure_rows = failures[:5] if short else failures
        for unit, result in failure_rows:
            print(f"FAIL {unit.path}:{unit.line} [{unit.unit_type}] {result.reason}")
        if short and len(failures) > len(failure_rows):
            print(f"... ({len(failures) - len(failure_rows)} more)")

    return 1 if fail_untranslated > 0 else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Ren'Py translation completion deterministically."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to scan for .rpy files.",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="Only print the first five untranslated candidate lines.",
    )
    parser.add_argument(
        "--marker",
        default="tl-keep-source",
        help="Comment marker that allows source==target.",
    )
    parser.add_argument(
        "--show-keep",
        action="store_true",
        help="Print allowed keep-source items.",
    )
    parser.add_argument(
        "--proper-nouns-file",
        help="Optional newline-separated proper nouns allowlist. Lines starting with # are ignored.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(
        args.paths, args.marker, args.show_keep, args.proper_nouns_file, args.short
    )


if __name__ == "__main__":
    sys.exit(main())
