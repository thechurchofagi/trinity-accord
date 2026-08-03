from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR = ROOT / "scripts" / "test_render_manual_deploy_behavior.py"
CONTRACT = ROOT / "scripts" / "test_render_manual_deploy_contract.py"

text = BEHAVIOR.read_text(encoding="utf-8")
old = '''        if wait:
            sys.argv += [
                "--wait",
                "--wait-timeout",
                "5",
                "--poll-seconds",
                "0",
            ]
'''
new = '''        sys.argv += ["--deploy-id-recovery-timeout", "0"]
        if wait:
            sys.argv += [
                "--wait",
                "--wait-timeout",
                "5",
                "--poll-seconds",
                "0",
            ]
'''
if text.count(old) != 1:
    raise SystemExit("behavior argv anchor mismatch")
text = text.replace(old, new, 1)

old = '''    code, _stdout, stderr, calls = invoke(active, {})
    require(code == 1 and calls == 1, "missing deploy ID must fail after one POST")
    require("without returning a deploy id" in stderr.lower(), "missing deploy ID failure must be explicit")
'''
new = '''    def accepted_without_id(path: str, _token: str, method: str = "GET", body: dict | None = None):
        if method == "POST":
            return {}
        if path.endswith("/deploys?limit=20"):
            return []
        return {}

    code, _stdout, stderr, calls = invoke(active, accepted_without_id)
    require(
        code == 1 and calls == 2,
        "missing deploy ID without an exact recoverable candidate must fail after POST and one list read",
    )
    require(
        "no unique exact-commit deploy" in stderr.lower(),
        "missing deploy ID recovery failure must be explicit",
    )
'''
if text.count(old) != 1:
    raise SystemExit("behavior missing-id anchor mismatch")
text = text.replace(old, new, 1)
BEHAVIOR.write_text(text, encoding="utf-8")

text = CONTRACT.read_text(encoding="utf-8")
old = '''        if "deploy_id_from_response" not in text or "deployment is unconfirmed" not in text:
            errors.append("render_manual_deploy.py does not require a confirmed deploy ID")
        else:
            ok("render_manual_deploy.py requires a confirmed deploy ID")
'''
new = '''        if (
            "deploy_id_from_response" not in text
            or "recover_unique_deploy_id" not in text
            or "no unique exact-commit" not in text
        ):
            errors.append(
                "render_manual_deploy.py does not require a confirmed or uniquely recovered deploy ID"
            )
        else:
            ok("render_manual_deploy.py requires a confirmed or uniquely recovered deploy ID")
'''
if text.count(old) != 1:
    raise SystemExit("static confirmed-id anchor mismatch")
text = text.replace(old, new, 1)

old = '''            "RENDER_DEPLOY_LIVE",
            "wait_for_deploy",
            "--reconcile-config",
'''
new = '''            "RENDER_DEPLOY_LIVE",
            "RENDER_DEPLOY_ID_RECOVERED",
            "recover_unique_deploy_id",
            "--recover-existing-since",
            "wait_for_deploy",
            "--reconcile-config",
'''
if text.count(old) != 1:
    raise SystemExit("static marker anchor mismatch")
text = text.replace(old, new, 1)
CONTRACT.write_text(text, encoding="utf-8")

print("PASS: synchronized Render manual-deploy contracts with fail-closed async recovery")
