#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    idempotency = ROOT / "apps/record_chain_intake_gateway/tests/test_idempotency_index.py"
    replace_once(
        idempotency,
        "from gateway.github_atomic import AtomicCreateConflict\n",
        "",
        "duplicate atomic exception import",
    )
    replace_once(
        idempotency,
        'AsyncMock(side_effect=AtomicCreateConflict("concurrent winner"))',
        'AsyncMock(side_effect=app_module.AtomicCreateConflict("concurrent winner"))',
        "atomic conflict class identity",
    )

    retired = ROOT / "apps/record_chain_intake_gateway/tests/test_retired_endpoints.py"
    replace_once(
        retired,
        '        mock_github["put_file"].assert_not_called()\n',
        '        mock_github["create_files_atomic"].assert_not_awaited()\n',
        "retired endpoint persistence assertion",
    )

    for path in (idempotency, retired):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    print("ATOMIC_GATEWAY_REMAINING_TESTS_MIGRATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
