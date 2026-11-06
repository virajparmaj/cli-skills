import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "installer", Path(__file__).resolve().parents[1] / "scripts" / "install-skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.target = self.base / "workflow" / "skills"
        self.target.mkdir(parents=True)
        self.skill("v-test")

    def skill(self, name, parent=None):
        folder = (parent or self.repo) / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill\n---\nTest instructions.\n")
        return folder

    def plan(self):
        return installer.make_plan(self.repo, installer.discover(self.repo), [self.target])

    def test_nested_skills_install_and_second_run_has_no_changes(self):
        nested = self.skill("good-css", self.repo / "v-ui")
        installer.apply_plan(self.plan())
        self.assertEqual((self.target / "good-css").resolve(), nested)
        self.assertTrue(all(a["action"] == "unchanged" for a in self.plan()))

    def test_real_directory_prevents_all_mutation(self):
        self.skill("v-other")
        existing = self.target / "v-test"
        existing.mkdir()
        original = existing / "user-file"
        original.write_text("keep me")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            installer.apply_plan(self.plan())
        self.assertEqual(original.read_text(), "keep me")
        self.assertFalse((self.target / "v-other").exists())

    def test_foreign_symlink_is_preserved(self):
        foreign = self.base / "other-author"
        foreign.mkdir()
        dest = self.target / "v-test"
        dest.symlink_to(foreign)
        with self.assertRaises(ValueError):
            installer.apply_plan(self.plan())
        self.assertEqual(dest.resolve(), foreign)

    def test_only_owned_retired_links_are_removed(self):
        owned = self.target / "v-test-functional"
        owned.symlink_to(self.repo / "v-test-functional")  # Broken retired link.
        foreign = self.target / "v-macos"
        foreign.symlink_to(self.base / "unrelated-macos")
        real = self.target / "v-delovable"
        real.mkdir()
        installer.apply_plan(self.plan())
        self.assertFalse(owned.is_symlink())
        self.assertTrue(foreign.is_symlink())
        self.assertTrue(real.is_dir())

    def test_repoint_owned_link_and_preserve_changed_preflight_target(self):
        dest = self.target / "v-test"
        dest.symlink_to(self.repo / "previous-skill")
        plan = self.plan()
        installer.apply_plan(plan)
        self.assertEqual(dest.resolve(), self.repo / "v-test")
        dest.unlink()
        dest.symlink_to(self.repo / "previous-skill")
        plan = self.plan()
        dest.unlink()
        dest.symlink_to(self.base / "foreign")
        with self.assertRaisesRegex(ValueError, "changed after preflight"):
            installer.apply_plan(plan)
        self.assertEqual(dest.resolve(), self.base / "foreign")

    def test_reject_source_tree_as_destination(self):
        with self.assertRaisesRegex(ValueError, "outside the source"):
            installer.make_plan(self.repo, installer.discover(self.repo), [self.repo / "skills"])

    def test_reject_duplicate_declared_names(self):
        self.skill("v-test", self.repo / "nested")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            installer.discover(self.repo)


if __name__ == "__main__":
    unittest.main()
