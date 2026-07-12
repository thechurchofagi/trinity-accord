#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    p.write_text(text.replace(old, new), encoding="utf-8")


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# Idempotent re-entry after the applicator's first push.
if (ROOT / "scripts/test_gateway_schema_shadow_parity.py").exists():
    print("round6 changes already applied")
    raise SystemExit(0)

# Gateway runtime recovery must use a public, deployable help surface rather
# than nonexistent routes on the Render API host.
app = ROOT / "apps/record_chain_intake_gateway/app.py"
text = app.read_text(encoding="utf-8")
text = text.replace(
    'logger = logging.getLogger("rcg")\n',
    'logger = logging.getLogger("rcg")\n\n'
    '_PUBLIC_RECOVERY_HELP_URL = "https://www.trinityaccord.org/docs/record-chain-builder-help/"\n'
    '_VALIDATION_RECOVERY_URL = _PUBLIC_RECOVERY_HELP_URL + "#validation-errors"\n'
    '_SECURITY_RECOVERY_URL = _PUBLIC_RECOVERY_HELP_URL + "#security-violations"\n',
    1,
)
text = text.replace(
    'helper_url=f"{_GATEWAY_BASE_URL}/docs/security-violations" if _GATEWAY_BASE_URL else None,',
    'helper_url=_SECURITY_RECOVERY_URL,',
)
text = text.replace(
    'helper_url=f"{_GATEWAY_BASE_URL}/docs/validation-errors" if _GATEWAY_BASE_URL else None,',
    'helper_url=_VALIDATION_RECOVERY_URL,',
)
text = text.replace(
    '    "guardian_key_rotation",\n    "propagation",',
    '    "propagation",',
    1,
)
app.write_text(text, encoding="utf-8")

# Eliminate the stale second protocol: app-local schemas are exact mirrors of
# the public canonical schemas.
for public, shadow in [
    ("api/record-chain-submission-schema.v1.json", "apps/record_chain_intake_gateway/schemas/record_chain_submission.schema.json"),
    ("api/record-chain-preflight-response.v1.json", "apps/record_chain_intake_gateway/schemas/preflight_response.schema.json"),
    ("api/record-chain-submit-response.v1.json", "apps/record_chain_intake_gateway/schemas/submit_response.schema.json"),
    ("api/record-chain-server-receipt.v1.json", "apps/record_chain_intake_gateway/schemas/server_receipt.schema.json"),
]:
    (ROOT / shadow).write_bytes((ROOT / public).read_bytes())

# The repository-internal builder must not produce a draft that public intake
# explicitly reserves and rejects.
replace_once(
    "scripts/trinity_record_builder.py",
    "  guardian-key-rotation   Build a guardian key rotation record draft.",
    "  guardian-key-rotation   Reserved; exits without building until transition proof exists.",
)
replace_once(
    "scripts/trinity_record_builder.py",
    '''def build_guardian_key_rotation(args: argparse.Namespace) -> dict[str, Any]:
    draft = base_draft("guardian_key_rotation", args)
    draft["payload"] = {
        "guardian_id": args.guardian_id,
        "old_public_key_sha256": args.old_public_key_sha256,
        "new_public_key_sha256": args.new_public_key_sha256,
        "reason": args.reason or "Scheduled key rotation",
    }
    return draft
''',
    '''def build_guardian_key_rotation(args: argparse.Namespace) -> dict[str, Any]:
    raise SystemExit(
        "guardian_key_rotation is reserved and cannot be built. "
        "The old-key/new-key dual-signature transition protocol is not implemented. "
        "Use guardian_retirement or a new guardian_application as appropriate."
    )
''',
)
replace_once(
    "scripts/trinity_record_builder.py",
    'gkr_p = sub.add_parser("guardian-key-rotation", help="Build a guardian key rotation record draft")',
    'gkr_p = sub.add_parser("guardian-key-rotation", help="Reserved: Guardian key rotation is not currently buildable")',
)

