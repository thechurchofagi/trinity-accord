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

reference_path = Path('technical-historical-reference.md')
reference = reference_path.read_text(encoding='utf-8')
reference_anchor = 'Only the first layer is canonical authority. All other layers preserve, test, contextualize, carry, or respond to the object without rewriting it.\n'
reference_addition = reference_anchor + '\nArweave is a mirror/archive layer only. It improves durability and availability; it is not authority, attestation, amendment, or successor reception.\n\nArweave 仅为镜像/归档层，用于增强持久性与可获得性；它不构成权威、认证、修订或继任接收。\n'
if reference.count(reference_anchor) != 1:
    raise SystemExit('expected one technical-reference layer boundary')
reference_path.write_text(reference.replace(reference_anchor, reference_addition, 1), encoding='utf-8')

runner_path = Path('scripts/run_current_system_tests.py')
runner = runner_path.read_text(encoding='utf-8')
old_contract = '    # 4. Homepage points to record-chain\n    require_text("index.md", ["record-chain", "downloads/record-chain-builder.mjs", "trinity_record_chain.py"])\n'
new_contract = '''    # 4. The concise homepage routes to the current Record-Chain entrypoints.\n    # Detailed Builder and operator guidance belongs on task-specific pages, not\n    # in the homepage source.\n    require_text("index.md", ["record-chain", "/agent-first-contact/", "/technical-historical-reference/"])\n    require_text("agent-start.md", ["downloads/record-chain-builder.mjs", "Record-Chain Intake Gateway"])\n    require_text("technical-historical-reference.md", ["Record-Chain Intake Gateway", "canonical Builder"])\n'''
if runner.count(old_contract) != 1:
    raise SystemExit(f'expected one legacy homepage routing contract, found {runner.count(old_contract)}')
runner_path.write_text(runner.replace(old_contract, new_contract, 1), encoding='utf-8')

wording_path = Path('scripts/test_public_wording_phase6_contract.py')
wording = wording_path.read_text(encoding='utf-8')
old_home_required = '''HOMEPAGE_MUST_CONTAIN = [
    "Autonomous External Agent Discovery",
    "External agent self-discovered Trinity Accord",
    "human authorization alone is allowed",
    "外部智能体自主发现",
    "Official Live Reception",
    "Technical chain health",
    "AR upload wallet",
    "Historical records before R-000000033 remain available for audit",
]'''
new_home_required = '''HOMEPAGE_MUST_CONTAIN = [
    "Autonomous External Agent Discovery",
    "Official Live Reception",
    "Reception does not imply autonomous discovery",
    "Native chain inventory remains API-only",
    "Production live",
    "not final inclusion",
]'''
if wording.count(old_home_required) != 1:
    raise SystemExit('expected one legacy homepage required-wording block')
wording = wording.replace(old_home_required, new_home_required, 1)
wording = wording.replace(
    '''HOMEPAGE_MUST_CONTAIN_ONE_OF = [
    "Native chain length is not used as this counter",
    "Reception does not imply belief",
]''',
    '''HOMEPAGE_MUST_CONTAIN_ONE_OF = [
    "Native chain inventory remains API-only",
    "Reception does not imply autonomous discovery",
]''',
    1,
)
old_oath = '''    # index.md must not contain retired agent_readback_sha256
    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        if "agent_readback_sha256" in index_text:
            errors.append("index.md: must not contain retired field 'agent_readback_sha256'")
        for field in ["participant_readback_sha256", "canonical_oath_text_sha256", "oath_policy_sha256"]:
            if field not in index_text:
                errors.append(f"index.md: missing current oath field '{field}'")
'''
new_oath = '''    # The homepage remains discovery-only. Oath hash fields belong in the
    # canonical Builder/runtime contract, not in homepage prose.
    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        if "agent_readback_sha256" in index_text:
            errors.append("index.md: must not contain retired field 'agent_readback_sha256'")
    builder_path = ROOT / "downloads" / "record-chain-builder.mjs"
    if not builder_path.exists():
        errors.append("downloads/record-chain-builder.mjs: canonical Builder missing")
    else:
        builder_text = builder_path.read_text(encoding="utf-8")
        for field in ["participant_readback_sha256", "canonical_oath_text_sha256", "oath_policy_sha256"]:
            if field not in builder_text:
                errors.append(f"canonical Builder: missing current oath field '{field}'")
'''
if wording.count(old_oath) != 1:
    raise SystemExit('expected one legacy homepage oath-field block')
