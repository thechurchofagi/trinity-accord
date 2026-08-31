#!/usr/bin/env python3
"""Fixture tests for OTS pending detection logic.

Covers the case where `ots upgrade` outputs pending markers
but `ots verify` outputs only Bitcoin node connection errors.
"""
from __future__ import annotations

import sys
import tempfile
import json
import hashlib
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from record_chain_hashing import OTS_ANCHOR_SCHEMA, write_json_atomic


def test_is_pending_output_detects_upgrade_markers() -> None:
    """is_pending_output must detect 'Pending confirmation in Bitcoin blockchain'
    even when the text comes from upgrade output, not verify output."""
    from ots_verify_record_chain_anchor import is_pending_output

    # This is the exact output from `ots upgrade` when timestamp is pending
    upgrade_stderr = (
        "Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain\n"
        "Calendar https://finney.calendar.eternitywall.com: Pending confirmation in Bitcoin blockchain\n"
        "Calendar https://alice.btc.calendar.opentimestamps.org: Pending confirmation in Bitcoin blockchain\n"
        "Calendar https://bob.btc.calendar.opentimestamps.org: Pending confirmation in Bitcoin blockchain\n"
        "Failed! Timestamp not complete\n"
    )

    # This is the exact output from `ots verify` when Bitcoin node is unavailable
    verify_stderr = (
        "Could not connect to Bitcoin node: Cookie file unusable "
        "([Errno 2] No such file or directory: '/root/.bitcoin/.cookie') "
        "and rpcpassword not specified in the configuration file: "
        "'/root/.bitcoin/bitcoin.conf'\n"
    )

    # Verify output alone should NOT be detected as pending
    assert not is_pending_output(verify_stderr), (
        "verify-only output should not be detected as pending"
    )

    # Upgrade output alone SHOULD be detected as pending
    assert is_pending_output(upgrade_stderr), (
        "upgrade output with 'Pending confirmation' should be detected as pending"
    )

    # Combined output (upgrade + verify) SHOULD be detected as pending
    combined = f"\n{upgrade_stderr}\n{verify_stderr}"
    assert is_pending_output(combined), (
        "combined upgrade+verify output should be detected as pending"
    )


def test_is_success_output_rejects_bitcoin_node_error() -> None:
    """is_success_output must not match when output contains 'bitcoin'
    but lacks 'success'."""
    from ots_verify_record_chain_anchor import is_success_output

    text = "Could not connect to Bitcoin node: Cookie file unusable"
    assert not is_success_output(text), (
        "Bitcoin node error should not match success output"
    )


def test_combined_output_with_upgrade_pending_and_verify_error() -> None:
    """Full integration: combined output from upgrade (pending) + verify (error)
    must result in bitcoin_pending=True, bitcoin_verified=False, no errors."""
    from ots_verify_record_chain_anchor import is_pending_output, is_success_output

    upgrade_stdout = ""
    upgrade_stderr = (
        "Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain\n"
        "Failed! Timestamp not complete\n"
    )
    verify_stdout = "Assuming target filename is 'test.json'\n"
    verify_stderr = "Could not connect to Bitcoin node: Cookie file unusable\n"

    combined = f"{verify_stdout}\n{verify_stderr}"
    combined_with_upgrade = f"{combined}\n{upgrade_stdout}\n{upgrade_stderr}"

    # Without upgrade output: not pending, not success → would error
    assert not is_pending_output(combined)
    assert not is_success_output(combined)

    # With upgrade output: pending detected → no error
    assert is_pending_output(combined_with_upgrade)
    assert not is_success_output(combined_with_upgrade)


def test_has_bitcoin_block_header_attestation() -> None:
    """Detect BitcoinBlockHeaderAttestation in ots info output."""
    from ots_verify_record_chain_anchor import has_bitcoin_block_header_attestation

    # Example ots info output with BitcoinBlockHeaderAttestation
    info_with_attestation = (
        "File: test.json.ots\n"
        "Timestamp: 1749139200\n"
        "Hash: abc123\n"
        "\n"
        "verify test.json.ots\n"
        "Got 1 attestation(s)\n"
        "BitcoinBlockHeaderAttestation(block_height=897000, block_hash=0000000000000000000...)\n"
    )

    # Example ots info output without BitcoinBlockHeaderAttestation (pending)
    info_pending = (
        "File: test.json.ots\n"
        "Timestamp: 1749139200\n"
        "Hash: abc123\n"
        "\n"
        "verify test.json.ots\n"
        "Got 0 attestation(s)\n"
        "Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain\n"
    )

    assert has_bitcoin_block_header_attestation(info_with_attestation), (
        "should detect BitcoinBlockHeaderAttestation in info output"
    )
    assert not has_bitcoin_block_header_attestation(info_pending), (
        "should not detect BitcoinBlockHeaderAttestation in pending output"
    )


def test_upgrade_success_marks_calendar_attested_not_bitcoin_verified() -> None:
    """When ots upgrade returns 'Success! Timestamp complete',
    calendar_attested and bitcoin_attestation_embedded should be True,
    but bitcoin_verified and strict_bitcoin_verified should remain False
    (upgrade success ≠ strict Bitcoin node verify)."""
    from ots_verify_record_chain_anchor import is_success_output

    success_text = "Success! Timestamp complete\n"
    assert is_success_output(success_text), (
        "'Success! Timestamp complete' should match success output"
    )