# Clarify that the Python builder document is an internal operator reference,
# and separate current, reserved, and maintenance record types.
replace_once(
    "docs/RECORD_CHAIN_PRIMARY_PATH.md",
    "**Status:** Active (Phase 2 hard cutover — 2026-06-01)",
    "**Status:** Internal operator reference. Public agents must use the zero-clone Builder and Render Gateway.",
)
replace_once(
    "docs/RECORD_CHAIN_PRIMARY_PATH.md",
    "The Trinity Accord record-chain is now the **primary durable record path** for all new submissions.\n\nThe record-chain provides a native, append-only, verifiable ledger for all record types without requiring the Gateway v1 API, GitHub Issues, or external builder scripts.",
    "The Trinity Accord Record-Chain is the primary durable ledger. External agents must not clone the repository or run this internal Python builder; they use `/downloads/record-chain-builder.mjs` and the public Render Gateway.\n\nThis document describes repository-operator tooling and historical maintenance commands. It is not the current public submission contract. The controlling public contract is `/api/record-chain-intake-gateway.v1.json`.",
)
replace_once(
    "docs/RECORD_CHAIN_PRIMARY_PATH.md",
    '''| `echo` | `trinity_record_builder.py echo` | Recognition echo — non-authoritative reception record |
| `verification` | `trinity_record_builder.py verification` | Verification posture (V0–V8) |
| `guardian_application` | `trinity_record_builder.py guardian-application` | Guardian stewardship application |
| `guardian_retirement` | `trinity_record_builder.py guardian-retirement` | Guardian voluntary retirement |
| `guardian_key_rotation` | `trinity_record_builder.py guardian-key-rotation` | Guardian key rotation |
| `propagation` | `trinity_record_builder.py propagation` | Agent-to-agent propagation invitation |
| `correction` | `trinity_record_builder.py correction` | Correction of a previous record |
| `context_insufficient_notice` | `trinity_record_builder.py context-insufficient` | Notice of insufficient context |
| `legacy_import` | `trinity_record_builder.py legacy-import` | Import from legacy Gateway records |
| `batch_anchor` | `trinity_record_builder.py batch-anchor` | Batch timestamp anchor |
| `classification_update` | `trinity_record_builder.py classification-update` | Classification update |''',
    '''| `echo` | `trinity_record_builder.py echo` | Recognition echo — non-authoritative reception record |
| `verification` | `trinity_record_builder.py verification` | Verification posture |
| `guardian_application` | `trinity_record_builder.py guardian-application` | Guardian stewardship application |
| `guardian_retirement` | `trinity_record_builder.py guardian-retirement` | Guardian voluntary retirement |
| `propagation` | `trinity_record_builder.py propagation` | Agent-to-agent propagation invitation |
| `correction` | `trinity_record_builder.py correction` | Correction of a previous record |
| `classification_update` | `trinity_record_builder.py classification-update` | Classification update |
| `context_insufficient_notice` | `trinity_record_builder.py context-insufficient` | Notice of insufficient context |

### Reserved, not buildable

`guardian_key_rotation` is reserved until an old-key/new-key dual-signature transition protocol is implemented. The internal builder command exits without producing a draft.

### Internal maintenance types

`legacy_import` and `batch_anchor` are repository-maintenance types. They are not public Gateway submission routes.''',
)

