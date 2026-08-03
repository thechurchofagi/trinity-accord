from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "downloads" / "record-chain-builder-core.mjs"
RECOVERY = ROOT / "downloads" / "record-chain-builder-recovery.mjs"
ENTRY = ROOT / "downloads" / "record-chain-builder.mjs"
MANIFEST = ROOT / "api" / "record-chain-builder-bundles.v1.json"
RECOVERY_TEST = ROOT / "tests" / "test_record_chain_submit_recovery.py"
AGENT_TEST = ROOT / "tests" / "test_external_agent_builder_resilience.py"


def sha_size(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


core = CORE.read_text(encoding="utf-8")
anchor = '''const ERROR_HELP_MAP = {
  INVALID_SELF_REPORTED_PROVENANCE: {'''
entries = '''const ERROR_HELP_MAP = {
  DUPLICATE_LOADED_CONTEXT_URL: {
    meaning: "loaded_context_urls contains the same normalized URL more than once.",
    fix: "Trim and deduplicate --loaded-urls, then rebuild and re-sign the submission with the current Builder.",
    help_url: "https://www.trinityaccord.org/docs/record-chain-builder-help/#context-readiness",
  },
  INVALID_LOADED_CONTEXT_URL: {
    meaning: "A loaded_context_urls item is not a valid absolute HTTP or HTTPS URL.",
    fix: "Use complete public http:// or https:// URLs only; remove relative, malformed, credential-bearing, or non-HTTP values, then rebuild and re-sign.",
    help_url: "https://www.trinityaccord.org/docs/record-chain-builder-help/#context-readiness",
  },
  PROVENANCE_DECISION_REQUEST_PARTY_MISMATCH: {
    meaning: "who_decided_to_create_this_record conflicts with the declared requesting_party_type.",
    fix: "Align --record-decision and --requesting-party-type with what actually happened. Do not infer one field from the other; rebuild and re-sign.",
    help_url: "https://www.trinityaccord.org/docs/record-chain-builder-help/#provenance",
  },
  PROVENANCE_REQUEST_FLAG_MISMATCH: {
    meaning: "The requesting-party type and requested-by provenance booleans are internally inconsistent.",
    fix: "Rebuild with the current Builder using the actual requester type and decision source. Do not hand-edit the signed record_draft.",
    help_url: "https://www.trinityaccord.org/docs/record-chain-builder-help/#provenance",
  },
  INVALID_SELF_REPORTED_PROVENANCE: {'''
core = replace_once(core, anchor, entries, "active diagnostic help insertion")
CORE.write_text(core, encoding="utf-8")

core_sha, core_size = sha_size(CORE)
recovery = RECOVERY.read_text(encoding="utf-8")
recovery, sha_count = re.subn(
    r'const CORE_SHA256 = "[0-9a-f]{64}";',
    f'const CORE_SHA256 = "{core_sha}";',
    recovery,
    count=1,
)
recovery, size_count = re.subn(
    r'const CORE_SIZE_BYTES = [0-9]+;',
    f'const CORE_SIZE_BYTES = {core_size};',
    recovery,
    count=1,
)
if sha_count != 1 or size_count != 1:
    raise SystemExit(f"recovery core pin update failed: sha={sha_count}, size={size_count}")
RECOVERY.write_text(recovery, encoding="utf-8")

entry_sha, entry_size = sha_size(ENTRY)
recovery_sha, recovery_size = sha_size(RECOVERY)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
canonical = manifest["canonical_builder"]
canonical["sha256"] = entry_sha
canonical["size_bytes"] = entry_size
canonical["recovery_wrapper"]["sha256"] = recovery_sha
canonical["recovery_wrapper"]["size_bytes"] = recovery_size
canonical["core"]["sha256"] = core_sha
canonical["core"]["size_bytes"] = core_size
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

text = RECOVERY_TEST.read_text(encoding="utf-8")
text, sha_count = re.subn(
    r'CORE_SHA256 = "[0-9a-f]{64}"',
    f'CORE_SHA256 = "{core_sha}"',
    text,
    count=1,
)
text, size_count = re.subn(
    r'CORE_SIZE_BYTES = [0-9]+',
    f'CORE_SIZE_BYTES = {core_size}',
    text,
    count=1,
)
if sha_count != 1 or size_count != 1:
    raise SystemExit(f"test core pin update failed: sha={sha_count}, size={size_count}")
RECOVERY_TEST.write_text(text, encoding="utf-8")

agent_test = AGENT_TEST.read_text(encoding="utf-8")
marker = "def test_error_help_covers_active_external_agent_diagnostics():"
if marker in agent_test:
    raise SystemExit("diagnostic help regression test already present")
agent_test += '''\n\ndef test_error_help_covers_active_external_agent_diagnostics():
    for code in [
        "DUPLICATE_LOADED_CONTEXT_URL",
        "INVALID_LOADED_CONTEXT_URL",
        "PROVENANCE_DECISION_REQUEST_PARTY_MISMATCH",
        "PROVENANCE_REQUEST_FLAG_MISMATCH",
    ]:
        result = run_node("error-help", "--code", code)
        assert result.returncode == 0, result.stdout + result.stderr
        assert f"Error Code: {code}" in result.stdout
        assert "Meaning:" in result.stdout
        assert "Fix:" in result.stdout
        assert "Help:" in result.stdout
'''
AGENT_TEST.write_text(agent_test, encoding="utf-8")

print(json.dumps({
    "entry": {"sha256": entry_sha, "size": entry_size},
    "recovery": {"sha256": recovery_sha, "size": recovery_size},
    "core": {"sha256": core_sha, "size": core_size},
}, indent=2))