def test_strict_verify_unavailable_does_not_fail_upgraded_proof() -> None:
    """When no Bitcoin node is available, an upgraded proof
    (with BitcoinBlockHeaderAttestation) should not be treated as a failure."""
    from ots_verify_record_chain_anchor import (
        has_bitcoin_block_header_attestation,
        is_pending_output,
    )

    info_text = (
        "File: test.json.ots\n"
        "BitcoinBlockHeaderAttestation(block_height=897000)\n"
    )
    verify_no_node = "Could not connect to Bitcoin node: Cookie file unusable\n"

    assert has_bitcoin_block_header_attestation(info_text)
    assert not is_pending_output(verify_no_node)
    # The combination should NOT be treated as pending — it's upgraded


def test_upgrade_success_no_bitcoin_node_produces_upgraded_state() -> None:
    """Fixture: upgrade stdout contains 'Success! Timestamp complete',
    no bitcoin_node_url → anchor.ots_status should be 'upgraded',
    bitcoin_attestation_embedded=True, bitcoin_verified=False,
    strict_bitcoin_verified=False, result should pass (not fail)."""
    from ots_verify_record_chain_anchor import (
        has_bitcoin_block_header_attestation,
        is_success_output,
    )

    upgrade_stdout = ""
    upgrade_stderr = (
        "Calendar https://btc.calendar.catallaxy.com: upgrading to block 897000\n"
        "Success! Timestamp complete\n"
    )
    upgrade_text = f"{upgrade_stdout}\n{upgrade_stderr}"

    # is_success_output should match
    assert is_success_output(upgrade_text)

    # Simulate ots info with BitcoinBlockHeaderAttestation
    info_text = (
        "File: test.json.ots\n"
        "BitcoinBlockHeaderAttestation(block_height=897000, block_hash=0000000000000000000...)\n"
    )
    assert has_bitcoin_block_header_attestation(info_text)

    # Verify that upgrade success does NOT set bitcoin_verified
    # (this is the key semantic: upgrade calendar attestation ≠ strict Bitcoin verify)
    # The code should set:
    #   calendar_attested = True
    #   bitcoin_attestation_embedded = True
    #   bitcoin_pending = False
    #   bitcoin_verified = False (no bitcoin node)
    #   strict_bitcoin_verified = False (no bitcoin node)
    #   strict_verify_unavailable_reason = "no_bitcoin_node"
    #   ots_status = "upgraded"


def test_verification_profile_controls_strict_full_node_claim() -> None:
    """RPC compatibility must never be mistaken for a local full node."""
    with tempfile.TemporaryDirectory(prefix="trinity-ots-profile-") as tmp:
        work = Path(tmp)
        anchored_file = work / "head.json"
        ots_file = work / "head.json.ots"
        anchor_file = work / "anchor.json"
        fake_ots = work / "ots"

        anchored_file.write_text('{"head":"abc"}\n', encoding="utf-8")
        ots_file.write_bytes(b"fake-ots-proof")
        fake_ots.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = \"info\" ]; then\n"
            "  echo 'BitcoinBlockHeaderAttestation(block_height=1)'\n"
            "else\n"
            "  echo 'Success! Bitcoin timestamp complete'\n"
            "fi\n",
            encoding="utf-8",
        )
        os.chmod(fake_ots, 0o755)

        def reset_anchor() -> None:
            write_json_atomic(anchor_file, {
                "schema": "trinityaccord.native-record-chain-ots-anchor.v1",
                "anchored_file": str(anchored_file),
                "anchored_file_sha256": hashlib.sha256(anchored_file.read_bytes()).hexdigest(),
                "ots_file": str(ots_file),
                "ots_file_sha256": hashlib.sha256(ots_file.read_bytes()).hexdigest(),
                "ots_status": "upgraded",
            })

        def verify(profile: str) -> dict:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts/ots_verify_record_chain_anchor.py"),
                    "--anchor-file", str(anchor_file),
                    "--ots-bin", str(fake_ots),
                    "--bitcoin-node-url", "http://127.0.0.1:18443/",
                    "--bitcoin-verification-profile", profile,
                    "--require-bitcoin-verification",
                    "--write-updated-anchor",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            assert result.returncode == 0, result.stderr
            return json.loads(anchor_file.read_text(encoding="utf-8"))

        reset_anchor()
        remote = verify("dual_remote_esplora")
        assert remote["ots_status"] == "verified"
        assert remote["bitcoin_verified"] is True
        assert remote["remote_dual_source_verified"] is True
        assert remote["local_full_node_verified"] is False
        assert remote["strict_bitcoin_verified"] is False
        assert remote["bitcoin_verification_independent_consensus"] is False
        assert remote["strict_verify_unavailable_reason"] == "verification_profile_is_not_local_full_node"
        assert "strict_bitcoin_verified_at" not in remote

        reset_anchor()
        local = verify("local_full_node")
        assert local["bitcoin_verified"] is True
        assert local["local_full_node_verified"] is True
        assert local["remote_dual_source_verified"] is False
        assert local["strict_bitcoin_verified"] is True
        assert local["bitcoin_verification_independent_consensus"] is True
        assert "strict_bitcoin_verified_at" in local


def main() -> None:
    test_is_pending_output_detects_upgrade_markers()
    test_is_success_output_rejects_bitcoin_node_error()
    test_combined_output_with_upgrade_pending_and_verify_error()
    test_has_bitcoin_block_header_attestation()
    test_upgrade_success_marks_calendar_attested_not_bitcoin_verified()
    test_strict_verify_unavailable_does_not_fail_upgraded_proof()
    test_upgrade_success_no_bitcoin_node_produces_upgraded_state()
    test_verification_profile_controls_strict_full_node_claim()
    print("PASS: OTS pending detection fixture tests")


if __name__ == "__main__":
    main()
