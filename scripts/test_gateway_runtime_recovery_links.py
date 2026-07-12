#!/usr/bin/env python3
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
