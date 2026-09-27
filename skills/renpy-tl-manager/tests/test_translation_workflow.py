"""Exercise the split, validation, merge, and progress workflow."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ROOT = PROJECT_ROOT / "skills" / "renpy-tl-manager" / "scripts"


def run_script(script_name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_ROOT / script_name), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )


def manifest_value(manifest_path: Path, key: str) -> object:
    value = cast(
        object,
        json.loads(manifest_path.read_text(encoding="utf-8")),
    )
    if not isinstance(value, dict):
        raise TypeError("manifest root is not an object")
    return cast(dict[str, object], value)[key]


class TranslationWorkflowTest(unittest.TestCase):
    def test_sequential_batches_and_strings_unit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="renpy-tl-test-") as raw_root:
            project_root = Path(raw_root)
            source_path = project_root / "game" / "tl" / "tChinese" / "demo.rpy"
            _ = source_path.parent.mkdir(parents=True)
            _ = source_path.write_text(
                """# game/demo.rpy:1
translate tChinese demo_one:

    # "Hello {w=.2}world"
    "Hello {w=.2}world"

# game/demo.rpy:2
translate tChinese demo_two:

    # "Second line [name]"
    "Second line [name]"

# game/demo.rpy:3
translate tChinese strings:

    # game/demo.rpy:4
    old "Menu"
    new "Menu"
""",
                encoding="utf-8",
            )

            first_split = run_script(
                "split_translation.py",
                str(source_path),
                "--project-root",
                str(project_root),
                "--context-units",
                "0",
                "--work-units",
                "2",
            )
            self.assertEqual(first_split.returncode, 0, first_split.stderr)
            draft_path = next(
                (project_root / ".renpy-tl" / "drafts").rglob("*.rpy")
            )
            manifest_path = next(
                (project_root / ".renpy-tl" / "drafts").rglob("*.json")
            )
            self.assertEqual(
                manifest_value(manifest_path, "translation_file"),
                "game/tl/tChinese/demo.rpy",
            )
            worker_before = run_script(
                "validation.py",
                str(draft_path),
                "--worker",
            )
            self.assertEqual(worker_before.returncode, 1, worker_before.stdout)
            self.assertIn("NEXT_ACTION=worker_continue", worker_before.stdout)
            draft_text = draft_path.read_text(encoding="utf-8")
            _ = draft_path.write_text(
                draft_text.replace(
                    '    "Hello {w=.2}world"',
                    '    "你好 {w=.2}世界"',
                ).replace(
                    '    "Second line [name]"',
                    '    "第二行 [name]"',
                ),
                encoding="utf-8",
            )
            worker_after = run_script(
                "validation.py",
                str(draft_path),
                "--worker",
            )
            self.assertEqual(worker_after.returncode, 0, worker_after.stdout)
            self.assertIn("NEXT_ACTION=worker_done", worker_after.stdout)

            first_validation = run_script(
                "validation.py",
                str(draft_path),
                "--manifest",
                str(manifest_path),
                "--project-root",
                str(project_root),
            )
            self.assertEqual(first_validation.returncode, 0, first_validation.stdout)
            self.assertIn("NEXT_ACTION=merge_ready", first_validation.stdout)

            merge = run_script(
                "merge_translation.py",
                str(draft_path),
                "--manifest",
                str(manifest_path),
                "--project-root",
                str(project_root),
                "--apply",
            )
            self.assertEqual(merge.returncode, 0, merge.stderr)
            self.assertNotIn("renpy-tl-draft:", source_path.read_text(encoding="utf-8"))
            draft_path.unlink()
            manifest_path.unlink()

            second_split = run_script(
                "split_translation.py",
                str(source_path),
                "--project-root",
                str(project_root),
                "--context-units",
                "1",
                "--work-units",
                "1",
            )
            self.assertEqual(second_split.returncode, 0, second_split.stderr)
            second_draft = next(
                (project_root / ".renpy-tl" / "drafts").rglob("*.rpy")
            )
            second_manifest = next(
                (project_root / ".renpy-tl" / "drafts").rglob("*.json")
            )
            second_text = second_draft.read_text(encoding="utf-8")
            _ = second_draft.write_text(
                second_text.replace('    new "Menu"', '    new "選單"'),
                encoding="utf-8",
            )

            second_validation = run_script(
                "validation.py",
                str(second_draft),
                "--manifest",
                str(second_manifest),
                "--project-root",
                str(project_root),
            )
            self.assertEqual(second_validation.returncode, 0, second_validation.stdout)
            self.assertIn("NEXT_ACTION=merge_ready", second_validation.stdout)

            second_merge = run_script(
                "merge_translation.py",
                str(second_draft),
                "--manifest",
                str(second_manifest),
                "--project-root",
                str(project_root),
                "--apply",
            )
            self.assertEqual(second_merge.returncode, 0, second_merge.stderr)
            final_validation = run_script("validation.py", str(source_path))
            self.assertEqual(final_validation.returncode, 0, final_validation.stdout)
            self.assertIn("NEXT_ACTION=mark_complete", final_validation.stdout)

    def test_progress_rebuild_preserves_completion(self) -> None:
        with tempfile.TemporaryDirectory(prefix="renpy-tl-progress-") as raw_root:
            project_root = Path(raw_root)
            game_root = project_root / "game"
            _ = game_root.mkdir()
            first = game_root / "first.rpy"
            second = game_root / "second.rpy"
            _ = first.write_text("", encoding="utf-8")
            _ = second.write_text("", encoding="utf-8")
            progress = project_root / "progress.md"
            _ = progress.write_text(
                "# Translation Progress\n\n- [x] game/first.rpy\n",
                encoding="utf-8",
            )

            result = run_script(
                "build_progress.py",
                str(game_root),
                "--project-root",
                str(project_root),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                progress.read_text(encoding="utf-8"),
                "# Translation Progress\n\n"
                + "- [x] game/first.rpy\n"
                + "- [ ] game/second.rpy\n",
            )


if __name__ == "__main__":
    _ = unittest.main()
