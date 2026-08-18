#!/usr/bin/env python3
import importlib.util
import pathlib

MODULE_PATH = pathlib.Path(__file__).with_name('publish-chronicle-sidechain-progress.py')
SPEC = importlib.util.spec_from_file_location('publish_chronicle_sidechain_progress', MODULE_PATH)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

report = {
    'schema': 'trinity-accord/chronicle-sidechain-offline-verification/v2',
    'pass': False,
    'records': 217,
    'car_files_checked': 212,
    'l2_records_checked': 215,
    'errors': [
        'L2 eip155:8453/erc721:0xabc/1: receipt mpt',
        'L2 eip155:8453/erc721:0xabc/2: receipt mpt',
        'CAR bafytest: linked block missing',
        'L1 merkle mismatch deadbeef',
    ],
}
summary = mod.summarize_offline(report, limit=2)
assert summary['error_count'] == 4
assert summary['error_classes'] == {'CAR': 1, 'L1': 1, 'L2:receipt mpt': 2}
assert len(summary['errors_sample']) == 2
assert summary['errors_omitted'] == 2
assert summary['records'] == 217
assert summary['pass'] is False
print('[PROGRESS PUBLISHER TEST PASS] offline diagnostics are bounded and classified')
