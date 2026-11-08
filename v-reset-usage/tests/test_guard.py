"""Exercise mechanical safeguards against real isolated Git repositories."""

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


GUARD = Path(__file__).resolve().parents[1] / "scripts" / "guard.py"


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.checkpoint = self.base / "checkpoint.json"
        self.git("init", "-b", "main")
        self.git("config", "user.name", "virajparmaj")
        self.git("config", "user.email", "viraj.parmaj89@gmail.com")
        self.git("config", "core.filemode", "true")
        self.write("src/helpers.py", "def unused():\n    return 1\n")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_guard(self, *args, eligible=True):
        result = subprocess.run([sys.executable, "-B", str(GUARD), *map(str, args)],
                                capture_output=True, text=True)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0 if eligible else 2, payload)
        self.assertEqual(payload["eligible"], eligible, payload)
        return payload

    def capture(self, eligible=True):
        return self.run_guard("capture", "--repo", self.repo, "--output", self.checkpoint,
                              eligible=eligible)

    def verify(self, *paths, eligible=True):
        args = ["verify", "--checkpoint", self.checkpoint]
        for path in paths:
            args.extend(["--allow", path])
        return self.run_guard(*args, eligible=eligible)

    def test_small_edit(self):
        self.capture()
        self.write("src/helpers.py", "def unused():\n    return 2\n")
        result = self.verify("src/helpers.py")
        self.assertEqual((result["added"], result["deleted"]), (1, 1))

    def test_deletion(self):
        self.capture()
        (self.repo / "src/helpers.py").unlink()
        self.assertEqual(self.verify("src/helpers.py")["deleted"], 2)

    def test_dirty_baseline(self):
        self.write("src/helpers.py", "changed\n")
        self.capture(eligible=False)
        self.verify("src/helpers.py", eligible=False)

    def test_untracked_baseline(self):
        self.write("scratch.txt", "keep me\n")
        self.capture(eligible=False)

    def test_staged_baseline(self):
        self.write("src/helpers.py", "changed\n")
        self.git("add", ".")
        self.capture(eligible=False)

    def test_staged_change(self):
        self.capture()
        self.write("src/helpers.py", "changed\n")
        self.git("add", ".")
        self.verify("src/helpers.py", eligible=False)

    def test_changed_head(self):
        self.capture()
        self.git("commit", "--allow-empty", "-m", "concurrent commit")
        self.verify(eligible=False)

    def test_changed_branch(self):
        self.capture()
        self.git("switch", "-c", "another")
        self.verify(eligible=False)

    def test_protected_paths(self):
        paths = ["src/auth/token.py", "src/pages/Home.tsx", "src/train_model.py",
                 "src/calculateRiskScore.ts", "src/financeMath.py",
                 "tests/check.py", "vite.config.ts", "src/index.ts", "scripts/tool.py"]
        for path in paths:
            self.write(path, "original\n")
        self.git("add", ".")
        self.git("commit", "-m", "protected fixtures")
        self.capture()
        for path in paths:
            with self.subTest(path=path):
                self.write(path, "changed\n")
                self.verify(path, eligible=False)
                self.write(path, "original\n")

    def test_unexpected_change(self):
        self.capture()
        self.write("src/helpers.py", "changed\n")
        self.verify(eligible=False)

    def test_untracked_change(self):
        self.capture()
        self.write("src/new.py", "new\n")
        self.verify("src/new.py", eligible=False)

    def test_over_line_budget(self):
        self.capture()
        self.write("src/helpers.py", "x\n" * 101)
        self.verify("src/helpers.py", eligible=False)

    def test_over_file_budget(self):
        paths = ["src/helper%d.py" % i for i in range(6)]
        for path in paths:
            self.write(path, "original\n")
        self.git("add", ".")
        self.git("commit", "-m", "six helpers")
        self.capture()
        for path in paths:
            self.write(path, "changed\n")
        self.verify(*paths, eligible=False)

    def test_binary_change(self):
        self.capture()
        (self.repo / "src/helpers.py").write_bytes(b"\0binary\n")
        self.verify("src/helpers.py", eligible=False)

    def test_mode_change(self):
        self.capture()
        (self.repo / "src/helpers.py").chmod(0o755)
        self.verify("src/helpers.py", eligible=False)

    def test_mode_change_when_repository_ignores_modes(self):
        self.git("config", "core.filemode", "false")
        self.capture()
        (self.repo / "src/helpers.py").chmod(0o755)
        self.verify("src/helpers.py", eligible=False)

    def test_binary_even_when_attributes_force_text_diff(self):
        self.write(".gitattributes", "*.py diff\n")
        self.git("add", ".")
        self.git("commit", "-m", "force text diff fixture")
        self.capture()
        (self.repo / "src/helpers.py").write_bytes(b"\0binary\n")
        self.verify("src/helpers.py", eligible=False)

    def test_inspection_preserves_repository_file_contents(self):
        before = {str(p.relative_to(self.repo)): p.read_bytes()
                  for p in self.repo.rglob("*") if p.is_file()}
        self.capture()
        self.verify("src/helpers.py")
        after = {str(p.relative_to(self.repo)): p.read_bytes()
                 for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_symlink_change(self):
        self.capture()
        path = self.repo / "src/helpers.py"
        path.unlink()
        path.symlink_to("elsewhere.py")
        self.verify("src/helpers.py", eligible=False)

    def test_deleted_tracked_symlink(self):
        path = self.repo / "src/link.py"
        path.symlink_to("helpers.py")
        self.git("add", ".")
        self.git("commit", "-m", "symlink fixture")
        self.capture()
        path.unlink()
        self.verify("src/link.py", eligible=False)

    def test_checkpoint_overwrite(self):
        self.capture()
        contents = self.checkpoint.read_bytes()
        self.capture(eligible=False)
        self.assertEqual(self.checkpoint.read_bytes(), contents)

    def test_checkpoint_inside_repo(self):
        self.run_guard("capture", "--repo", self.repo, "--output",
                       self.repo / "checkpoint.json", eligible=False)
        self.assertFalse((self.repo / "checkpoint.json").exists())

    def test_checkpoint_inside_git_dir(self):
        self.run_guard("capture", "--repo", self.repo, "--output",
                       self.repo / ".git/checkpoint.json", eligible=False)

    def test_pending_operation_and_lock(self):
        for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "BISECT_LOG", "index.lock"):
            with self.subTest(name=name):
                path = self.repo / ".git" / name
                path.write_text("pending")
                self.run_guard("capture", "--repo", self.repo, "--output",
                               self.base / (name + ".json"), eligible=False)
                path.unlink()

    def test_linked_worktree_operation_and_lock_markers(self):
        linked = self.base / "linked"
        self.git("worktree", "add", "-b", "fixture-link", str(linked))
        gitdir = Path(subprocess.check_output(
            ["git", "-C", str(linked), "rev-parse", "--absolute-git-dir"], text=True).strip())
        for name in ("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD",
                     "BISECT_LOG", "index.lock", "HEAD.lock"):
            with self.subTest(name=name):
                path = gitdir / name
                path.write_text("pending")
                self.run_guard("capture", "--repo", linked, "--output",
                               self.base / (name + ".json"), eligible=False)
                path.unlink()

    def test_shared_ref_lock(self):
        (self.repo / ".git/refs/heads/main.lock").write_text("locked")
        self.capture(eligible=False)

    def test_submodule_dirt_cannot_be_hidden_by_config(self):
        source = self.base / "submodule-source"
        source.mkdir()
        self.git("-C", str(source), "init", "-b", "main")
        self.git("-C", str(source), "config", "user.name", "virajparmaj")
        self.git("-C", str(source), "config", "user.email", "viraj.parmaj89@gmail.com")
        (source / "value.py").write_text("original\n")
        self.git("-C", str(source), "add", ".")
        self.git("-C", str(source), "commit", "-m", "submodule fixture")
        self.git("-c", "protocol.file.allow=always", "submodule", "add", str(source), "deps/library")
        self.git("commit", "-am", "add submodule")
        self.git("config", "diff.ignoreSubmodules", "all")
        self.git("config", "submodule.deps/library.ignore", "all")
        self.capture()
        self.write("deps/library/value.py", "changed\n")
        self.verify(eligible=False)
        self.run_guard("capture", "--repo", self.repo, "--output",
                       self.base / "dirty-submodule.json", eligible=False)

    def test_timeout_returns_json_audit_only(self):
        spec = importlib.util.spec_from_file_location("reset_usage_guard", GUARD)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = io.StringIO()
        with mock.patch.object(module.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 20)):
            with redirect_stdout(output):
                code = module.main(["capture", "--repo", str(self.repo), "--output", str(self.checkpoint)])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(output.getvalue())["eligible"])
        self.assertFalse(self.checkpoint.exists())

    def test_detached_head(self):
        self.git("checkout", "--detach")
        self.capture(eligible=False)

    def test_missing_head(self):
        empty = self.base / "empty"
        empty.mkdir()
        subprocess.run(["git", "init", "-b", "main", str(empty)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.run_guard("capture", "--repo", empty, "--output", self.checkpoint,
                       eligible=False)

    def test_path_escape(self):
        self.capture()
        self.verify("../helpers.py", eligible=False)

    def test_assume_unchanged_index(self):
        self.git("update-index", "--assume-unchanged", "src/helpers.py")
        self.capture(eligible=False)


if __name__ == "__main__":
    unittest.main()
