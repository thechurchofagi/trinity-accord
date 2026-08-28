#!/usr/bin/env python3
"""One-shot exact patcher for sidechain OTS lifecycle idempotency.

This file is removed by the workflow that executes it. Every replacement is
count-checked so repository drift fails closed instead of producing a partial
workflow edit.
"""

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_anchor() -> None:
    path = Path('.github/workflows/chronicle-sidechain-ots-anchor.yml')
    text = path.read_text(encoding='utf-8')

    marker = "      - name: Reconstruct exact canonical payload and verify message SHA-256\n        run: |\n"
    insert = '''      - name: Reverify existing immutable OTS anchor
        id: existing_anchor
        run: |
          set -euo pipefail
          short_sha="${SOURCE_SHA:0:12}"
          SOURCE_TAG="chronicle-sidechain-evidence-v2-${short_sha}"
          ANCHOR_TAG="chronicle-sidechain-ots-v2-${short_sha}"
          export SOURCE_TAG ANCHOR_TAG
          if ! gh release view "$ANCHOR_TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
            echo "exists=false" >> "$GITHUB_OUTPUT"
            echo "[OTS ANCHOR ABSENT] a new immutable receipt may be created"
            exit 0
          fi
          root="$RUNNER_TEMP/existing-ots-anchor"
          rm -rf "$root"
          mkdir -p "$root"
          gh release download "$ANCHOR_TAG" --repo "$GITHUB_REPOSITORY" --dir "$root"
          test -s "$root/ANCHOR-REQUEST.json"
          test -s "$root/anchor-payload.canonical.json"
          test -s "$root/anchor-payload.canonical.json.ots"
          test -s "$root/MESSAGE-SHA256.txt"
          test -s "$root/OTS-RECEIPT.json"
          test -s "$root/SHA256SUMS"
          (cd "$root" && sha256sum -c SHA256SUMS)
          EXISTING_ROOT="$root" python3 - <<'PYVERIFY'
          import hashlib, json, os, pathlib
          root = pathlib.Path(os.environ['EXISTING_ROOT'])
          request = json.loads((root / 'ANCHOR-REQUEST.json').read_text())
          receipt = json.loads((root / 'OTS-RECEIPT.json').read_text())
          payload = (root / 'anchor-payload.canonical.json').read_bytes()
          message = hashlib.sha256(payload).hexdigest()
          expected = request.get('message_sha256')
          checks = {
              'request_schema': request.get('schema') == 'trinity-accord/chronicle-sidechain-anchor-request/v2',
              'receipt_schema': receipt.get('schema') == 'trinity-accord/chronicle-sidechain-ots-receipt/v1',
              'message_hash': message == expected == receipt.get('message_sha256'),
              'source_sha': receipt.get('source_commit_sha') == os.environ['SOURCE_SHA'],
              'source_tag': receipt.get('source_release_tag') == os.environ['SOURCE_TAG'],
              'anchor_tag': receipt.get('anchor_release_tag') == os.environ['ANCHOR_TAG'],
          }
          if not all(checks.values()):
              raise SystemExit(f'existing immutable OTS anchor failed binding checks: {checks}')
          print('[EXISTING OTS ANCHOR REVERIFIED] ' + json.dumps(checks, sort_keys=True))
          PYVERIFY
          echo "exists=true" >> "$GITHUB_OUTPUT"

''' + marker
    text = replace_once(text, marker, insert, 'anchor preflight insertion')

    for name in (
        'Reconstruct exact canonical payload and verify message SHA-256',
        'Submit new OpenTimestamps proof',
        'Build OTS receipt and checksums',
        'Publish immutable OTS receipt release',
    ):
        old = f"      - name: {name}\n"
        new = old + "        if: steps.existing_anchor.outputs.exists != 'true'\n"
        text = replace_once(text, old, new, f'anchor condition {name}')

    old_race = '''          if gh release view "$ANCHOR_TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
            echo "OTS receipt release already exists; refusing to mutate it." >&2
            exit 1
          fi
'''
    new_race = '''          if gh release view "$ANCHOR_TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
            echo "[OTS ANCHOR RACE] immutable release appeared after preflight; re-verifying instead of mutating"
            root="$RUNNER_TEMP/raced-ots-anchor"
            rm -rf "$root"
            mkdir -p "$root"
            gh release download "$ANCHOR_TAG" --repo "$GITHUB_REPOSITORY" --dir "$root"
            test -s "$root/SHA256SUMS"
            (cd "$root" && sha256sum -c SHA256SUMS)
            echo "[OTS ANCHOR RACE REVERIFIED] $ANCHOR_TAG"
            exit 0
          fi
'''
    text = replace_once(text, old_race, new_race, 'anchor race handling')
    path.write_text(text, encoding='utf-8')


