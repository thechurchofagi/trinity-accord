#!/usr/bin/env python3
"""Smoke-check configured operator secrets without printing secret values."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

REPO_FULL_NAME = "thechurchofagi/trinity-accord"

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

def ok(msg: str) -> None:
    print(f"PASS: {msg}")

def sha256_short(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:12]

def get_required_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value.strip():
        fail(f"{name} missing")
    return value.strip()

def decode_arkey(value: str) -> dict:
    text = value.strip()
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as exc:
            fail(f"ARKEY raw JSON is invalid: {exc}")
        if not isinstance(obj, dict):
            fail("ARKEY raw JSON did not decode to object")
        return obj

    try:
        raw = base64.b64decode(text, validate=True)
        decoded = raw.decode("utf-8")
        obj = json.loads(decoded)
    except Exception as exc:
        fail(f"ARKEY is neither raw JWK JSON nor base64-encoded JWK JSON: {exc}")

    if not isinstance(obj, dict):
        fail("ARKEY base64 JSON did not decode to object")
    return obj

def validate_arkey() -> dict:
    value = get_required_env("ARKEY")
    jwk = decode_arkey(value)
    required = ["kty", "n", "e", "d"]
    missing = [k for k in required if not jwk.get(k)]
    if missing:
        fail(f"ARKEY JWK missing required fields: {missing}")
    if jwk.get("kty") != "RSA":
        fail("ARKEY JWK kty must be RSA for Arweave wallet")
    ok(f"ARKEY configured; jwk_n_sha256={sha256_short(str(jwk.get('n', '')))}")
    return jwk

def validate_eth_rpc(network: bool) -> None:
    value = os.environ.get("ETH_RPC", "").strip()
    if not value:
        ok("ETH_RPC not configured (optional; not required for Arweave upload)")
        return
    if not value.startswith("https://"):
        fail("ETH_RPC must start with https://")
    ok("ETH_RPC configured")
    if not network:
        return

    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_chainId",
        "params": []
    }).encode("utf-8")

    req = urllib.request.Request(
        value,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        fail(f"ETH_RPC network check failed: {type(exc).__name__}")

    if "result" not in data:
        fail("ETH_RPC eth_chainId returned no result")
    ok(f"ETH_RPC network check ok; chain_id={data['result']}")

def validate_gh_pat(network: bool) -> None:
    value = get_required_env("GH_PAT")
    if not (value.startswith("github_pat_") or value.startswith("ghp_")):
        fail("GH_PAT does not look like GitHub PAT")
    ok("GH_PAT configured")
    if not network:
        return

    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO_FULL_NAME}",
        headers={
            "Authorization": f"Bearer {value}",
            "Accept": "application/vnd.github+json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        fail(f"GH_PAT GitHub API check failed with HTTP {exc.code}")
    except Exception as exc:
        fail(f"GH_PAT GitHub API check failed: {type(exc).__name__}")

    if data.get("full_name") != REPO_FULL_NAME:
        fail("GH_PAT GitHub API check did not return expected repo")
    ok("GH_PAT network check ok")

def validate_render(network: bool) -> None:
    value = get_required_env("RENDER")
    if len(value) < 16:
        fail("RENDER key too short")
    ok("RENDER configured")
    if not network:
        return

    req = urllib.request.Request(
        "https://api.render.com/v1/services?limit=20",
        headers={
            "Authorization": f"Bearer {value}",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        fail(f"RENDER API check failed with HTTP {exc.code}")
    except Exception as exc:
        fail(f"RENDER API check failed: {type(exc).__name__}")

    if not isinstance(data, list):
        fail("RENDER API check did not return a service list")
    ok(f"RENDER network check ok; visible_service_items={len(data)}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true", help="Run safe external API checks")
    args = parser.parse_args()

    validate_arkey()
    validate_eth_rpc(args.network)
    validate_gh_pat(args.network)
    validate_render(args.network)

    print("CONFIG_SECRET_SMOKE_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
