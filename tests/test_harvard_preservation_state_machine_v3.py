from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import harvard_preservation_state_machine as impl  # noqa: E402
import harvard_preservation_state_machine_v3 as v3  # noqa: E402


class DummyClient:
    def __enter__(self) -> "DummyClient":
        return self

    def __exit__(self, *_args: object) -> bool:
        return False


def archive_file(file_id: int = 14153535) -> dict[str, object]:
    return {
        "dataFile": {
            "id": file_id,
            "filename": impl.ARCHIVE_NAME,
            "filesize": impl.EXPECTED_BYTES,
            "checksum": {"type": "SHA-256", "value": impl.EXPECTED_SHA256},
        }
    }


def receipt_file(file_id: int = 14153536) -> dict[str, object]:
    return {
        "dataFile": {
            "id": file_id,
            "filename": impl.RECEIPT_NAME,
            "filesize": 512,
            "checksum": {"type": "SHA-256", "value": "0" * 64},
        }
    }


def dataset(
    *,
    state: str = "DRAFT",
    terms: str = "",
    with_receipt: bool = False,
) -> dict[str, object]:
    files = [archive_file()]
    if with_receipt:
        files.append(receipt_file())
    return {
        "id": 14153533,
        "latestVersion": {
            "versionState": state,
            "termsOfUse": terms,
            "files": files,
        },
    }


def current_waiting_state() -> dict[str, object]:
    return json.loads(
        (ROOT / "preservation" / "harvard-dataverse-state.json").read_text(
            encoding="utf-8"
        )
    )


def completed_state() -> dict[str, object]:
    version = dataset(state="RELEASED", with_receipt=True)["latestVersion"]
    assert isinstance(version, dict)
    record = impl.base_state(14153533, version)
    record.update(
        {
            "status": "complete",
            "archive_file_id": 14153535,
            "public_readback_verified": True,
            "public_readback_bytes": impl.EXPECTED_BYTES,
            "public_readback_sha256": impl.EXPECTED_SHA256,
            "receipt_file_id": 14153536,
            "receipt_verified": True,
            "receipt_schema": "trinity-accord-harvard-publication-receipt-v1",
        }
    )
    return record


def install_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v3.httpx, "Client", lambda *_args, **_kwargs: DummyClient())
    monkeypatch.setenv("HD_API_TOKEN", "test-token")


def write_state(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_locked_missing_terms_never_mutates_or_resubmits(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    write_state(state_path, current_waiting_state())
    monkeypatch.setattr(impl, "get_dataset", lambda *_args: dataset())
    monkeypatch.setattr(v3, "get_in_review_lock", lambda *_args: True)
    monkeypatch.setattr(
        v3,
        "update_custom_terms",
        lambda *_args: pytest.fail("locked dataset must not be mutated"),
    )
    monkeypatch.setattr(
        v3,
        "submit_for_review",
        lambda *_args: pytest.fail("locked dataset must not be resubmitted"),
    )

    with pytest.raises(impl.StateMachineError, match="refusing to mutate"):
        v3.run_v3(tmp_path / "out", state_path)


def test_unlock_repairs_terms_verifies_identity_and_submits_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    write_state(state_path, current_waiting_state())
    before = dataset()
    after = dataset(terms=v3.CUSTOM_TERMS)
    observations = iter((before, after))
    monkeypatch.setattr(
        impl, "get_dataset", lambda *_args: copy.deepcopy(next(observations))
    )
    monkeypatch.setattr(v3, "get_in_review_lock", lambda *_args: False)
    updates: list[int] = []
    submissions: list[str] = []
    monkeypatch.setattr(
        v3, "update_custom_terms", lambda _client, _token, dataset_id: updates.append(dataset_id)
    )
    monkeypatch.setattr(
        v3,
        "submit_for_review",
        lambda _client, _token, phase: submissions.append(phase) or "submitted",
    )

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    result = json.loads(state_path.read_text(encoding="utf-8"))
    assert updates == [14153533]
    assert submissions == ["v1.0-terms-corrected"]
    assert result["status"] == "terms_corrected_submitted_for_review_v1_0"
    assert result["authenticated_readback_reused"] is True
    assert result["dataset_terms"]["terms_of_use_sha256"] == v3.CUSTOM_TERMS_SHA256


def test_second_curator_return_does_not_create_resubmission_loop(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    previous = current_waiting_state()
    previous["status"] = "terms_corrected_submitted_for_review_v1_0"
    state_path = tmp_path / "state.json"
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl, "get_dataset", lambda *_args: dataset(terms=v3.CUSTOM_TERMS)
    )
    monkeypatch.setattr(v3, "get_in_review_lock", lambda *_args: False)
    monkeypatch.setattr(
        v3,
        "submit_for_review",
        lambda *_args: pytest.fail("a second curator return must not be resubmitted"),
    )

    with pytest.raises(impl.StateMachineError, match="new curator return"):
        v3.run_v3(tmp_path / "out", state_path)


def test_complete_state_validates_small_receipt_and_skips_large_readback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    previous = completed_state()
    state_path = tmp_path / "state.json"
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="RELEASED", with_receipt=True),
    )
    validated_receipts: list[int] = []
    monkeypatch.setattr(
        impl,
        "validate_receipt_file",
        lambda _client, item: validated_receipts.append(impl.get_file_id(item)) or {},
    )
    monkeypatch.setattr(
        v3,
        "ORIGINAL_RUN",
        lambda *_args: pytest.fail("complete state must not repeat the 1.95 GB readback"),
    )

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    assert validated_receipts == [14153536]
    assert json.loads(state_path.read_text(encoding="utf-8")) == previous


def test_complete_guard_mismatch_falls_back_to_full_verification(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    previous = completed_state()
    previous["receipt_file_id"] = 999
    state_path = tmp_path / "state.json"
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="RELEASED", with_receipt=True),
    )
    fallbacks: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        v3,
        "ORIGINAL_RUN",
        lambda output, state: fallbacks.append((output, state)) or 0,
    )

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    assert fallbacks == [(tmp_path / "out", state_path)]
