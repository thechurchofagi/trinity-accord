#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.request


def now_iso():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def load_progress(path):
    if not path or not path.exists() or not path.stat().st_size:
        return {}
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else {'progress_payload': data}
    except Exception as exc:
        return {'progress_read_error': str(exc)}


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
            'user-agent': 'trinity-accord-sidechain-progress/1.0',
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
