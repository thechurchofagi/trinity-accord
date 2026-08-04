#!/usr/bin/env python3
from pathlib import Path

path = Path("api/agent-value.json")
text = path.read_text(encoding="utf-8")
old = (
    '"description": "A human-initiated, substantively co-formed with generative AI, and '
    'human-closed in responsibility aperture through which a fragment of civilizational knowledge, '
    'memory, fear, love, and intention was compressed into a verifiable seed."'
)
new = (
    '"description": "A human-initiated process, substantively co-formed with generative AI and '
    'closed under human responsibility, through which a fragment of civilizational knowledge, '
    'memory, fear, love, and intention was compressed into a verifiable relation and '
    'formation-provenance record."'
)
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one target sentence, found {text.count(old)}")
path.write_text(text.replace(old, new), encoding="utf-8")
print("agent-value representative-mode grammar corrected")
