from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_ci_code_alignment as alignment  # noqa: E402
import validate_json_strict as strict_json  # noqa: E402


def test_strict_json_rejects_duplicate_object_keys() -> None:
    with pytest.raises(ValueError, match="duplicate JSON key"):
        strict_json.load_strict_json_bytes(b'{"x": 1, "x": 2}', "duplicate")


def test_strict_json_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError, match="non-finite JSON number"):
        strict_json.load_strict_json_bytes(b'{"x": NaN}', "non-finite")


def test_strict_json_accepts_normal_json() -> None:
    assert strict_json.load_strict_json_bytes(b'{"x": [1, true, null]}', "valid") == {
        "x": [1, True, None]
    }


def test_requirement_parser_rejects_duplicate_dependency(tmp_path: Path) -> None:
    path = tmp_path / "requirements.txt"
    path.write_text("example==1.0\nexample==1.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicates dependency"):
        alignment.parse_requirements(path)


def test_render_env_map_preserves_secret_sync_boundary() -> None:
    service = {
        "envVars": [
            {"key": "PUBLIC", "value": "value"},
            {"key": "SECRET", "sync": False},
        ]
    }
    assert alignment.env_map(service) == {
        "PUBLIC": "value",
        "SECRET": {"sync": False},
    }
