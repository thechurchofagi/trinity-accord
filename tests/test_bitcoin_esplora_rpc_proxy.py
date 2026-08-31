from __future__ import annotations

import hashlib

import pytest

from scripts.bitcoin_esplora_rpc_proxy import ConsensusSource, ProxyError, Trace


def source(tmp_path) -> ConsensusSource:
    return ConsensusSource(Trace(tmp_path / "bitcoin-rpc-proxy.jsonl"), timeout=0.1)


def test_tip_uses_conservative_height_when_providers_are_close(tmp_path, monkeypatch) -> None:
    consensus = source(tmp_path)
    heights = {"blockstream": "964720", "mempool": "964718"}
    monkeypatch.setattr(
        consensus,
        "_get_text",
        lambda provider, path: heights[provider],
    )

    assert consensus.getblockcount() == 964718


def test_tip_fails_closed_when_provider_spread_is_too_large(tmp_path, monkeypatch) -> None:
    consensus = source(tmp_path)
    heights = {"blockstream": "964720", "mempool": "964710"}
    monkeypatch.setattr(
        consensus,
        "_get_text",
        lambda provider, path: heights[provider],
    )

    with pytest.raises(ProxyError, match="tip height spread too large"):
        consensus.getblockcount()


def test_block_hash_requires_exact_two_provider_agreement(tmp_path, monkeypatch) -> None:
    consensus = source(tmp_path)
    values = {"blockstream": "0" * 64, "mempool": "1" * 64}
    monkeypatch.setattr(
        consensus,
        "_get_text",
        lambda provider, path: values[provider],
    )

    with pytest.raises(ProxyError, match="independent providers disagree"):
        consensus.getblockhash(964715)


def test_raw_header_is_locally_hashed_back_to_requested_block(tmp_path, monkeypatch) -> None:
    consensus = source(tmp_path)
    header = bytes(range(80))
    header_hex = header.hex()
    block_hash = hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1].hex()
    monkeypatch.setattr(
        consensus,
        "_get_text",
        lambda provider, path: header_hex,
    )

    assert consensus.getblockheader(block_hash, verbose=False) == header_hex


def test_raw_header_hash_mismatch_fails_closed(tmp_path, monkeypatch) -> None:
    consensus = source(tmp_path)
    header_hex = bytes(range(80)).hex()
    monkeypatch.setattr(
        consensus,
        "_get_text",
        lambda provider, path: header_hex,
    )

    with pytest.raises(ProxyError, match="header hash mismatch"):
        consensus.getblockheader("0" * 64, verbose=False)
