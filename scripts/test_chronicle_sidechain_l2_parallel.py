#!/usr/bin/env python3
import concurrent.futures
import importlib.util
import json
import pathlib
import tempfile
import threading

MODULE_PATH = pathlib.Path(__file__).with_name('capture-chronicle-sidechain-l2-parallel.py')
SPEC = importlib.util.spec_from_file_location('capture_chronicle_sidechain_l2_parallel', MODULE_PATH)
parallel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parallel)


def main():
    assert len(parallel.capture.RPC['base']) >= 2

    barrier = threading.Barrier(2, timeout=2)
    original_raw = parallel.raw_rpc_request

    def fake_raw(chain, endpoint_index, method, params):
        barrier.wait()
        return {'endpoint': endpoint_index}

    parallel.raw_rpc_request = fake_raw
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            a = ex.submit(parallel.rpc_once_parallel, 'base', 0, 'eth_test', [])
            b = ex.submit(parallel.rpc_once_parallel, 'base', 1, 'eth_test', [])
            assert {a.result(timeout=3)['endpoint'], b.result(timeout=3)['endpoint']} == {0, 1}
    finally:
        parallel.raw_rpc_request = original_raw

    parallel.ROUTE_CURSOR['base'] = 0
    first = parallel.next_endpoint_order('base')
    second = parallel.next_endpoint_order('base')
    assert first[0] != second[0]

    original_once = parallel.rpc_once_parallel
    calls = []

    def fake_once(chain, endpoint_index, method, params):
        calls.append(endpoint_index)
        if endpoint_index == 0:
            raise parallel.capture.RpcFailure('HTTP Error 429: Too Many Requests')
        return {'ok': True}

    parallel.rpc_once_parallel = fake_once
    parallel.ROUTE_CURSOR['base'] = 0
    try:
        assert parallel.rpc_parallel('base', 'eth_test', [], retries=0) == {'ok': True}
        assert calls[:2] == [0, 1]
    finally:
        parallel.rpc_once_parallel = original_once

    with tempfile.TemporaryDirectory() as td:
        parallel.PROGRESS_FILE = pathlib.Path(td) / 'progress.json'
        parallel.progress_event('unit_test', value=1)
        saved = json.loads(parallel.PROGRESS_FILE.read_text())
        assert saved['schema'] == 'trinity-accord/chronicle-sidechain-live-progress/v1'
        assert saved['last_event']['kind'] == 'unit_test'
        assert saved['last_event']['value'] == 1

    print('[L2 PARALLEL TEST PASS] endpoint parallelism + failover + durable progress')


if __name__ == '__main__':
    main()
