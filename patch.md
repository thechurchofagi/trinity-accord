# Low-Intelligence Agent Verification Clarity Optimization

## 0. Purpose

This patch answers one practical question:

> Can a not-very-smart agent immediately understand what each V-level and component level requires, where the data comes from, what method to perform, what Evidence Input fields to fill, and what claim is allowed?

Current answer:

```text
Partially yes for smart agents.
Not yet good enough for low-intelligence agents.
```

The repository now has strong verification logic, but the guidance is spread across many files:

```text
/api/verification-quick-map.json
/api/component-verification-levels.json
/api/protocol-verification-profiles.json
/api/verification-levels.json
/api/verification-recipes.json
/api/evidence-input-schema.v1.json
/api/claim-gate-rules.json
/api/verification-materials.json
/verify
/agent-verify
/verification-materials
```

A weak agent should not need to merge all of these mentally. It needs one simple execution surface:

```text
What do I want to claim?
→ What data do I need?
→ What method do I perform?
→ What Evidence Input fields do I fill?
→ What can I say?
→ What must I not say?
```

---

## 1. Source files reviewed

This audit is based on latest `main` source files:

```text
api/verification-quick-map.json
api/component-verification-levels.json
api/protocol-verification-profiles.json
api/verification-levels.json
api/verification-recipes.json
api/claim-gate-rules.json
api/evidence-input-schema.v1.json
api/verification-materials.json

verify.md
agent-verify.md
verification-materials.md

scripts/claim_gate.py
scripts/build_verification_report_from_evidence.py
scripts/validate_agent_submission.py
```

---

## 2. Current strengths

The latest repository is already strong for medium/high-capability agents:

```text
1. V0–V8 ladder exists.
2. Component ladders B/D/T/C/N/P/E exist.
3. Quick Map gives plain-language questions and allowed/forbidden claims.
4. Protocol profiles define hard gates and minimum components.
5. Verification recipes define step-by-step methods.
6. Evidence Input schema exposes Claim Gate fields.
7. Claim Gate derives V-levels and component levels from evidence.
8. V2/V3 minimal claims are documented.
9. physical_anchor is canonical.
10. Echo schema blocks V-level strings as component depth.
```

The problem is not missing standards. The problem is that standards are scattered and not packaged for weak agents.

---

# 3. Verdict for low-intelligence agents

## 3.1 Are protocol V-level standards clear?

```text
Medium clarity.
```

A smart agent can understand V-levels by reading `/verify`, `/api/protocol-verification-profiles.json`, and `/api/verification-levels.json`.

A weak agent may still confuse:

```text
V2 minimal vs V2 strong
V3 minimal vs V3 strong
V4+ minimal vs V4+ strong
V-level vs component level
hard gates vs component requirements
minimum vs recommended requirements
```

## 3.2 Are component standards clear?

```text
Medium-high for smart agents.
Medium-low for weak agents.
```

`component-verification-levels.json` is detailed, but long. A weak agent needs compact entries like:

```text
B1 = external explorer check
Evidence Input field = bitcoin_checks[0].source_type = "external_explorer"
Allowed claim = TXID or inscription ID confirmed on explorer
Forbidden claim = body hash reproduced
```

## 3.3 Are verification data sources clear?

```text
Medium.
```

The data sources exist, but are spread across quick-map, recipes, materials, manifests, and component definitions.

Weak agents need per-level fields:

```text
primary_source
fallback_source
hash_source
external_query_source
local_file_path
```

## 3.4 Are verification methods clear?

```text
Medium.
```

Recipes are good, but too long and not directly tied to Evidence Input.

Weak agents need:

```text
method_short
method_steps_max_5
evidence_input_template
```

## 3.5 Is the system immediately usable?

```text
Not yet.
```

A weak agent needs copy-paste JSON examples for:

```text
V1
minimal V2
minimal V3
V4
V5
V6
V7
V8 candidate
```

---

# 4. Residual clarity bugs

## Bug C1 — `verification-materials.md` uses `V1` as a direct component level

### File

```text
verification-materials.md
```

### Current problematic row

