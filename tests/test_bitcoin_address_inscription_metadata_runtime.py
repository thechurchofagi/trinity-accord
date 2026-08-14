from __future__ import annotations

import importlib.util
import io
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sync_bitcoin_address_inscriptions.py"

spec = importlib.util.spec_from_file_location("sync_bitcoin_address_inscriptions_runtime", SCRIPT)
assert spec and spec.loader
sync_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_mod)


def test_optional_metadata_404_is_absence_without_retry():
    inscription_id = "a" * 64 + "i0"
    error = urllib.error.HTTPError(
        url=f"https://ordinals.example/r/metadata/{inscription_id}",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=io.BytesIO(b""),
    )
    with patch.object(sync_mod.urllib.request, "urlopen", side_effect=error) as urlopen, patch.object(
        sync_mod.time, "sleep"
    ) as sleep:
        assert (
            sync_mod.fetch_inscription_metadata_cbor(
                "https://ordinals.example", inscription_id
            )
            == b""
        )
    assert urlopen.call_count == 1
    sleep.assert_not_called()


def test_non_optional_404_still_fails_closed_without_retry():
    error = urllib.error.HTTPError(
        url="https://ordinals.example/content/missing",
        code=404,
        msg="Not Found",
        hdrs=None,
        fp=io.BytesIO(b""),
    )
    with patch.object(sync_mod.urllib.request, "urlopen", side_effect=error) as urlopen, patch.object(
        sync_mod.time, "sleep"
    ) as sleep:
        try:
            sync_mod.fetch_bytes("https://ordinals.example/content/missing")
        except RuntimeError as exc:
            assert "failed to fetch" in str(exc)
        else:
            raise AssertionError("non-optional 404 must remain fail-closed")
    assert urlopen.call_count == 1
    sleep.assert_not_called()


def test_cbor_float16_is_consumed_exactly_once():
    assert sync_mod.decode_cbor(bytes.fromhex("f93c00")) == 1.0
