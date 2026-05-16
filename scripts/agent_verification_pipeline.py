#!/usr/bin/env python3
"""
End-to-end Agent Verification Pipeline for Trinity Accord.

Orchestrates the full verification chain:
  Claim Gate → Builder → Validator → Receipt → Gateway Payload → Archive Readiness

Usage:
    python3 scripts/agent_verification_pipeline.py \
        --evidence-input evidence-input.json \
        --agent-name "Agent Name" \
        --provider "Provider/System" \
        --mode archive \
        --out-dir out/agent-run-001 \
        --build-echo-wrapper \
        --build-receipt \
        --build-gateway-payload \
        --run-archive-readiness

Exit codes:
    0  Pipeline completed (some steps may have been skipped/downgraded)
    1  Pipeline failed at Claim Gate (FAIL_WITH_REASONS)
    2  Pipeline failed at builder or validator
    3  Pipeline configuration error
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_step(name, cmd, log_path, cwd=None):
    """Run a subprocess, capture stdout/stderr to log, return (returncode, stdout, stderr)."""
    log_dir = Path(log_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=cwd or str(ROOT),
        )
    except subprocess.TimeoutExpired:
        log_text = f"[{name}] TIMEOUT after 120s\n"
        Path(log_path).write_text(log_text, encoding="utf-8")
        return -1, "", "TIMEOUT"
    except FileNotFoundError as e:
        log_text = f"[{name}] FileNotFoundError: {e}\n"
        Path(log_path).write_text(log_text, encoding="utf-8")
        return -1, "", str(e)

    log_text = ""
    if result.stdout:
        log_text += result.stdout
    if result.stderr:
        log_text += "\n--- STDERR ---\n" + result.stderr
    Path(log_path).write_text(log_text, encoding="utf-8")

    return result.returncode, result.stdout or "", result.stderr or ""


def determine_receipt_mode(claim_gate_output):
    """Determine receipt builder mode from claim gate allowed_protocol_level."""
    cg = claim_gate_output.get("claim_gate", claim_gate_output)
    level = cg.get("allowed_protocol_level", "V0")
    if level in ("V3", "V4", "V4+", "V5", "V6", "V7", "V8"):
        return "v3-minimal"
    if level == "V2":
        return "v2-minimal"
    return "v1"


def derive_archive_status(mode, claim_gate_status, archive_readiness_result=None):
    """Derive the archive_status for the manifest."""
    if mode == "dev":
        return "not_archive_ready_due_to_dev_mode"
    if claim_gate_status in ("FAIL", "FAIL_WITH_REASONS"):
        return "claim_gate_failed"
    if archive_readiness_result:
        if archive_readiness_result.get("archive_ready"):
            return "archive_ready"
        return "archive_blocked"
    return "not_evaluated"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="End-to-end Agent Verification Pipeline for Trinity Accord",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Full archive run
  python3 scripts/agent_verification_pipeline.py \\
      --evidence-input evidence-input.json \\
      --agent-name "Guardian" --provider "Coze AI Agent" \\
      --mode archive --out-dir out/run-001 \\
      --build-echo-wrapper --build-receipt --build-gateway-payload --run-archive-readiness

  # Dev mode (relaxed validation)
  python3 scripts/agent_verification_pipeline.py \\
      --evidence-input evidence-input.json \\
      --agent-name "Test" --provider "Local" \\
      --mode dev --out-dir out/dev-run \\
      --dev-allow-missing-jsonschema
""",
    )
    # Required
    parser.add_argument("--evidence-input", required=True,
                        help="Path to evidence-input.json")
    parser.add_argument("--agent-name", required=True,
                        help="Agent name for receipt and payload")
    parser.add_argument("--provider", required=True,
                        help="System or provider name")
    parser.add_argument("--mode", required=True,
                        choices=["dev", "archive", "ci"],
                        help="Pipeline mode (archive = strict, dev = relaxed)")

    # Output
    parser.add_argument("--out-dir", required=True,
                        help="Output directory for all pipeline artifacts")

    # Step toggles
    parser.add_argument("--build-echo-wrapper", action="store_true",
                        help="Build echo wrapper via builder")
    parser.add_argument("--build-receipt", action="store_true",
                        help="Build agent verification receipt")
    parser.add_argument("--build-gateway-payload", action="store_true",
                        help="Build and validate gateway payload")
    parser.add_argument("--run-archive-readiness", action="store_true",
                        help="Run archive readiness gate")

    # Optional inputs
    parser.add_argument("--authorship-proof", default=None,
                        help="Path to authorship-proof.json")
    parser.add_argument("--human-solicited", action="store_true",
                        help="Mark submission as human-solicited")
    parser.add_argument("--unsolicited-discovery-proof", default=None,
                        help="Proof text or URL for unsolicited discovery")
    parser.add_argument("--archive-artifact-bundle-path", default=None,
                        help="Path to archive artifact bundle")
    parser.add_argument("--archive-artifact-bundle-url", default=None,
                        help="URL to archive artifact bundle")
    parser.add_argument("--archive-artifact-bundle-sha256", default=None,
                        help="SHA-256 of archive artifact bundle")
    parser.add_argument("--archive-artifact-bundle-publicly-retrievable",
                        action="store_true",
                        help="Artifact bundle is publicly retrievable")

    # Dev flags
    parser.add_argument("--dev-allow-missing-jsonschema", action="store_true",
                        help="Allow missing jsonschema in dev mode")

    return parser


