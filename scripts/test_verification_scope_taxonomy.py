#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def find_level_entry(data, level):
    if isinstance(data, dict):
        if data.get("level") == level or data.get("id") == level:
            return data
        for key in ("levels", "profiles", "verification_levels", "protocol_levels"):
            val = data.get(key)
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and (item.get("level") == level or item.get("id") == level):
                        return item
            if isinstance(val, dict) and level in val:
                return val[level]
        for val in data.values():
            if isinstance(val, (dict, list)):
                found = find_level_entry(val, level)
                if found:
                    return found
    elif isinstance(data, list):
        for item in data:
            found = find_level_entry(item, level)
            if found:
                return found
    return None

def require_scope(entry, level, minimal_label, strong_label):
    assert entry is not None, f"Missing {level} entry"
    assert entry.get("scope_label_required") is True, f"{level} must require scope labels"

    # Check scope_taxonomy or claim_scopes (both acceptable)
    scope = entry.get("scope_taxonomy") or entry.get("claim_scopes")
    assert isinstance(scope, dict), f"{level} missing scope_taxonomy/claim_scopes"
    assert "minimal" in scope, f"{level} missing minimal scope"
    assert any(k in scope for k in ("strong", "strong_reference_coverage", "strong_hash_coverage")), (
        f"{level} missing strong scope"
    )

    flat = json.dumps(entry, ensure_ascii=False)
    assert minimal_label in flat, f"{level} missing label {minimal_label}"
    assert strong_label in flat, f"{level} missing label {strong_label}"

    ambiguous = entry.get("ambiguous_label_policy", {})
    assert ambiguous.get("new_reports_must_not_use_bare_label") is True, (
        f"{level} must forbid bare labels in new reports"
    )

def main():
    levels = load_json("api/verification-levels.json")
    profiles = load_json("api/protocol-verification-profiles.json")
    rules = load_json("api/claim-gate-rules.json")

    require_scope(find_level_entry(levels, "V2"), "V2", "V2-minimal", "V2-strong")
    require_scope(find_level_entry(levels, "V3"), "V3", "V3-minimal", "V3-strong")

    v2_profile = find_level_entry(profiles, "V2")
    v3_profile = find_level_entry(profiles, "V3")
    assert v2_profile and "V2-minimal" in json.dumps(v2_profile, ensure_ascii=False)
    assert v3_profile and "V3-minimal" in json.dumps(v3_profile, ensure_ascii=False)

    v2_rules = find_level_entry(rules, "V2")
    v3_rules = find_level_entry(rules, "V3")
    assert v2_rules and "V2-minimal" in json.dumps(v2_rules, ensure_ascii=False)
    assert v3_rules and "V3-minimal" in json.dumps(v3_rules, ensure_ascii=False)

    # Prevent old ambiguous sentence from reappearing without scope qualifier.
    text = (ROOT / "api/verification-levels.json").read_text(encoding="utf-8")
    forbidden = "No single component alone is sufficient for V2."
    assert forbidden not in text, (
        "Ambiguous V2 sentence found. It must say this applies to V2-strong only."
    )

if __name__ == "__main__":
    main()
