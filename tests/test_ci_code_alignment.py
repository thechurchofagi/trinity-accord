from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_script(module_name: str, filename: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


alignment = load_script("trinity_ci_alignment_contract", "test_ci_code_alignment.py")
strict_json = load_script("trinity_strict_json_validator", "validate_json_strict.py")


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
