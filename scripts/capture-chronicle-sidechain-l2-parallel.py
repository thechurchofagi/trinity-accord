#!/usr/bin/env python3
import importlib.util
import json
import os
import pathlib
import threading
import time
import urllib.error
import urllib.request

MODULE_PATH = pathlib.Path(__file__).with_name('capture-chronicle-sidechain-l2.py')
SPEC = importlib.util.spec_from_file_location('capture_chronicle_sidechain_l2_base', MODULE_PATH)
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)

PROGRESS_FILE = pathlib.Path(os.getenv('CHRONICLE_L2_PROGRESS_FILE', '/tmp/chronicle-sidechain-l2-progress.json'))
PER_ENDPOINT_INFLIGHT = max(1, min(4, int(os.getenv('CHRONICLE_L2_RPC_ENDPOINT_INFLIGHT', '1'))))
PROGRESS_EVENT_LIMIT = max(20, min(500, int(os.getenv('CHRONICLE_L2_PROGRESS_EVENT_LIMIT', '120'))))
STATE_LOCK = threading.Lock()
ROUTE_CURSOR = {chain: 0 for chain in capture.RPC}
ENDPOINT_SLOTS = {
    chain: [threading.BoundedSemaphore(PER_ENDPOINT_INFLIGHT) for _ in endpoints]
    for chain, endpoints in capture.RPC.items()
}
ENDPOINT_THROTTLE_LOCKS = {
    chain: [threading.Lock() for _ in endpoints]
    for chain, endpoints in capture.RPC.items()
}
ENDPOINT_LAST_CALL = {chain: [0.0] * len(endpoints) for chain, endpoints in capture.RPC.items()}
RPC_RETRIES = {chain: 0 for chain in capture.RPC}
RPC_FAILURES = {chain: [0] * len(endpoints) for chain, endpoints in capture.RPC.items()}

PROGRESS = {
    'schema': 'trinity-accord/chronicle-sidechain-live-progress/v1',
    'run_id': os.getenv('GITHUB_RUN_ID'),
    'run_attempt': os.getenv('GITHUB_RUN_ATTEMPT'),
    'source_sha': os.getenv('GITHUB_SHA'),
    'phase': 'l2_initializing',
    'status': 'running',
    'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'last_event_at': None,
    'last_event': None,
    'unique_blocks_total': 0,
    'blocks_completed': 0,
    'blocks_failed': 0,
    'records_pass': 0,
    'records_expected': 0,
    'concurrency': capture.CONCURRENCY,
    'rpc_endpoint_inflight_limit': PER_ENDPOINT_INFLIGHT,
    'rpc_min_interval_ms': int(capture.RPC_MIN_INTERVAL * 1000),
    'chains': {chain: {'blocks_completed': 0, 'blocks_failed': 0} for chain in capture.RPC},
    'events': [],
}


def atomic_json_write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def snapshot_locked():
    snap = dict(PROGRESS)
    snap['chains'] = {k: dict(v) for k, v in PROGRESS['chains'].items()}
    snap['events'] = list(PROGRESS['events'])
    snap['rpc_routes'] = {
        chain: {
            'endpoint_count': len(capture.RPC[chain]),
            'successful_requests_by_endpoint': list(capture.RPC_SUCCESSES[chain]),
            'failed_requests_by_endpoint': list(RPC_FAILURES[chain]),
            'retry_rounds': RPC_RETRIES[chain],
        }
        for chain in sorted(capture.RPC)
    }
    return snap


def progress_event(kind, **fields):
    now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with STATE_LOCK:
        event = {'at': now, 'kind': kind, **fields}
        PROGRESS['last_event_at'] = now
        PROGRESS['last_event'] = event
        PROGRESS['events'].append(event)
        if len(PROGRESS['events']) > PROGRESS_EVENT_LIMIT:
            del PROGRESS['events'][:-PROGRESS_EVENT_LIMIT]
        atomic_json_write(PROGRESS_FILE, snapshot_locked())


def raw_rpc_request(chain, endpoint_index, method, params):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    req = urllib.request.Request(
        capture.RPC[chain][endpoint_index],
        data=payload,
        headers={'content-type': 'application/json', 'user-agent': 'trinity-accord-sidechain-l2/2.3-parallel'},
    )
    try:
        with urllib.request.urlopen(req, timeout=capture.TIMEOUT) as res:
            data = json.loads(res.read())
    except urllib.error.HTTPError as e:
        retry_after = 0
        try:
            retry_after = float(e.headers.get('retry-after') or 0)
        except (TypeError, ValueError):
            pass
        raise capture.RpcFailure(f'HTTP Error {e.code}: {e.reason}', retry_after) from e
    except Exception as e:
        raise capture.RpcFailure(str(e)) from e
    if not isinstance(data, dict):
        raise capture.RpcFailure('non-object JSON-RPC response')
    if data.get('error'):
        raise capture.RpcFailure(f"{method}: {data['error']}")
    return data.get('result')


