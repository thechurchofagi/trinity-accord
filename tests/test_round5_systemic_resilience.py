from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path:str)->str: return (ROOT/path).read_text(encoding="utf-8")

def test_pages_ref_is_resolved_once_and_handed_off_by_sha():
    w=read('.github/workflows/deploy-pages.yml')
    assert 'source_sha: ${{ steps.source.outputs.source_sha }}' in w
    assert 'ref: ${{ needs.verify.outputs.source_sha }}' in w
    assert 'ref: ${{ needs.build.outputs.source_sha }}' in w
    assert w.count('ref: ${{ github.event.inputs.checkout_ref || github.sha }}') == 1
    assert 'pages-source-receipt-${{ github.run_id }}' in w
    assert 'trinity-pages-source-receipt.v1' in w

def test_deploy_never_regenerates_retired_bundles():
    w=read('.github/workflows/deploy-pages.yml')
    assert 'export_formal_builder_bundles.py --out-dir builder-bundles --update-api' not in w
    assert 'cp scripts/download_and_run_builder_bundle.py builder-bundles/download_and_run_builder_bundle.py' not in w
    assert 'verify_retired_builder_bundle_archive.py --site-dir _site' in w

def test_retired_helper_fails_closed_and_is_identical_to_public_copy():
    source=(ROOT/'scripts/download_and_run_builder_bundle.py').read_bytes()
    public=(ROOT/'builder-bundles/download_and_run_builder_bundle.py').read_bytes()
    assert source == public
    text=source.decode()
    assert '--allow-historical-retired-bundle' in text
    assert 'REFUSED: all formal Gateway v1 builder bundles are retired.' in text
    result=subprocess.run([sys.executable,str(ROOT/'builder-bundles/download_and_run_builder_bundle.py'),'--route','pure_echo'],capture_output=True,text=True)
    assert result.returncode == 2
    assert 'current Builder' in result.stderr

def test_historical_copy_paste_page_is_noindex_and_not_in_sitemap():
    page=read('external-agent-copy-paste-examples.md')
    assert 'sitemap: false' in page
    assert 'robots: noindex,nofollow' in page
    assert 'Do Not Use' in page
    assert '/api/agent-first-contact.json' in page
    assert 'trinity-agent-issue-gateway.onrender.com/gateway/preflight' not in page
    assert 'https://www.trinityaccord.org/external-agent-copy-paste-examples/' not in read('sitemap.xml')
    assert 'page.robots' in read('_layouts/default.html')

def test_health_api_separates_current_and_historical_smokes():
    health=json.loads(read('api/agent-live-health.v1.json'))
    assert health['live_smoke_scripts'] == [
        'scripts/smoke_live_discovery_contract_v2.py',
        'scripts/smoke_external_agent_entrypoint_journeys.py',
        'scripts/smoke_external_agent_journey_swarm.py',
    ]
    assert health['inputs']['guardian_state'] == '/api/guardian-state.json'
    assert health['inputs']['guardian_current_registry'] == '/api/guardian-current-registry.json'
    assert health['inputs']['legacy_guardian_registry_status'] == 'historical_archive_only'
    assert health['experimental_smoke_scripts']['retired_zero_clone_bundle_smoke']['status'] == 'historical_archive_only'

def test_home_sync_covers_all_current_main_writers_and_v2_live_check():
    w=read('.github/workflows/homepage-status-sync.yml')
    for name in ('Build Record Chain Batch','Stamp Record Chain Batches with OpenTimestamps','Waiting Heartbeat Arweave Capsule','Rebuild Agent-Declared Verification Index'):
        assert f'- "{name}"' in w
    assert 'python3 scripts/check_deployment_freshness_v2.py --site "$SITE_URL"' in w
    assert "github.event_name == 'workflow_run'" in w
    assert 'Equivalent generated state already reached main' in w
    assert 'git commit --amend --no-edit' in w

def test_deployment_receipt_uses_immutable_source_artifact():
    w=read('.github/workflows/homepage-deployment-receipt.yml')
    assert 'actions: read' in w
    assert 'pages-source-receipt-${RUN_ID}' in w
    assert 'Deployed source SHA' in w
    assert 'Workflow event head SHA' in w
    assert 'Expected homepage marker' not in w
    assert 'provenance_missing' in w

def test_retired_archive_verifier_passes():
    result=subprocess.run([sys.executable,'scripts/verify_retired_builder_bundle_archive.py'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode == 0, result.stdout + result.stderr