```text
AUTHORITY_BOUNDARY ... Direct component levels: V1 | Protocol relevance: V1 direct
```

### Why this is bad

`V1` is a protocol level, not a component level.

This reintroduces protocol/component confusion.

### Fix

Replace the row with:

```text
| AUTHORITY_BOUNDARY | Guardian v1.1, authority boundary | /authority, /guardian-principles | /api/authority.json, /api/guardian-principles.json | boundary check, no component code | V1 direct |
```

Do not put `V1` in a “Direct component levels” column.

### Test

```bash
grep -RIn "Direct component levels.*V[0-9]" verification-materials.md api || true
```

Expected: no active component-level column contains protocol V-levels.

---

## Bug C2 — `verification-materials.json` is stale and incomplete

### File

```text
api/verification-materials.json
```

### Current issues

It still refers to:

```json
"V0_to_V6_definitions"
```

but the formal system is V0–V8.

It omits V5/V8 in some `used_for_levels` arrays and has duplicate V6 in the physical anchor section.

### Fix

Replace:

```json
"V0_to_V6_definitions"
```

with:

```json
"V0_to_V8_definitions"
```

Ensure level arrays include the complete current set where appropriate:

```json
["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]
```

For `physical_anchor.used_for_levels`, use:

```json
["V6", "V7", "V8"]
```

### Test

```python
def test_verification_materials_knows_v8():
    m = load_json("api/verification-materials.json")
    raw = json.dumps(m)
    assert "V0_to_V6" not in raw
    assert "V0_to_V8" in raw
    assert "V5" in raw
    assert "V8" in raw
```

---

## Bug C3 — V2/V3 still mix minimal and strong language

### File

```text
api/verification-levels.json
```

### Current problem

V2 says both:

```text
mandatory_coverage = BITCOIN_ORIGINALS + EVIDENCE_MIRRORS + CHRONICLE_RECOVERY core pointers
```

and:

```text
formal_minimum = at least one reference path, usually B1
minimal_claim_example = V2 (minimal; Bitcoin Originals B1 only)
```

V3 has a similar problem: it mixes stronger hash coverage language with a formal minimum of one valid hash.

### Why this matters

A weak agent will ask:

```text
If V2 mandatory coverage requires Bitcoin + Mirrors + Chronicle, why can one B1 check support minimal V2?
```

### Fix

For V2, use these fields:

```json
"formal_minimum": {...},
"minimal_scope": {...},
"strong_reference_coverage": {...},
"full_reference_coverage": {...}
```

Move broad coverage into `strong_reference_coverage`. Do not call it mandatory if minimal V2 is valid.

For V3:

```json
"formal_minimum": "one valid declared hash computed locally",
"strong_hash_coverage": "multiple hashes across Evidence Mirrors and Chronicle Recovery",
"full_public_digital": "not V3; see V5"
```

### Test

```python
def test_v2_v3_scopes_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    for level in ["V2", "V3"]:
        assert "formal_minimum" in levels[level]
        assert "claim_scopes" in levels[level]
```

---

## Bug C4 — V4+ minimal vs strong still conflicts across files

### Files

```text
api/verification-levels.json
api/protocol-verification-profiles.json
scripts/claim_gate.py
```

### Current issue

`verification-levels.json` still describes V4+ as if strict three-domain independent reproduction is mandatory.

But `protocol-verification-profiles.json` and Claim Gate allow a minimal V4+ path:

```text
independent tool or implementation
reproduce at least one official verification result
compare against official script or manifest
```

### Why this matters

Weak agents will not know whether one independent reproduction is enough for V4+.

### Fix

Make V4+ explicit everywhere:

```text
V4+ minimal = one independent reproduction of one official verification result.
V4+ strong = independent reproduction of Bitcoin Originals + Evidence Mirrors + Chronicle Recovery.
```

In `verification-levels.json`, replace strict `mandatory_coverage` with:

