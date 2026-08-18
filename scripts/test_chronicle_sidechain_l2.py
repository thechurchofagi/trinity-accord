#!/usr/bin/env python3
import importlib.util
import pathlib

import rlp


MODULE_PATH = pathlib.Path(__file__).with_name('capture-chronicle-sidechain-l2.py')
SPEC = importlib.util.spec_from_file_location('capture_chronicle_sidechain_l2', MODULE_PATH)
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)


def main():
    assert capture.endpoint_list('https://one.example/', 'https://one.example,https://two.example/') == [
        'https://one.example', 'https://two.example'
    ]

    capture.RPC['base'] = ['https://limited.example', 'https://healthy.example']
    capture.RPC_PREFERRED['base'] = 0
    capture.RPC_SUCCESSES['base'] = [0, 0]
    calls=[]
    def fake_rpc_once(chain, endpoint_index, method, params):
        calls.append((chain, endpoint_index, method, params))
        if endpoint_index == 0: raise capture.RpcFailure('HTTP Error 429: Too Many Requests')
        return {'number': '0x1'}
    capture.rpc_once = fake_rpc_once
    assert capture.rpc('base', 'eth_getBlockByHash', ['0xabc', True], retries=0) == {'number': '0x1'}
    assert [call[1] for call in calls] == [0, 1]
    assert capture.RPC_PREFERRED['base'] == 1
    assert capture.RPC_SUCCESSES['base'] == [0, 1]

    tx = {
        'type': '0x4',
        'chainId': '0x89',
        'nonce': '0x1',
        'maxPriorityFeePerGas': '0x3b9aca00',
        'maxFeePerGas': '0x77359400',
        'gas': '0x5208',
        'to': '0x' + '11' * 20,
        'value': '0x0',
        'input': '0x1234',
        'accessList': [{'address': '0x' + '22' * 20, 'storageKeys': ['0x' + '33' * 32]}],
        'authorizationList': [{
            'chainId': '0x89',
            'address': '0x' + '44' * 20,
            'nonce': '0x2',
            'yParity': '0x1',
            'r': '0x5',
            's': '0x6',
        }],
        'yParity': '0x0',
        'r': '0x7',
        's': '0x8',
    }
    expected_fields = [
        capture.intb(tx['chainId']), capture.intb(tx['nonce']), capture.intb(tx['maxPriorityFeePerGas']),
        capture.intb(tx['maxFeePerGas']), capture.intb(tx['gas']), capture.h2b(tx['to']),
        capture.intb(tx['value']), capture.h2b(tx['input']), capture.access_list(tx['accessList']),
        [[capture.intb('0x89'), capture.h2b('0x' + '44' * 20), capture.intb('0x2'),
          capture.intb('0x1'), capture.intb('0x5'), capture.intb('0x6')]],
        capture.intb('0x0'), capture.intb('0x7'), capture.intb('0x8'),
    ]
    encoded = capture.encode_tx(tx)
    assert encoded == b'\x04' + rlp.encode(expected_fields)

    snake_case = dict(tx)
    snake_case.pop('authorizationList')
    snake_case['authorization_list'] = [{
        'chain_id': '0x89', 'address': '0x' + '44' * 20, 'nonce': '0x2',
        'y_parity': '0x1', 'r': '0x5', 's': '0x6',
    }]
    assert capture.encode_tx(snake_case) == encoded

    receipt = {
        'type': '0x4', 'status': '0x1', 'cumulativeGasUsed': '0x5208',
        'logsBloom': '0x' + '00' * 256, 'logs': [],
    }
    assert capture.encode_receipt(receipt).startswith(b'\x04')
    print('[L2 CAPTURE TEST PASS] EIP-7702 type-4 encoding + RPC endpoint failover')


if __name__ == '__main__':
    main()
