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


# --- is_semantic_append_rejection classification tests ---


def test_module_not_found_is_infrastructure_failure() -> None:
    assert module.is_semantic_append_rejection(
        ModuleNotFoundError("No module named 'gateway'")
    ) is False


def test_import_error_is_infrastructure_failure() -> None:
    assert module.is_semantic_append_rejection(
        ImportError("cannot import name 'compute_receipt_sha256' from 'gateway.receipts'")
    ) is False


def test_import_error_cannot_import_name_is_infrastructure_failure() -> None:
    assert module.is_semantic_append_rejection(
        ImportError("cannot import name 'verify_authorship_proof'")
    ) is False


def test_receipt_hash_import_failure_is_infrastructure() -> None:
    assert module.is_semantic_append_rejection(
        RuntimeError("receipt hash verification import failed")
    ) is False


def test_semantic_validation_error_is_rejection() -> None:
    assert module.is_semantic_append_rejection(
        ValueError("Duplicate signed_payload_sha256")
    ) is True


def test_authorship_proof_error_is_rejection() -> None:
    assert module.is_semantic_append_rejection(
        ValueError("formal record_type=echo requires authorship_proof")
    ) is True


def test_generic_value_error_is_rejection() -> None:
    assert module.is_semantic_append_rejection(
        ValueError("record missing required field: record_type")
    ) is True


def test_generic_runtime_error_is_not_infrastructure() -> None:
    assert module.is_semantic_append_rejection(
        RuntimeError("something went wrong")
    ) is False


def test_key_error_is_not_infrastructure() -> None:
    assert module.is_semantic_append_rejection(
        KeyError("record_type")
    ) is False