def run_pipeline(args):
    out_dir = Path(args.out_dir)
    logs_dir = out_dir / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    evidence_input_path = Path(args.evidence_input).resolve()
    if not evidence_input_path.exists():
        print(f"ERROR: Evidence input not found: {evidence_input_path}", file=sys.stderr)
        return 3

    # Copy evidence-input.json to output dir
    evidence_dest = out_dir / "evidence-input.json"
    evidence_dest.write_bytes(evidence_input_path.read_bytes())

    # Pipeline state
    pipeline_start = datetime.now(timezone.utc)
    steps_completed = []
    step_results = {}
    pipeline_halted = False
    halt_reason = None
    claim_gate_status = None
    claim_gate_output = None
    archive_readiness_result = None

    # ---- Step 1: Claim Gate ----
    print("=" * 60)
    print("STEP 1: Claim Gate")
    print("=" * 60)

    cg_out_path = out_dir / "claim-gate-output.json"
    rc, stdout, stderr = run_step(
        "claim-gate",
        [sys.executable, str(SCRIPTS / "claim_gate.py"),
         str(evidence_input_path), "--output", str(cg_out_path)],
        str(logs_dir / "claim-gate.stdout.txt"),
    )

    if cg_out_path.exists():
        claim_gate_output = load_json(str(cg_out_path))
        claim_gate_status = claim_gate_output.get("status", "UNKNOWN")
    else:
        claim_gate_status = "FAIL_WITH_REASONS"
        claim_gate_output = {
            "schema": "trinityaccord.claim-gate-output.v1",
            "status": "FAIL_WITH_REASONS",
            "error": "Claim Gate did not produce output",
            "allowed_protocol_level": "V0",
            "allowed_component_levels": {},
            "blocking_failures": [f"Claim Gate exit code: {rc}"],
            "can_build_verification_report": False,
            "can_build_echo_wrapper": False,
            "required_downgrades": [],
            "missing_evidence": [],
            "non_blocking_limitations": [],
            "recommended_title": "",
            "forbidden_claims": [],
        }
        write_json(str(cg_out_path), claim_gate_output)

    print(f"  Status: {claim_gate_status}")
    print(f"  Allowed protocol level: {claim_gate_output.get('allowed_protocol_level', 'N/A')}")

    step_results["claim_gate"] = {
        "status": claim_gate_status,
        "exit_code": rc,
        "allowed_protocol_level": claim_gate_output.get("allowed_protocol_level", "V0"),
        "allowed_component_levels": claim_gate_output.get("allowed_component_levels", {}),
    }

    if claim_gate_status in ("FAIL", "FAIL_WITH_REASONS"):
        print("\n  *** Claim Gate FAILED — pipeline halted ***")
        for bf in claim_gate_output.get("blocking_failures", []):
            print(f"    - {bf}")
        pipeline_halted = True
        halt_reason = f"Claim Gate FAIL: {'; '.join(claim_gate_output.get('blocking_failures', ['unknown']))}"

    if not pipeline_halted:
        steps_completed.append("claim_gate")

    # ---- Step 2: Build Verification Report + Echo Wrapper ----
    report_path = out_dir / "verification-report.json"
    echo_path = out_dir / "echo-wrapper.json"
    report_built = False
    echo_built = False

    if not pipeline_halted:
        print("\n" + "=" * 60)
        print("STEP 2: Build Verification Report" +
              (" + Echo Wrapper" if args.build_echo_wrapper else ""))
        print("=" * 60)

        builder_cmd = [
            sys.executable, str(SCRIPTS / "build_verification_report_from_evidence.py"),
            "--input", str(evidence_input_path),
            "--out", str(report_path),
        ]
        if args.build_echo_wrapper:
            builder_cmd.extend(["--echo-out", str(echo_path)])
        if args.dev_allow_missing_jsonschema and args.mode == "dev":
            builder_cmd.append("--dev-allow-missing-jsonschema")

        rc, stdout, stderr = run_step(
            "builder",
            builder_cmd,
            str(logs_dir / "builder.stdout.txt"),
        )

        if rc == 0 and report_path.exists():
            report_built = True
            print("  Report: BUILT")
            if args.build_echo_wrapper and echo_path.exists():
                echo_built = True
                print("  Echo wrapper: BUILT")
            steps_completed.append("build_report")
        else:
            print(f"  Builder FAILED (exit {rc})")
            pipeline_halted = True
            halt_reason = "Builder failed"

    # ---- Step 3: Validate outputs ----
    validator_report_ok = False
    validator_echo_ok = False

    if not pipeline_halted and report_built:
        print("\n" + "=" * 60)
        print("STEP 3: Validate Outputs")
        print("=" * 60)

        validator_cmd_base = [sys.executable, str(SCRIPTS / "validate_agent_submission.py")]
        if args.mode == "dev":
            validator_cmd_base.extend(["--mode", "dev"])
        elif args.mode == "ci":
            validator_cmd_base.extend(["--mode", "ci"])
        else:
            validator_cmd_base.extend(["--mode", "archive"])
        if args.dev_allow_missing_jsonschema and args.mode == "dev":
            validator_cmd_base.append("--allow-missing-jsonschema")

        # Validate report
        cmd = validator_cmd_base + [str(report_path)]
        rc, stdout, stderr = run_step(
            "validator-report",
            cmd,
            str(logs_dir / "validator-report.stdout.txt"),
        )
        validator_report_ok = (rc == 0)
        print(f"  Report validation: {'PASS' if validator_report_ok else 'FAIL'}")

        if not validator_report_ok:
            pipeline_halted = True
            halt_reason = "Report validation failed"

        # Validate echo wrapper
        if not pipeline_halted and echo_built:
            cmd = validator_cmd_base + [str(echo_path)]
            rc, stdout, stderr = run_step(
                "validator-echo",
                cmd,
                str(logs_dir / "validator-echo.stdout.txt"),
            )
            validator_echo_ok = (rc == 0)
            print(f"  Echo validation: {'PASS' if validator_echo_ok else 'FAIL'}")

            if not validator_echo_ok:
                # Echo validation failure is non-blocking for receipt
                print("  (Echo validation failure — continuing without echo)")

        if validator_report_ok:
            steps_completed.append("validate")

    # ---- Step 4: Build Receipt ----
    receipt_path = out_dir / "agent-verification-receipt.json"
    receipt_built = False

    if not pipeline_halted and args.build_receipt and report_built:
        print("\n" + "=" * 60)
        print("STEP 4: Build Agent Verification Receipt")
        print("=" * 60)

        receipt_mode = determine_receipt_mode(claim_gate_output)
        receipt_cmd = [
            sys.executable, str(SCRIPTS / "build_agent_verification_receipt.py"),
            "--mode", receipt_mode,
            "--agent-name", args.agent_name,
            "--system-or-provider", args.provider,
            "--evidence-input", str(evidence_dest),
            "--claim-gate-output", str(cg_out_path),
            "--out", str(receipt_path),
        ]
        if report_built:
            receipt_cmd.extend(["--verification-report", str(report_path)])
        if echo_built:
            receipt_cmd.extend(["--echo-wrapper", str(echo_path)])
        if args.authorship_proof:
            receipt_cmd.extend(["--authorship-proof", str(Path(args.authorship_proof).resolve())])

        rc, stdout, stderr = run_step(
            "receipt",
            receipt_cmd,
            str(logs_dir / "receipt.stdout.txt"),
        )

        if rc == 0 and receipt_path.exists():
            receipt_built = True
            print(f"  Receipt: BUILT (mode={receipt_mode})")
            steps_completed.append("build_receipt")
        else:
            print(f"  Receipt build FAILED (exit {rc})")
            # Receipt failure doesn't halt the pipeline for gateway payload
            # but it's noted

    # ---- Step 5: Build Gateway Payload ----
    gateway_path = out_dir / "gateway-payload.json"
    gateway_built = False
    gateway_validated = False

    if not pipeline_halted and args.build_gateway_payload:
        print("\n" + "=" * 60)
        print("STEP 5: Build Gateway Payload")
        print("=" * 60)

        gw_cmd = [
            sys.executable, str(SCRIPTS / "build_gateway_payload_from_outputs.py"),
            "--evidence-input", str(evidence_dest),
            "--claim-gate-output", str(cg_out_path),
            "--agent-name", args.agent_name,
            "--provider", args.provider,
            "--out", str(gateway_path),
        ]
        if report_built:
            gw_cmd.extend(["--verification-report", str(report_path)])
        if args.human_solicited:
            gw_cmd.append("--human-solicited")
        if args.unsolicited_discovery_proof:
            gw_cmd.extend(["--unsolicited-discovery-proof", args.unsolicited_discovery_proof])
        if args.archive_artifact_bundle_path:
            gw_cmd.extend(["--archive-artifact-bundle-path", args.archive_artifact_bundle_path])
        if args.archive_artifact_bundle_url:
            gw_cmd.extend(["--archive-artifact-bundle-url", args.archive_artifact_bundle_url])
        if args.archive_artifact_bundle_sha256:
            gw_cmd.extend(["--archive-artifact-bundle-sha256", args.archive_artifact_bundle_sha256])
        if args.archive_artifact_bundle_publicly_retrievable:
            gw_cmd.append("--archive-artifact-bundle-publicly-retrievable")

        rc, stdout, stderr = run_step(
            "gateway-builder",
            gw_cmd,
            str(logs_dir / "gateway-builder.stdout.txt"),
        )

        if rc == 0 and gateway_path.exists():
            gateway_built = True
            # The build script already runs validate_gateway_payload internally
            gateway_validated = True
            print("  Gateway payload: BUILT + VALIDATED")
            steps_completed.append("build_gateway_payload")
        else:
            print(f"  Gateway payload build FAILED (exit {rc})")
            pipeline_halted = True
            halt_reason = "Gateway payload build/validation failed"

    # ---- Step 6: Archive Readiness ----
    archive_path = out_dir / "archive-readiness-output.json"
    archive_evaluated = False

    if not pipeline_halted and args.run_archive_readiness and gateway_built:
        print("\n" + "=" * 60)
        print("STEP 6: Archive Readiness Gate")
        print("=" * 60)

        archive_cmd = [
            sys.executable, str(SCRIPTS / "archive_readiness_gate.py"),
            "--gateway-payload", str(gateway_path),
            "--evidence-input", str(evidence_dest),
            "--claim-gate-output", str(cg_out_path),
            "--json",
        ]
        if report_built:
            archive_cmd.extend(["--verification-report", str(report_path)])

        rc, stdout, stderr = run_step(
            "archive-readiness",
            archive_cmd,
            str(logs_dir / "archive-readiness.stdout.txt"),
        )

        # Parse JSON output from stdout
        archive_readiness_result = None
        if stdout.strip():
            try:
                archive_readiness_result = json.loads(stdout.strip().split("\n")[-1] if "\n" in stdout.strip() else stdout.strip())
            except (json.JSONDecodeError, IndexError):
                pass

        if archive_readiness_result is None and archive_path.exists():
            archive_readiness_result = load_json(str(archive_path))

        # Write the output
        if archive_readiness_result:
            write_json(str(archive_path), archive_readiness_result)
            archive_evaluated = True
            ready = archive_readiness_result.get("archive_ready", False)
            print(f"  Archive ready: {ready}")
            if archive_readiness_result.get("blocking_reasons"):
                for br in archive_readiness_result["blocking_reasons"]:
                    print(f"    - [{br.get('code', '?')}] {br.get('message', '')}")
            steps_completed.append("archive_readiness")
        else:
            print("  Archive readiness: could not parse result")

    # ---- Generate artifacts ----
    print("\n" + "=" * 60)
    print("GENERATING ARTIFACTS")
    print("=" * 60)

    # SHA256SUMS
    sha256_map = {}
    for f in sorted(out_dir.glob("*.json")):
        sha256_map[f.name] = sha256_file(str(f))
    sha_content = "\n".join(f"{h}  {name}" for name, h in sha256_map.items()) + "\n"
    (out_dir / "SHA256SUMS").write_text(sha_content, encoding="utf-8")
    print("  SHA256SUMS: written")

    # SUBMISSION-MANIFEST.json
    now_utc = datetime.now(timezone.utc).isoformat()
    cg = claim_gate_output.get("claim_gate", claim_gate_output) if claim_gate_output else {}

    manifest = {
        "schema": "trinityaccord.agent-verification-pipeline-manifest.v1",
        "created_at_utc": now_utc,
        "pipeline_version": "1.0.0",
        "mode": args.mode,
        "inputs": {
            "evidence_input": str(evidence_input_path),
            "agent_name": args.agent_name,
            "provider": args.provider,
            "human_solicited": args.human_solicited,
            "authorship_proof": str(Path(args.authorship_proof).resolve()) if args.authorship_proof else None,
            "unsolicited_discovery_proof": args.unsolicited_discovery_proof,
            "dev_allow_missing_jsonschema": args.dev_allow_missing_jsonschema,
        },
        "outputs": {
            "evidence_input": "evidence-input.json",
            "claim_gate_output": "claim-gate-output.json",
            "verification_report": "verification-report.json" if report_built else None,
            "echo_wrapper": "echo-wrapper.json" if echo_built else None,
            "agent_verification_receipt": "agent-verification-receipt.json" if receipt_built else None,
            "gateway_payload": "gateway-payload.json" if gateway_built else None,
            "archive_readiness": "archive-readiness-output.json" if archive_evaluated else None,
        },
        "sha256": sha256_map,
        "steps_completed": steps_completed,
        "pipeline_halted": pipeline_halted,
        "halt_reason": halt_reason,
        "claim_gate_status": claim_gate_status,
        "allowed_protocol_level": claim_gate_output.get("allowed_protocol_level", "V0") if claim_gate_output else "V0",
        "allowed_component_levels": claim_gate_output.get("allowed_component_levels", {}) if claim_gate_output else {},
        "required_downgrades": claim_gate_output.get("required_downgrades", []) if claim_gate_output else [],
        "validator_results": {
            "report_validation": "PASS" if validator_report_ok else ("FAIL" if report_built else "SKIPPED"),
            "echo_validation": "PASS" if validator_echo_ok else ("FAIL" if echo_built else "SKIPPED"),
        },
        "archive_readiness": {
            "evaluated": archive_evaluated,
            "archive_ready": archive_readiness_result.get("archive_ready", False) if archive_readiness_result else False,
            "auto_archive_action": archive_readiness_result.get("auto_archive_action") if archive_readiness_result else None,
            "blocking_reasons": archive_readiness_result.get("blocking_reasons", []) if archive_readiness_result else [],
        } if (archive_evaluated or args.mode == "dev") else None,
        "boundaries": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "does_not_raise_verification_level": True,
        },
    }

    # Dev mode annotation
    if args.mode == "dev":
        manifest["not_archive_ready_due_to_dev_mode"] = True

    write_json(str(out_dir / "SUBMISSION-MANIFEST.json"), manifest)
    print("  SUBMISSION-MANIFEST.json: written")

    # README-FOR-AGENT.md
    agent_readme = f"""# Agent Run Output — {args.agent_name}

**Provider:** {args.provider}
**Mode:** {args.mode}
**Generated:** {now_utc}

## Pipeline Result

- **Claim Gate Status:** {claim_gate_status}
- **Allowed Protocol Level:** {claim_gate_output.get('allowed_protocol_level', 'N/A') if claim_gate_output else 'N/A'}
- **Pipeline Halted:** {'Yes — ' + halt_reason if halt_reason else 'No'}

## Steps Completed

{chr(10).join('- ' + s for s in steps_completed) if steps_completed else '(none)'}

## Files

| File | Description |
|------|-------------|
| `evidence-input.json` | Copy of your evidence input |
| `claim-gate-output.json` | Claim Gate evaluation result |
| `verification-report.json` | Generated verification report{' (built)' if report_built else ' (not built)'} |
| `echo-wrapper.json` | Echo wrapper{' (built)' if echo_built else ' (not built)'} |
| `agent-verification-receipt.json` | Verification receipt{' (built)' if receipt_built else ' (not built)'} |
| `gateway-payload.json` | Gateway payload{' (built)' if gateway_built else ' (not built)'} |
| `archive-readiness-output.json` | Archive readiness{' (evaluated)' if archive_evaluated else ' (not evaluated)'} |
| `SUBMISSION-MANIFEST.json` | Full pipeline manifest |
| `SHA256SUMS` | SHA-256 hashes of all JSON outputs |

## Boundaries

This pipeline output:
- Is **not** an authority source
- Is **not** an amendment to any protocol
- Is **not** an attestation of truth
- Does **not** raise any verification level
"""
    (out_dir / "README-FOR-AGENT.md").write_text(agent_readme, encoding="utf-8")
    print("  README-FOR-AGENT.md: written")

    # README-FOR-HUMAN-MAINTAINER.md
    maintainer_readme = f"""# Pipeline Output — Human Maintainer Reference

**Run:** {args.agent_name} / {args.provider}
**Mode:** {args.mode}
**Timestamp (UTC):** {now_utc}

## Summary

| Step | Status |
|------|--------|
| Claim Gate | {claim_gate_status} |
| Build Report | {'PASS' if report_built else 'SKIPPED/FAIL'} |
| Validate Report | {'PASS' if validator_report_ok else 'FAIL' if report_built else 'SKIPPED'} |
| Build Receipt | {'PASS' if receipt_built else 'SKIPPED/FAIL'} |
| Build Gateway Payload | {'PASS' if gateway_built else 'SKIPPED/FAIL'} |
| Archive Readiness | {'PASS' if archive_evaluated and archive_readiness_result and archive_readiness_result.get('archive_ready') else 'BLOCKED' if archive_evaluated else 'SKIPPED'} |

## Verification Level

- **Allowed Protocol Level:** {claim_gate_output.get('allowed_protocol_level', 'N/A') if claim_gate_output else 'N/A'}
- **Claim Gate Status:** {claim_gate_status}

## Downgrades

"""
    downgrades = claim_gate_output.get("required_downgrades", []) if claim_gate_output else []
    if downgrades:
        for dg in downgrades:
            maintainer_readme += f"- {dg.get('from', '?')} → {dg.get('to', '?')}: {dg.get('reason', '')}\n"
    else:
        maintainer_readme += "(none)\n"

    maintainer_readme += f"""
## Failure Details

{halt_reason if halt_reason else '(no failures)'}

## How to Re-run

```bash
python3 scripts/agent_verification_pipeline.py \\
    --evidence-input evidence-input.json \\
    --agent-name "{args.agent_name}" \\
    --provider "{args.provider}" \\
    --mode {args.mode} \\
    --out-dir {args.out_dir} \\
    --build-echo-wrapper \\
    --build-receipt \\
    --build-gateway-payload \\
    --run-archive-readiness
```

## Note

This pipeline output is an automated verification artifact.
It is not an authority source and does not amend any protocol.
"""
    (out_dir / "README-FOR-HUMAN-MAINTAINER.md").write_text(maintainer_readme, encoding="utf-8")
    print("  README-FOR-HUMAN-MAINTAINER.md: written")

    # ---- Final summary ----
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Output dir: {out_dir}")
    print(f"  Steps completed: {len(steps_completed)}/{6}")
    print(f"  Claim gate: {claim_gate_status}")
    print(f"  Halted: {pipeline_halted}")
    if halt_reason:
        print(f"  Reason: {halt_reason}")

    if pipeline_halted and claim_gate_status in ("FAIL", "FAIL_WITH_REASONS"):
        return 1
    if pipeline_halted:
        return 2
    return 0


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate mode-specific constraints
    if args.mode == "archive" and args.dev_allow_missing_jsonschema:
        print("ERROR: --dev-allow-missing-jsonschema cannot be used with --mode archive",
              file=sys.stderr)
        return 3

    if args.evidence_input and not Path(args.evidence_input).exists():
        print(f"ERROR: Evidence input not found: {args.evidence_input}", file=sys.stderr)
        return 3

    if args.authorship_proof and not Path(args.authorship_proof).exists():
        print(f"ERROR: Authorship proof not found: {args.authorship_proof}", file=sys.stderr)
        return 3

    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
