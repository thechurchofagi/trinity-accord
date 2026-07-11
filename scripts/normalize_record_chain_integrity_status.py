#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / 'api/record-chain-status.json'
TIP = ROOT / 'record-chain/chain-tip.json'


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n'


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def expected_status(current: dict[str, Any]) -> dict[str, Any]:
    status = json.loads(json.dumps(current))
    tip = read_json(TIP)
    record_id = tip.get('latest_record_id')
    record_path = ROOT / 'record-chain/records' / f'{record_id}.json'
    record = read_json(record_path)
    record_time = record.get('assigned_at') or record.get('created_at') or tip.get('updated_at')

    rc = status.setdefault('record_chain', {})
    rc['last_integrity_check_at'] = record_time
    rc['last_integrity_check_at_semantics'] = (
        'deterministic lower bound from the latest verified record timestamp; '
        'the publication workflow runs a full chain verification immediately before generation'
    )
    rc['integrity_verified_through_record_id'] = tip.get('latest_record_id')
    rc['integrity_verified_through_record_index'] = tip.get('latest_record_index')
    rc['integrity_verified_through_record_sha256'] = tip.get('latest_record_sha256')
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    current = read_json(STATUS)
    expected = expected_status(current)
    expected_text = dump_json(expected)
    current_text = STATUS.read_text(encoding='utf-8')
    if args.check:
        if current_text != expected_text:
            print('record-chain integrity status drift detected')
            return 1
        print('record-chain integrity status is current')
        return 0
    if current_text != expected_text:
        STATUS.write_text(expected_text, encoding='utf-8')
        print('updated deterministic record-chain integrity status')
    else:
        print('record-chain integrity status unchanged')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
