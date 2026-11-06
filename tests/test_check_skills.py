import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-skills.py"
SPEC = importlib.util.spec_from_file_location("collection_check", SCRIPT)
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class CollectionCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / "v-sample"
        self.skill.mkdir()
        self.entry = self.skill / "SKILL.md"
        self.entry.write_text("---\nname: v-sample\ndescription: Validate a sample workflow\n---\nInstructions.\n")

    def test_nested_skills_and_generated_folder_exclusions(self):
        nested = self.skill / "nested-ui"
        nested.mkdir()
        (nested / "SKILL.md").write_text("---\nname: nested-ui\ndescription: Nested UI skill\n---\nInstructions.\n")
        excluded = self.root / "node_modules" / "broken"
        excluded.mkdir(parents=True)
        (excluded / "SKILL.md").write_text("invalid frontmatter")
        (excluded / "bad.py").write_text("this is invalid python !!!")
        records, files, errors = check.validate_catalog(self.root)
        self.assertEqual({r["name"] for r in records}, {"v-sample", "nested-ui"})
        self.assertFalse(any("node_modules" in p.parts for p in files))
        self.assertEqual(errors, [])

    def test_empty_description_and_real_missing_reference_fail(self):
        self.entry.write_text("---\nname: v-sample\ndescription: ''\n---\nRead [the procedure](references/missing.md).\n")
        _, _, errors = check.validate_catalog(self.root)
        self.assertTrue(any("description" in error for error in errors))
        self.assertTrue(any("missing linked resource" in error for error in errors))

    def test_examples_do_not_become_broken_navigation(self):
        with self.entry.open("a") as output:
            output.write("\n```markdown\n[Example](generated/report.md)\n```\n")
            output.write("Inline example: `[Sample](generated/sample.png)`\n")
        _, _, errors = check.validate_catalog(self.root)
        self.assertEqual(errors, [])

    def test_duplicate_names_and_invalid_yaml_are_reported(self):
        another = self.root / "nested" / "v-sample"
        another.mkdir(parents=True)
        (another / "SKILL.md").write_text(self.entry.read_text())
        records, _, errors = check.validate_catalog(self.root)
        self.assertEqual(len(records), 2)
        self.assertTrue(any("duplicate skill name" in error for error in errors))
        self.entry.write_text("---\nname: [invalid\n---\nInstructions.\n")
        _, _, errors = check.validate_catalog(self.root)
        self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_metadata_references_its_actual_skill(self):
        agents = self.skill / "agents"
        agents.mkdir()
        (agents / "openai.yaml").write_text('interface:\n  default_prompt: "Use $different-skill"\n')
        _, _, errors = check.validate_catalog(self.root)
        self.assertTrue(any("default_prompt" in error for error in errors))

    def test_skipped_skill_tests_fail_instead_of_claiming_coverage(self):
        tests = self.skill / "tests"
        tests.mkdir()
        (tests / "test_optional.py").write_text(
            "import unittest\n@unittest.skip('missing dependency')\n"
            "class OptionalTests(unittest.TestCase):\n"
            "    def test_optional(self): pass\n")
        records, _, _ = check.validate_catalog(self.root)
        results, errors = check.run_tests(self.root, records, sys.executable)
        self.assertEqual(results[0]["run"], 1)
        self.assertEqual(results[0]["skipped"], 1)
        self.assertTrue(errors)

    def test_cli_returns_nonzero_and_json_for_broken_skill(self):
        self.entry.write_text("---\nname: v-sample\ndescription: ''\n---\nInstructions.\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.root), "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["skills"], 1)
        self.assertTrue(json.loads(result.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
