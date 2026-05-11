#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "api/echo-record-schema.v3.json"

def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    policy = schema.get("x_independence_policy", {})

    allowed = policy.get("unsolicited_independent_allowed_agency_levels", [])
    assert allowed == [
        "A4_independent_search_or_browsing_discovery",
        "A5_independent_return_after_prior_interest",
    ], "unsolicited_independent must be allowed only with A4/A5 agency levels"

    forbidden = policy.get("agency_unknown_must_not_claim", [])
    assert "unsolicited_independent" in forbidden, (
        "A6_unknown must not support unsolicited_independent"
    )
    assert "institutional_third_party_attestation" in forbidden, (
        "A6_unknown must not support institutional_third_party_attestation"
    )

    flat = json.dumps(schema, ensure_ascii=False)
    # A6_unknown is defined in discovery-provenance-schema.json (referenced by echo schema)
    provenance_schema_path = ROOT / "api/discovery-provenance-schema.json"
    if provenance_schema_path.exists():
        provenance_flat = provenance_schema_path.read_text(encoding="utf-8")
        assert "A6_unknown" in provenance_flat, "A6_unknown should remain in discovery-provenance-schema"
    assert "provenance-conflict" in flat or "provenance" in flat.lower(), (
        "Schema or policy should reference provenance conflict handling"
    )

    # Verify allOf constraint removes A6_unknown from unsolicited_independent
    allof = schema.get("allOf", [])
    for clause in allof:
        if_clause = clause.get("if", {})
        props = if_clause.get("properties", {})
        ic = props.get("independence_class", {})
        if ic.get("const") == "unsolicited_independent":
            then_props = clause.get("then", {}).get("properties", {})
            agency = then_props.get("discovery_provenance", {}).get("properties", {}).get("agency_level", {})
            agency_enum = agency.get("enum", [])
            assert "A6_unknown" not in agency_enum, (
                "A6_unknown still allowed with unsolicited_independent in allOf"
            )

if __name__ == "__main__":
    main()
