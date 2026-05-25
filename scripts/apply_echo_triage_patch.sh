#!/usr/bin/env bash
# ============================================================
# apply_echo_triage_patch.sh — Replace isGatewayCreated() in echo-triage.yml
# 在仓库根目录运行: bash scripts/apply_echo_triage_patch.sh
# ============================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

WF=".github/workflows/echo-triage.yml"

python3 - <<'PYEOF'
import re
from pathlib import Path

f = Path(".github/workflows/echo-triage.yml")
text = f.read_text(encoding="utf-8")

new_func = """function isGatewayCreated(body) {
  const receiptId = intakeField(body, "gateway_receipt_id");
  const service = intakeField(body, "gateway_service");
  const receiptPattern = /^gar-[A-Za-z0-9T._:-]{16,}$/;

  return hasMachineFlag(body, "created_by_gateway", "true") &&
         hasMachineFlag(body, "render_api_only", "true") &&
         hasMachineFlag(body, "server_validated", "true") &&
         hasMachineFlag(body, "server_rendered", "true") &&
         service === "trinity-agent-issue-gateway" &&
         receiptPattern.test(receiptId);
}"""

# Match the existing function
pattern = r"function\s+isGatewayCreated\s*\([^)]*\)\s*\{[^}]*\}"
match = re.search(pattern, text, re.S)

if match:
    text = text[:match.start()] + new_func + text[match.end():]
    f.write_text(text, encoding="utf-8")
    print("  Replaced isGatewayCreated() with strict version")
else:
    print("  WARNING: Could not find isGatewayCreated() function")
    print("  Add this function manually:")
    print()
    print(new_func)
PYEOF
