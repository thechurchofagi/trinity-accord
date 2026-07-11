#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    detector = load('detect_archive_backlog', ROOT / 'scripts/detect_archive_backlog.py')
    require(
        detector.status_after_previous({'archive_status': 'waiting_for_upgrade'}, 'upgrade_due') == 'upgrade_due',
        'historical pending OTS anchor was not promoted to upgrade_due',
    )
    require(
        detector.status_after_previous({'archive_status': 'waiting_for_upgrade'}, 'waiting_for_upgrade') == 'waiting_for_upgrade',
        'current latest pending OTS anchor must remain waiting_for_upgrade',
    )

    volatile = load('restore_volatile', ROOT / 'scripts/restore_json_if_only_volatile_changes.py')
    left = {'status': 'ok', 'updated_at': 'old', 'nested': {'checked_at': 'old'}}
    right = {'status': 'ok', 'updated_at': 'new', 'nested': {'checked_at': 'new'}}
    require(
        volatile.strip_volatile(left, {'updated_at', 'checked_at'}) == volatile.strip_volatile(right, {'updated_at', 'checked_at'}),
        'volatile timestamp normalization failed',
    )
    right['status'] = 'changed'
    require(
        volatile.strip_volatile(left, {'updated_at', 'checked_at'}) != volatile.strip_volatile(right, {'updated_at', 'checked_at'}),
        'semantic changes must not be hidden by volatile normalization',
    )

    status = json.loads((ROOT / 'api/record-chain-status.json').read_text(encoding='utf-8'))
    tip = json.loads((ROOT / 'record-chain/chain-tip.json').read_text(encoding='utf-8'))
    rc = status.get('record_chain', {})
    require(rc.get('integrity_verified_through_record_id') == tip.get('latest_record_id'), 'integrity record id drift')
    require(rc.get('integrity_verified_through_record_sha256') == tip.get('latest_record_sha256'), 'integrity record sha drift')

    home = (ROOT / '.github/workflows/homepage-status-sync.yml').read_text(encoding='utf-8')
    require("if: ${{ steps.commit.outputs.changed == 'true' ||" in home, 'generated changes do not explicitly dispatch Pages')
    print('PASS: system audit round 3 contracts')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
