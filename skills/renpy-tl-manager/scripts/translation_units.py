#!/usr/bin/env python3
"""Parse generated Ren'Py translation files into complete translation units."""

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

TRANSLATE_HEADER_RE = re.compile(
    r"^\s*translate\s+(?P<language>\S+)\s+(?P<label>[^\s:]+)\s*:\s*$"
)
SOURCE_LOC_COMMENT_RE = re.compile(r"^\s*#\s+.+:\d+\s*$")
OLD_RE = re.compile(r'^\s*old\s+"((?:[^"\\]|\\.)*)"\s*$')
NEW_RE = re.compile(r'^\s*new\s+"((?:[^"\\]|\\.)*)"\s*(#.*)?$')
SKIP_RE = re.compile(r"\s+#\s*i18n:\s*skip\s*$", re.IGNORECASE)
DRAFT_WORK_BEGIN = "renpy-tl-draft: work-begin"
DRAFT_WORK_END = "renpy-tl-draft: work-end"


@dataclass(frozen=True)
class TranslationUnit:
    """One generated translation unit using one-based inclusive line numbers."""

    index: int
    kind: str
    language: str
    label: str
    start: int
    end: int
    block_start: int
    block_end: int
    source_texts: tuple[str, ...]
    target_texts: tuple[str, ...]
    untranslated: bool
    errors: tuple[str, ...] = ()

    @property
    def is_structurally_valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class ParsedTranslationFile:
    path: Path | None
    lines: tuple[str, ...]
    units: tuple[TranslationUnit, ...]


def line_without_ending(line: str) -> str:
    return line.rstrip("\r\n")


def is_blank(line: str) -> bool:
    return not line_without_ending(line).strip()


def is_full_line_comment(line: str) -> bool:
    return line_without_ending(line).lstrip().startswith("#")


def is_source_location_comment(line: str) -> bool:
    return bool(SOURCE_LOC_COMMENT_RE.match(line_without_ending(line)))


def is_draft_marker(line: str) -> bool:
    return "renpy-tl-draft:" in line_without_ending(line)


def strip_skip_marker(text: str) -> str:
    return SKIP_RE.sub("", text).rstrip()


def comparable_text(text: str) -> str:
    return strip_skip_marker(text).strip()


def next_nonblank(lines: Sequence[str], start: int, stop: int) -> int | None:
    for idx in range(start, stop):
        if not is_blank(lines[idx]):
            return idx
    return None


def previous_nonblank(lines: Sequence[str], start: int) -> int | None:
    for idx in range(start, -1, -1):
        if not is_blank(lines[idx]):
            return idx
    return None


def last_nonblank(lines: Sequence[str], start: int, end: int) -> int | None:
    for idx in range(end, start - 1, -1):
        if not is_blank(lines[idx]):
            return idx
    return None


def comment_text(line: str) -> str:
    body = line_without_ending(line).lstrip()
    return body[1:].strip() if body.startswith("#") else body


def parse_normal_unit(
    lines: Sequence[str],
    header_idx: int,
    block_end_idx: int,
    unit_start_idx: int,
    language: str,
    label: str,
    index: int,
) -> TranslationUnit:
    source_texts: list[str] = []
    target_texts: list[str] = []
    errors: list[str] = []

    for line in lines[header_idx + 1 : block_end_idx + 1]:
        if is_blank(line) or is_draft_marker(line):
            continue
        if is_full_line_comment(line):
            if is_source_location_comment(line):
                continue
            source_texts.append(comment_text(line))
            continue
        target_texts.append(line_without_ending(line).strip())

    if not source_texts:
        errors.append("missing source text comment")
    if not target_texts:
        errors.append("missing translated text")
    if len(source_texts) != len(target_texts):
        errors.append(
            f"source/target count mismatch: {len(source_texts)} != {len(target_texts)}"
        )

    untranslated = False
    for source_text, target_text in zip(source_texts, target_texts):
        if (
            comparable_text(source_text) == comparable_text(target_text)
            and not SKIP_RE.search(target_text)
        ):
            untranslated = True
            break

    end_idx = last_nonblank(lines, header_idx, block_end_idx)
    while end_idx is not None and is_source_location_comment(lines[end_idx]):
        end_idx = last_nonblank(lines, header_idx, end_idx - 1)
    if end_idx is None:
        end_idx = header_idx

    return TranslationUnit(
        index=index,
        kind="dialogue",
        language=language,
        label=label,
        start=unit_start_idx + 1,
        end=end_idx + 1,
        block_start=header_idx + 1,
        block_end=block_end_idx + 1,
        source_texts=tuple(source_texts),
        target_texts=tuple(target_texts),
        untranslated=untranslated,
        errors=tuple(errors),
    )


