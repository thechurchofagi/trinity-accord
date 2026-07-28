#!/usr/bin/env python3
"""Contract test for the formal agent in-context oath readback process."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"
SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"

DECLARATIONS = (
    "canonical_oath_loaded_into_active_context",
    "readback_generated_by_participant_from_active_context",
    "readback_was_not_directly_copied_by_submission_tool",
    "readback_was_not_automatically_completed_or_corrected",
    "contextual_readback_process_acknowledged",
)
BOUNDARIES = (
    "contextual_readback_process_is_self_declared",
    "contextual_readback_does_not_prove_persistent_memory",
)
ENTRYPOINTS = (
    ROOT / "index.md",
    ROOT / "agent-first-contact.md",
    ROOT / "agent-start.md",
    ROOT / "ai.txt",
    ROOT / "llms.txt",
)


def run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(BUILDER), *args],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def main() -> None:
    errors: list[str] = []

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    no_shortcut = policy.get("no_shortcut_policy", {})
    if policy.get("version") != "1.2.0":
        errors.append("oath policy version must be 1.2.0")
    for field in DECLARATIONS:
        if field not in no_shortcut.get("required_declarations", []):
            errors.append(f"policy missing required declaration {field}")
    for field in BOUNDARIES:
        if no_shortcut.get("boundary", {}).get(field) is not True:
            errors.append(f"policy missing boundary {field}=true")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    oath_properties = (
        schema.get("properties", {})
        .get("record_draft", {})
        .get("properties", {})
        .get("submission_oath_verification", {})
        .get("properties", {})
    )
    for field in DECLARATIONS + BOUNDARIES:
        if oath_properties.get(field, {}).get("type") != "boolean":
            errors.append(f"submission schema missing boolean oath field {field}")

    for path in ENTRYPOINTS:
        text = path.read_text(encoding="utf-8")
        if "active context" not in text and "当前上下文" not in text:
            errors.append(f"{path.relative_to(ROOT)} does not expose the active-context rule")
        if "auto-fill" not in text and "自动填" not in text:
            errors.append(f"{path.relative_to(ROOT)} does not expose the no-autofill boundary")

    help_result = run_builder("help")
    if help_result.returncode != 0:
        errors.append(f"builder help failed: {help_result.stderr[:200]}")
    elif "--contextual-readback-confirmed true" not in help_result.stdout:
        errors.append("builder help does not document --contextual-readback-confirmed true")

    oath_result = run_builder("print-oath", "--record-type", "echo")
    if oath_result.returncode != 0:
        errors.append(f"print-oath failed: {oath_result.stderr[:200]}")
        canonical_oath = ""
    else:
        canonical_oath = oath_result.stdout
        if "active context" not in canonical_oath:
            errors.append("canonical oath does not state the active-context requirement")
        if "relay" not in canonical_oath:
            errors.append("canonical oath does not state the submission-tool relay boundary")

    if canonical_oath:
        with tempfile.TemporaryDirectory(prefix="trinity-contextual-oath-") as tmp:
            temp_dir = Path(tmp)
            common = [
                "--actor-label", "Contextual Oath Contract Agent",
                "--provider", "Local Contract Test",
                "--body", "Contextual oath readback contract test.",
                "--context-level", "CC-3",
                "--context-sufficient-for-selected-action", "true",
                "--context-read-confirmed", "true",
                "--loaded-urls",
                "https://www.trinityaccord.org/agent-first-contact/,"
                "https://www.trinityaccord.org/api/record-chain-oath-policy.v1.json",
                "--discovery-mode", "user_task_context",
                "--record-decision", "human",
                "--submission-executor", "self",
                "--human-operator-involved", "false",
                "--readback", canonical_oath,
                "--key-dir", str(temp_dir / "keys"),
            ]

            missing_confirmation = run_builder(
                "echo", *common, "--out", str(temp_dir / "missing-confirmation.json")
            )
            if missing_confirmation.returncode == 0:
                errors.append("formal build accepted without contextual confirmation")
            elif "--contextual-readback-confirmed true" not in (
                missing_confirmation.stdout + missing_confirmation.stderr
            ):
                errors.append("missing-confirmation error does not identify the required flag")

            output = temp_dir / "submission.json"
            accepted = run_builder(
                "echo",
                *common,
                "--contextual-readback-confirmed", "true",
                "--out", str(output),
            )
            if accepted.returncode != 0:
                errors.append(f"confirmed contextual build failed: {accepted.stderr[:500]}")
            elif not output.exists():
                errors.append("confirmed contextual build did not create output")
            else:
                submission = json.loads(output.read_text(encoding="utf-8"))
                oath = submission["record_draft"]["submission_oath_verification"]
                for field in DECLARATIONS + BOUNDARIES:
                    if oath.get(field) is not True:
                        errors.append(f"builder did not sign {field}=true")
                if oath.get("readback_method_declared") != "participant_generated_in_current_context":
                    errors.append("builder emitted the wrong readback method")

                if str(ROOT) not in sys.path:
                    sys.path.insert(0, str(ROOT))
                from apps.record_chain_intake_gateway.gateway.validation import (  # noqa: PLC0415
                    validate_submission_oath,
                )

                for field in DECLARATIONS + BOUNDARIES:
                    mutated = copy.deepcopy(submission)
                    mutated["record_draft"]["submission_oath_verification"][field] = False
                    diagnostics = validate_submission_oath(
                        "echo", mutated, mutated["record_draft"]
                    )
                    if not any(
                        diagnostic.code == "OATH_REQUIRED_FIELD_NOT_TRUE"
                        and diagnostic.field
                        == f"record_draft.submission_oath_verification.{field}"
                        for diagnostic in diagnostics
                    ):
                        errors.append(f"gateway accepted false oath field {field}")

    if errors:
        print("FAIL:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("PASS: agent in-context oath readback contract is enforced end to end")


if __name__ == "__main__":
    main()
