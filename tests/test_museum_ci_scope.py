"""Boundary regressions for the museum-only CI and publication route."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import museum_change_scope as scope
from scripts import smoke_live_museum as live


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "CI fixture")
        self.write("index.md", "main\n")
        self.write("museum/dist/index.html", "museum\n")
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE).decode().strip()

    def write(self, name, content):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def classify(self, *, before=None, deployment=False, baseline=None):
        head = self.git("rev-parse", "HEAD")
        return scope.classify({"before": before or self.base, "after": head,
                               "ref": "refs/heads/main", "repository": {"full_name": "owner/repo"}},
                              "push", head, root=self.root, deployment=deployment,
                              baseline_lookup=lambda *args: baseline or self.base)

    def test_museum_only_and_pull_request(self):
        self.write("museum/dist/index.html", "new museum")
        head = self.commit()
        self.assertTrue(self.classify()["museum_only"])
        self.assertTrue(scope.classify({"pull_request": {"base": {"sha": self.base}}},
                                      "pull_request", head, root=self.root)["museum_only"])

    def test_main_and_mixed_changes_stay_full(self):
        for name in ["index.md", "_config.yml", ".github/workflows/deploy-pages.yml", "scripts/tool.py"]:
            with self.subTest(name=name):
                self.write(name, "changed")
                self.write("museum/dist/index.html", name)
                self.commit()
                self.assertFalse(self.classify()["museum_only"])
                self.git("reset", "--hard", self.base)

    def test_large_changeset_does_not_hide_last_main_file(self):
        for i in range(350):
            self.write(f"museum/dist/{i}.txt", str(i))
        self.write("zz-main.txt", "must not be truncated")
        self.commit()
        result = self.classify()
        self.assertEqual(result["changed_count"], 351)
        self.assertFalse(result["museum_only"])

    def test_rename_from_main_is_not_museum_only(self):
        self.git("mv", "index.md", "museum/dist/renamed.md")
        self.commit()
        self.assertFalse(self.classify()["museum_only"])

    def test_deleted_main_file_is_not_museum_only(self):
        (self.root / "index.md").unlink()
        self.commit()
        self.assertFalse(self.classify()["museum_only"])

    def test_symlink_and_submodule_are_not_static_exports(self):
        (self.root / "museum/escape").symlink_to("../index.md")
        self.commit()
        self.assertFalse(self.classify()["museum_only"])
        self.git("reset", "--hard", self.base)
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.base + ",museum/submodule")
        self.git("commit", "-qm", "gitlink")
        self.assertFalse(self.classify()["museum_only"])

    def test_unknown_missing_empty_and_wrong_checkout_stay_full(self):
        self.assertFalse(self.classify()["museum_only"])
        self.write("museum/dist/index.html", "edit")
        head = self.commit()
        for event_name, event in [("workflow_dispatch", {}), ("schedule", {}),
                                  ("push", {"before": None, "after": head}),
                                  ("push", {"before": "0" * 40, "after": head}),
                                  ("push", {"before": self.base, "after": self.base})]:
            with self.subTest(event=event_name, data=event):
                self.assertFalse(scope.classify(event, event_name, head, root=self.root)["museum_only"])
        self.assertFalse(self.classify(before="1" * 40)["museum_only"])

    def test_unpublished_main_change_prevents_fast_deploy(self):
        self.write("index.md", "not yet published")
        unpublished = self.commit()
        self.write("museum/dist/index.html", "museum")
        self.commit()
        self.assertTrue(self.classify(before=unpublished)["museum_only"])
        self.assertFalse(self.classify(before=unpublished, deployment=True)["museum_only"])
        self.assertTrue(self.classify(before=unpublished, deployment=True,
                                      baseline=unpublished)["museum_only"])

    def test_workflow_run_requires_successful_same_repo_push(self):
        self.write("museum/dist/index.html", "new")
        head = self.commit()
        run = {"event": "push", "head_branch": "main", "head_sha": head,
               "conclusion": "success", "head_repository": {"full_name": "owner/repo"},
               "id": 10, "created_at": "2026-09-06T00:00:00Z"}
        def check(value):
            return scope.classify({"workflow_run": value, "repository": {"full_name": "owner/repo"}},
                                  "workflow_run", head, deployment=True, root=self.root,
                                  baseline_lookup=lambda *args: self.base)["museum_only"]
        self.assertTrue(check(run))
        for key, value in [("event", "workflow_dispatch"), ("head_branch", "topic"),
                           ("conclusion", "failure"), ("head_sha", self.base),
                           ("head_repository", {"full_name": "fork/repo"})]:
            self.assertFalse(check({**run, key: value}))

    def test_baseline_api_failure_runs_full(self):
        self.write("museum/dist/index.html", "new")
        head = self.commit()
        with patch.object(scope, "previous_pages_sha", side_effect=OSError("offline")):
            result = scope.classify({"before": self.base, "after": head, "ref": "refs/heads/main",
                                     "repository": {"full_name": "owner/repo"}}, "push", head,
                                    deployment=True, root=self.root, baseline_lookup=scope.previous_pages_sha)
        self.assertFalse(result["museum_only"])

    def test_api_baseline_excludes_manual_future_and_wrong_repo(self):
        def run(id, created, **overrides):
            return {"id": id, "created_at": created, "event": "push", "conclusion": "success",
                    "head_branch": "main", "head_repository": {"full_name": "owner/repo"},
                    "head_sha": str(id) * 40, **overrides}
        runs = [run(1, "01"), run(2, "02", event="workflow_dispatch"), run(3, "03"),
                run(4, "04", head_repository={"full_name": "fork/repo"}), run(5, "05")]
        with patch.object(scope.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps({"workflow_runs": runs}).encode())):
            self.assertEqual(scope.previous_pages_sha("owner/repo", "3", "04", "fixture-token"), "1" * 40)


class LiveTests(unittest.TestCase):
    def item(self, data=b"published"):
        return {"path": "index.html", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    def response(self, data, url="https://www.trinityaccord.org/museum/"):
        response = io.BytesIO(data)
        response.status = 200
        response.geturl = lambda: url
        return response

    def test_wrong_bytes_and_redirects_fail(self):
        for response in [self.response(b"corrupted"), self.response(b"published", "https://other.invalid/")]:
            with self.assertRaises(ValueError):
                live.verify_url("https://www.trinityaccord.org/museum/", self.item(), attempts=1,
                                opener=lambda *a, **k: response)

    def test_transient_failure_retries_only_file(self):
        from unittest.mock import Mock
        opener = Mock(side_effect=[OSError("connection reset"), self.response(b"published")])
        live.verify_url("https://www.trinityaccord.org/museum/", self.item(),
                        opener=opener, pause=lambda _: None)
        self.assertEqual(opener.call_count, 2)

    def test_unchanged_big_media_skipped_but_new_and_runtime_checked(self):
        old = {"big": {**self.item(), "bytes": 300000, "path": "big"}}
        current = {**old, "new": {**old["big"], "path": "new"}, "index.html": self.item()}
        self.assertEqual({i["path"] for i in live.selected_files(current, old)}, {"new", "index.html"})
        self.assertEqual(len(live.selected_files(current, {})), 3)

    def test_inventory_rejects_escape_duplicate_and_missing_entrypoints(self):
        good = [{**self.item(), "path": p} for p in ["index.html", "archive.html", "museum.js"]]
        self.assertEqual(len(live.inventory(json.dumps({"files": good}).encode())), 3)
        for files in [[], good + [good[0]], good + [{**self.item(), "path": "../index.html"}],
                      good + [{**self.item(), "path": "/index.html"}]]:
            with self.assertRaises(ValueError):
                live.inventory(json.dumps({"files": files}).encode())


if __name__ == "__main__":
    unittest.main()
