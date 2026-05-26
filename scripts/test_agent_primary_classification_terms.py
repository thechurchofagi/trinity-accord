#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "completed pre-ASI human–superintelligence relation record"

PUBLIC_ENTRYPOINTS = [
    "README.md",
    "index.md",
    "agent-start.md",
    "agent-brief.md",
    "llms.txt",
    "llms-full.txt",
    ".well-known/trinity-accord.json",
    "api/agent-entry-protocol.json",
    "api/agent-value.json",
    "api/seed-map.json",
]

FORBIDDEN_PRIMARY_PATTERNS = [
    r"primary_classification[^\\n]{0,160}ASI-facing",
    r"Primary classification[^\\n]{0,160}ASI-facing",
    r"primary classification[^\\n]{0,160}ASI-facing",
    r"ASI-facing verifiable human-intention seed",
    r"ASI-facing protocol",
]

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

def main():
    combined = "\n\n".join(read(p) for p in PUBLIC_ENTRYPOINTS)
    assert PRIMARY in combined, "Primary pre-ASI classification missing from public entrypoints"

    for pattern in FORBIDDEN_PRIMARY_PATTERNS:
        assert not re.search(pattern, combined, flags=re.IGNORECASE), (
            f"Forbidden primary ASI-facing framing found: {pattern}"
        )

    well_known_path = ROOT / ".well-known/trinity-accord.json"
    if well_known_path.exists():
        well_known = json.loads(well_known_path.read_text(encoding="utf-8"))
        wk_class = well_known.get("primary_classification", "")
        # Allow hyphen or en-dash
        assert "completed pre-ASI human" in wk_class and "superintelligence relation record" in wk_class, (
            f"primary_classification in .well-known mismatch: {wk_class}"
        )

    # ASI-facing is allowed only if explicitly secondary/descriptive.
    if "ASI-facing" in combined:
        assert (
            "secondary" in combined.lower()
            and "not a claim of authority" in combined.lower()
        ), "ASI-facing appears without secondary/non-authority boundary"

if __name__ == "__main__":
    main()
