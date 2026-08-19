#!/usr/bin/env python3
"""Only explicitly noncritical workflow triggers may be warning-only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"

allowed_warning_fragments = {
    'gh workflow run build-echo-index.yml --ref main || echo "::warning::Could not trigger echo index rebuild"',
    'git checkout -b "$PROGRESS_BRANCH" 2>/dev/null || true',
    'git push origin "$PROGRESS_BRANCH" 2>/dev/null || true',
    'git push origin --delete "$PROGRESS_BRANCH" 2>/dev/null || true',
    'gh issue edit "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --remove-label "needs-human-review" || true',
    'git add archive/ --intent-to-add 2>/dev/null || true',
    'SIZE=$(stat -c%s /tmp/arweave-raw.bin 2>/dev/null || echo 0)',
    'ls -la archive/evidence/flaw-archive-bundle.zip 2>/dev/null || true',
    'sha256sum archive/evidence/flaw-archive-bundle.zip 2>/dev/null || true',
    'git commit -m "feat: mirror flaw images from Arweave (11 JPGs, Core Object Alpha physical evidence)" || echo "No changes"',
    'git rebase --abort || true',
    'git stash --include-untracked || true',
    'git stash pop 2>/dev/null || true',
    'git add record-chain/ots/arweave-bundles/ record-chain/ots/arweave-registry.json api/record-chain-ots-arweave-registry.json 2>/dev/null || true',
    '"${GATEWAY}/gateway/capabilities" || echo "000")',
    '"${GATEWAY}/gateway/preflight" || echo "000")',
    'python3 scripts/generate_verification_archive_index.py || echo "::warning::Could not rebuild verification archive index"',
    # Sidechain live progress publication and local daemon cleanup are operational
    # telemetry only. Evidence verification itself remains fail-closed.
    'run: python3 scripts/publish-chronicle-sidechain-progress.py --phase setup --status running || true',
    'run: python3 scripts/publish-chronicle-sidechain-progress.py --phase car_l1 --status running || true',
    'kill "$kubo_pid" 2>/dev/null || true',
    'wait "$kubo_pid" 2>/dev/null || true',
    'wait "$publisher_pid" || true',
    'run: python3 scripts/publish-chronicle-sidechain-progress.py --phase offline_verify --status running || true',
    'run: python3 scripts/publish-chronicle-sidechain-progress.py --phase finalize --status running || true',
    'run: python3 scripts/publish-chronicle-sidechain-progress.py --phase release --status running || true',
    'python3 scripts/publish-chronicle-sidechain-progress.py --phase workflow_complete --status "${{ job.status }}" || true',
    'python3 scripts/sidechain-debug-live.py mark --phase workflow_complete --step terminal --status "${{ job.status }}" --detail "terminal workflow status" || true',
}

bad = []

for path in sorted(WF.glob("*.yml")):
    text = path.read_text(encoding="utf-8")

    for line in text.splitlines():
        stripped = line.strip()
        if "|| echo" not in stripped and "|| true" not in stripped:
            continue

        if stripped in allowed_warning_fragments:
            continue

        bad.append(f"{path.name}: unexpected warning/fail-open fallback: {stripped}")

if bad:
    print("FAIL: unexpected workflow warning/fail-open fallbacks:")
    for item in bad:
        print("  -", item)
    sys.exit(1)

print("PASS: workflow warning fallbacks are explicitly allowlisted")