def parse_strings_units(
    lines: Sequence[str],
    header_idx: int,
    block_end_idx: int,
    language: str,
    index_start: int,
) -> list[TranslationUnit]:
    source_locations = [
        idx
        for idx in range(header_idx + 1, block_end_idx + 1)
        if is_source_location_comment(lines[idx])
    ]
    boundaries = source_locations + [block_end_idx + 1]
    units: list[TranslationUnit] = []

    for offset, start_idx in enumerate(source_locations):
        segment_end = boundaries[offset + 1]
        old_idx = next_nonblank(lines, start_idx + 1, segment_end)
        errors: list[str] = []
        source_texts: list[str] = []
        target_texts: list[str] = []
        skip = False

        old_match = (
            OLD_RE.match(line_without_ending(lines[old_idx]))
            if old_idx is not None
            else None
        )
        if old_match is None:
            errors.append("missing old string")
        else:
            source_texts.append(old_match.group(1))

        new_idx = (
            next_nonblank(lines, old_idx + 1, segment_end)
            if old_idx is not None
            else None
        )
        new_match = (
            NEW_RE.match(line_without_ending(lines[new_idx]))
            if new_idx is not None
            else None
        )
        if new_match is None:
            errors.append("missing new string")
        else:
            target_texts.append(new_match.group(1))
            if new_match.group(2) and "i18n:" in new_match.group(2).lower():
                # A skip marker intentionally accepts an unchanged new string.
                skip = True
            else:
                skip = False

        end_idx = last_nonblank(lines, start_idx, segment_end - 1)
        if end_idx is None:
            end_idx = start_idx

        untranslated = False
        if source_texts and target_texts:
            untranslated = (
                comparable_text(source_texts[0]) == comparable_text(target_texts[0])
                and not skip
            )

        label = "strings"
        units.append(
            TranslationUnit(
                index=index_start + len(units),
                kind="string",
                language=language,
                label=label,
                start=start_idx + 1,
                end=end_idx + 1,
                block_start=header_idx + 1,
                block_end=block_end_idx + 1,
                source_texts=tuple(source_texts),
                target_texts=tuple(target_texts),
                untranslated=untranslated,
                errors=tuple(errors),
            )
        )

    return units


def parse_lines(lines: Sequence[str], path: Path | None = None) -> ParsedTranslationFile:
    source_lines = tuple(lines)
    headers: list[tuple[int, str, str]] = []
    for idx, line in enumerate(source_lines):
        match = TRANSLATE_HEADER_RE.match(line_without_ending(line))
        if match:
            headers.append((idx, match.group("language"), match.group("label")))

    units: list[TranslationUnit] = []
    for header_offset, (header_idx, language, label) in enumerate(headers):
        next_header_idx = (
            headers[header_offset + 1][0]
            if header_offset + 1 < len(headers)
            else len(source_lines)
        )
        block_end_idx = next_header_idx - 1

        if label == "strings":
            units.extend(
                parse_strings_units(
                    source_lines,
                    header_idx,
                    block_end_idx,
                    language,
                    len(units),
                )
            )
            continue

        previous_idx = previous_nonblank(source_lines, header_idx - 1)
        if previous_idx is not None and is_source_location_comment(
            source_lines[previous_idx]
        ):
            unit_start_idx = previous_idx
        else:
            unit_start_idx = header_idx

        units.append(
            parse_normal_unit(
                source_lines,
                header_idx,
                block_end_idx,
                unit_start_idx,
                language,
                label,
                len(units),
            )
        )

    return ParsedTranslationFile(path=path, lines=source_lines, units=tuple(units))


def parse_file(path: Path) -> ParsedTranslationFile:
    return parse_lines(path.read_text(encoding="utf-8").splitlines(keepends=True), path)


def unit_lines(parsed: ParsedTranslationFile, unit: TranslationUnit) -> tuple[str, ...]:
    return parsed.lines[unit.start - 1 : unit.end]


def iter_untranslated(parsed: ParsedTranslationFile) -> Iterable[TranslationUnit]:
    return (unit for unit in parsed.units if unit.untranslated)