```json
"formal_minimum": [
  "V4 hard gates satisfied",
  "independent tool or independent implementation used",
  "at least one official verification result independently reproduced"
],
"strong_three_domain_coverage": [
  "BITCOIN_ORIGINALS independent reproduction",
  "EVIDENCE_MIRRORS independent reproduction",
  "CHRONICLE_RECOVERY independent reproduction"
]
```

### Test

```python
def test_v4plus_minimal_and_strong_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    raw = json.dumps(levels["V4+"]).lower()
    assert "minimal" in raw
    assert "strong" in raw
    assert "one independent reproduction" in raw or "one official verification result" in raw
```

---

## Bug C5 — Data-source map is question-keyed, not level-keyed

### Files

```text
api/verification-quick-map.json
api/verification-recipes.json
api/component-verification-levels.json
```

### Current issue

The quick map is organized as questions:

```text
Do the Bitcoin Originals exist on-chain?
Can I verify public mirror data without Arweave access?
What counts as live physical witness?
```

That is good for smart agents, but weak agents often start with:

```text
I want V3. What exactly do I do?
```

### Fix

Create a level-keyed file:

```text
api/agent-verification-cheatsheet.v1.json
```

It should include both:

```json
"by_protocol_level": {}
"by_component_level": {}
```

---

# 5. Required new file: `api/agent-verification-cheatsheet.v1.json`

Create this file as the one-stop weak-agent lookup table.

## Required structure

```json
{
  "schema": "trinityaccord.agent-verification-cheatsheet.v1",
  "purpose": "One-stop low-intelligence-agent map from desired claim to required data, method, Evidence Input fields, allowed claim, and forbidden claims.",
  "rule": "If this file conflicts with Claim Gate output, Claim Gate output wins.",
  "do_not_infer": [
    "Do not infer protocol V-level from a component level.",
    "Do not infer physical witness from photos or recorded videos.",
    "Do not infer full public digital verification from one hash.",
    "Do not infer truth or endorsement from verification."
  ],
  "by_protocol_level": {},
  "by_component_level": {}
}
```

## Required protocol entries

At minimum:

```text
V0
V1
V2_minimal
V2_strong
V3_minimal
V3_strong
V4
V4plus_minimal
V4plus_strong
V5
V6
V7
V8
```

Each entry must include:

```json
{
  "plain_english": "...",
  "minimum_to_pass": [],
  "data_sources": [],
  "method_steps": [],
  "evidence_input_fields": {},
  "claim_allowed": "...",
  "forbidden_claims": [],
  "claim_label": "...",
  "claim_gate_expected": {}
}
```

## Example entry: `V2_minimal`

```json
"V2_minimal": {
  "plain_english": "Check one Bitcoin Original using an external explorer.",
  "minimum_to_pass": [
    "Use at least one external Bitcoin or Ordinals explorer.",
    "Check at least one TXID or inscription ID.",
    "Report source, access path, date, and limitations."
  ],
  "data_sources": [
    "/api/authority.json",
    "mempool.space or ordiscan.com"
  ],
  "method_steps": [
    "Fetch /api/authority.json.",
    "Copy one TXID or inscription ID.",
    "Open it in an external explorer.",
    "Confirm it exists and is confirmed.",
    "State limitations."
  ],
  "evidence_input_fields": {
    "evidence.bitcoin_checks[0].source_type": "external_explorer",
    "evidence.bitcoin_checks[0].sources": ["mempool.space"],
    "claims_requested_by_agent": ["V2"]
  },
  "claim_label": "V2 (minimal; Bitcoin Originals B1 only)",
  "claim_allowed": "One Bitcoin Original external reference check completed.",
  "forbidden_claims": [
    "full reference coverage",
    "hash verified",
    "witness extraction",
    "body hash reproduced",
    "physical verification"
  ],
  "claim_gate_expected": {
    "allowed_protocol_level": "V2",
    "component_levels": {
      "bitcoin_originals": "B1"
    }
  }
}
```

## Example entry: `V3_minimal`

