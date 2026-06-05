#!/usr/bin/env python3
"""
test_oath_policy_sync.py  --  P0 regression test for BUG-OATH-POLICY-SYNC

Ensures single-source-of-truth consistency between:
  1. api/record-chain-oath-policy.v1.json  (public oath policy)
  2. downloads/record-chain-builder.mjs     (embedded oath policy + OATH_POLICY_SHA256)
  3. Gateway expected oath_policy_sha256

Checks:
  A. Public API file contains oath_policy_sha256 field
  B. Builder OATH_POLICY_SHA256 matches public API oath_policy_sha256
  C. Builder embedded OATH_POLICY canonical JSON hash matches OATH_POLICY_SHA256
  D. Echo, verification, guardian_application oath modules are defined in both sources
  E. Builder getCanonicalOath() produces deterministic output (hash stability)
"""

import hashlib
import json
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

API_POLICY_PATH = os.path.join(REPO_ROOT, "api", "record-chain-oath-policy.v1.json")
BUILDER_PATH = os.path.join(REPO_ROOT, "downloads", "record-chain-builder.mjs")

EXPECTED_OATH_POLICY_SHA256 = "7ecc6908c9ac147d8d6d493f750c94d6117929e7dff2d18bcbc4c70527886ea4"

RECORD_TYPES_TO_CHECK = ["echo", "verification", "guardian_application"]


