"""High-value regressions for packaging and text counting, not prose scoring."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import package_skills as package
import text_stats
import rules


class TextCountTests(unittest.TestCase):
    def test_visible_text_excludes_urls_and_code_blocks(self):
        text = "[说明](https://example.com/很长的地址) **AI** 帮我。\n```python\n不计入正文\n```\n"
        counts = text_stats.count_text(text)
        self.assertEqual(counts["han_characters"], 4)
        self.assertEqual(counts["other_letter_number_groups"], 1)

    def test_stop_heading_is_not_triggered_inside_code(self):
        text = "# 正文\n甲乙。\n```\n## 注释\n不应截断\n```\n丙丁。\n## 注释\n戊己。\n"
        self.assertEqual(text_stats.count_text(text, stop_before="注释")["han_characters"], 6)
        self.assertEqual(text_stats.count_text(text)["han_characters"], 10)

    def test_plain_mode_retains_literal_content(self):
        text = "```\n甲乙\n```"
        self.assertEqual(text_stats.count_text(text)["han_characters"], 0)
        self.assertEqual(text_stats.count_text(text, markdown=False)["han_characters"], 2)


class PackageTests(unittest.TestCase):
    def test_all_entries_build_self_contained_packages(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            outputs = package.build(ROOT, directory / "output", list(package.ENTRIES))
            self.assertEqual(len(outputs), 3)
            for kind, archive_path in zip(package.ENTRIES, outputs):
                with zipfile.ZipFile(archive_path) as archive:
                    archive.extractall(directory / "expanded")
                skill = directory / "expanded" / package.NAMES[kind]
                package.check_entry(skill / "SKILL.md", package.NAMES[kind])
                package.check_links(skill)
                self.assertTrue((skill / "shared/core.md").is_file())
                self.assertTrue((skill / "scripts/text_stats.py").is_file())
                self.assertFalse((skill / "evals").exists())
                self.assertEqual(len(list(skill.rglob("SKILL.md"))), 1)
                self.assertFalse((skill / "shared/methods").exists())
                registry = rules.collect(skill)
                if kind == "combined":
                    self.assertTrue((skill / "roles/guide.md").is_file())
                    self.assertFalse((skill / "roles/guide.md").read_text(encoding="utf-8").startswith("---"))
                    self.assertEqual(registry["EDIT-02"].path, "roles/guide/revise.md")
                    self.assertEqual(registry["AUDIT-03"].path, "roles/audit/prohibitions.md")
                    self.assertEqual(set(registry), set(rules.collect(ROOT)))
                elif kind == "guide":
                    self.assertEqual(registry["EDIT-02"].path, "references/revise.md")
                    self.assertNotIn("AUDIT-01", registry)
                    self.assertNotIn("REVIEW-01", registry)
                else:
                    self.assertEqual(registry["AUDIT-03"].path, "references/prohibitions.md")
                    self.assertNotIn("EDIT-01", registry)
                    self.assertNotIn("WRITE-01", registry)

    def test_source_archive_is_repository_not_install_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "source.zip"
            package.archive_source(ROOT, output)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
            for relative in ["SKILL.md", "skills/humanistic-writing-guide/SKILL.md", "docs/design.md", "scripts/package_skills.py", "evals/cases.json", "tests/test_tools.py", "skills/humanistic-writing-guide/references/revise.md", "skills/humanistic-writing-audit/references/prohibitions.md", "evals/fixtures/local-edit/article.md"]:
                self.assertIn(f"humanistic-writing/{relative}", names)
            self.assertFalse(any("/__pycache__/" in name or "/dist/" in name or "/.git/" in name
                                 or "/shared/methods/" in name for name in names))

    def test_runtime_links_do_not_escape(self):
        with self.assertRaises(package.RepositoryError):
            package.resolve_local(ROOT, ROOT / "SKILL.md", "../../outside.md")

    def test_rewrite_does_not_touch_fenced_or_inline_code(self):
        source = (ROOT / "skills/humanistic-writing-guide/SKILL.md").resolve()
        target = (ROOT / "shared/core.md").resolve()
        text = "[core](../../shared/core.md)\n`[literal](../../shared/core.md)`\n```md\n[example](../../shared/core.md)\n```\n"
        result = package.rewrite_links(text, source, Path("SKILL.md"), {target: Path("shared/core.md")}, ROOT)
        self.assertIn("[core](shared/core.md)", result)
        self.assertIn("`[literal](../../shared/core.md)`", result)
        self.assertIn("[example](../../shared/core.md)", result)

    def test_missing_resource_stops_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("dist", "__pycache__", ".git"))
            with (root / "SKILL.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[missing](shared/no-such-file.md)\n")
            with self.assertRaisesRegex(package.RepositoryError, "missing link target"):
                package.check_source(root)


if __name__ == "__main__":
    unittest.main()