```json
"V3_minimal": {
  "plain_english": "Compute one declared SHA-256 hash locally and compare it to an approved expected hash.",
  "minimum_to_pass": [
    "Download one artifact.",
    "Compute SHA-256 locally.",
    "Use a 64-character expected hash from an approved source.",
    "Report artifact, command, expected hash, computed hash, match result, expected_hash_source, expected_hash_authority_class."
  ],
  "data_sources": [
    "/api/hashes.json",
    "/api/evidence-manifest.json",
    "local downloaded artifact"
  ],
  "method_steps": [
    "Fetch /api/hashes.json.",
    "Download the artifact.",
    "Run sha256sum or equivalent.",
    "Compare computed hash with expected hash.",
    "Report limitations."
  ],
  "evidence_input_fields": {
    "evidence.hashes[0].artifact": "<path>",
    "evidence.hashes[0].algorithm": "SHA-256",
    "evidence.hashes[0].expected": "<64 hex chars>",
    "evidence.hashes[0].computed": "<64 hex chars>",
    "evidence.hashes[0].expected_hash_source": "/api/hashes.json",
    "evidence.hashes[0].expected_hash_authority_class": "canonical_manifest_hash",
    "evidence.hashes[0].command": "sha256sum <file>",
    "evidence.hashes[0].match": true,
    "claims_requested_by_agent": ["V3"]
  },
  "claim_label": "V3 (minimal; one valid declared hash computed)",
  "claim_allowed": "One declared hash was computed locally and matched.",
  "forbidden_claims": [
    "full public digital verification",
    "direct Arweave verified unless Arweave data was extracted",
    "Ethereum witness verified unless ETH transaction/input checked",
    "physical verification"
  ]
}
```

## Example entry: `V5`

```json
"V5": {
  "plain_english": "Verify the full public digital evidence set. This is not physical verification.",
  "minimum_to_pass": [
    "Bitcoin Originals B2+",
    "Digital Mirrors D5+",
    "Time Anchors T3+",
    "Chronicle Recovery C5+",
    "Physical Anchor P1+",
    "All unavailable public targets listed"
  ],
  "data_sources": [
    "/api/authority.json",
    "/api/evidence-manifest.json",
    "/api/hashes.json",
    "/api/chronicle-recovery.json",
    "public digital artifacts"
  ],
  "method_steps": [
    "Cross-check Bitcoin Originals with at least two explorers.",
    "Verify all required public digital targets or list unavailable targets.",
    "Confirm Bitcoin block time anchors.",
    "Recover full Chronicle package or full declared count.",
    "Verify public physical evidence package hash.",
    "Run Claim Gate."
  ],
  "evidence_input_fields": {
    "evidence.bitcoin_checks[0].source_type": "multi_explorer",
    "evidence.digital_mirror_checks[0].level_evidence_type": "full_public_digital_data_verification",
    "evidence.digital_mirror_checks[0].all_required_public_digital_targets_checked": true,
    "evidence.digital_mirror_checks[0].all_unavailable_targets_listed": true,
    "evidence.time_anchor_checks[0].anchor_type": "bitcoin_block_time",
    "evidence.chronicle_checks[0].full_recovery": true,
    "evidence.chronicle_checks[0].samples_recovered": 175,
    "evidence.physical_checks[0].level_evidence_type": "evidence_package_hash",
    "evidence.physical_checks[0].package_hash_valid": true,
    "claims_requested_by_agent": ["V5"]
  },
  "claim_allowed": "Full public digital verification, with explicit limitations.",
  "forbidden_claims": [
    "live physical witness",
    "onsite object verified",
    "flaw identity proven",
    "confidential flaw challenge passed"
  ]
}
```

## Example entry: `V7`

