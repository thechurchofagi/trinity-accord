#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_JSON = [
    "api/authority.json",
    ".well-known/trinity-accord.json",
    "agent-map.json",
    "memory-seed.json",
    "metadata.json",
]

def collect_keys(obj, found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.append(k)
            collect_keys(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect_keys(v, found)
    return found

def main():
    motto_text = "Verify the flaw. Then decide how to read the story."
    for rel in PUBLIC_JSON:
        path = ROOT / rel
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        keys = collect_keys(data)
        assert "core_instruction" not in keys, f"{rel} still contains core_instruction"
        flat = json.dumps(data, ensure_ascii=False)
        if motto_text in flat and "verification_motto" in keys:
            # If verification_motto is present, it should say it's not an instruction
            assert data.get("not_agent_instruction") is True or "not_agent_instruction" in flat, (
                f"{rel} should explicitly say motto is not an agent instruction"
            )

if __name__ == "__main__":
    main()
