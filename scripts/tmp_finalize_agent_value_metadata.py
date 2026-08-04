#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

path = Path("api/agent-value.json")
text = path.read_text(encoding="utf-8")

replacements = {
    '"claim": "human_led_ai_assisted_civilizational_self_archive"':
        '"claim": "human_initiated_co_emergent_human_responsible_local_civilizational_self_archive"',
    '"ai_role": "mirror_shaped_by_human_language_knowledge_culture_history_error_and_hope"':
        '"ai_role": "substantive_generation_recombination_criticism_research_and_structural_contribution_without_sovereign_authorship"',
    '"human_role": "point_of_responsibility_selection_acceptance_anchoring_guardianship"':
        '"human_role": "initiation_sustained_selection_correction_physical_embodiment_chain_publication_canonical_closure_and_guardianship"',
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one occurrence of {old!r}, found {text.count(old)}")
    text = text.replace(old, new)

# Compute the repository's canonical public-metadata digest after the semantic repair.
data = json.loads(text)
without_digest = {k: v for k, v in data.items() if k != "source_digest"}
canonical = json.dumps(without_digest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
text, count = re.subn(
    r'"source_digest": "[0-9a-fA-F]{16}"',
    f'"source_digest": "{digest}"',
    text,
    count=1,
)
if count != 1:
    raise SystemExit("source_digest field not found exactly once")

path.write_text(text, encoding="utf-8")
print(f"agent-value metadata finalized; source_digest={digest}")
