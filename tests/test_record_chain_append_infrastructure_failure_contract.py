from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    """Load trinity_record_chain as a module for testing."""
    spec = importlib.util.spec_from_file_location(
        "trinity_record_chain_under_test",
        ROOT / "scripts" / "trinity_record_chain.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


module = _load_module()


# --- is_infrastructure_append_error classification tests ---


def test_module_not_found_is_infrastructure_failure() -> None:
    assert module.is_infrastructure_append_error(
        ModuleNotFoundError("No module named 'gateway'")
    ) is True


def test_import_error_is_infrastructure_failure() -> None:
    assert module.is_infrastructure_append_error(
        ImportError("cannot import name 'compute_receipt_sha256' from 'gateway.receipts'")
    ) is True


def test_import_error_cannot_import_name_is_infrastructure_failure() -> None:
    assert module.is_infrastructure_append_error(
        ImportError("cannot import name 'verify_authorship_proof'")
    ) is True


def test_receipt_hash_import_failure_is_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        RuntimeError("receipt hash verification import failed")
    ) is True


def test_semantic_validation_error_is_not_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        ValueError("Duplicate signed_payload_sha256")
    ) is False


def test_authorship_proof_error_is_not_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        ValueError("formal record_type=echo requires authorship_proof")
    ) is False


def test_generic_value_error_is_not_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        ValueError("record missing required field: record_type")
    ) is False


def test_generic_runtime_error_is_not_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        RuntimeError("something went wrong")
    ) is False


def test_key_error_is_not_infrastructure() -> None:
    assert module.is_infrastructure_append_error(
        KeyError("record_type")
    ) is False
