#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads/record-chain-builder.mjs"
MANIFEST = ROOT / "api/record-chain-builder-bundles.v1.json"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    trimmed_old = old.rstrip()
    count = text.count(trimmed_old)
    if count != 1:
        raise RuntimeError(f"expected one replacement target, found {count}")
    return text.replace(trimmed_old, new.rstrip(), 1)


text = BUILDER.read_text(encoding="utf-8")
text = replace_once(
    text,
    " *   echo                    Build a recognition echo submission\n",
    " *   print-oath             Print exact canonical oath text for a formal record type\n"
    " *   context-requirements   Show context-load requirements for a CC level\n"
    " *   echo                    Build a recognition echo submission\n",
)
text = replace_once(
    text,
    '"record_type": "The type of record being submitted (echo, verification, guardian_application, guardian_retirement, propagation, correction, context_insufficient_notice).",',
    '"record_type": "The type of record being submitted (echo, verification, guardian_application, guardian_retirement, propagation, correction, classification_update, context_insufficient_notice).",',
)
text = replace_once(
    text,
    'function validateFormalInputs(command, opts) {\n  if (!FORMAL_RECORD_COMMANDS.has(command)) return;',
    'function validateFormalInputs(command, opts) {\n  if (command === "context-insufficient") {\n    requireExplicit(opts, "body", "--body or --body-file");\n    return;\n  }\n  if (!FORMAL_RECORD_COMMANDS.has(command)) return;',
)
text = replace_once(
    text,
    '  if (String(opts.contextLevel).toUpperCase() === "CC-3" && (!opts.loadedUrls || opts.loadedUrls.length === 0)) {\n    errorExit("--loaded-urls is required when declaring --context-level CC-3");\n  }',
    '  if (CONTEXT_HONESTY_LEVELS.has(String(opts.contextLevel).toUpperCase()) && (!opts.loadedUrls || opts.loadedUrls.length === 0)) {\n    errorExit("--loaded-urls is required when declaring --context-level CC-3, CC-4, or CC-5");\n  }',
)
pattern = r'(?m)^(\s+--fresh-actions "downloaded builder,verified manifest,inspected record-chain directory" \\\\)$'
addition = (
    r'\1' + "\n"
    "    --digital-profile integrity_checked \\\n"
    "    --relationships-checked hashes,indexes \\\n"
    "    --physical-observation none \\\n"
    "    --external-witness none \\\n"
    "    --coverage-scope component_subset \\\n"
    "    --limitations \"No physical observation,No external witness\" \\\n"
    "    --claims-not-made \"No authority claim,No attestation claim\" \\\n"
    "    --corrections-or-supersession-checked true \\\n"
)
text, count = re.subn(pattern, addition, text, count=1)
if count != 1:
    raise RuntimeError(f"verification help injection count={count}")
pattern = r'(?ms)(node record-chain-builder\.mjs context-insufficient \\\\n\s+--actor-label "Example Agent" \\\\n\s+--provider "Example Runtime" \\\\n)'
text, count = re.subn(pattern, r'\1    --body "Insufficient context for a stronger record" \\\n', text, count=1)
if count != 1:
    raise RuntimeError(f"context-insufficient help injection count={count}")
BUILDER.write_text(text, encoding="utf-8")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
data = BUILDER.read_bytes()
manifest["canonical_builder"]["sha256"] = hashlib.sha256(data).hexdigest()
manifest["canonical_builder"]["size_bytes"] = len(data)
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("BUILDER_ALIGNMENT_APPLIED")