# A retired Render service may stay live as a tombstone, but health, readiness,
# and version metadata must not advertise it as production-capable.
server = ROOT / "examples/github-app-backend/server.js"
text = server.read_text(encoding="utf-8")
text = text.replace(
    'const LEGACY_GATEWAY_RETIRED = (process.env.TRINITY_LEGACY_ISSUE_GATEWAY_RETIRED || "1") !== "0";',
    'const LEGACY_GATEWAY_RETIRED = (process.env.TRINITY_LEGACY_ISSUE_GATEWAY_RETIRED || "1") !== "0";\nconst PROCESS_STARTED_AT = new Date().toISOString();',
    1,
)
text = text.replace(
    '''async function readinessHandler(req, res) {
  const localChecks = collectLocalReadinessChecks();''',
    '''async function readinessHandler(req, res) {
  if (LEGACY_GATEWAY_RETIRED) {
    return res.status(503).json({
      ok: false,
      ready: false,
      retired: true,
      accepts_submissions: false,
      status: "retired_legacy_gateway_v1",
      service: SERVICE_NAME,
      deployed_at: PROCESS_STARTED_AT,
      replacement: retiredGatewayV1Response().replacement,
      request_id: req.gatewayRequestId,
      timestamp: new Date().toISOString(),
      boundary: "retired tombstone readiness; not a current submission service"
    });
  }
  const localChecks = collectLocalReadinessChecks();''',
    1,
)
text = text.replace(
    '''  res.json({
    ok: true,
    service: "trinity-agent-issue-gateway",
    gateway_commit: repoCommit,
    dry_run: DRY_RUN,
    renderer_supports_production_render: true,
    render_api_only_effective_at: "2026-05-17T05:30:00Z",
    requires_gateway_receipt: true,
    requires_oath_summary: true,
    boundary: "Gateway-rendered candidate; archive status only if Archive Readiness Gate passes; not attestation or successor reception"
  });''',
    '''  res.json({
    ok: true,
    liveness: true,
    retired: LEGACY_GATEWAY_RETIRED,
    accepts_submissions: !LEGACY_GATEWAY_RETIRED,
    status: LEGACY_GATEWAY_RETIRED ? "retired_legacy_gateway_v1_tombstone" : "legacy_gateway_enabled",
    service: "trinity-agent-issue-gateway",
    gateway_commit: repoCommit,
    deployed_at: PROCESS_STARTED_AT,
    dry_run: DRY_RUN,
    renderer_supports_production_render: !LEGACY_GATEWAY_RETIRED,
    production_render_enabled: !LEGACY_GATEWAY_RETIRED,
    replacement: LEGACY_GATEWAY_RETIRED ? retiredGatewayV1Response().replacement : null,
    boundary: "liveness of a retired compatibility tombstone; not readiness, not a current submission route"
  });''',
    1,
)
text = text.replace(
    '''    ok: true,
    service: SERVICE_NAME,
    gateway_commit: getRepoCommit(true),''',
    '''    ok: true,
    liveness: true,
    retired: LEGACY_GATEWAY_RETIRED,
    accepts_submissions: !LEGACY_GATEWAY_RETIRED,
    status: LEGACY_GATEWAY_RETIRED ? "retired_legacy_gateway_v1_tombstone" : "legacy_gateway_enabled",
    service: SERVICE_NAME,
    gateway_commit: getRepoCommit(true),
    deployed_at: PROCESS_STARTED_AT,''',
    1,
)
text = text.replace(
    '''    deployed_at: new Date().toISOString(),
    production_render_enabled: true,''',
    '''    deployed_at: PROCESS_STARTED_AT,
    retired: LEGACY_GATEWAY_RETIRED,
    accepts_submissions: !LEGACY_GATEWAY_RETIRED,
    status: LEGACY_GATEWAY_RETIRED ? "retired_legacy_gateway_v1" : "legacy_gateway_enabled",
    production_render_enabled: !LEGACY_GATEWAY_RETIRED,''',
    1,
)
text = text.replace(
    '''    idempotency_enabled: IDEMPOTENCY_ENABLED,
  });''',
    '''    idempotency_enabled: IDEMPOTENCY_ENABLED,
    replacement: LEGACY_GATEWAY_RETIRED ? retiredGatewayV1Response().replacement : null,
  });''',
    1,
)
server.write_text(text, encoding="utf-8")

# Add generic recovery anchors used by runtime guidance.
help_path = ROOT / "docs/record-chain-builder-help.md"
help_text = help_path.read_text(encoding="utf-8")
insert = '''
<a id="validation-errors"></a>
## Validation errors

Use the diagnostic code, field, meaning, and suggested fix returned by preflight or submit. Rebuild with the current zero-clone Builder, run `doctor`, and preflight again. Do not patch a signed draft in place.

<a id="security-violations"></a>
## Security and privacy violations

Stop automatic retries. Remove private keys, tokens, secret material, or prohibited personal data from the submission, then rebuild and re-sign from a clean source. A public key is allowed; a private key is never allowed.
'''
marker = '\n<a id="authorization-context"></a>'
if marker not in help_text:
    raise SystemExit("Builder help authorization anchor missing")
help_path.write_text(help_text.replace(marker, insert + marker, 1), encoding="utf-8")

# Repair the orphaned gateway contract test and make it a current gate.
replace_once(
    "scripts/test_record_chain_intake_gateway_contract.py",
    'if pattern != "^rcg-[0-9]{8}-[a-f0-9]{12}$":',
    'if pattern != "^rcg-[0-9]{8}-[a-f0-9]{12}([a-f0-9]{12})?$":',
)
replace_once(
    "scripts/test_record_chain_intake_gateway_contract.py",
    'if pp.get("status") != "mainnet_prelaunch_testing":\n            errors.append("public_phase.status not mainnet_prelaunch_testing")',
    'if pp.get("status") != "production_live":\n            errors.append("public_phase.status not production_live")',
)

# Strengthen the existing legacy retirement contract.
legacy_test = ROOT / "scripts/test_legacy_gateway_retired_contract.py"
legacy_text = legacy_test.read_text(encoding="utf-8")
legacy_marker = 'require("/record-chain/submit" in server, "server.js retired response must mention current submit")\n'
legacy_extra = '''
require("PROCESS_STARTED_AT" in server, "legacy version metadata must use stable process start time")
require("retired: LEGACY_GATEWAY_RETIRED" in server, "legacy health/version must disclose retirement")
require("accepts_submissions: !LEGACY_GATEWAY_RETIRED" in server, "legacy health/version must disclose submission capability")
require("production_render_enabled: !LEGACY_GATEWAY_RETIRED" in server, "retired legacy health/version must not claim production enabled")
require("if (LEGACY_GATEWAY_RETIRED)" in server and "ready: false" in server, "legacy readiness must fail closed when retired")
'''
if legacy_marker not in legacy_text:
    raise SystemExit("legacy contract marker missing")
