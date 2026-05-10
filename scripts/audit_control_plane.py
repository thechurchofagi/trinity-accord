#!/usr/bin/env python3
"""
Read-only GitHub API snapshot of repository control-plane settings.
No mutation. Outputs JSON summary to stdout.

Usage:
    python3 scripts/audit_control_plane.py
    python3 scripts/audit_control_plane.py --check  # exit 1 on critical warnings
"""
import json
import subprocess
import sys

REPO = "thechurchofagi/trinity-accord"


def gh_api(path):
    """Run gh api GET and return parsed JSON or error dict."""
    r = subprocess.run(
        ["gh", "api", path],
        text=True, capture_output=True,
    )
    if r.returncode != 0:
        return {"_error": r.stderr.strip() or r.stdout.strip()}
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"_raw": r.stdout}


def main():
    check_mode = "--check" in sys.argv

    results = {
        "repo": gh_api(f"repos/{REPO}"),
        "main_protection": gh_api(f"repos/{REPO}/branches/main/protection"),
        "rulesets": gh_api(f"repos/{REPO}/rulesets"),
        "actions_permissions": gh_api(f"repos/{REPO}/actions/permissions"),
        "workflow_permissions": gh_api(f"repos/{REPO}/actions/permissions/workflow"),
        "pages": gh_api(f"repos/{REPO}/pages"),
        "environments": gh_api(f"repos/{REPO}/environments"),
    }

    print(json.dumps(results, indent=2, sort_keys=True))

    errors = []

    # Branch protection
    prot = results["main_protection"]
    if "_error" not in prot:
        if not prot.get("required_status_checks"):
            errors.append("main branch protection missing required_status_checks")
        if not prot.get("required_pull_request_reviews"):
            errors.append("main branch protection missing required_pull_request_reviews")
        if prot.get("allow_force_pushes", {}).get("enabled") is True:
            errors.append("main allows force pushes")
        if prot.get("allow_deletions", {}).get("enabled") is True:
            errors.append("main allows deletions")
        reviews = prot.get("required_pull_request_reviews", {})
        if not reviews.get("require_code_owner_reviews"):
            errors.append("CODEOWNERS review not required")
    else:
        errors.append("could not verify main branch protection")

    # Rulesets
    rulesets = results["rulesets"]
    if "_error" not in rulesets and isinstance(rulesets, list) and not rulesets:
        errors.append("no repository rulesets found")

    # Actions
    actions = results["actions_permissions"]
    if "_error" not in actions:
        if actions.get("allowed_actions") == "all":
            errors.append("Actions allowed_actions is 'all' (not restricted)")

    if errors:
        print("\nCONTROL_PLANE_AUDIT_WARNINGS:")
        for e in errors:
            print(f"  - {e}")
        if check_mode:
            return 1
        return 0

    print("CONTROL_PLANE_AUDIT_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