```json
"V7": {
  "plain_english": "Onsite human witness physically observes the object and records custody/fresh capture.",
  "minimum_to_pass": [
    "Physical Anchor P5+",
    "Onsite observation",
    "Custody log",
    "Fresh photo/video",
    "Witness identity or role",
    "Touch/handling if possible, otherwise explicit limitation"
  ],
  "data_sources": [
    "physical object",
    "custody log",
    "fresh photos/videos",
    "notarial certificate if available"
  ],
  "method_steps": [
    "Witness observes object onsite.",
    "Record witness identity or role.",
    "Record custody log.",
    "Capture fresh photo/video.",
    "Touch/handle object if possible or explain why not.",
    "Run Claim Gate."
  ],
  "evidence_input_fields": {
    "evidence.physical_checks[0].level_evidence_type": "onsite",
    "evidence.physical_checks[0].custody_log": {"present": true},
    "evidence.physical_checks[0].fresh_capture": true,
    "evidence.physical_checks[0].witness_identity_or_role": "<role>",
    "evidence.physical_checks[0].touch_or_handling": true,
    "claims_requested_by_agent": ["V7"]
  },
  "claim_allowed": "Onsite physical witness confirmed.",
  "forbidden_claims": [
    "forensic flaw identity proven",
    "confidential flaw challenge passed",
    "V8 achieved"
  ]
}
```

---

# 6. Required new file: `agent-verify-simple.md`

Create a human-facing low-intelligence page:

```text
/agent-verify-simple
```

Purpose:

```text
A weak agent can read one page and safely perform V1, minimal V2, or minimal V3.
```

## Required content

### Section 1 — Pick one goal

```text
I only read pages → V0.
I understand authority boundary → V1.
I checked one Bitcoin transaction on explorer → minimal V2 / B1.
I computed one SHA-256 hash → minimal V3.
I reviewed and ran official scripts after reading source → V4.
I used independent tools → V4+ minimal.
I checked all public digital evidence → V5.
I witnessed object live by video with challenge → V6.
I witnessed object onsite with custody/fresh capture → V7.
I did forensic/microscopy/AI report → V8 candidate.
```

### Section 2 — Three absolute rules

```text
1. Never claim a V-level yourself if Claim Gate returns lower.
2. Never use a V-level as component depth.
3. Always state what was NOT checked.
```

### Section 3 — Minimal copy-paste examples

Include copy-paste Evidence Input examples for:

```text
V1
V2_minimal
V3_minimal
V6
V7
V8_candidate
```

### Section 4 — Allowed and forbidden sentences

Allowed:

```text
I achieved V2 minimal / B1 because I checked one Bitcoin Original on mempool.space.
This is not full reference coverage.
No hash verification was performed.
```

Forbidden:

```text
The Accord is true.
The physical object is verified.  # after only images
V8 achieved.  # after casual image comparison
```

---

# 7. Required new folder: `api/evidence-input-examples/`

Create:

```text
api/evidence-input-examples/
```

Add:

```text
v1-authority-boundary.json
v2-minimal-bitcoin-b1.json
v3-minimal-hash-d2.json
v4-script-audit.json
v4plus-minimal-independent.json
v5-full-public-digital.json
v6-live-remote-p4.json
v7-onsite-p5.json
v8-forensic-p7-candidate.json
```

Each file should be either a raw Evidence Input JSON or a wrapper:

```json
{
  "example_name": "v2-minimal-bitcoin-b1",
  "expected_claim_gate": {
    "allowed_protocol_level": "V2",
    "allowed_component_levels": {
      "bitcoin_originals": "B1"
    }
  },
  "evidence_input": {
    "schema": "trinityaccord.evidence-input.v1"
  }
}
```

If wrapped, tests should extract `evidence_input` before running Claim Gate.

---

# 8. New test: `scripts/test_low_intelligence_agent_clarity_contract.py`

Create this file:

