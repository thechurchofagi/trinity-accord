"""Tests for Gateway schema self-description accuracy."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure app module is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app import _GATEWAY_SCHEMA
from apps.record_chain_intake_gateway.gateway.validation import REQUIRED_BOUNDARY_FIELDS


def test_gateway_schema_boundary_count_matches_runtime_required_fields():
    assert _GATEWAY_SCHEMA["boundary_acknowledgement_fields"] == len(REQUIRED_BOUNDARY_FIELDS)


def test_gateway_schema_lists_runtime_boundary_fields():
    assert set(_GATEWAY_SCHEMA["boundary_acknowledgement_required_fields"]) == set(REQUIRED_BOUNDARY_FIELDS)