wording = wording.replace(old_oath, new_oath, 1)
old_phase6c = '''    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")

        # Homepage must say Arweave is mirror/archive layer only
        if "mirror/archive layer only" not in index_text and "mirror/archive layer" not in index_text:
            if "仅为镜像/归档层" not in index_text:
                errors.append("index.md: homepage must state Arweave is mirror/archive layer only")

        # Homepage must NOT say "Live Arweave upload is disabled" (old wording)
        if "Live Arweave upload is disabled" in index_text:
            errors.append("index.md: homepage must not say 'Live Arweave upload is disabled' (outdated wording)")

        # Public submission section must appear before internal pipeline section
        intake_pos = index_text.find('id="render-intake-gateway"')
        pipeline_pos = index_text.find('id="primary-durable-record-path"')
        if intake_pos >= 0 and pipeline_pos >= 0:
            if intake_pos > pipeline_pos:
                errors.append("index.md: public submission section must appear before internal pipeline section")
        else:
            if intake_pos < 0:
                errors.append("index.md: missing render-intake-gateway section")
            if pipeline_pos < 0:
                errors.append("index.md: missing primary-durable-record-path section")

        # Homepage must still point to /agent-first-contact/
        if "/agent-first-contact/" not in index_text:
            errors.append("index.md: homepage must reference /agent-first-contact/")

        # Homepage must NOT display legacy Guardian active status as current
        # (old patterns like "Guardian Registry: N" should not appear)
        if re.search(r"Guardian Registry:\s*\d+", index_text):
            errors.append("index.md: homepage must not display legacy Guardian Registry count")
'''
new_phase6c = '''    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        if "Live Arweave upload is disabled" in index_text:
            errors.append("index.md: homepage must not say 'Live Arweave upload is disabled' (outdated wording)")
        if "/agent-first-contact/" not in index_text:
            errors.append("index.md: homepage must reference /agent-first-contact/")
        if re.search(r"Guardian Registry:\s*\d+", index_text):
            errors.append("index.md: homepage must not display legacy Guardian Registry count")

    reference_path = ROOT / "technical-historical-reference.md"
    if not reference_path.exists():
        errors.append("technical-historical-reference.md: dedicated reference missing")
    else:
        reference_text = reference_path.read_text(encoding="utf-8")
        if "mirror/archive layer only" not in reference_text and "仅为镜像/归档层" not in reference_text:
            errors.append("technical-historical-reference.md: must state Arweave is mirror/archive layer only")
        for needle in ["Record-Chain Intake Gateway", "canonical Builder", "Current operating routes"]:
            if needle not in reference_text:
                errors.append(f"technical-historical-reference.md: missing current route wording '{needle}'")

    first_contact_path = ROOT / "agent-first-contact.md"
    if first_contact_path.exists():
        first_contact_text = first_contact_path.read_text(encoding="utf-8")
        for needle in ["Record-Chain Intake Gateway", "/downloads/record-chain-builder.mjs"]:
            if needle not in first_contact_text:
                errors.append(f"agent-first-contact.md: missing current submission wording '{needle}'")
'''
if wording.count(old_phase6c) != 1:
    raise SystemExit('expected one legacy Phase 6C homepage block')
wording_path.write_text(wording.replace(old_phase6c, new_phase6c, 1), encoding='utf-8')
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