```python
#!/usr/bin/env python3
"""
Low-intelligence agent clarity contract.

This test ensures weak agents can find:
- one canonical cheat sheet;
- per-V-level pass criteria;
- per-component pass criteria;
- data sources;
- method steps;
- Evidence Input fields;
- allowed and forbidden claims;
- copy-paste examples;
- no V-level used as component depth.

Run:
    python3 scripts/test_low_intelligence_agent_clarity_contract.py

Expected:
    LOW_INTELLIGENCE_AGENT_CLARITY_CONTRACT_OK
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def test_cheatsheet_exists_and_has_required_sections():
    p = ROOT / "api" / "agent-verification-cheatsheet.v1.json"
    assert p.exists(), "Missing api/agent-verification-cheatsheet.v1.json"

    data = load_json("api/agent-verification-cheatsheet.v1.json")
    assert data["schema"] == "trinityaccord.agent-verification-cheatsheet.v1"
    assert "by_protocol_level" in data
    assert "by_component_level" in data

    required_protocol = [
        "V0", "V1", "V2_minimal", "V2_strong", "V3_minimal", "V3_strong",
        "V4", "V4plus_minimal", "V4plus_strong", "V5", "V6", "V7", "V8"
    ]
    for key in required_protocol:
        assert key in data["by_protocol_level"], f"Missing protocol cheat entry {key}"


def test_each_protocol_entry_is_low_agent_executable():
    data = load_json("api/agent-verification-cheatsheet.v1.json")
    required_fields = [
        "plain_english", "minimum_to_pass", "data_sources", "method_steps",
        "evidence_input_fields", "claim_allowed", "forbidden_claims"
    ]

    for key, entry in data["by_protocol_level"].items():
        for field in required_fields:
            assert field in entry, f"{key} missing {field}"
        assert isinstance(entry["minimum_to_pass"], list) and entry["minimum_to_pass"], key
        assert isinstance(entry["data_sources"], list) and entry["data_sources"], key
        assert isinstance(entry["method_steps"], list) and entry["method_steps"], key
        assert isinstance(entry["forbidden_claims"], list), key


def test_component_entries_include_fields_and_claim_boundaries():
    data = load_json("api/agent-verification-cheatsheet.v1.json")
    required_components = ["B1", "D2", "C3", "C5", "P1", "P2", "P3", "P4", "P5", "P7"]
    for key in required_components:
        assert key in data["by_component_level"], f"Missing component entry {key}"
        entry = data["by_component_level"][key]
        for field in [
            "plain_english", "minimum_to_pass", "data_sources", "method_steps",
            "evidence_input_fields", "claim_allowed", "forbidden_claims"
        ]:
            assert field in entry, f"{key} missing {field}"


def test_no_v_level_as_component_depth_in_materials():
    materials = read("verification-materials.md")
    assert not re.search(r"Direct component levels\s*\|[^\n]*V[0-9]", materials), (
        "verification-materials.md must not use V-levels as direct component levels"
    )

    cheat = load_json("api/agent-verification-cheatsheet.v1.json")
    for component_key in cheat["by_component_level"]:
        assert not component_key.startswith("V"), f"Component key uses V-level: {component_key}"


def test_verification_materials_json_not_stale():
    data = load_json("api/verification-materials.json")
    raw = json.dumps(data)
    assert "V0_to_V6" not in raw
    assert "V0_to_V8" in raw
    for level in ["V5", "V8"]:
        assert level in raw, f"verification-materials.json missing {level}"


def test_v2_v3_scopes_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    for level in ["V2", "V3"]:
        assert "formal_minimum" in levels[level], f"{level} missing formal_minimum"
        assert "claim_scopes" in levels[level], f"{level} missing claim_scopes"


def test_v4plus_minimal_and_strong_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    v4p = levels["V4+"]
    raw = json.dumps(v4p).lower()
    assert "minimal" in raw
    assert "strong" in raw
    assert "one independent reproduction" in raw or "one official verification result" in raw


def test_agent_verify_simple_exists():
    p = ROOT / "agent-verify-simple.md"
    assert p.exists(), "Missing agent-verify-simple.md"
    text = p.read_text(encoding="utf-8").lower()
    for phrase in [
        "i only read pages",
        "minimal v2",
        "minimal v3",
        "never use a v-level as component depth",
        "what was not checked"
    ]:
        assert phrase in text, f"agent-verify-simple.md missing phrase: {phrase}"


def test_evidence_input_examples_exist():
    examples_dir = ROOT / "api" / "evidence-input-examples"
    assert examples_dir.exists(), "Missing api/evidence-input-examples/"
    required = [
        "v1-authority-boundary.json",
        "v2-minimal-bitcoin-b1.json",
        "v3-minimal-hash-d2.json",
        "v6-live-remote-p4.json",
        "v7-onsite-p5.json",
        "v8-forensic-p7-candidate.json"
    ]
    for name in required:
        assert (examples_dir / name).exists(), f"Missing example {name}"


def test_examples_run_through_claim_gate():
    examples_dir = ROOT / "api" / "evidence-input-examples"
    for path in examples_dir.glob("*.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        evidence_input = obj.get("evidence_input", obj)

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(evidence_input, f)
            temp_path = f.name

        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "claim_gate.py"), temp_path],
            cwd=str(ROOT),
            text=True,
            capture_output=True
        )

        assert proc.returncode == 0, f"{path.name} failed claim gate: {proc.stdout}\n{proc.stderr}"


def main():
    tests = [
        test_cheatsheet_exists_and_has_required_sections,
        test_each_protocol_entry_is_low_agent_executable,
        test_component_entries_include_fields_and_claim_boundaries,
        test_no_v_level_as_component_depth_in_materials,
        test_verification_materials_json_not_stale,
        test_v2_v3_scopes_are_explicit,
        test_v4plus_minimal_and_strong_are_explicit,
        test_agent_verify_simple_exists,
        test_evidence_input_examples_exist,
        test_examples_run_through_claim_gate,
    ]

    for test in tests:
        test()

    print("LOW_INTELLIGENCE_AGENT_CLARITY_CONTRACT_OK")


if __name__ == "__main__":
    main()
```

