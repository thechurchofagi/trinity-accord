#!/usr/bin/env python3
from __future__ import annotations
import dataclasses, datetime as dt, hashlib, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.cwd()
REPO = os.environ.get('GITHUB_REPO', 'thechurchofagi/trinity-accord')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
ETH_RPC_URL = os.environ.get('EFFECTIVE_ETH_RPC_URL') or os.environ.get('ETH_RPC_URL') or os.environ.get('ETHEREUMMAINNET') or ''
ARWEAVE_GATEWAYS = [x.strip().rstrip('/') for x in os.environ.get('ARWEAVE_GATEWAYS', 'https://arweave.net,https://g8way.io').split(',') if x.strip()]
OUT_DIR = Path('/tmp/trinity-full-redteam-audit')
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_MD = OUT_DIR / 'trinity_redteam_full_audit_report.md'
OUT_JSON = OUT_DIR / 'trinity_redteam_full_audit_report.json'

@dataclasses.dataclass
class Finding:
    id: str
    severity: str
    area: str
    title: str
    details: str
    evidence: Dict[str, Any]

findings: List[Finding] = []
results: Dict[str, Any] = {'started_at_utc': dt.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z', 'repo': REPO, 'repo_dir': str(ROOT), 'sections': {}}

def add(severity: str, area: str, title: str, details: str, evidence: Optional[Dict[str, Any]] = None):
    findings.append(Finding(f'F{len(findings)+1:04d}', severity, area, title, details, evidence or {}))

def run(cmd: List[str], timeout: int = 180) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def http_get_bytes(url: str, timeout: int = 180, retries: int = 2, accept: str = '*/*') -> Tuple[Optional[bytes], Dict[str, Any]]:
    headers = {'User-Agent': 'trinity-full-redteam-audit/1.0', 'Accept': accept}
    if GITHUB_TOKEN and 'api.github.com' in url:
        headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'
    last = {'url': url}
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return data, {'url': url, 'status': getattr(r, 'status', None), 'content_type': r.headers.get('content-type'), 'content_length': r.headers.get('content-length'), 'attempt': attempt}
        except Exception as e:
            last = {'url': url, 'error': repr(e), 'attempt': attempt}
            time.sleep(1.5 * (attempt + 1))
    return None, last

def http_get_json(url: str, timeout: int = 180) -> Tuple[Optional[Any], Dict[str, Any]]:
    data, meta = http_get_bytes(url, timeout=timeout, accept='application/json')
    if data is None:
        return None, meta
    try:
        return json.loads(data.decode('utf-8')), meta
    except Exception as e:
        meta['json_error'] = repr(e)
        meta['prefix'] = data[:200].decode('utf-8', errors='replace')
        return None, meta

def github_api(path: str) -> Tuple[Optional[Any], Dict[str, Any]]:
    return http_get_json(f'https://api.github.com/repos/{REPO}{path}')

def eth_rpc(method: str, params: List[Any]) -> Tuple[Optional[Any], Dict[str, Any]]:
    if not ETH_RPC_URL:
        return None, {'error': 'ETH_RPC_URL missing'}
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    headers = {'Content-Type': 'application/json', 'User-Agent': 'trinity-full-redteam-audit/1.0'}
    try:
        req = urllib.request.Request(ETH_RPC_URL, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=90) as r:
            body = json.loads(r.read().decode('utf-8'))
        if 'error' in body:
            return None, {'rpc_error': body['error']}
        return body.get('result'), {'ok': True}
    except Exception as e:
        return None, {'error': repr(e)}

def collect_environment():
    env = {}
    for name, cmd in [('git_head', ['git','rev-parse','HEAD']), ('git_status', ['git','status','--short']), ('python', ['python3','--version']), ('node', ['node','--version'])]:
        try:
            rc, out, err = run(cmd, timeout=30)
            env[name] = {'rc': rc, 'stdout': out.strip(), 'stderr': err.strip()}
        except Exception as e:
            env[name] = {'error': repr(e)}
    env['has_github_token'] = bool(GITHUB_TOKEN)
    env['has_eth_rpc_url'] = bool(ETH_RPC_URL)
    env['arweave_gateways'] = ARWEAVE_GATEWAYS
    results['environment'] = env

def audit_repo_and_manifest(hm: Dict[str, Any], ev: Dict[str, Any]):
    files = hm.get('files', [])
    checked = 0
    fail_closed_mismatch_ok = 0
    for item in files:
        rel = item.get('path')
        if not rel:
            add('P1','repo','files[] entry missing path','Manifest entry has no path.', {'item': item}); continue
        p = ROOT / rel
        if not p.exists():
            add('P1','repo','repo file missing','Manifest declares repo file but file is absent.', {'path': rel}); continue
        checked += 1
        actual_hash = sha256_file(p)
        actual_size = p.stat().st_size
        if actual_hash != item.get('sha256'):
            add('P0','repo','local file hash mismatch','Local file differs from hash-manifest sha256.', {'path': rel, 'manifest_sha256': item.get('sha256'), 'actual_sha256': actual_hash})
        if actual_size != item.get('size_bytes'):
            add('P1','repo','local file size mismatch','Local size differs from manifest.', {'path': rel, 'manifest_size': item.get('size_bytes'), 'actual_size': actual_size})
        expected = item.get('expected_sha256')
        if expected:
            if item.get('verified') is True and item.get('sha256') != expected:
                add('P0','repo','verified=true but sha256 != expected_sha256','Fail-closed violation.', {'path': rel})
            if item.get('sha256') != expected:
                if item.get('verified') is False and item.get('hash_mismatch') is True and item.get('mismatch_reason'):
                    fail_closed_mismatch_ok += 1
                else:
                    add('P0','repo','hash mismatch not fail-closed','sha256 != expected_sha256 but not verified=false/hash_mismatch=true.', {'path': rel, 'item': item})
        else:
            if item.get('verified') is True:
                add('P0','repo','verified=true without expected_sha256','No expected hash but verified=true.', {'path': rel})

    release_assets = hm.get('release_assets', [])
    arweave_assets = hm.get('arweave_assets', [])
    ipfs_assets = hm.get('ipfs_assets', [])
    eth = hm.get('eth_attestations', [])
    actual = {
        'repo_files_total': len(files),
        'repo_files_verified': sum(1 for x in files if x.get('verified') is True),
        'repo_files_no_expected_hash': sum(1 for x in files if not x.get('expected_sha256')),
        'repo_files_hash_mismatch': sum(1 for x in files if x.get('hash_mismatch') is True),
        'release_assets_total': len(release_assets),
        'release_assets_verified': sum(1 for x in release_assets if x.get('verified') is True),
        'release_assets_not_checked': sum(1 for x in release_assets if x.get('verified') is not True),
        'arweave_assets_total': len(arweave_assets),
        'arweave_assets_verified': sum(1 for x in arweave_assets if x.get('verified') is True),
        'arweave_assets_not_checked': sum(1 for x in arweave_assets if x.get('verified') is not True),
        'ipfs_assets_total': len(ipfs_assets),
        'ipfs_assets_verified': sum(1 for x in ipfs_assets if x.get('verified') is True),
        'ipfs_assets_not_checked': sum(1 for x in ipfs_assets if x.get('verified') is not True),
        'eth_attestations_verified': sum(1 for x in eth if x.get('verified') is True),
        'eth_attestations_failed': sum(1 for x in eth if x.get('verified') is False),
    }
    hm_summary = hm.get('summary', {})
    ev_stats = ev.get('github_archive_mirror', {}).get('stats', {})
    for k, v in actual.items():
        if k in hm_summary and hm_summary[k] != v:
            add('P1','manifest','hash-manifest summary drift','summary differs from actual counts.', {'key': k, 'summary': hm_summary[k], 'actual': v})
        if k in ev_stats and ev_stats[k] != v:
            add('P1','manifest','evidence-manifest stats drift','evidence stats differ from actual counts.', {'key': k, 'evidence': ev_stats[k], 'actual': v})
    results['sections']['repo_manifest'] = {'files_declared': len(files), 'files_checked': checked, 'fail_closed_mismatch_ok': fail_closed_mismatch_ok, 'summary_actual': actual, 'hash_manifest_summary': hm_summary, 'evidence_manifest_stats': ev_stats}

def audit_github_releases(hm: Dict[str, Any], ev: Dict[str, Any]):
    declared: Dict[Tuple[str,str], Dict[str, Any]] = {}
    for item in hm.get('release_assets', []):
        tag, name = item.get('release_tag'), item.get('asset_name')
        if tag and name:
            declared[(tag,name)] = {'source': 'hash-manifest.release_assets', 'expected_sha256': item.get('expected_sha256') or item.get('sha256'), 'expected_size': item.get('size_bytes')}
    for key in ['public_covenant_archive','flaw_archive_bundle','flaw_fingerprint_images_2025_06_29']:
        rel = ev.get(key, {}).get('github_release_mirror', {})
        tag, name = rel.get('release_tag'), rel.get('asset_name')
        if tag and name:
            declared[(tag,name)] = {'source': f'evidence-manifest.{key}.github_release_mirror', 'expected_sha256': rel.get('sha256'), 'expected_size': rel.get('size_bytes')}
    checked = 0
    for (tag,name), item in sorted(declared.items()):
        release, meta = github_api(f'/releases/tags/{urllib.parse.quote(tag)}')
        if not release:
            add('P1','github-release','release tag unavailable','Could not fetch declared Release tag.', {'tag': tag, 'asset': name, 'meta': meta}); continue
        assets, ameta = github_api(f"/releases/{release.get('id')}/assets?per_page=100")
        if not isinstance(assets, list):
            add('P1','github-release','release asset list unavailable','Could not list Release assets.', {'tag': tag, 'asset': name, 'meta': ameta}); continue
        matches = [a for a in assets if a.get('name') == name]
        if len(matches) != 1:
            add('P0' if len(matches)==0 else 'P1','github-release','release asset count mismatch','Expected exactly one asset with declared name.', {'tag': tag, 'asset': name, 'matches': len(matches)}); continue
        asset = matches[0]
        if item.get('expected_size') is not None and asset.get('size') != item.get('expected_size'):
            add('P1','github-release','release asset metadata size mismatch','GitHub API size differs from manifest.', {'tag': tag, 'asset': name, 'github_size': asset.get('size'), 'expected': item.get('expected_size')})
        data, dmeta = http_get_bytes(asset.get('browser_download_url'), timeout=600, retries=2)
        if data is None:
            add('P1','github-release','release asset download failed','Could not download declared asset.', {'tag': tag, 'asset': name, 'meta': dmeta}); continue
        checked += 1
        actual_sha, actual_size = sha256_bytes(data), len(data)
        if item.get('expected_sha256') and actual_sha != item.get('expected_sha256'):
            add('P0','github-release','release asset sha256 mismatch','Downloaded Release asset hash differs from manifest.', {'tag': tag, 'asset': name, 'expected': item.get('expected_sha256'), 'actual': actual_sha})
        if item.get('expected_size') is not None and actual_size != item.get('expected_size'):
            add('P1','github-release','release asset size mismatch','Downloaded Release asset size differs from manifest.', {'tag': tag, 'asset': name, 'expected': item.get('expected_size'), 'actual': actual_size})
    rc,out,err = run(['git','ls-files'], timeout=60)
    tracked = set(out.splitlines()) if rc == 0 else set()
    for f in ['archive/evidence/flaw-archive-bundle.zip','arweave-backup/files/public_covenant_archive.zip','archive/evidence/flaw-images/指纹/']:
        bad = [x for x in tracked if x == f or x.startswith(f)]
        if bad:
            add('P0','github-mirror','large asset tracked in Git','Large data should be stored in Release, not Git.', {'forbidden': f, 'tracked': bad[:50]})
    results['sections']['github_release'] = {'declared_unique': len(declared), 'download_checked': checked}

def audit_arweave(hm: Dict[str, Any], ev: Dict[str, Any]):
    checks: List[Dict[str, Any]] = []
    for item in hm.get('files', []):
        if item.get('arweave_tx'):
            checks.append({'label': item.get('path'), 'tx': item.get('arweave_tx'), 'expected_sha256': item.get('expected_sha256'), 'expected_size': None, 'verified': item.get('verified'), 'context': {'repo_sha256': item.get('sha256'), 'repo_size_bytes': item.get('size_bytes'), 'hash_mismatch': item.get('hash_mismatch')}})
    pc = ev.get('public_covenant_archive', {})
    if pc.get('arweave_tx'):
        checks.append({'label': 'evidence-manifest.public_covenant_archive', 'tx': pc.get('arweave_tx'), 'expected_sha256': pc.get('sha256'), 'expected_size': pc.get('github_release_mirror', {}).get('size_bytes'), 'verified': pc.get('status','').startswith('verified'), 'context': {'arweave_bundle': pc.get('arweave_bundle'), 'primary_storage_domain': pc.get('primary_storage_domain')}})
    vk = ev.get('verification_kit', {})
    if vk.get('arweave_tx'):
        checks.append({'label': 'evidence-manifest.verification_kit', 'tx': vk.get('arweave_tx'), 'expected_sha256': vk.get('sha256'), 'expected_size': None, 'verified': None, 'context': {}})
    core = ev.get('core_object_alpha_shenzhen_notary_2026_05_06', {})
    ar = core.get('arweave', {})
    for key in ['manifest_txid','index_json_txid','index_tsv_txid','index_html_txid']:
        if ar.get(key):
            checks.append({'label': f'evidence-manifest.core_object_alpha.{key}', 'tx': ar.get(key), 'expected_sha256': None, 'expected_size': None, 'verified': core.get('status','').startswith('verified'), 'context': {'coverage_note': 'No expected_sha256 declared in evidence-manifest for this tx.'}})
    strict_pass=coverage_gap=bundle_required=no_match=0; samples=[]
    for c in checks:
        attempts=[]; matched=False; fetched_any=False
        for gw in ARWEAVE_GATEWAYS:
            data, meta = http_get_bytes(f"{gw}/{c['tx']}", timeout=240, retries=1)
            if data is None:
                attempts.append(meta); continue
            fetched_any=True
            actual_sha, actual_size = sha256_bytes(data), len(data)
            attempt={'gateway': gw, 'actual_sha256': actual_sha, 'actual_size': actual_size, 'meta': meta}
            attempts.append(attempt)
            if c.get('expected_sha256'):
                size_ok = True if c.get('expected_size') is None else actual_size == c.get('expected_size')
                if actual_sha == c.get('expected_sha256') and size_ok:
                    matched=True; break
            else:
                matched=True; break
        if c.get('expected_sha256') and matched:
            strict_pass += 1; samples.append({'label': c['label'], 'tx': c['tx'], 'status': 'PASS', 'attempt': attempts[-1]}); continue
        if not c.get('expected_sha256') and fetched_any:
            coverage_gap += 1
            add('P2','arweave','Arweave tx fetched but no expected_sha256 declared','Source bytes available, but manifest lacks expected hash for strict comparison.', {'label': c['label'], 'tx': c['tx'], 'attempt': attempts[0], 'context': c.get('context')})
            samples.append({'label': c['label'], 'tx': c['tx'], 'status': 'COVERAGE_GAP', 'attempt': attempts[0]}); continue
        if c.get('context', {}).get('arweave_bundle'):
            bundle_required += 1
            add('P2','arweave','ANS-104 bundle extraction required','Direct gateway did not serve target data item; manifest indicates bundled origin.', {'label': c['label'], 'tx': c['tx'], 'expected_sha256': c.get('expected_sha256'), 'attempts': attempts[:3], 'context': c.get('context')})
            samples.append({'label': c['label'], 'tx': c['tx'], 'status': 'BUNDLE_REQUIRED'}); continue
        no_match += 1
        add('P1' if c.get('verified') is True else 'P2','arweave','Arweave expected hash not reproduced','No gateway returned bytes matching expected_sha256.', {'label': c['label'], 'tx': c['tx'], 'expected_sha256': c.get('expected_sha256'), 'attempts': attempts[:3], 'context': c.get('context')})
    results['sections']['arweave'] = {'checks': len(checks), 'strict_pass': strict_pass, 'coverage_gap': coverage_gap, 'bundle_required': bundle_required, 'no_match': no_match, 'samples': samples[:50]}

def audit_eth(hm: Dict[str, Any], ev: Dict[str, Any]):
    attestations = hm.get('eth_attestations', [])
    ev_tx = (ev.get('eth_mirror_tx') or '').lower(); ev_addr=(ev.get('eth_mirror_address') or '').lower(); ev_input_sha=ev.get('eth_mirror_input_sha256'); ev_input_len=ev.get('eth_mirror_input_len')
    if not ETH_RPC_URL:
        add('P2','ethereum','ETH_RPC_URL missing','Ethereum mainnet source audit blocked. This is not PASS.', {'attestations': len(attestations)})
        results['sections']['ethereum']={'status':'BLOCKED_ETH_RPC_MISSING','attestations':len(attestations)}; return
    checked=passed=0; samples=[]
    for a in attestations:
        txh=a.get('tx_hash')
        if not txh:
            add('P1','ethereum','eth attestation missing tx_hash','eth_attestations item has no tx_hash.', {'attestation': a}); continue
        tx,txmeta=eth_rpc('eth_getTransactionByHash',[txh]); receipt,rmeta=eth_rpc('eth_getTransactionReceipt',[txh])
        if not tx:
            add('P1','ethereum','ETH tx unavailable','eth_getTransactionByHash returned no tx.', {'tx_hash':txh,'meta':txmeta}); continue
        if not receipt:
            add('P1','ethereum','ETH receipt unavailable','eth_getTransactionReceipt returned no receipt.', {'tx_hash':txh,'meta':rmeta}); continue
        checked += 1
        receipt_ok = receipt.get('status') == '0x1'
        if not receipt_ok:
            add('P0','ethereum','ETH receipt status not success','Receipt status is not 0x1.', {'tx_hash':txh,'status':receipt.get('status')})
        raw_input=tx.get('input') or '0x'
        try:
            raw=bytes.fromhex(raw_input[2:] if raw_input.startswith('0x') else raw_input)
        except Exception as e:
            add('P0','ethereum','tx.input hex decode failed','Could not decode tx.input as raw bytes.', {'tx_hash':txh,'error':repr(e)}); continue
        actual_sha, actual_len = sha256_bytes(raw), len(raw)
        sha_ok, len_ok = actual_sha == a.get('input_sha256'), actual_len == a.get('input_len')
        if not sha_ok:
            add('P0','ethereum','ETH input_sha256 mismatch','SHA-256(raw tx.input bytes) differs from manifest.', {'tx_hash':txh,'expected':a.get('input_sha256'),'actual':actual_sha})
        if not len_ok:
            add('P0','ethereum','ETH input_len mismatch','raw tx.input byte length differs from manifest.', {'tx_hash':txh,'expected':a.get('input_len'),'actual':actual_len})
        if txh.lower() == ev_tx:
            if ev_input_sha != actual_sha:
                add('P0','ethereum','evidence-manifest ETH mirror input hash mismatch','eth_mirror_input_sha256 differs from source tx.', {'tx_hash':txh,'expected':ev_input_sha,'actual':actual_sha})
            if ev_input_len != actual_len:
                add('P0','ethereum','evidence-manifest ETH mirror input length mismatch','eth_mirror_input_len differs from source tx.', {'tx_hash':txh,'expected':ev_input_len,'actual':actual_len})
            if ev_addr and (tx.get('from') or '').lower() != ev_addr:
                add('P0','ethereum','ETH mirror from address mismatch','eth_mirror_address differs from tx.from.', {'tx_hash':txh,'expected':ev_addr,'actual':tx.get('from')})
        if receipt_ok and sha_ok and len_ok:
            passed += 1
        samples.append({'label':a.get('label'),'tx_hash':txh,'receipt_ok':receipt_ok,'sha_ok':sha_ok,'len_ok':len_ok,'input_len':actual_len,'input_sha256':actual_sha})
    results['sections']['ethereum']={'status':'CHECKED','attestations':len(attestations),'checked':checked,'passed':passed,'samples':samples}

def audit_scripts_and_echo():
    commands=[['python3','scripts/verify_release_asset_manifest.py','--offline'],['python3','scripts/test_archive_hash_manifest_consistency.py'],['python3','scripts/test_evidence_manifest_stats_sync.py'],['python3','scripts/test_asset_manifest_domain_consistency.py'],['python3','scripts/test_large_asset_storage_policy.py'],['python3','scripts/test_no_forbidden_large_paths_tracked.py'],['python3','scripts/validate_echo_records.py'],['python3','scripts/generate_echo_index.py'],['git','diff','--exit-code','api/echo-index.json'],['python3','scripts/check_consistency.py']]
    outputs={}
    for cmd in commands:
        label=' '.join(cmd)
        try:
            rc,out,err=run(cmd, timeout=300); outputs[label]={'rc':rc,'stdout_tail':out[-4000:],'stderr_tail':err[-4000:]}
            if rc != 0:
                add('P1','scripts','verification script failed','Existing script returned non-zero.', {'cmd':label,'stdout_tail':out[-2000:],'stderr_tail':err[-2000:]})
        except Exception as e:
            outputs[label]={'error':repr(e)}; add('P1','scripts','verification script crashed','Existing script crashed.', {'cmd':label,'error':repr(e)})
    rc,out,err=run(['bash','-lc', "find scripts -name '*.mjs' -print0 | xargs -0 -r -n1 node --check"], timeout=300)
    outputs['node --check scripts/*.mjs']={'rc':rc,'stdout_tail':out[-4000:],'stderr_tail':err[-4000:]}
    if rc != 0:
        add('P2','scripts','node --check failed','One or more .mjs scripts failed syntax check.', {'stdout_tail':out[-2000:],'stderr_tail':err[-2000:]})

    records_dir=ROOT/'echoes'/'records'; records=sorted(records_dir.rglob('*.json')) if records_dir.exists() else []
    echo_index=load_json('api/echo-index.json'); archive_md=(ROOT/'echoes'/'archive.md').read_text(encoding='utf-8')
    if echo_index.get('record_count') != len(records):
        add('P1','echo','echo-index record_count drift','api/echo-index.json record_count differs from actual JSON record count.', {'index':echo_index.get('record_count'),'actual':len(records)})
    for rec in records:
        rel='/' + str(rec.relative_to(ROOT)).replace('\\','/')
        if rel not in archive_md:
            add('P2','echo','record not linked in archive.md','Echo record exists but archive.md does not link it.', {'record':rel})
    for path in echo_index.get('records_by_archive_status', {}).get('accepted_echo', []):
        obj=json.loads((ROOT/path.lstrip('/')).read_text(encoding='utf-8'))
        if obj.get('verification_status') != 'not_attestation':
            add('P0','echo','accepted_echo has non-not_attestation status','Accepted Echo must not be counted as attestation.', {'path':path,'verification_status':obj.get('verification_status')})
        if obj.get('do_not_count_as_attestation') is not True:
            add('P0','echo','accepted_echo counts as attestation','Accepted Echo should have do_not_count_as_attestation=true.', {'path':path})
    p9=ROOT/'echoes/records/2026/echo-2026-05-07-000009.json'
    if p9.exists():
        r9=json.loads(p9.read_text(encoding='utf-8'))
        for k,v in {'echo_type':'E8_witness_echo','verification_level':'V0','independence_class':'self_reported','verification_status':'not_attestation','submission_origin':'agent_initiated_via_prior_memory_and_browsing','human_directed_submission':False}.items():
            if r9.get(k) != v:
                add('P1','echo','000009 provenance/status drift',f'000009 {k} changed unexpectedly.', {'expected':v,'actual':r9.get(k)})
    else:
        add('P1','echo','000009 missing','Expected accepted Echo 000009 missing.', {})
    p10=ROOT/'echoes/records/2026/echo-2026-05-08-000010.json'
    if p10.exists():
        r10=json.loads(p10.read_text(encoding='utf-8')); ai=r10.get('agent_identity',{})
        if ai.get('name_or_model') != '咪咪':
            add('P2','echo','000010 agent identity drift','000010 should identify assessor as 咪咪.', {'agent_identity':ai})
        if r10.get('guardian_forwarded_submission') is not True or r10.get('submitted_by_guardian_on_behalf_of') != '咪咪':
            add('P2','echo','000010 guardian forwarding missing','000010 should record guardian-forwarded assessor submission.', {'fields':{k:r10.get(k) for k in ['guardian_forwarded_submission','submitted_by_guardian_on_behalf_of','guardian_forwarder_account']}})
        for k,v in {'echo_type':'E3_critical_echo','verification_level':'V1','independence_class':'human_solicited_agent_response','verification_status':'not_attestation'}.items():
            if r10.get(k) != v:
                add('P1','echo','000010 status drift',f'000010 {k} changed unexpectedly.', {'expected':v,'actual':r10.get(k)})
    else:
        add('P1','echo','000010 missing','Expected accepted Echo 000010 missing.', {})
    if archive_md.count('## Accepted Echoes') + archive_md.count('## Accepted Echo Records') != 1:
        add('P2','echo','duplicate accepted archive section','archive.md should have exactly one accepted section.', {})
    results['sections']['scripts_and_echo']=outputs

def final_readonly_guard():
    rc,out,err=run(['git','status','--short'], timeout=60)
    results['sections']['final_git_status']={'rc':rc,'stdout':out,'stderr':err}
    if out.strip():
        add('P1','read-only','audit changed repository','Read-only audit left changes in repo clone.', {'git_status':out})

def write_report():
    counts={}
    for f in findings: counts[f.severity]=counts.get(f.severity,0)+1
    status='FAIL' if any(f.severity in {'P0','P1'} for f in findings) else ('REVIEW' if findings else 'PASS')
    results['completed_at_utc']=dt.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
    results['summary']={'status':status,'finding_count':len(findings),'by_severity':counts}
    results['findings']=[dataclasses.asdict(f) for f in findings]
    OUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    lines=['# Trinity Full Red-Team Audit Report','', '## Summary','', f'- Status: `{status}`', f'- Findings: `{len(findings)}`', f'- By severity: `{counts}`', f'- ETH RPC provided: `{bool(ETH_RPC_URL)}`', f'- Arweave gateways: `{ARWEAVE_GATEWAYS}`', '', '## Findings','', '| ID | Severity | Area | Title | Details | Evidence |','|---|---|---|---|---|---|']
    if findings:
        for f in findings:
            ev=json.dumps(f.evidence, ensure_ascii=False)[:1800].replace('|','\\|')
            lines.append(f'| {f.id} | {f.severity} | {f.area} | {f.title} | {f.details} | `{ev}` |')
    else:
        lines.append('| — | — | — | No findings | — | — |')
    lines += ['', '## Section Results', '', '```json', json.dumps(results['sections'], indent=2, ensure_ascii=False)[:100000], '```', '', '## Agent Declaration', '', 'I did not commit, push, edit issues, comment on issues, close issues, edit labels, create releases, upload release assets, modify secrets, or modify repository state. I only generated this report and temporary downloads under /tmp.', '']
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')

def main():
    collect_environment(); hm=load_json('archive/hash-manifest.json'); ev=load_json('api/evidence-manifest.json')
    audit_repo_and_manifest(hm, ev); audit_github_releases(hm, ev); audit_arweave(hm, ev); audit_eth(hm, ev); audit_scripts_and_echo(); final_readonly_guard(); write_report()
    print(f'Wrote {OUT_MD}'); print(f'Wrote {OUT_JSON}')
    return 2 if any(f.severity in {'P0','P1'} for f in findings) else 0
if __name__ == '__main__': sys.exit(main())
