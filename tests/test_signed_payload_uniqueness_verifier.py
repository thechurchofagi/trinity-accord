from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.trinity_record_chain as trc


def _write_record(
    directory: Path,
    record_id: str,
    *,
    signed_payload_sha256: str,
    record_sha256: str,
) -> Path:
    path = directory / f"{record_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "record_id": record_id,
        "record_type": "echo",
        "record_sha256": record_sha256,
        "authorship_proof": {"signed_payload_sha256": signed_payload_sha256},
    }), encoding="utf-8")
    return path


def test_exact_historical_echo_duplicate_is_explicit_warning_not_blanket_bypass():
    records = [
        ROOT / "record-chain/records/R-000000030.json",
        ROOT / "record-chain/records/R-000000031.json",
    ]
    errors, warnings = trc.signed_payload_uniqueness_findings(records)
    assert errors == []
    assert len(warnings) == 1
    assert "R-000000030, R-000000031" in warnings[0]
    assert "pre-A-066" in warnings[0]


def test_any_new_signed_payload_duplicate_is_hard_error(tmp_path):
    duplicate_hash = "a" * 64
    records = [
        _write_record(
            tmp_path,
            "R-000000200",
            signed_payload_sha256=duplicate_hash,
            record_sha256="b" * 64,
        ),
        _write_record(
            tmp_path,
            "R-000000201",
            signed_payload_sha256=duplicate_hash,
            record_sha256="c" * 64,
        ),
    ]
    errors, warnings = trc.signed_payload_uniqueness_findings(records)
    assert warnings == []
    assert len(errors) == 1
    assert "outside exact historical exception" in errors[0]


def test_historical_hash_exception_is_bound_to_exact_record_hashes(tmp_path):
    historical_hash = next(iter(trc.KNOWN_HISTORICAL_SIGNED_PAYLOAD_DUPLICATES))[1]
    records = [
        _write_record(
            tmp_path,
            "R-000000030",
            signed_payload_sha256=historical_hash,
            record_sha256="0" * 64,
        ),
        _write_record(
            tmp_path,
            "R-000000031",
            signed_payload_sha256=historical_hash,
            record_sha256="1" * 64,
        ),
    ]
    errors, warnings = trc.signed_payload_uniqueness_findings(records)
    assert warnings == []
    assert len(errors) == 1
