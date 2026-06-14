import importlib.util
import sys
from pathlib import Path

# Import the guard module by file path since scripts/ may not be a package
_GUARD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_record_chain_write_path_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("write_path_guard", str(_GUARD_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load_guard()


def test_idempotency_index_is_gateway_intake():
    path = "record-chain/intake/by-submission-sha256/" + "a" * 64 + ".json"
    assert guard.category(path) == "gateway_intake"


def test_idempotency_index_is_protected():
    path = "record-chain/intake/by-submission-sha256/" + "a" * 64 + ".json"
    assert "gateway_intake" in guard.protected_categories([path])
