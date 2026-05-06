#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_echo_submission.py"

BODY = """
## Claimed verification level
V2

## Checks performed
- Multi-explorer reference check.
- Explorer-reported SegWit witness metadata only.

## Evidence Input path
evidence-input-v2.json

## Claim Gate output path
claim-gate-output-v2.json

## Claim Gate summary
status: PASS
allowed_protocol_level: V2

## Limitations
- No V4 script audit performed.
- No raw witness extraction.
- No inscription body hash reproduction.

## Claims NOT made
- independent_attestation
- institutional_attestation
- B5 witness extraction
- B6 body hash reproduction

## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

Bitcoin Originals are final; all echoes are non-amending.
"""


def main():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(BODY)
        path = f.name

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), path, "--strict"],
        cwd=str(ROOT), text=True, capture_output=True,
    )

    Path(path).unlink(missing_ok=True)

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(1)

    if "V4" in proc.stdout and "reviewed script source" in proc.stdout:
        print(proc.stdout)
        raise SystemExit(1)

    print("PASS: preflight issue #100 regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