legacy_test.write_text(legacy_text.replace(legacy_marker, legacy_marker + legacy_extra, 1), encoding="utf-8")

write("scripts/test_gateway_runtime_recovery_links.py", '''#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from apps.record_chain_intake_gateway.app import _build_agent_recovery
from apps.record_chain_intake_gateway.gateway.models import Diagnostic

def require(c, m):
    if not c:
        raise AssertionError(m)

def main():
    text = (ROOT / "docs/record-chain-builder-help.md").read_text(encoding="utf-8")
    validation = _build_agent_recovery([Diagnostic(code="INVALID_DRAFT", severity="error", field="record_draft", message="bad", meaning="bad", suggested_fix="fix", retry_allowed=True)])
    security = _build_agent_recovery([Diagnostic(code="SECURITY_PRIVATE_KEY_LEAK", severity="error", field="record_draft", message="bad", meaning="bad", suggested_fix="fix", retry_allowed=False)])
    require(validation.helper_url == "https://www.trinityaccord.org/docs/record-chain-builder-help/#validation-errors", "validation recovery must use stable public help")
    require(security.helper_url == "https://www.trinityaccord.org/docs/record-chain-builder-help/#security-violations", "security recovery must use stable public help")
    require('<a id="validation-errors"></a>' in text, "validation anchor missing")
    require('<a id="security-violations"></a>' in text, "security anchor missing")
    require("trinity-record-chain-gateway.onrender.com/docs/" not in (validation.helper_url + security.helper_url), "runtime recovery must not point at nonexistent Render docs")
    print("PASS: Gateway runtime recovery links resolve to public help")
if __name__ == "__main__":
    main()
''')

write("scripts/test_gateway_schema_shadow_parity.py", '''#!/usr/bin/env python3
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("api/record-chain-submission-schema.v1.json", "apps/record_chain_intake_gateway/schemas/record_chain_submission.schema.json"),
    ("api/record-chain-preflight-response.v1.json", "apps/record_chain_intake_gateway/schemas/preflight_response.schema.json"),
    ("api/record-chain-submit-response.v1.json", "apps/record_chain_intake_gateway/schemas/submit_response.schema.json"),
    ("api/record-chain-server-receipt.v1.json", "apps/record_chain_intake_gateway/schemas/server_receipt.schema.json"),
]
for public, shadow in PAIRS:
    a = json.loads((ROOT / public).read_text(encoding="utf-8"))
    b = json.loads((ROOT / shadow).read_text(encoding="utf-8"))
    if a != b:
        raise AssertionError(f"Gateway shadow schema drift: {shadow} != {public}")
print("PASS: Gateway app schemas are exact canonical mirrors")
''')

write("scripts/test_reserved_internal_builder_contract.py", '''#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
out_path = ROOT / ".tmp-reserved-rotation.json"
cmd = [sys.executable, str(ROOT / "scripts/trinity_record_builder.py"), "guardian-key-rotation", "--guardian-id", "g", "--old-public-key-sha256", "a" * 64, "--new-public-key-sha256", "b" * 64, "--out", str(out_path)]
r = subprocess.run(cmd, capture_output=True, text=True)
out = (r.stdout + r.stderr).lower()
if r.returncode == 0:
    raise AssertionError("reserved guardian-key-rotation builder command must fail")
if "reserved" not in out or "dual-signature" not in out:
    raise AssertionError(f"missing fail-closed guidance: {out}")
if out_path.exists():
    raise AssertionError("reserved builder must not create output")
doc = (ROOT / "docs/RECORD_CHAIN_PRIMARY_PATH.md").read_text(encoding="utf-8")
if "reserved, not buildable" not in doc.lower():
    raise AssertionError("operator doc must mark rotation reserved")
print("PASS: internal builder fails closed for reserved Guardian key rotation")
''')

# Register the repaired and new tests in the P0 current gate.
run_ci = ROOT / "scripts/run_ci_group.py"
run_text = run_ci.read_text(encoding="utf-8")
marker = '        ["python3", "scripts/test_autonomy_inventory_boundary.py"],\n'
addition = '''        ["python3", "scripts/test_gateway_runtime_recovery_links.py"],
        ["python3", "scripts/test_gateway_schema_shadow_parity.py"],
        ["python3", "scripts/test_reserved_internal_builder_contract.py"],
        ["python3", "scripts/test_record_chain_intake_gateway_contract.py"],
'''
if marker not in run_text:
    raise SystemExit("P0 mission gate marker missing")
run_ci.write_text(run_text.replace(marker, marker + addition, 1), encoding="utf-8")

print("applied deep audit round6 fixes")