def rpc_once_parallel(chain, endpoint_index, method, params):
    slot = ENDPOINT_SLOTS[chain][endpoint_index]
    throttle_lock = ENDPOINT_THROTTLE_LOCKS[chain][endpoint_index]
    with slot:
        with throttle_lock:
            elapsed = time.monotonic() - ENDPOINT_LAST_CALL[chain][endpoint_index]
            if elapsed < capture.RPC_MIN_INTERVAL:
                time.sleep(capture.RPC_MIN_INTERVAL - elapsed)
            ENDPOINT_LAST_CALL[chain][endpoint_index] = time.monotonic()
        return raw_rpc_request(chain, endpoint_index, method, params)


def next_endpoint_order(chain):
    with STATE_LOCK:
        n = len(capture.RPC[chain])
        start = ROUTE_CURSOR[chain] % n
        ROUTE_CURSOR[chain] = (ROUTE_CURSOR[chain] + 1) % n
    return list(range(start, len(capture.RPC[chain]))) + list(range(0, start))


def rpc_parallel(chain, method, params, retries=None):
    rounds = (capture.RETRIES if retries is None else max(0, retries)) + 1
    last = None
    for attempt in range(rounds):
        order = next_endpoint_order(chain)
        errors = []
        retry_after = 0
        for endpoint_index in order:
            try:
                result = rpc_once_parallel(chain, endpoint_index, method, params)
                with capture.RPC_STATE_LOCK:
                    previous = capture.RPC_PREFERRED[chain]
                    capture.RPC_PREFERRED[chain] = endpoint_index
                    capture.RPC_SUCCESSES[chain][endpoint_index] += 1
                if endpoint_index != previous:
                    print(
                        f'[L2 RPC ROUTE] {chain} endpoint={endpoint_index+1}/{len(capture.RPC[chain])} method={method}',
                        flush=True,
                    )
                return result
            except capture.RpcFailure as e:
                last = e
                retry_after = max(retry_after, e.retry_after)
                with STATE_LOCK:
                    RPC_FAILURES[chain][endpoint_index] += 1
                errors.append(f'endpoint={endpoint_index+1}/{len(capture.RPC[chain])} {e}')
        with STATE_LOCK:
            RPC_RETRIES[chain] += 1
        progress_event('rpc_retry', chain=chain, method=method, attempt=attempt + 1, rounds=rounds)
        print(f'[L2 RETRY] {chain} {method} attempt={attempt+1}/{rounds} error={"; ".join(errors)}', flush=True)
        if attempt < rounds - 1:
            time.sleep(max(retry_after, min(.5 * (2 ** attempt), 30)))
    raise RuntimeError(str(last))


def configure_progress_totals():
    index = json.loads((capture.EVID / 'SIDECHAIN-NFT-IDENTITY-INDEX.json').read_text())
    records = index['records']
    groups = {(r['chain']['name'], r['origin']['block_hash']) for r in records}
    with STATE_LOCK:
        PROGRESS['records_expected'] = len(records)
        PROGRESS['unique_blocks_total'] = len(groups)
        PROGRESS['phase'] = 'l2_capture'
    progress_event('l2_start', records=len(records), unique_blocks=len(groups), concurrency=capture.CONCURRENCY)


def install_capture_group_progress():
    original = capture.capture_group

    def wrapped(item):
        chain, block_hash = item[0]
        progress_event('block_start', chain=chain, block_hash=block_hash)
        try:
            rows = original(item)
        except Exception as e:
            with STATE_LOCK:
                PROGRESS['blocks_completed'] += 1
                PROGRESS['blocks_failed'] += 1
                PROGRESS['chains'][chain]['blocks_completed'] += 1
                PROGRESS['chains'][chain]['blocks_failed'] += 1
            progress_event('block_failed', chain=chain, block_hash=block_hash, error_type=type(e).__name__)
            raise
        with STATE_LOCK:
            PROGRESS['blocks_completed'] += 1
            PROGRESS['records_pass'] += len(rows)
            PROGRESS['chains'][chain]['blocks_completed'] += 1
        progress_event('block_complete', chain=chain, block_hash=block_hash, records=len(rows))
        return rows

    capture.capture_group = wrapped


def main():
    capture.rpc = rpc_parallel
    configure_progress_totals()
    install_capture_group_progress()
    try:
        capture.main()
    except BaseException as e:
        with STATE_LOCK:
            PROGRESS['status'] = 'failed'
            PROGRESS['phase'] = 'l2_failed'
        progress_event('l2_failed', error_type=type(e).__name__)
        raise
    else:
        with STATE_LOCK:
            PROGRESS['status'] = 'success'
            PROGRESS['phase'] = 'l2_complete'
        progress_event('l2_complete')


if __name__ == '__main__':
    main()