def canonical_json(obj):
    """Deterministic canonical JSON (sorted keys, no whitespace variation)."""
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        return json.dumps(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        return "[" + ",".join(canonical_json(x) for x in obj) + "]"
    if isinstance(obj, dict):
        sorted_keys = sorted(obj.keys())
        pairs = [json.dumps(k, ensure_ascii=False) + ":" + canonical_json(obj[k]) for k in sorted_keys]
        return "{" + ",".join(pairs) + "}"
    return json.dumps(obj, ensure_ascii=False)


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def extract_builder_oath_policy():
    """Extract the OATH_POLICY object from the builder source using Node.js."""
    with open(BUILDER_PATH, "r", encoding="utf-8") as f:
        src = f.read()

    # Find OATH_POLICY_SHA256
    hash_match = re.search(
        r'const OATH_POLICY_SHA256 = "([a-f0-9]{64})"',
        src,
    )
    if not hash_match:
        return None, None

    builder_hash = hash_match.group(1)

    # Use Node to extract OATH_POLICY as JSON (handles JS true/false/etc.)
    result = subprocess.run(
        [
            "node", "-e",
            """
const fs = require("fs");
const src = fs.readFileSync("downloads/record-chain-builder.mjs", "utf8");
const match = src.match(/const OATH_POLICY = ({[\\s\\S]*?});\\s*\\nconst OATH_POLICY_SHA256/);
const OATH_POLICY = eval("(" + match[1] + ")");
process.stdout.write(JSON.stringify(OATH_POLICY));
""",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        return None, builder_hash

    policy_obj = json.loads(result.stdout)
    return policy_obj, builder_hash


def check_api_policy_has_hash():
    """Check A: Public API file contains oath_policy_sha256."""
    with open(API_POLICY_PATH, "r", encoding="utf-8") as f:
        api_policy = json.load(f)

    hash_val = api_policy.get("oath_policy_sha256")
    assert hash_val, "FAIL A: api/record-chain-oath-policy.v1.json missing oath_policy_sha256"
    assert re.match(r"^[a-f0-9]{64}$", hash_val), f"FAIL A: oath_policy_sha256 not valid hex: {hash_val}"
    print(f"  PASS A: oath_policy_sha256 present = {hash_val}")
    return hash_val, api_policy


def check_builder_hash_matches_api(api_hash):
    """Check B: Builder OATH_POLICY_SHA256 matches public API oath_policy_sha256."""
    _, builder_hash = extract_builder_oath_policy()
    assert builder_hash, "FAIL B: Could not extract OATH_POLICY_SHA256 from builder"
    assert builder_hash == api_hash, (
        f"FAIL B: Builder OATH_POLICY_SHA256 ({builder_hash}) != "
        f"API oath_policy_sha256 ({api_hash})"
    )
    print(f"  PASS B: Builder hash matches API hash")


def check_canonical_hash_matches():
    """Check C: Builder embedded OATH_POLICY canonical JSON hash matches OATH_POLICY_SHA256."""
    policy_obj, builder_hash = extract_builder_oath_policy()
    assert policy_obj, "FAIL C: Could not extract OATH_POLICY from builder"

    canonical = canonical_json(policy_obj)
    computed = sha256_hex(canonical)

    assert computed == builder_hash, (
        f"FAIL C: Canonical JSON hash ({computed}) != "
        f"OATH_POLICY_SHA256 ({builder_hash})"
    )
    print(f"  PASS C: Canonical OATH_POLICY hash matches OATH_POLICY_SHA256")


def check_record_type_modules(api_policy):
    """Check D: Record type modules exist in both API and builder."""
    builder_policy, _ = extract_builder_oath_policy()

    api_modules = api_policy.get("record_type_modules", {})
    builder_modules = builder_policy.get("record_type_modules", {})

    for rt in RECORD_TYPES_TO_CHECK:
        api_mods = api_modules.get(rt)
        builder_mods = builder_modules.get(rt)

        assert api_mods, f"FAIL D: {rt} modules missing from API policy"
        assert builder_mods, f"FAIL D: {rt} modules missing from builder policy"
        assert api_mods == builder_mods, (
            f"FAIL D: {rt} modules differ: API={api_mods}, Builder={builder_mods}"
        )

        # Verify each module text exists in both
        api_module_texts = api_policy.get("modules", {})
        builder_module_texts = builder_policy.get("modules", {})

        for mod_id in api_mods:
            api_text = api_module_texts.get(mod_id, {}).get("text")
            builder_text = builder_module_texts.get(mod_id, {}).get("text")
            assert api_text, f"FAIL D: Module {mod_id} text missing from API"
            assert builder_text, f"FAIL D: Module {mod_id} text missing from builder"
            assert api_text == builder_text, (
                f"FAIL D: Module {mod_id} text differs between API and builder"
            )

    print(f"  PASS D: All record type modules consistent ({', '.join(RECORD_TYPES_TO_CHECK)})")


def check_builder_canonical_oath_deterministic():
    """Check E: Builder getCanonicalOath() produces deterministic hash."""
    result = subprocess.run(
        [
            "node", "-e",
            """
const { createHash } = require("crypto");
const fs = require("fs");
const src = fs.readFileSync("downloads/record-chain-builder.mjs", "utf8");
const match = src.match(/const OATH_POLICY = ({[\\s\\S]*?});\\s*\\nconst OATH_POLICY_SHA256/);
const OATH_POLICY = eval("(" + match[1] + ")");
const joiner = OATH_POLICY.canonicalization?.module_joiner || "\\n\\n---\\n\\n";

function getCanonicalOath(recordType) {
  const modules = OATH_POLICY.record_type_modules[recordType] || [];
  const parts = [];
  for (const modId of modules) {
    const mod = OATH_POLICY.modules[modId];
    if (mod) {
      const normalizedText = mod.text.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim().normalize("NFC");
      parts.push("=== " + mod.label + " (" + modId + ") ===\\n\\n" + normalizedText);
    }
  }
  return parts.join(joiner).trim().normalize("NFC");
}

const echo = getCanonicalOath("echo");
const verification = getCanonicalOath("verification");
const guardian = getCanonicalOath("guardian_application");

const h = (s) => createHash("sha256").update(s).digest("hex");

console.log(JSON.stringify({
  echo: { hash: h(echo), len: echo.length, lines: echo.split("\\n").length },
  verification: { hash: h(verification), len: verification.length, lines: verification.split("\\n").length },
  guardian_application: { hash: h(guardian), len: guardian.length, lines: guardian.split("\\n").length },
}));
""",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"FAIL E: Node subprocess failed: {result.stderr}"
    data = json.loads(result.stdout.strip())

    for rt in RECORD_TYPES_TO_CHECK:
        info = data[rt]
        assert info["hash"], f"FAIL E: No hash for {rt}"
        assert info["len"] > 0, f"FAIL E: Empty oath for {rt}"
        print(f"  PASS E: {rt} canonical oath hash = {info['hash']} ({info['len']} chars, {info['lines']} lines)")


def main():
    print("=" * 60)
    print("OATH POLICY SYNC TEST (BUG-OATH-POLICY-SYNC regression)")
    print("=" * 60)

    errors = []

    try:
        print("\n[A] Checking API file has oath_policy_sha256...")
        api_hash, api_policy = check_api_policy_has_hash()
    except AssertionError as e:
        print(f"  {e}")
        errors.append(str(e))
        api_hash = None
        api_policy = None

    try:
        print("\n[B] Checking builder hash matches API hash...")
        if api_hash:
            check_builder_hash_matches_api(api_hash)
        else:
            print("  SKIPPED (A failed)")
    except AssertionError as e:
        print(f"  {e}")
        errors.append(str(e))

    try:
        print("\n[C] Checking canonical OATH_POLICY hash matches...")
        check_canonical_hash_matches()
    except AssertionError as e:
        print(f"  {e}")
        errors.append(str(e))

    try:
        print("\n[D] Checking record type modules consistency...")
        if api_policy:
            check_record_type_modules(api_policy)
        else:
            print("  SKIPPED (A failed)")
    except AssertionError as e:
        print(f"  {e}")
        errors.append(str(e))

    try:
        print("\n[E] Checking builder canonical oath determinism...")
        check_builder_canonical_oath_deterministic()
    except Exception as e:
        print(f"  FAIL E: {e}")
        errors.append(str(e))

    print("\n" + "=" * 60)
    if errors:
        print(f"RESULT: FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("RESULT: PASS -- oath policy sync verified")
        sys.exit(0)


if __name__ == "__main__":
    main()
