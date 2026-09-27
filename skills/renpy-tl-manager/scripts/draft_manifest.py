#!/usr/bin/env python3
"""Typed manifest model and loader for Ren'Py translation drafts."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass(frozen=True)
class LineRange:
    """One-based inclusive line range in the original translation file."""

    start: int
    end: int

    def as_dict(self) -> dict[str, int]:
        return {"start": self.start, "end": self.end}


@dataclass(frozen=True)
class DraftManifest:
    """Machine-readable mapping from a draft back to its source file."""

    translation_file: str
    translation_file_lines: LineRange
    work_lines: LineRange
    draft_file: str

    def as_dict(self) -> dict[str, object]:
        return {
            "translation_file": self.translation_file,
            "translation_file_lines": self.translation_file_lines.as_dict(),
            "work_lines": self.work_lines.as_dict(),
            "draft_file": self.draft_file,
        }


def _read_string(mapping: dict[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Manifest field {key!r} must be a non-empty string.")
    return value


def _read_line_range(value: object, field_name: str) -> LineRange:
    if not isinstance(value, dict):
        raise TypeError(f"Manifest field {field_name!r} must be an object.")
    mapping = cast(dict[str, object], value)
    start = mapping.get("start")
    end = mapping.get("end")
    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError(
            f"Manifest field {field_name!r} must contain integer start/end."
        )
    if start < 1 or end < start:
        raise ValueError(
            f"Manifest field {field_name!r} has invalid range {start}-{end}."
        )
    return LineRange(start=start, end=end)


def from_object(value: object) -> DraftManifest:
    if not isinstance(value, dict):
        raise TypeError("Manifest root must be an object.")
    mapping = cast(dict[str, object], value)
    return DraftManifest(
        translation_file=_read_string(mapping, "translation_file"),
        translation_file_lines=_read_line_range(
            mapping.get("translation_file_lines"),
            "translation_file_lines",
        ),
        work_lines=_read_line_range(mapping.get("work_lines"), "work_lines"),
        draft_file=_read_string(mapping, "draft_file"),
    )


def load_manifest(path: Path) -> DraftManifest:
    raw = cast(object, json.loads(path.read_text(encoding="utf-8")))
    return from_object(raw)