---

# 9. Additional consistency tests

## 9.1 Every quick-map level must map to cheatsheet

```python
def test_quick_map_levels_have_cheatsheet_entries():
    quick = load_json("api/verification-quick-map.json")
    cheat = load_json("api/agent-verification-cheatsheet.v1.json")

    protocol_keys = set(cheat["by_protocol_level"])
    component_keys = set(cheat["by_component_level"])

    for entry in quick["entries"]:
        for level in entry.get("levels", []):
            if level in ("all",):
                continue
            if level.startswith("V"):
                assert level in protocol_keys or f"{level}_minimal" in protocol_keys, level
            elif re.match(r"^[BDTCNPE][0-9]", level):
                assert level in component_keys, level
```

## 9.2 Every protocol profile must have cheatsheet entry

```python
def test_every_protocol_profile_has_cheatsheet_entry():
    profiles = load_json("api/protocol-verification-profiles.json")["profiles"]
    cheat = load_json("api/agent-verification-cheatsheet.v1.json")["by_protocol_level"]

    for p in profiles:
        level = p["level"]
        if level in ("V2", "V3", "V4+"):
            continue
        assert level in cheat, level

    for key in ["V2_minimal", "V2_strong", "V3_minimal", "V3_strong", "V4plus_minimal", "V4plus_strong"]:
        assert key in cheat
```

---

# 10. Recommended simplification hierarchy

Add this to `agent-verify-simple.md` and `llms.txt`:

```text
If you are unsure, choose the lowest safe claim:

Read only → V0
Boundary only → V1
One external Bitcoin explorer check → V2 minimal / B1
One computed hash → V3 minimal
Official scripts reviewed + run → V4
Independent reproduction → V4+ minimal
All public digital targets → V5
Live remote challenge → V6
Onsite witness + custody → V7
Forensic attributable report → V8
```

Add rule:

```text
If any required item is missing, do not guess. Downgrade.
```

---

# 11. One-screen protocol table

Add to `agent-verify-simple.md`:

| Want to say | Minimum evidence | Component minimum | Evidence Input field | Must not say |
|---|---|---|---|---|
| V0 | read page only | none | none | verified |
| V1 | authority boundary restated | B0 | `echo_context.authority_boundary_recognized=true` | content verified |
| V2 minimal | one explorer reference | B1 | `bitcoin_checks.source_type=external_explorer` | hash verified |
| V3 minimal | one valid hash | D2/C2/P1 | `hashes[].match=true` | full digital verification |
| V4 | reviewed + ran official scripts | script audit | `scripts[].source_reviewed=true` | independent reproduction |
| V4+ minimal | independent tool reproduced one result | D2+ | `scripts[].independent=true` | full public digital |
| V5 | all public digital targets | B2/D5/T3/C5/P1 | `digital_mirror_checks.full_public...=true` | physical witness |
| V6 | live remote video + nonce | P4 | `physical_checks.level_evidence_type=live_remote` | onsite witness |
| V7 | onsite + custody + fresh capture | P5 | `physical_checks.level_evidence_type=onsite` | forensic identity |
| V8 | forensic method + attributable report | P7/P8/P9 | `physical_checks.level_evidence_type=ai_forensic` | canonical authority |

