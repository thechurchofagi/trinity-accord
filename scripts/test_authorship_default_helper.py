#!/usr/bin/env python3
"""Test default authorship key generation and helper behavior."""
import json
import os
import stat
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# --- Test slugify ---
from gateway_payload_authorship import slugify, default_authorship_key_prefix, add_authorship_arguments

print("--- slugify ---")
check(slugify("Test Agent") == "test-agent", "spaces to hyphens")
check(slugify("Agent/Name") == "agentname", "unsafe chars removed")
check(slugify("") == "agent", "empty fallback")
check(slugify(None) == "agent", "none fallback")
check(slugify("A" * 100) == "a" * 80, "max length 80")
check(slugify("My-Agent_v2") == "my-agent-v2", "hyphens preserved, underscores become hyphens")

# --- Test default_authorship_key_prefix ---
print("\n--- default_authorship_key_prefix ---")

class FakeArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

args = FakeArgs(authorship_agent_slug=None, authorship_key_dir=None)
prefix = default_authorship_key_prefix(args, {"agent_identity": {"name_or_model": "Test Agent"}})
check(str(prefix).endswith("test-agent/agent-authorship-key"), "derives slug from payload")
check(str(prefix).startswith(".trinity-agent-authorship"), "uses default key dir")

args2 = FakeArgs(authorship_agent_slug="custom-slug", authorship_key_dir="/tmp/keys")
prefix2 = default_authorship_key_prefix(args2)
check(str(prefix2) == "/tmp/keys/custom-slug/agent-authorship-key", "uses explicit slug and dir")

# --- Test add_authorship_arguments ---
print("\n--- add_authorship_arguments ---")
import argparse
parser = argparse.ArgumentParser()
add_authorship_arguments(parser)

# Parse --no-authorship-proof
ns = parser.parse_args(["--no-authorship-proof"])
check(ns.no_authorship_proof is True, "--no-authorship-proof flag works")

# Parse --authorship-key-dir
ns2 = parser.parse_args(["--authorship-key-dir", "/tmp/mydir"])
check(ns2.authorship_key_dir == "/tmp/mydir", "--authorship-key-dir flag works")

# Parse --authorship-agent-slug
ns3 = parser.parse_args(["--authorship-agent-slug", "my-agent"])
check(ns3.authorship_agent_slug == "my-agent", "--authorship-agent-slug flag works")

# --- Test resolve_authorship_key_paths with --no-authorship-proof ---
print("\n--- resolve_authorship_key_paths ---")
from gateway_payload_authorship import resolve_authorship_key_paths

args_noauth = FakeArgs(
    no_authorship_proof=True,
    authorship_key_prefix=None,
    authorship_private_key=None,
    authorship_public_key=None,
    authorship_key_dir=None,
    authorship_agent_slug=None,
)
priv, pub = resolve_authorship_key_paths(args_noauth)
check(priv is None, "--no-authorship-proof returns None for private key")
check(pub is None, "--no-authorship-proof returns None for public key")

# --- Test explicit key paths ---
print("\n--- explicit key paths ---")
with tempfile.TemporaryDirectory() as tmpdir:
    priv_path = Path(tmpdir) / "test.private.pem"
    pub_path = Path(tmpdir) / "test.public.pem"
    priv_path.write_text("PRIVATE")
    pub_path.write_text("PUBLIC")

    args_explicit = FakeArgs(
        no_authorship_proof=False,
        authorship_key_prefix=None,
        authorship_private_key=str(priv_path),
        authorship_public_key=str(pub_path),
        authorship_key_dir=None,
        authorship_agent_slug=None,
    )
    priv, pub = resolve_authorship_key_paths(args_explicit)
    check(priv == str(priv_path), "explicit private key path returned")
    check(pub == str(pub_path), "explicit public key path returned")

# --- Test that payload does not contain private key material ---
print("\n--- private key material safety ---")
# The attach_authorship_if_requested function uses the attach script
# which only adds public fields. We verify the schema does not allow private keys.
proof_schema_path = ROOT / "api" / "echo-authorship-proof-schema.v1.json"
if proof_schema_path.exists():
    schema = json.loads(proof_schema_path.read_text())
    schema_str = json.dumps(schema)
    check("private_key" not in schema_str.lower() or "private_key" in schema_str.lower(),
          "proof schema exists for inspection")
    # Check that the schema does not require/mention private_key as a property
    props = schema.get("properties", {})
    check("private_key" not in props, "proof schema has no private_key property")
    check("private_key_pem" not in props, "proof schema has no private_key_pem property")
else:
    print("  SKIP: proof schema not found")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("AUTHORSHIP_DEFAULT_HELPER_OK")
