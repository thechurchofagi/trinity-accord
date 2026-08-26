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


def legacy_receipt_file(file_id: int = 14153536) -> dict[str, object]:
    return {
        "dataFile": {
            "id": file_id,
            "filename": impl.LEGACY_RECEIPT_NAME,
            "filesize": 512,
            "checksum": {"type": "SHA-256", "value": "0" * 64},
        }
    }


def dataset(
    *,
    state: str = "DRAFT",
    terms: str = "",
    with_legacy_receipt: bool = False,
) -> dict[str, object]:
    files = [archive_file()]
    if with_legacy_receipt:
        files.append(legacy_receipt_file())
    latest: dict[str, object] = {
        "versionState": state,
        "termsOfUse": terms,
        "files": files,
    }
    if state == "RELEASED":
        latest.update({"versionNumber": 1, "versionMinorNumber": 0})
    return {
        "id": 14153533,
        "latestVersion": latest,
    }


def current_waiting_state() -> dict[str, object]:
    return json.loads(
        (ROOT / "preservation" / "harvard-dataverse-state.json").read_text(
            encoding="utf-8"
        )
    )


def completed_state() -> dict[str, object]:
    version = dataset(state="RELEASED")["latestVersion"]
    assert isinstance(version, dict)
    record = impl.base_state(14153533, version)
    record.update(
        {
            "status": "complete",
            "archive_file_id": 14153535,
            "public_readback_verified": True,
            "public_readback_bytes": impl.EXPECTED_BYTES,
            "public_readback_sha256": impl.EXPECTED_SHA256,
            "completion_policy": "v1_0_public_readback_only",
            "released_version": "1.0",
            "harvard_dataset_mutated_after_release": False,
            "verification_evidence_location": "repository_state_and_workflow_audit",
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
    assert result["target_completion_policy"] == "v1_0_public_readback_only"
    assert result["post_release_harvard_mutation_authorized"] is False
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

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    result = json.loads(state_path.read_text(encoding="utf-8"))
    assert result["review_submission"] == "left_draft_for_curator_direct_publication"
    assert result["status"] == "terms_corrected_submitted_for_review_v1_0"
    assert result["version_state"] == "DRAFT"


def test_complete_v10_state_skips_repeated_large_readback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    previous = completed_state()
    state_path = tmp_path / "state.json"
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="RELEASED"),
    )
    monkeypatch.setattr(
        v3,
        "ORIGINAL_RUN",
        lambda *_args: pytest.fail("complete state must not repeat the 1.95 GB readback"),
    )

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    assert json.loads(state_path.read_text(encoding="utf-8")) == previous


def test_complete_guard_mismatch_falls_back_to_full_verification(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    previous = completed_state()
    previous["public_readback_sha256"] = "0" * 64
    state_path = tmp_path / "state.json"
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="RELEASED"),
    )
    fallbacks: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        v3,
        "ORIGINAL_RUN",
        lambda output, state: fallbacks.append((output, state)) or 0,
    )

    assert v3.run_v3(tmp_path / "out", state_path) == 0
    assert fallbacks == [(tmp_path / "out", state_path)]


def test_released_v10_public_readback_completes_without_harvard_mutation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    write_state(state_path, current_waiting_state())
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="RELEASED", terms=v3.CUSTOM_TERMS),
    )
    public_reads: list[tuple[int, str | None, bool]] = []

    def verify_public(
        _client: object, file_id: int, token: str | None, public: bool
    ) -> tuple[int, str]:
        public_reads.append((file_id, token, public))
        return impl.EXPECTED_BYTES, impl.EXPECTED_SHA256

    monkeypatch.setattr(impl, "verify_archive_bytes", verify_public)
    monkeypatch.setattr(
        impl,
        "submit_for_review",
        lambda *_args: pytest.fail("released v1.0 must not be submitted again"),
    )

    output_dir = tmp_path / "out"
    assert v3.run_v3(output_dir, state_path) == 0
    result = json.loads(state_path.read_text(encoding="utf-8"))
    assert public_reads == [(14153535, None, True)]
    assert result["status"] == "complete"
    assert result["version_state"] == "RELEASED"
    assert result["public_readback_verified"] is True
    assert result["completion_policy"] == "v1_0_public_readback_only"
    assert result["harvard_dataset_mutated_after_release"] is False
    assert not (output_dir / impl.LEGACY_RECEIPT_NAME).exists()


def test_legacy_receipt_presence_fails_closed_instead_of_creating_v11(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    write_state(state_path, current_waiting_state())
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(
            state="DRAFT",
            terms=v3.CUSTOM_TERMS,
            with_legacy_receipt=True,
        ),
    )

    with pytest.raises(impl.StateMachineError, match="v1.0-only policy"):
        v3.run_v3(tmp_path / "out", state_path)


def test_v11_version_fails_closed_before_readback_or_submission(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    write_state(state_path, current_waiting_state())
    returned = dataset(state="DRAFT", terms=v3.CUSTOM_TERMS)
    latest = returned["latestVersion"]
    assert isinstance(latest, dict)
    latest["versionNumber"] = 1
    latest["versionMinorNumber"] = 1
    monkeypatch.setattr(impl, "get_dataset", lambda *_args: returned)
    monkeypatch.setattr(
        impl,
        "verify_archive_bytes",
        lambda *_args, **_kwargs: pytest.fail("v1.1 must not be read or advanced"),
    )
    monkeypatch.setattr(
        v3,
        "submit_for_review",
        lambda *_args: pytest.fail("v1.1 must not be submitted"),
    )

    with pytest.raises(impl.StateMachineError, match="v1.0-only policy"):
        v3.run_v3(tmp_path / "out", state_path)


def test_unversioned_draft_without_frozen_v10_state_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    install_client(monkeypatch)
    state_path = tmp_path / "state.json"
    previous = completed_state()
    write_state(state_path, previous)
    monkeypatch.setattr(
        impl,
        "get_dataset",
        lambda *_args: dataset(state="DRAFT", terms=v3.CUSTOM_TERMS),
    )

    with pytest.raises(impl.StateMachineError, match="not bound to the frozen v1.0"):
        v3.run_v3(tmp_path / "out", state_path)


def test_v10_only_policy_has_no_v11_or_receipt_upload_path() -> None:
    base = (SCRIPTS / "harvard_preservation_state_machine.py").read_text(encoding="utf-8")
    wrapper = (SCRIPTS / "harvard_preservation_state_machine_v3.py").read_text(encoding="utf-8")
    workflow = (
        ROOT / ".github" / "workflows" / "harvard-preservation-state-machine.yml"
    ).read_text(encoding="utf-8")

    for text in (base, wrapper, workflow):
        assert "submitted_for_review_v1_1" not in text
    assert "def upload_receipt" not in base
    assert "receipt_uploaded" not in base
    assert "$RUNNER_TEMP/harvard-state-machine/harvard-publication-receipt.json" not in workflow
