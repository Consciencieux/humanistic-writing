"""Resource routing and installed lookup behavior; no prose quality scoring."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import package_skills as package
import rules


class CapabilityTests(unittest.TestCase):
    def test_lookup_returns_one_complete_section(self):
        registry = rules.collect(ROOT)
        rule = registry['PROSE-07']
        lines = (ROOT / rule.path).read_text(encoding='utf-8').splitlines()
        self.assertEqual(rule.text, '\n'.join(lines[rule.start_line - 1:rule.end_line]) + '\n')
        self.assertNotIn('## PROSE-08', rule.text)

    def test_examples_inside_code_fences_are_not_definitions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / 'shared'
            shared.mkdir()
            (shared / 'example.md').write_text(
                '# Example\n\n<a id="real-01"></a>\n## REAL-01 Real rule\n\n'
                'Rule content.\n\n```md\n<a id="fake-99"></a>\n## FAKE-99 Example\n```\n',
                encoding='utf-8')
            self.assertEqual(set(rules.collect(root)), {'REAL-01'})

    def test_duplicate_definition_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / 'shared'
            shared.mkdir()
            content = '# Rules\n\n<a id="test-01"></a>\n## TEST-01 Example\n\nContent.\n'
            for name in ('first.md', 'second.md'):
                (shared / name).write_text(content, encoding='utf-8')
            with self.assertRaisesRegex(rules.RuleError, 'Duplicate ID'):
                rules.collect(root)

    def test_incomplete_entry_and_unknown_reference_are_rejected(self):
        for fault in ('baseline', 'unknown'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / 'repo'
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('dist', '__pycache__', '.git'))
                entry = root / 'SKILL.md'
                text = entry.read_text(encoding='utf-8')
                if fault == 'baseline':
                    text = text.replace('[加载协议](shared/protocols/context.md)', '加载协议')
                    expected = 'missing baseline pointer'
                else:
                    text += '\nUse PROSE-99 here.\n'
                    expected = 'unknown rule ID'
                entry.write_text(text, encoding='utf-8')
                with self.assertRaisesRegex(package.RepositoryError, expected):
                    package.check_source(root)

    def test_installed_lookup_reads_role_method_and_rejects_absent_role(self):
        for kind, ident, absent in (("guide", "EDIT-02", "AUDIT-01"),
                                    ("guide", "HEADING-02", "AUDIT-08"),
                                    ("audit", "AUDIT-08", "HEADING-01")):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                skill = package.populate(ROOT, directory, kind)
                command = [sys.executable, str(skill / 'scripts/rules.py')]
                result = subprocess.run(command + [ident, '--file', '--json'],
                                        cwd=directory, text=True, encoding='utf-8', capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                items = json.loads(result.stdout)
                self.assertEqual(len(items), 1)
                self.assertTrue(items[0]['path'].startswith('references/'))
                self.assertEqual(items[0]['text'],
                                 (skill / items[0]['path']).read_text(encoding='utf-8'))
                unknown = subprocess.run(command + [absent], cwd=directory,
                                         text=True, encoding='utf-8', capture_output=True)
                self.assertNotEqual(unknown.returncode, 0)
                self.assertIn('Unknown ID', unknown.stderr)

    def test_role_definitions_are_discovered_but_fixture_definitions_are_not(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'shared').mkdir()
            for folder, ident in [('skills/example/references', 'ROLE-01'),
                                  ('evals/fixtures', 'FIXTURE-01')]:
                path = root / folder / 'example.md'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'<a id="{ident.lower()}"></a>\n## {ident} Example\n\nContent.\n',
                                encoding='utf-8')
            self.assertEqual(set(rules.collect(root)), {'ROLE-01'})

    def test_shared_resources_cannot_depend_on_role_links_or_ids(self):
        for reference in ('[review](../skills/humanistic-writing-audit/references/review.md)',
                          'Apply REVIEW-02 here.'):
            with self.subTest(reference=reference), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / 'repo'
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('dist', '__pycache__', '.git'))
                with (root / 'shared/core.md').open('a', encoding='utf-8') as stream:
                    stream.write('\n' + reference + '\n')
                with self.assertRaisesRegex(package.RepositoryError, 'shared resource depends on a role'):
                    package.check_source(root)

    def test_unreachable_role_method_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'repo'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('dist', '__pycache__', '.git'))
            orphan = root / 'skills/humanistic-writing-guide/references/unlinked.md'
            orphan.write_text('<a id="orphan-01"></a>\n## ORPHAN-01 Unlinked method\n\nContent.\n',
                              encoding='utf-8')
            with self.assertRaisesRegex(package.RepositoryError, 'Unreachable runtime resource'):
                package.check_source(root)


if __name__ == '__main__':
    unittest.main()
