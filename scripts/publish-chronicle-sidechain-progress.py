#!/usr/bin/env python3
import argparse
import collections
import json
import os
import pathlib
import time
import urllib.error
import urllib.request


def now_iso():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def load_json(path):
    if not path or not path.exists() or not path.stat().st_size:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def load_progress(path):
    data = load_json(path)
    if isinstance(data, dict):
        return data
    if data is not None:
        return {'progress_payload': data}
    return {}


def load_jsonl_tail(path, limit=25):
    if not path or not path.exists() or not path.stat().st_size:
        return []
    rows = []
    try:
        for line in path.read_text(errors='replace').splitlines()[-limit:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                rows.append({'unparsed': line[:1000]})
    except Exception:
        return []
    return rows


def classify_error(value):
    text = str(value)
    if text.startswith('L1 '): return 'L1'
    if text.startswith('CAR '): return 'CAR'
    if text.startswith('L2 '):
        tail = text.rsplit(': ', 1)[-1]
        return f'L2:{tail}'
    return 'other'


def summarize_offline(report, limit=40):
    if not isinstance(report, dict):
        return None
    errors = [str(x) for x in report.get('errors', [])]
    counts = collections.Counter(classify_error(x) for x in errors)
    return {
        'schema': report.get('schema'),
        'pass': report.get('pass'),
        'records': report.get('records'),
        'car_files_checked': report.get('car_files_checked'),
        'l2_records_checked': report.get('l2_records_checked'),
        'error_count': len(errors),
        'error_classes': dict(sorted(counts.items())),
        'errors_sample': errors[:limit],
        'errors_omitted': max(0, len(errors) - limit),
    }


def summarize_l1(report, limit=40):
    if not isinstance(report, dict):
        return None
    mismatches = report.get('leaf_mismatches') if isinstance(report.get('leaf_mismatches'), list) else []
    return {
        'schema': report.get('schema'),
        'records': report.get('records'),
        'commitment_leaf_count': report.get('commitment_leaf_count'),
        'leaf_mismatch_count': report.get('leaf_mismatch_count'),
        'leaf_mismatches': mismatches[:limit],
        'leaf_mismatches_omitted': report.get('leaf_mismatches_omitted', max(0, len(mismatches) - limit)),
        'order_matches': report.get('order_matches'),
        'first_order_difference': report.get('first_order_difference'),
    }


def summarize_car(report):
    if not isinstance(report, dict):
        return None
    keys = [
        'schema', 'phase', 'status', 'run_id', 'run_attempt', 'source_sha',
        'evidence_concurrency', 'car_block_concurrency', 'whole_dag_endpoint_limit',
        'cache_audit', 'records_completed', 'records_expected', 'workers',
        'failed_cids', 'car_failed_events', 'recovery_event_counts',
        'last_cid', 'last_event', 'last_event_detail', 'last_event_at',
        'last_recovery_event', 'recent_recovery_events', 'recent_recovery_failures',
        'whole_dag_verified', 'blockwise_completed', 'historical_chunk_verified',
        'kubo_blocks_verified', 'lassie_starts', 'lassie_root_reuse',
        'raw_blocks_verified', 'cache_rejected_events', 'started_at',
        'finished_at', 'published_at',
    ]
    return {key: report.get(key) for key in keys if key in report}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', default=None)
    ap.add_argument('--status', default=None)
    ap.add_argument('--progress-file', default=os.getenv('CHRONICLE_L2_PROGRESS_FILE', ''))
    args = ap.parse_args()

    repo = os.getenv('GITHUB_REPOSITORY')
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    issue = os.getenv('CHRONICLE_PROGRESS_ISSUE', '1020')
    if not repo or not token:
        raise SystemExit('GITHUB_REPOSITORY and GH_TOKEN/GITHUB_TOKEN are required')

    progress_path = pathlib.Path(args.progress_file) if args.progress_file else None
    progress = load_progress(progress_path)
    if not progress:
        progress = {
            'schema': 'trinity-accord/chronicle-sidechain-live-progress/v1',
            'run_id': os.getenv('GITHUB_RUN_ID'),
            'run_attempt': os.getenv('GITHUB_RUN_ATTEMPT'),
            'source_sha': os.getenv('GITHUB_SHA'),
        }
    progress['published_at'] = now_iso()
    progress['run_id'] = progress.get('run_id') or os.getenv('GITHUB_RUN_ID')
    progress['run_attempt'] = progress.get('run_attempt') or os.getenv('GITHUB_RUN_ATTEMPT')
    progress['source_sha'] = progress.get('source_sha') or os.getenv('GITHUB_SHA')
    if args.phase:
        progress['workflow_phase'] = args.phase
    if args.status:
        progress['workflow_status'] = args.status
    elif progress.get('status'):
        progress['workflow_status'] = progress['status']

    out = pathlib.Path(os.getenv('CHRONICLE_OUT', 'artifacts/chronicle-sidechain-scan'))
    car = summarize_car(load_json(out / 'runtime' / 'CAR-PROGRESS.json'))
    if car is not None:
        progress['car_l1_progress'] = car
    trace_tail = load_jsonl_tail(out / 'runtime' / 'CAR-TRACE.jsonl', 25)
    if trace_tail:
        progress['car_trace_tail'] = trace_tail
    offline = summarize_offline(load_json(out / 'evidence-v2' / 'OFFLINE-VERIFICATION.json'))
    if offline is not None:
        progress['offline_verification'] = offline
    l1 = summarize_l1(load_json(out / 'evidence-v2' / 'L1-LEAF-DIAGNOSTICS.json'))
    if l1 is not None:
        progress['l1_leaf_diagnostics'] = l1

    run_id = progress.get('run_id')
    run_url = f'https://github.com/{repo}/actions/runs/{run_id}' if run_id else None
    lines = [
        '# Sidechain evidence live progress',
        '',
        '> Operational telemetry only. This does not amend Canon or evidence contents.',
        '',
        f'- Repository: `{repo}`',
        f'- Run: `{run_id or "unknown"}`' + (f' — {run_url}' if run_url else ''),
        f'- Source SHA: `{progress.get("source_sha") or "unknown"}`',
        f'- Phase: `{progress.get("workflow_phase") or progress.get("phase") or "unknown"}`',
        f'- Status: `{progress.get("workflow_status") or progress.get("status") or "unknown"}`',
        f'- Published heartbeat: `{progress["published_at"]}`',
        '',
        '```json',
        json.dumps(progress, indent=2, sort_keys=True),
        '```',
    ]
    body = '\n'.join(lines)
    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/issues/{issue}',
        data=json.dumps({'body': body}).encode(),
        method='PATCH',
        headers={
            'authorization': f'Bearer {token}',
            'accept': 'application/vnd.github+json',
            'content-type': 'application/json',
            'user-agent': 'trinity-accord-sidechain-progress/1.3',
            'x-github-api-version': '2022-11-28',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            if res.status < 200 or res.status >= 300:
                raise RuntimeError(f'GitHub issue update HTTP {res.status}')
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:1000]
        raise SystemExit(f'progress issue update failed: HTTP {exc.code}: {detail}') from exc
    print(f'[PROGRESS PUBLISHED] issue=#{issue} phase={progress.get("workflow_phase")} status={progress.get("workflow_status")}', flush=True)


if __name__ == '__main__':
    main()