def patch_closure() -> None:
    path = Path('.github/workflows/chronicle-sidechain-ots-bitcoin-closure.yml')
    text = path.read_text(encoding='utf-8')

    marker = "      - name: Ensure exact OTS submission exists\n        env:\n"
    insert = '''      - name: Reverify terminal Bitcoin confirmation if already published
        id: terminal_confirmation
        run: |
          set -euo pipefail
          set -a
          . ots-closure/source.env
          set +a
          git fetch origin "refs/tags/${SOURCE_TAG}:refs/tags/${SOURCE_TAG}"
          SOURCE_SHA="$(git rev-list -n 1 "$SOURCE_TAG")"
          CONFIRMATION_TAG="chronicle-sidechain-ots-bitcoin-v2-${SOURCE_SHORT}"
          export SOURCE_SHA CONFIRMATION_TAG
          if ! gh release view "$CONFIRMATION_TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
            echo "closed=false" >> "$GITHUB_OUTPUT"
            echo "[OTS CONFIRMATION ABSENT] closure work remains"
            exit 0
          fi
          root="$RUNNER_TEMP/existing-ots-confirmation"
          rm -rf "$root"
          mkdir -p "$root"
          gh release download "$CONFIRMATION_TAG" --repo "$GITHUB_REPOSITORY" --dir "$root"
          if [ -s "$root/RELEASE-ASSETS-SHA256.txt" ]; then
            (cd "$root" && sha256sum -c RELEASE-ASSETS-SHA256.txt)
          fi
          if [ -s "$root/CLOSURE-SHA256SUMS" ]; then
            (cd "$root" && sha256sum -c CLOSURE-SHA256SUMS)
          fi
          EXISTING_ROOT="$root" python3 - <<'PYVERIFY'
          import json, os, pathlib
          root = pathlib.Path(os.environ['EXISTING_ROOT'])
          candidates = [root / 'OTS-STRICT-BITCOIN-VERIFICATION.json', root / 'OTS-CLOSURE.json']
          reports = [p for p in candidates if p.is_file() and p.stat().st_size > 0]
          if not reports:
              raise SystemExit('published confirmation has no recognized Bitcoin verification report')
          report = json.loads(reports[0].read_text())
          checks = {
              'bitcoin_verified': report.get('bitcoin_verified') is True,
              'source_sha': report.get('source_commit_sha') == os.environ['SOURCE_SHA'],
              'confirmation_tag': report.get('confirmation_release_tag') == os.environ['CONFIRMATION_TAG'],
          }
          if not all(checks.values()):
              raise SystemExit(f'published Bitcoin confirmation failed terminal checks: {checks}')
          print(f'[TERMINAL OTS CONFIRMATION REVERIFIED] report={reports[0].name} checks={checks}')
          PYVERIFY
          run_url="https://github.com/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
          target="${run_url}#trinity-ots?state=already_verified&run=${GITHUB_RUN_ID}"
          gh api --method POST -H "Accept: application/vnd.github+json" "repos/$GITHUB_REPOSITORY/statuses/$GITHUB_SHA" -f state=success -f context="$STATUS_CONTEXT" -f description="existing OTS Bitcoin confirmation reverified" -f target_url="$target" >/dev/null
          echo "closed=true" >> "$GITHUB_OUTPUT"

''' + marker
    text = replace_once(text, marker, insert, 'closure terminal insertion')

    for name in ('Ensure exact OTS submission exists', 'Upgrade and strictly verify Bitcoin attestation'):
        old = f"      - name: {name}\n"
        new = old + "        if: steps.terminal_confirmation.outputs.closed != 'true'\n"
        text = replace_once(text, old, new, f'closure condition {name}')

    path.write_text(text, encoding='utf-8')


def validate() -> None:
    import yaml

    for path in (
        Path('.github/workflows/chronicle-sidechain-ots-anchor.yml'),
        Path('.github/workflows/chronicle-sidechain-ots-bitcoin-closure.yml'),
    ):
        yaml.safe_load(path.read_text(encoding='utf-8'))
        print(f'YAML_OK {path}')


if __name__ == '__main__':
    patch_anchor()
    patch_closure()
    validate()
