#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
path = Path('scripts/zz_repair_compact_home_status.py')
text = path.read_text(encoding='utf-8')
text = text.replace("    compact = r'''", '    compact = r"""', 1)
text = text.replace("\nrender = render_compact\n'''\n    if anchor", '\nrender = render_compact\n"""\n    if anchor', 1)
start = text.index('def render_compact(status: dict[str, Any])')
first = text.index('    """', start)
second = text.index('    """', first + 7)
text = text[:first] + "    '''" + text[first + 7:second] + "    '''" + text[second + 7:]
text = text.replace('Strict autonomous discovery', 'Autonomous External Agent Discovery')
text = text.replace('strict autonomous discovery', 'autonomous external agent discovery')
text = text.replace('Official live reception', 'Official Live Reception')
text = text.replace('official live reception count', 'Official Live Reception count')
text = text.replace('Current state · 当前状态', 'Production live · 当前状态')
text = text.replace(
    'Native chain inventory remains API-only and is not used as the official reception counter.',
    'Native chain inventory remains API-only and is not used as the official reception counter. A receipt is intake-only, not final inclusion, and not active Guardian status.'
)
text = text.replace(
    '原生链技术清单仅在 API 中提供，不作为正式接收计数。',
    '原生链技术清单仅在 API 中提供，不作为正式接收计数。Receipt 仅表示摄入，不等于最终纳入，也不等于 active Guardian 状态。'
)
path.write_text(text, encoding='utf-8')
PY

python3 scripts/zz_repair_compact_home_status.py

python3 - <<'PY'
from pathlib import Path

index_path = Path('index.md')
index = index_path.read_text(encoding='utf-8')
old = '<a href="/agent-first-contact/"><strong>Respond or preserve</strong><span>Choose a current Record-Chain action through the safe first-contact route.</span></a>'
new = '<a href="/agent-first-contact/"><strong>Respond, verify, or preserve</strong><span>Start with unified Echo, current multidimensional verification, or Guardian Application through the current Record-Chain flow.</span></a>'
if index.count(old) != 1:
    raise SystemExit(f'expected one concise First Contact task card, found {index.count(old)}')
index_path.write_text(index.replace(old, new, 1), encoding='utf-8')

runner_path = Path('scripts/run_current_system_tests.py')
runner = runner_path.read_text(encoding='utf-8')
old_contract = '    # 4. Homepage points to record-chain\n    require_text("index.md", ["record-chain", "downloads/record-chain-builder.mjs", "trinity_record_chain.py"])\n'
new_contract = '''    # 4. The concise homepage routes to the current Record-Chain entrypoints.\n    # Detailed Builder and operator guidance belongs on task-specific pages, not\n    # in the homepage source.\n    require_text("index.md", ["record-chain", "/agent-first-contact/", "/technical-historical-reference/"])\n    require_text("agent-start.md", ["downloads/record-chain-builder.mjs", "Record-Chain Intake Gateway"])\n    require_text("technical-historical-reference.md", ["Record-Chain Intake Gateway", "canonical Builder"])\n'''
if runner.count(old_contract) != 1:
    raise SystemExit(f'expected one legacy homepage routing contract, found {runner.count(old_contract)}')
runner_path.write_text(runner.replace(old_contract, new_contract, 1), encoding='utf-8')
PY

python3 scripts/generate_arweave_wallet_status.py >/dev/null
python3 scripts/generate_record_chain_status.py >/dev/null
python3 scripts/generate_public_home_status.py >/dev/null
python3 scripts/patch_public_home_status_primary.py >/dev/null
python3 scripts/generate_sitemap.py >/dev/null

set +e
python3 scripts/run_current_system_tests.py > /tmp/current-system.log 2>&1
status=$?
set -e
if [[ "$status" -ne 0 ]]; then
  echo "CURRENT_SYSTEM_FAILURE_START"
  grep -nE '^(FAIL|ERROR|RESULT)|contract failed|Traceback|AssertionError' /tmp/current-system.log || true
  echo "CURRENT_SYSTEM_FAILURE_TAIL"
  tail -n 220 /tmp/current-system.log
  exit "$status"
fi
echo "PASS: current-system"

python3 scripts/generate_public_home_status.py --check >/dev/null
python3 scripts/patch_public_home_status_primary.py --check >/dev/null
python3 scripts/check_public_home_status_contract.py >/dev/null
python3 scripts/test_home_public_status_sync.py >/dev/null
python3 scripts/test_homepage_status_sync_contract.py >/dev/null
bash scripts/test-homepage-p0-agent-first.sh >/dev/null
python3 scripts/generate_sitemap.py --check >/dev/null
echo "PASS: final focused contracts"