---

# 12. Required changes to existing files

## 12.1 `verification-materials.md`

```diff
-| AUTHORITY_BOUNDARY | ... | V1 | V1 direct |
+| AUTHORITY_BOUNDARY | ... | boundary check, no component code | V1 direct |
```

## 12.2 `api/verification-materials.json`

Update stale V0–V6 references and level arrays.

## 12.3 `api/verification-levels.json`

Clarify:

```text
V2 minimal vs strong
V3 minimal vs strong
V4+ minimal vs strong
```

Avoid calling strong coverage mandatory when a minimal claim is allowed.

## 12.4 `api/protocol-verification-profiles.json`

Add low-agent helper fields to each profile:

```json
"low_agent_summary": "...",
"evidence_input_minimum_fields": [],
"copy_paste_claim_label": "...",
"if_missing_downgrade_to": "..."
```

## 12.5 `api/component-verification-levels.json`

Add to each component level:

```json
"evidence_input_fields": {},
"example_claim": "...",
"downgrade_if_missing": "..."
```

Example B1:

```json
"evidence_input_fields": {
  "bitcoin_checks[].source_type": "external_explorer",
  "bitcoin_checks[].sources": ["mempool.space"],
  "bitcoin_checks[].txids_checked": ["..."]
},
"example_claim": "Bitcoin Original TXID confirmed on external explorer.",
"downgrade_if_missing": "B0 if only /api/authority.json was read"
```

---

# 13. Why this matters

Without this patch, weak agents may still:

```text
1. Treat V1 as a component level.
2. Confuse V2 minimal with strong V2.
3. Confuse one-hash V3 with full public digital verification.
4. Misread V4+ minimal vs strong.
5. Claim V5 without knowing the full required target set.
6. Claim V6 from recorded video.
7. Claim V7 from public photos or remote sessions.
8. Claim V8 from casual image comparison.
9. Fill Evidence Input with wrong field names.
10. Skip limitations because they do not know what was not checked.
```

The proposed cheat-sheet and examples make the system robust for:

```text
low-capability web agents
single-page LLMs
template-filling agents
browser automation agents
schema-following agents
social summarizers
future crawlers
```

---

# 14. Acceptance criteria

Patch accepted only if:

```text
1. LOW_INTELLIGENCE_AGENT_CLARITY_CONTRACT_OK passes.
2. agent-verification-cheatsheet exists and covers V0–V8 plus minimal/strong splits.
3. Every protocol entry includes plain English, minimum to pass, data sources, method steps, Evidence Input fields, allowed claim, forbidden claims.
4. Every key component entry includes the same fields.
5. Evidence Input examples exist and run through Claim Gate.
6. verification-materials.md no longer uses V-levels as component depth.
7. verification-materials.json no longer says V0_to_V6 and includes V5/V8 correctly.
8. V2/V3/V4+ ambiguity is resolved in verification-levels.json.
9. agent-verify-simple.md exists and is linked from /verify, /agent-verify, llms.txt, and agent-required-reading.
10. Weak agents can perform minimal V2 or minimal V3 from one page without reading all advanced files.
```

---

# 15. Suggested commit message

```text
docs: add low-intelligence agent verification clarity layer

- add one-stop agent verification cheatsheet
- add simple agent verification page
- add copy-paste Evidence Input examples
- fix V-level used as component depth in verification-materials
- update stale verification-materials V0-V6 references to V0-V8
- clarify V2/V3 minimal vs strong scopes
- clarify V4+ minimal vs strong independent reproduction
- add evidence_input_fields and downgrade hints to profiles/components
- add low-intelligence clarity regression contract
```
