"""Keep the fast museum route narrow and preserve the full publication gates."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


class WorkflowTests(unittest.TestCase):
    def test_archive_uses_one_automatic_pages_dispatch_owner(self):
        legacy = workflow("deploy-pages-after-record-chain-archive.yml")
        self.assertEqual(set(legacy.get("on", legacy.get(True))), {"workflow_dispatch"})
        sync = workflow("homepage-status-sync.yml")
        trigger = sync.get("on", sync.get(True))
        self.assertIn("Record Chain Arweave Archive", trigger["workflow_run"]["workflows"])
        self.assertTrue(any("gh workflow run deploy-pages.yml" in s.get("run", "")
                            for s in sync["jobs"]["deploy"]["steps"]))

    def test_required_jobs_always_report_and_heavy_steps_require_full_scope(self):
        jobs = {
            "repository-integrity.yml": ["current-system-integrity"],
            "run-current-tests.yml": ["current-tests"],
            "record-chain-ci.yml": ["verify-record-chain"],
            "record-chain-gateway-tests.yml": ["gateway-tests", "gateway-python-312-compat"],
            "public-verification-context-contract.yml": ["contract"],
        }
        for name, ids in jobs.items():
            data = workflow(name)
            trigger = data.get("on", data.get(True))
            self.assertNotIn("paths-ignore", trigger["pull_request"] or {})
            for id in ids:
                job = data["jobs"][id]
                self.assertNotIn("if", job)
                steps = job["steps"]
                classifier = next(s for s in steps if s.get("id") == "museum_scope")
                self.assertNotIn("if", classifier)
                self.assertNotIn("continue-on-error", classifier)
                for s in steps:
                    run = s.get("run", "")
                    if any(x in run for x in ["pip install", "npm ci", "run_current_system_tests.py", "trinity_record_chain.py verify", "pytest"]):
                        self.assertEqual(s.get("if"), "steps.museum_scope.outputs.museum_only != 'true'", (name, s))
                        self.assertLess(steps.index(classifier), steps.index(s))
        integrity = workflow("repository-integrity.yml")["jobs"]
        self.assertIn("museum_only != 'true'", integrity["refresh-repository-preservation-doi"]["if"])
        validators = integrity["current-system-integrity"]["steps"]
        self.assertTrue(any("museum/scripts/validate.py" in s.get("run", "") and "== 'true'" in s.get("if", "") for s in validators))
        for s in validators:
            if "test_no_secret_material_committed.py" in s.get("run", ""):
                self.assertNotIn("if", s)

    def test_deployment_scope_and_live_verifiers_are_complementary(self):
        data = workflow("deploy-pages.yml")
        self.assertEqual(data["permissions"]["actions"], "read")
        jobs = data["jobs"]
        classifier = next(s for s in jobs["verify"]["steps"] if s.get("id") == "museum_scope")
        self.assertIn("--deployment", classifier["run"])
        for id in ["verify", "build"]:
            self.assertIn("museum_only", jobs[id]["outputs"])
            self.assertIn("baseline_sha", jobs[id]["outputs"])
        steps = jobs["verify-live-deployment"]["steps"]
        museum = next(s for s in steps if "smoke_live_museum.py" in s.get("run", ""))
        full = next(s for s in steps if "smoke_live_discovery_contract_v2.py" in s.get("run", ""))
        self.assertEqual(museum["if"], "needs.build.outputs.museum_only == 'true'")
        self.assertEqual(full["if"], "needs.build.outputs.museum_only != 'true'")
        self.assertNotIn("continue-on-error", museum)
        self.assertIn("--strict-digest", full["run"])
        build = jobs["build"]["steps"]
        for name in ["Publish exact static museum at /museum/", "Verify exact Pages artifact contract"]:
            self.assertNotIn("if", next(s for s in build if s.get("name") == name))

    def test_receipts_do_not_claim_unrun_main_checks(self):
        receipt = (ROOT / ".github/workflows/homepage-deployment-receipt.yml").read_text()
        self.assertIn('scope not in ("full", "museum")', receipt)
        self.assertIn("unrelated main-site live contracts were not rerun", receipt)
        closure = workflow("verify-pages-production.yml")["jobs"]["verify-production"]["steps"]
        self.assertTrue(any("museum_change_scope.py --deployment" in s.get("run", "") for s in closure))
        report = next(s for s in closure if s.get("name") == "Publish final production evidence")["run"]
        self.assertIn('static_outcome="not-run (museum-only changes)"', report)
        self.assertIn('museum_outcome="$LIVE_OUTCOME"', report)


if __name__ == "__main__":
    unittest.main()
