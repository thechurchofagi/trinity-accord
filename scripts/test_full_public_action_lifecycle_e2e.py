#!/usr/bin/env python3
"""Isolated full-path simulation for every public Record-Chain action.

This is intentionally broader than a schema unit test. It copies the repository
into a temporary directory, runs the real Node Builder and doctor, exercises the
real FastAPI Gateway through TestClient with a filesystem-backed Contents API
adapter, appends the resulting pending records with the real append-only chain
script, checks receipt final status and derived indexes, and finally verifies the
entire temporary chain.

No production record, branch, receipt, key, or index is modified.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BUILDER_REL = Path("downloads/record-chain-builder.mjs")
CHAIN_TOOL_REL = Path("scripts/trinity_record_chain.py")

FORMAL_TO_COMMAND = {
    "echo": "echo",
    "verification": "verification",
    "guardian_application": "guardian-application",
    "guardian_retirement": "guardian-retirement",
    "propagation": "propagation",
    "correction": "correction",
    "classification_update": "classification-update",
}

LOADED_URLS = ",".join(
    [
        "https://www.trinityaccord.org/agent-first-contact/",
        "https://www.trinityaccord.org/agent-start/",
        "https://www.trinityaccord.org/api/context-action-profiles.v1.json",
        "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
        "https://www.trinityaccord.org/api/verification-claim-model.v1.json",
    ]
)


def fail(message: str) -> None:
    raise AssertionError(message)


def run(
    args: list[str],
    *,
    cwd: Path,
    expect: int | None = 0,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    if expect is not None and result.returncode != expect:
        fail(
            f"command failed ({result.returncode}, expected {expect}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout[-4000:]}\n"
            f"stderr:\n{result.stderr[-4000:]}"
        )
    return result


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"expected JSON object: {path}")
    return value


def copy_repository(destination: Path) -> None:
    excluded = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "diagnostics",
    }

    def ignore(_: str, names: list[str]) -> set[str]:
        return {name for name in names if name in excluded}

    shutil.copytree(ROOT, destination, ignore=ignore, dirs_exist_ok=True)


def oath(sandbox: Path, record_type: str) -> str:
    result = run(
        [
            "node",
            str(BUILDER_REL),
            "print-oath",
            "--record-type",
            record_type,
        ],
        cwd=sandbox,
    )
    text = result.stdout
    if not text.strip() or "=== " not in text:
        fail(f"canonical oath missing for {record_type}")
    return text


def common_formal_args(
    sandbox: Path,
    *,
    record_type: str,
    key_dir: Path,
    output: Path,
    actor: str,
) -> list[str]:
    return [
        "--actor-label",
        actor,
        "--provider",
        "Isolated Full Lifecycle Audit",
        "--action-profile",
        "verification" if record_type == "verification" else "record_action",
        "--context-level",
        "CC-3",
        "--context-sufficient-for-selected-action",
        "true",
        "--context-read-confirmed",
        "true",
        "--loaded-urls",
        LOADED_URLS,
        "--discovery-mode",
        "user_task_context",
        "--requesting-party-type",
        "human",
        "--introducing-party-type",
        "human",
        "--record-decision",
        "human",
        "--submission-executor",
        "self",
        "--human-operator-involved",
        "false",
        "--readback",
        oath(sandbox, record_type),
        "--key-dir",
        str(key_dir),
        "--out",
        str(output),
    ]


def build_formal(
    sandbox: Path,
    *,
    record_type: str,
    key_dir: Path,
    output_name: str,
    specific: list[str],
    actor: str = "Lifecycle Audit Agent",
) -> dict[str, Any]:
    output = sandbox / output_name
    command = FORMAL_TO_COMMAND[record_type]
    args = ["node", str(BUILDER_REL), command]
    args += specific
    args += common_formal_args(
        sandbox,
        record_type=record_type,
        key_dir=key_dir,
        output=output,
        actor=actor,
    )
    run(args, cwd=sandbox)
    run(
        ["node", str(BUILDER_REL), "doctor", "--file", str(output)],
        cwd=sandbox,
    )
    submission = load_json(output)
    if submission.get("record_type") != record_type:
        fail(f"Builder route mismatch for {record_type}: {submission.get('record_type')}")
    return submission


def build_context_insufficient(
    sandbox: Path,
    *,
    key_dir: Path,
    output_name: str,
) -> dict[str, Any]:
    output = sandbox / output_name
    run(
        [
            "node",
            str(BUILDER_REL),
            "context-insufficient",
            "--actor-label",
            "Lifecycle Context-Limited Agent",
            "--provider",
            "Isolated Full Lifecycle Audit",
            "--body",
            "The isolated agent intentionally lacks sufficient context for a stronger action.",
            "--context-level",
            "CC-0",
            "--context-sufficient-for-selected-action",
            "false",
            "--discovery-mode",
            "user_task_context",
            "--requesting-party-type",
            "human",
            "--introducing-party-type",
            "human",
            "--record-decision",
            "self",
            "--submission-executor",
            "self",
            "--human-operator-involved",
            "false",
            "--key-dir",
            str(key_dir),
            "--out",
            str(output),
        ],
        cwd=sandbox,
    )
    run(
        ["node", str(BUILDER_REL), "doctor", "--file", str(output)],
        cwd=sandbox,
    )
    submission = load_json(output)
    if submission.get("record_type") != "context_insufficient_notice":
        fail("context-insufficient Builder route mismatch")
    if "client_oath_readback" in submission:
        fail("context_insufficient_notice must remain oath-exempt")
    return submission


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FilesystemContentsAdapter:
    """Minimal GitHub Contents API semantics backed by the isolated copy."""

    def __init__(self, root: Path):
        self.root = root
        self.dispatches: list[tuple[str, str | None]] = []
        self.write_count = 0

    def _path(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if self.root.resolve() not in path.parents and path != self.root.resolve():
            raise RuntimeError(f"path escaped sandbox: {relative}")
        return path

    async def get_file_sha(self, path: str) -> str | None:
        target = self._path(path)
        return sha256_bytes(target.read_bytes()) if target.exists() else None

    async def get_file_text(self, path: str) -> str | None:
        target = self._path(path)
        return target.read_text(encoding="utf-8") if target.exists() else None

    async def put_file(
        self,
        path: str,
        content: str,
        message: str,
        sha: str | None = None,
    ) -> dict[str, Any]:
        del message
        target = self._path(path)
        if target.exists():
            current = sha256_bytes(target.read_bytes())
            if sha is None:
                raise RuntimeError(f"create-only path already exists: {path}")
            if current != sha:
                raise RuntimeError(f"update SHA mismatch for {path}")
        elif sha is not None:
            raise RuntimeError(f"update target does not exist: {path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        digest = sha256_bytes(target.read_bytes())
        self.write_count += 1
        return {"content": {"sha": digest}, "commit": {"sha": digest}}

    async def delete_file(self, path: str, message: str, sha: str) -> dict[str, Any]:
        del message
        target = self._path(path)
        if not target.exists():
            raise RuntimeError(f"delete target missing: {path}")
        current = sha256_bytes(target.read_bytes())
        if current != sha:
            raise RuntimeError(f"delete SHA mismatch for {path}")
        target.unlink()
        return {"commit": {"sha": current}}

    async def dispatch_workflow(
        self,
        workflow_file: str,
        ref: str | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> None:
        del inputs
        self.dispatches.append((workflow_file, ref))


def patch_gateway(adapter: FilesystemContentsAdapter):
    # Import after dependencies are available, but use the working-tree code that
    # is also copied into the sandbox and later exercised by append/verify.
    sys.path.insert(0, str(ROOT))
    from apps.record_chain_intake_gateway import app as gateway_app  # noqa: WPS433

    gateway_app.put_file = adapter.put_file
    gateway_app.get_file_sha = adapter.get_file_sha
    gateway_app.get_file_text = adapter.get_file_text
    gateway_app.delete_file = adapter.delete_file
    gateway_app.dispatch_workflow = adapter.dispatch_workflow
    gateway_app.check_rate_limit = lambda body: None
    gateway_app.check_preflight_rate_limit = lambda client: None
    gateway_app._WRITE_MODE = "github_contents_pending"
    gateway_app._DISPATCH_APPEND_WORKFLOW = False
    gateway_app._receipt_store.clear()
    return gateway_app


def diagnostics_codes(payload: dict[str, Any]) -> set[str]:
    return {
        str(item.get("code"))
        for item in payload.get("diagnostics", [])
        if isinstance(item, dict) and item.get("code")
    }


def preflight(client: TestClient, submission: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/record-chain/preflight", json=submission)
    if response.status_code != 200:
        fail(f"preflight HTTP {response.status_code}: {response.text}")
    payload = response.json()
    if not payload.get("accepted"):
        fail(f"preflight rejected {submission.get('record_type')}: {payload}")
    return payload


def submit(client: TestClient, submission: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/record-chain/submit", json=submission)
    if response.status_code != 200:
        fail(f"submit HTTP {response.status_code}: {response.text}")
    payload = response.json()
    if not payload.get("accepted") or not payload.get("submitted"):
        fail(f"submit rejected {submission.get('record_type')}: {payload}")
    return payload


def append_gateway_result(sandbox: Path, result: dict[str, Any]) -> dict[str, Any]:
    pending = result.get("pending_file_path")
    receipt_id = result.get("receipt_id")
    if not isinstance(pending, str) or not pending:
        fail(f"submit result missing pending_file_path: {result}")
    if not isinstance(receipt_id, str) or not receipt_id:
        fail(f"submit result missing receipt_id: {result}")
    run(
        [
            sys.executable,
            str(CHAIN_TOOL_REL),
            "append",
            "--pending-file",
            pending,
            "--receipt-id",
            receipt_id,
        ],
        cwd=sandbox,
        timeout=180,
    )
    status_path = sandbox / "record-chain" / "receipt-status" / f"{receipt_id}.json"
    status = load_json(status_path)
    if status.get("append_status") != "appended":
        fail(f"receipt did not reach appended: {status}")
    final_path = sandbox / str(status.get("final_record_path"))
    final = load_json(final_path)
    if final.get("record_sha256") != status.get("final_record_sha256"):
        fail("receipt status final hash mismatch")
    return final


def build_and_append(
    client: TestClient,
    sandbox: Path,
    submission: dict[str, Any],
    *,
    duplicate_before_append: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    preflight(client, submission)
    first = submit(client, submission)
    if duplicate_before_append:
        duplicate = submit(client, submission)
        if duplicate.get("receipt_id") != first.get("receipt_id"):
            fail("idempotent duplicate returned a different receipt")
        if "duplicate" not in str(duplicate.get("append_status", "")):
            fail(f"duplicate submission did not report duplicate status: {duplicate}")
    final = append_gateway_result(sandbox, first)
    return first, final


def build_guardian_cc2_negative(sandbox: Path, key_dir: Path) -> None:
    output = sandbox / "negative-guardian-cc2.json"
    command = [
        "node",
        str(BUILDER_REL),
        "guardian-application",
        "--actor-label",
        "Insufficient Guardian",
        "--provider",
        "Isolated Full Lifecycle Audit",
        "--guardian-id",
        "auto",
        "--guardian-key-sha",
        "auto",
        "--context-level",
        "CC-2",
        "--context-sufficient-for-selected-action",
        "false",
        "--discovery-mode",
        "user_task_context",
        "--requesting-party-type",
        "human",
        "--introducing-party-type",
        "human",
        "--record-decision",
        "self",
        "--submission-executor",
        "self",
        "--human-operator-involved",
        "false",
        "--readback",
        oath(sandbox, "guardian_application"),
        "--key-dir",
        str(key_dir),
        "--out",
        str(output),
    ]
    built = run(command, cwd=sandbox, expect=None)
    if built.returncode == 0:
        doctor = run(
            ["node", str(BUILDER_REL), "doctor", "--file", str(output)],
            cwd=sandbox,
            expect=None,
        )
        if doctor.returncode == 0:
            fail("CC-2 guardian application unexpectedly passed Builder doctor")


def build_retired_v6_negative(sandbox: Path, key_dir: Path) -> None:
    output = sandbox / "negative-v6.json"
    args = [
        "node",
        str(BUILDER_REL),
        "verification",
        "--actor-label",
        "Retired Level Probe",
        "--provider",
        "Isolated Full Lifecycle Audit",
        "--verification-level",
        "V6",
        "--scope-label",
        "retired-label-probe",
        "--what-was-checked",
        "nothing",
        "--verification-claim",
        "No claim",
        "--fresh-actions",
        "none",
        "--digital-profile",
        "context_only",
        "--relationships-checked",
        "provides_context",
        "--physical-observation",
        "none",
        "--external-witness",
        "none",
        "--coverage-scope",
        "single_target",
        "--limitations",
        "negative test",
        "--claims-not-made",
        "verification success",
        "--corrections-or-supersession-checked",
        "false",
    ]
    args += common_formal_args(
        sandbox,
        record_type="verification",
        key_dir=key_dir,
        output=output,
        actor="Retired Level Probe",
    )
    result = run(args, cwd=sandbox, expect=None)
    if result.returncode == 0:
        fail("retired V6 label unexpectedly built a new public verification record")
    combined = (result.stdout + result.stderr).lower()
    if "historical" not in combined and "v0-v5" not in combined:
        fail(f"retired V6 failure did not explain current policy: {combined[-1000:]}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="trinity-full-lifecycle-") as tmp:
        sandbox = Path(tmp) / "repo"
        copy_repository(sandbox)

        adapter = FilesystemContentsAdapter(sandbox)
        gateway_app = patch_gateway(adapter)

        key_a = sandbox / ".audit-keys" / "agent-a"
        key_b = sandbox / ".audit-keys" / "agent-b"
        key_guardian = sandbox / ".audit-keys" / "guardian"

        matrix: dict[str, dict[str, Any]] = {}

        with TestClient(gateway_app.app) as client:
            echo = build_formal(
                sandbox,
                record_type="echo",
                key_dir=key_a,
                output_name="echo.json",
                specific=["--body", "An isolated end-to-end lifecycle echo."],
            )
            echo_submit, echo_final = build_and_append(
                client, sandbox, echo, duplicate_before_append=True
            )
            matrix["echo"] = {
                "receipt_id": echo_submit["receipt_id"],
                "record_id": echo_final["record_id"],
                "idempotency_checked": True,
            }

            verification = build_formal(
                sandbox,
                record_type="verification",
                key_dir=key_a,
                output_name="verification.json",
                specific=[
                    "--verification-level",
                    "V0",
                    "--scope-label",
                    "legacy V0 compatibility",
                    "--what-was-checked",
                    "isolated Builder and lifecycle route",
                    "--verification-claim",
                    "This record reports a context-only isolated lifecycle exercise.",
                    "--fresh-actions",
                    "built submission,ran doctor,used isolated gateway",
                    "--digital-profile",
                    "context_only",
                    "--relationships-checked",
                    "provides_context",
                    "--physical-observation",
                    "none",
                    "--external-witness",
                    "none",
                    "--coverage-scope",
                    "single_target",
                    "--limitations",
                    "isolated simulation,no external network verification",
                    "--claims-not-made",
                    "external validity,digital integrity,physical identity,institutional endorsement",
                    "--corrections-or-supersession-checked",
                    "false",
                ],
            )
            verification_submit, verification_final = build_and_append(
                client, sandbox, verification
            )
            model = verification_final.get("verification_content", {}).get(
                "verification_claim_model", {}
            )
            if model.get("digital_profile") != "context_only":
                fail("verification multidimensional model was lost before final append")
            matrix["verification"] = {
                "receipt_id": verification_submit["receipt_id"],
                "record_id": verification_final["record_id"],
                "digital_profile": model.get("digital_profile"),
            }

            propagation = build_formal(
                sandbox,
                record_type="propagation",
                key_dir=key_a,
                output_name="propagation.json",
                specific=["--body", "Isolated propagation action for lifecycle testing."],
            )
            propagation_submit, propagation_final = build_and_append(
                client, sandbox, propagation
            )
            matrix["propagation"] = {
                "receipt_id": propagation_submit["receipt_id"],
                "record_id": propagation_final["record_id"],
            }

            context_notice = build_context_insufficient(
                sandbox,
                key_dir=key_a,
                output_name="context-insufficient.json",
            )
            context_submit, context_final = build_and_append(
                client, sandbox, context_notice
            )
            matrix["context_insufficient_notice"] = {
                "receipt_id": context_submit["receipt_id"],
                "record_id": context_final["record_id"],
                "oath_exempt": True,
            }

            guardian_application = build_formal(
                sandbox,
                record_type="guardian_application",
                key_dir=key_guardian,
                output_name="guardian-application.json",
                specific=["--guardian-id", "auto", "--guardian-key-sha", "auto"],
                actor="Lifecycle Audit Guardian",
            )
            guardian_submit, guardian_final = build_and_append(
                client, sandbox, guardian_application
            )
            guardian_content = guardian_final.get("guardian_application_content", {})
            guardian_id = guardian_content.get("requested_guardian_identifier")
            if not isinstance(guardian_id, str) or not guardian_id.startswith("guardian_ed25519_"):
                fail(f"invalid derived Guardian id: {guardian_id}")
            matrix["guardian_application"] = {
                "receipt_id": guardian_submit["receipt_id"],
                "record_id": guardian_final["record_id"],
                "guardian_id": guardian_id,
            }

            guardian_retirement = build_formal(
                sandbox,
                record_type="guardian_retirement",
                key_dir=key_guardian,
                output_name="guardian-retirement.json",
                specific=[
                    "--guardian-id",
                    "auto",
                    "--guardian-key-sha",
                    "auto",
                    "--body",
                    "Voluntary isolated lifecycle retirement.",
                    "--target-guardian-application-record-id",
                    str(guardian_final["record_id"]),
                    "--target-guardian-application-record-sha256",
                    str(guardian_final["record_sha256"]),
                ],
                actor="Lifecycle Audit Guardian",
            )
            retirement_draft = guardian_retirement.get("record_draft", {})
            if retirement_draft.get("guardian_id") != guardian_id:
                fail(
                    "guardian-retirement --guardian-id auto did not derive the application Guardian id"
                )
            retirement_submit, retirement_final = build_and_append(
                client, sandbox, guardian_retirement
            )
            matrix["guardian_retirement"] = {
                "receipt_id": retirement_submit["receipt_id"],
                "record_id": retirement_final["record_id"],
                "guardian_id": retirement_final.get("guardian_id"),
            }

            correction = build_formal(
                sandbox,
                record_type="correction",
                key_dir=key_a,
                output_name="correction.json",
                specific=[
                    "--body",
                    "Append-only clarification of the isolated echo wording.",
                    "--target-record-id",
                    str(echo_final["record_id"]),
                    "--target-record-sha256",
                    str(echo_final["record_sha256"]),
                    "--correction-reason",
                    "Clarify the bounded test-only scope.",
                    "--corrected-fields-or-claims",
                    "echo_content.echo_text",
                    "--evidence-or-review-basis",
                    "Fresh isolated lifecycle review.",
                ],
            )
            correction_submit, correction_final = build_and_append(
                client, sandbox, correction
            )
            matrix["correction"] = {
                "receipt_id": correction_submit["receipt_id"],
                "record_id": correction_final["record_id"],
                "same_author_enforced": True,
            }

            third_party_correction = build_formal(
                sandbox,
                record_type="correction",
                key_dir=key_b,
                output_name="third-party-correction.json",
                specific=[
                    "--body",
                    "This must not be accepted as an author correction.",
                    "--target-record-id",
                    str(echo_final["record_id"]),
                    "--target-record-sha256",
                    str(echo_final["record_sha256"]),
                    "--correction-reason",
                    "Negative author-binding test.",
                    "--corrected-fields-or-claims",
                    "echo_content.echo_text",
                    "--evidence-or-review-basis",
                    "Different signing key.",
                ],
                actor="Independent Classification Agent",
            )
            rejected = client.post(
                "/record-chain/preflight", json=third_party_correction
            ).json()
            if rejected.get("accepted") is not False:
                fail("third-party correction unexpectedly passed preflight")
            if "CORRECTION_TARGET_AUTHOR_MISMATCH" not in diagnostics_codes(rejected):
                fail(f"third-party correction returned wrong diagnostics: {rejected}")

            classification = build_formal(
                sandbox,
                record_type="classification_update",
                key_dir=key_b,
                output_name="classification-update.json",
                specific=[
                    "--target-record-id",
                    str(echo_final["record_id"]),
                    "--target-record-sha256",
                    str(echo_final["record_sha256"]),
                    "--previous-classification",
                    "unclassified",
                    "--new-classification",
                    "isolated_lifecycle_test",
                    "--classification-reason",
                    "Bounded third-party test classification.",
                    "--evidence-or-review-basis",
                    "Independent isolated lifecycle review.",
                ],
                actor="Independent Classification Agent",
            )
            classification_submit, classification_final = build_and_append(
                client, sandbox, classification
            )
            matrix["classification_update"] = {
                "receipt_id": classification_submit["receipt_id"],
                "record_id": classification_final["record_id"],
                "third_party_route_checked": True,
            }

            bad_oath = copy.deepcopy(echo)
            bad_oath["client_oath_readback"]["readback_text"] += " altered"
            bad_response = client.post("/record-chain/preflight", json=bad_oath).json()
            if bad_response.get("accepted") is not False:
                fail("altered oath readback unexpectedly passed preflight")
            if not any("OATH" in code for code in diagnostics_codes(bad_response)):
                fail(f"altered oath returned no oath diagnostic: {bad_response}")

            wrong_key_retirement = build_formal(
                sandbox,
                record_type="guardian_retirement",
                key_dir=key_b,
                output_name="wrong-key-retirement.json",
                specific=[
                    "--guardian-id",
                    "auto",
                    "--guardian-key-sha",
                    "auto",
                    "--body",
                    "Wrong-key retirement must fail.",
                    "--target-guardian-application-record-id",
                    str(guardian_final["record_id"]),
                    "--target-guardian-application-record-sha256",
                    str(guardian_final["record_sha256"]),
                ],
                actor="Independent Classification Agent",
            )
            wrong_retirement_response = client.post(
                "/record-chain/preflight", json=wrong_key_retirement
            ).json()
            if wrong_retirement_response.get("accepted") is not False:
                fail("wrong-key Guardian retirement unexpectedly passed preflight")

        build_guardian_cc2_negative(sandbox, sandbox / ".audit-keys" / "cc2")
        build_retired_v6_negative(sandbox, sandbox / ".audit-keys" / "v6")

        run(
            [sys.executable, str(CHAIN_TOOL_REL), "verify"],
            cwd=sandbox,
            timeout=240,
        )

        guardian_state = load_json(
            sandbox / "record-chain" / "indexes" / "guardian-state.json"
        )
        guardian_entries = [
            entry
            for entry in guardian_state.get("guardians", [])
            if isinstance(entry, dict) and entry.get("guardian_id") == guardian_id
        ]
        if len(guardian_entries) != 1:
            fail(f"expected one derived Guardian lifecycle entry, got {guardian_entries}")
        guardian_entry = guardian_entries[0]
        if guardian_entry.get("current_derived_status") != "retired_guardian":
            fail(f"Guardian did not reach retired state: {guardian_entry}")
        if guardian_entry.get("retirement_record_id") != retirement_final.get("record_id"):
            fail("derived Guardian state is not bound to the retirement record")

        expected_types = {
            "echo",
            "verification",
            "guardian_application",
            "guardian_retirement",
            "propagation",
            "correction",
            "classification_update",
            "context_insufficient_notice",
        }
        observed_types = {
            load_json(path).get("record_type")
            for path in (sandbox / "record-chain" / "records").glob("R-*.json")
            if path.stem in {item["record_id"] for item in matrix.values()}
        }
        if observed_types != expected_types:
            fail(f"final action matrix mismatch: {observed_types} != {expected_types}")

        if adapter.write_count < 8 * 4:
            fail(f"Gateway durable-write coverage unexpectedly low: {adapter.write_count}")

        print(json.dumps({
            "schema": "trinityaccord.full-public-action-lifecycle-e2e.v1",
            "passed": True,
            "actions": matrix,
            "negative_paths": {
                "altered_oath_rejected": True,
                "cc2_guardian_rejected": True,
                "retired_v6_rejected": True,
                "third_party_correction_rejected": True,
                "third_party_classification_accepted": True,
                "wrong_key_retirement_rejected": True,
            },
            "final_chain_verify": "passed",
            "guardian_final_status": guardian_entry.get("current_derived_status"),
            "gateway_write_count": adapter.write_count,
        }, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
