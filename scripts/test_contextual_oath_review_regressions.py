#!/usr/bin/env python3
"""Regression coverage for the post-merge contextual-oath review findings."""
from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
import os
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from apps.record_chain_intake_gateway.gateway import validation
from contextual_readback_bundle import (
    BUNDLE_SCHEMA,
    ReadbackBundleError,
    load_contextual_readbacks,
)
import smoke_live_external_agent_three_core_preflight as three_core
import smoke_external_agent_write_lifecycle_canary as lifecycle
import trinity_record_chain as chain


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_policy_downgrade_is_bound_to_immutable_history() -> None:
    historical = json.loads(
        (ROOT / "record-chain/records/R-000000089.json").read_text(encoding="utf-8")
    )
    errors: list[str] = []
    chain._verify_oath_in_record(historical, "R-000000089.json", errors)
    require(not errors, f"immutable v1.1 historical record must remain valid: {errors}")
    require(
        chain.record_requires_contextual_readback(historical) is False,
        "R-000000089 must be recognized from append-assigned identity, not version",
    )
    wrong_historical_policy = copy.deepcopy(historical)
    wrong_historical_policy["submission_oath_verification"][
        "oath_policy_sha256"
    ] = "6327c8fbf16cb859d951c42f77c7e185c453df5f05cd648ff94c7eca4d3caf7d"
    errors = []
    chain._verify_oath_in_record(
        wrong_historical_policy,
        "R-000000089.json",
        errors,
    )
    require(
        any("historical oath policy identity is not recognized" in error for error in errors),
        "a historical record must not substitute a policy from another old index range",
    )

    downgraded = copy.deepcopy(historical)
    downgraded["record_id"] = "R-000000103"
    downgraded["record_index"] = 103
    downgraded["record_sha256"] = "a" * 64
    downgraded_oath = downgraded["submission_oath_verification"]
    for field in chain.CONTEXTUAL_READBACK_REQUIRED_DECLARATIONS:
        downgraded_oath.pop(field, None)

    errors = []
    chain._verify_oath_in_record(downgraded, "R-000000103.json", errors)
    require(
        any("oath policy must equal current" in error for error in errors),
        f"new record with v1.1 policy must fail current policy identity: {errors}",
    )
    require(
        any("contextual" in error for error in errors),
        f"new record must require contextual declarations regardless of claimed version: {errors}",
    )
    try:
        chain.require_pending_oath_is_appendable(
            downgraded,
            next_index=103,
            source_path=ROOT
            / "record-chain/pending/contextual-oath-review-fixture.echo.pending.json",
        )
    except ValueError as exc:
        require(
            "pending oath verification failed" in str(exc),
            "append rejection must identify the pre-mutation oath gate",
        )
    else:
        raise AssertionError(
            "append must reject a downgraded post-activation oath before mutation"
        )

    downgraded_oath["oath_policy_version"] = "not-a-version"
    errors = []
    chain._verify_oath_in_record(downgraded, "R-000000103.json", errors)
    require(
        any("oath policy must equal current" in error for error in errors),
        "unparsable participant-controlled version must fail closed",
    )

    activation = chain._guardian_activation_assessment(
        downgraded,
        guardian_id_counts={
            downgraded["guardian_application_content"]["requested_guardian_identifier"]: 1
        },
        guardian_key_counts={
            downgraded["guardian_application_content"]["guardian_public_key_sha256"]: 1
        },
    )
    require(
        "contextual_oath_policy_not_current" in activation["blocking_reasons"],
        f"downgraded new Guardian application must not activate: {activation}",
    )

    current = copy.deepcopy(downgraded)
    oath = current["submission_oath_verification"]
    oath["oath_policy"] = chain.CURRENT_OATH_POLICY_ID
    oath["oath_policy_schema"] = chain.CURRENT_OATH_POLICY_SCHEMA
    oath["oath_policy_version"] = chain.CURRENT_OATH_POLICY_VERSION
    oath["oath_policy_sha256"] = chain.CURRENT_OATH_POLICY_SHA256
    oath["oath_modules"] = chain.CURRENT_OATH_POLICY["record_type_modules"][
        "guardian_application"
    ]
    oath["readback_method_declared"] = "participant_generated_in_current_context"
    for field in chain.CONTEXTUAL_READBACK_REQUIRED_DECLARATIONS:
        oath[field] = True
    expected_canonical = chain._current_canonical_oath(
        current,
        "guardian_application",
    )
    require(expected_canonical is not None, "current Guardian oath must be canonicalizable")
    oath["canonical_oath_text_sha256"] = expected_canonical[1]
    oath["participant_readback_sha256"] = expected_canonical[1]
    errors = []
    chain._verify_oath_in_record(current, "R-000000103.json", errors)
    require(not errors, f"fully current post-activation oath must pass: {errors}")

    missing_legacy_declaration = copy.deepcopy(current)
    missing_legacy_declaration["submission_oath_verification"][
        "readback_was_not_generated_by_external_automation"
    ] = False
    errors = []
    chain._verify_oath_in_record(
        missing_legacy_declaration,
        "R-000000103.json",
        errors,
    )
    require(
        any(
            "readback_was_not_generated_by_external_automation is not true"
            in error
            for error in errors
        ),
        "current final records must enforce every declaration in the exact policy",
    )
    activation = chain._guardian_activation_assessment(
        missing_legacy_declaration,
        guardian_id_counts={
            missing_legacy_declaration["guardian_application_content"][
                "requested_guardian_identifier"
            ]: 1
        },
        guardian_key_counts={
            missing_legacy_declaration["guardian_application_content"][
                "guardian_public_key_sha256"
            ]: 1
        },
    )
    require(
        "contextual_oath_readback_not_verified" in activation["blocking_reasons"],
        "Guardian activation must enforce the current policy's full declaration set",
    )

    arbitrary_equal_hashes = copy.deepcopy(current)
    arbitrary_equal_hashes["submission_oath_verification"][
        "canonical_oath_text_sha256"
    ] = "f" * 64
    arbitrary_equal_hashes["submission_oath_verification"][
        "participant_readback_sha256"
    ] = "f" * 64
    errors = []
    chain._verify_oath_in_record(
        arbitrary_equal_hashes,
        "R-000000103.json",
        errors,
    )
    require(
        any("canonical text hash does not match current policy" in error for error in errors),
        "two equal arbitrary hashes must not replace the policy-derived canonical oath hash",
    )
    activation = chain._guardian_activation_assessment(
        arbitrary_equal_hashes,
        guardian_id_counts={
            arbitrary_equal_hashes["guardian_application_content"][
                "requested_guardian_identifier"
            ]: 1
        },
        guardian_key_counts={
            arbitrary_equal_hashes["guardian_application_content"][
                "guardian_public_key_sha256"
            ]: 1
        },
    )
    require(
        "contextual_oath_readback_not_verified" in activation["blocking_reasons"],
        "Guardian activation must recompute the current canonical oath hash",
    )

    extra_module = copy.deepcopy(current)
    extra_module["submission_oath_verification"]["oath_modules"] = [
        *oath["oath_modules"],
        "unrecognized_module",
    ]
    activation = chain._guardian_activation_assessment(
        extra_module,
        guardian_id_counts={
            extra_module["guardian_application_content"][
                "requested_guardian_identifier"
            ]: 1
        },
        guardian_key_counts={
            extra_module["guardian_application_content"][
                "guardian_public_key_sha256"
            ]: 1
        },
    )
    require(
        "contextual_oath_modules_invalid" in activation["blocking_reasons"],
        "Guardian activation must require the exact current module sequence",
    )

    linked_echo = json.loads(
        (ROOT / "record-chain/records/R-000000088.json").read_text(encoding="utf-8")
    )
    linked_echo["record_id"] = "R-000000103"
    linked_echo["record_index"] = 103
    linked_echo["optional_linked_guardian_application_request"] = {
        "does_participant_request_guardian_application_with_this_record": True
    }
    linked_oath = linked_echo["submission_oath_verification"]
    linked_oath["oath_policy"] = chain.CURRENT_OATH_POLICY_ID
    linked_oath["oath_policy_schema"] = chain.CURRENT_OATH_POLICY_SCHEMA
    linked_oath["oath_policy_version"] = chain.CURRENT_OATH_POLICY_VERSION
    linked_oath["oath_policy_sha256"] = chain.CURRENT_OATH_POLICY_SHA256
    linked_oath["oath_modules"] = chain._current_oath_modules_for_record(
        linked_echo,
        "echo",
    )
    linked_oath["readback_method_declared"] = (
        "participant_generated_in_current_context"
    )
    for field in chain.CONTEXTUAL_READBACK_REQUIRED_DECLARATIONS:
        linked_oath[field] = True
    linked_expected = chain._current_canonical_oath(linked_echo, "echo")
    require(linked_expected is not None, "linked Echo oath must be canonicalizable")
    linked_oath["canonical_oath_text_sha256"] = linked_expected[1]
    linked_oath["participant_readback_sha256"] = linked_expected[1]
    errors = []
    chain._verify_oath_in_record(linked_echo, "R-000000103.json", errors)
    require(
        not errors,
        f"current linked-Guardian Echo must accept its policy-defined extra module: {errors}",
    )


def test_gateway_rolling_policy_is_exact_and_bounded() -> None:
    current = json.loads(
        (ROOT / "api/record-chain-oath-policy.v1.json").read_text(encoding="utf-8")
    )
    current_hash = validation.compute_oath_policy_sha256(current)
    resolved, mode = validation.resolve_submission_oath_policy(current_hash, current)
    require(resolved == current and mode == "current", "current policy must resolve locally")
    require(
        validation.ROLLING_PREDECESSOR_POLICY_IDENTITIES.get(
            "27a2f8ce244542e6ca76e9f75f6e4c95745b0e5e007d274a6b4b3228b67f6b51"
        )
        == "1.1.0",
        "rolling compatibility must be pinned to the exact public v1.1 predecessor",
    )

    corrupt_current = copy.deepcopy(current)
    corrupt_current["oath_policy_sha256"] = "0" * 64
    resolved, mode = validation.resolve_submission_oath_policy(
        current_hash,
        corrupt_current,
    )
    require(
        resolved is None and mode == "current_policy_hash_metadata_mismatch",
        "Gateway must fail closed if its local policy self-hash metadata drifts",
    )

    previous = copy.deepcopy(current)
    previous["version"] = "1.1.0"
    legacy_declarations = (
        "oath_read",
        "participant_readback_provided",
        "readback_matches_canonical_oath",
        "readback_was_not_piped_from_file",
        "readback_was_not_generated_by_script",
        "readback_was_not_loaded_from_cache",
        "readback_was_not_summary_or_paraphrase",
        "readback_was_not_generated_by_external_automation",
        "readback_was_not_auto_filled_by_builder",
        "no_shortcut_oath_acknowledged",
    )
    legacy_boundaries = (
        "oath_does_not_prove_subjective_understanding",
        "oath_verifies_exact_readback_only",
    )
    previous["no_shortcut_policy"]["required_declarations"] = list(
        legacy_declarations
    )
    previous["no_shortcut_policy"]["boundary"] = {
        field: True for field in legacy_boundaries
    }
    previous_hash = validation.compute_oath_policy_sha256(previous)
    previous["oath_policy_sha256"] = previous_hash

    original_loader = validation.load_published_oath_policy
    original_predecessors = validation.ROLLING_PREDECESSOR_POLICY_IDENTITIES
    try:
        calls = 0

        def unexpected_loader() -> dict:
            nonlocal calls
            calls += 1
            raise AssertionError("unknown policy hash must not trigger public fetch")

        validation.load_published_oath_policy = unexpected_loader
        resolved, mode = validation.resolve_submission_oath_policy("a" * 64, current)
        require(
            resolved is None
            and mode == "not_current_or_known_predecessor"
            and calls == 0,
            "unknown hashes must be rejected locally without outbound fetch",
        )

        validation.ROLLING_PREDECESSOR_POLICY_IDENTITIES = {
            previous_hash: previous["version"]
        }
        validation.load_published_oath_policy = lambda: previous
        resolved, mode = validation.resolve_submission_oath_policy(previous_hash, current)
        require(
            resolved == previous and mode == "rolling_published",
            "exact policy still published with public Builder must be accepted during rollout",
        )

        modules = previous["record_type_modules"]["echo"]
        canonical_parts = []
        for module_id in modules:
            module = previous["modules"][module_id]
            text = unicodedata.normalize(
                "NFC",
                validation.normalize_oath_text(module["text"]),
            )
            canonical_parts.append(
                f"=== {module['label']} ({module_id}) ===\n\n{text}"
            )
        canonical = previous["canonicalization"]["module_joiner"].join(
            canonical_parts
        ).strip()
        canonical_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        legacy_oath = {
            "oath_policy": previous["policy_id"],
            "oath_policy_schema": previous["schema"],
            "oath_policy_version": previous["version"],
            "oath_policy_sha256": previous_hash,
            "oath_modules": modules,
            "canonical_oath_text_sha256": canonical_hash,
            "participant_readback_sha256": canonical_hash,
            "readback_method_declared": "participant_generated_in_current_context",
        }
        for field in (*legacy_declarations, *legacy_boundaries):
            legacy_oath[field] = True
        legacy_client_oath = {
            "record_type": "echo",
            "oath_policy_sha256": previous_hash,
            "oath_modules": modules,
            "readback_method_declared": "participant_generated_in_current_context",
            "readback_text": canonical,
            "readback_text_sha256": canonical_hash,
            "readback_text_char_count": len(canonical),
        }
        diagnostics = validation.validate_submission_oath(
            "echo",
            {"client_oath_readback": legacy_client_oath},
            {"submission_oath_verification": legacy_oath},
        )
        require(
            not diagnostics,
            "rolling compatibility must validate declarations from the exact "
            f"published v1.1-shaped policy: {[d.code for d in diagnostics]}",
        )

        validation.load_published_oath_policy = lambda: current
        resolved, mode = validation.resolve_submission_oath_policy(previous_hash, current)
        require(
            resolved is None and mode == "not_current_or_published",
            "old policy must stop being accepted as soon as Pages publishes current policy",
        )

        future = copy.deepcopy(current)
        future["version"] = "9.0.0"
        future_hash = validation.compute_oath_policy_sha256(future)
        future["oath_policy_sha256"] = future_hash
        validation.ROLLING_PREDECESSOR_POLICY_IDENTITIES = {
            future_hash: future["version"]
        }
        validation.load_published_oath_policy = lambda: future
        resolved, mode = validation.resolve_submission_oath_policy(future_hash, current)
        require(
            resolved is None and mode == "published_policy_not_older",
            "rolling compatibility must never let an older Gateway accept a future policy",
        )
    finally:
        validation.load_published_oath_policy = original_loader
        validation.ROLLING_PREDECESSOR_POLICY_IDENTITIES = original_predecessors


def test_gateway_published_policy_fetch_is_single_flight_cached() -> None:
    current = json.loads(
        (ROOT / "api/record-chain-oath-policy.v1.json").read_text(encoding="utf-8")
    )
    original_fetch = validation._fetch_published_oath_policy
    calls = 0

    def fake_fetch(_url: str) -> dict:
        nonlocal calls
        calls += 1
        return current

    try:
        validation._reset_published_oath_policy_cache_for_tests()
        validation._fetch_published_oath_policy = fake_fetch
        first = validation.load_published_oath_policy()
        second = validation.load_published_oath_policy()
        require(first == current and second == current, "cached public policy must be stable")
        require(
            calls == 1,
            "repeated known-predecessor validation must not amplify public fetch latency",
        )

        def failing_fetch(_url: str) -> dict:
            nonlocal calls
            calls += 1
            raise OSError("simulated public policy outage")

        validation._reset_published_oath_policy_cache_for_tests()
        validation._fetch_published_oath_policy = failing_fetch
        for _attempt in range(2):
            try:
                validation.load_published_oath_policy()
            except (OSError, ValueError):
                pass
            else:
                raise AssertionError("public policy outage must fail closed")
        require(
            calls == 2,
            "a public policy outage must be negatively cached after one new fetch",
        )
    finally:
        validation._fetch_published_oath_policy = original_fetch
        validation._reset_published_oath_policy_cache_for_tests()


def test_smokes_only_relay_participant_bundle() -> None:
    readbacks = {
        "echo": "participant echo readback",
        "verification": "participant verification readback",
        "guardian_application": "participant guardian readback",
    }
    with tempfile.TemporaryDirectory(prefix="trinity-readback-regression-") as temp:
        work = Path(temp)
        bundle = work / "readbacks.json"
        bundle.write_text(
            json.dumps(
                {
                    "schema": BUNDLE_SCHEMA,
                    "participant": {"label": "Regression Participant"},
                    "participant_process_declaration": {
                        "canonical_oaths_loaded_into_participant_active_context": True,
                        "readbacks_generated_by_participant_from_active_context": True,
                        "readbacks_not_directly_copied_by_submission_tool": True,
                        "readbacks_not_automatically_completed_or_corrected": True,
                        "submission_tool_is_relay_only": True,
                    },
                    "readbacks": readbacks,
                }
            ),
            encoding="utf-8",
        )
        loaded = load_contextual_readbacks(bundle, three_core.CORE_RECORD_TYPES)
        require(loaded == readbacks, "bundle loader must preserve participant strings exactly")

        calls: list[list[str]] = []
        original_runner = three_core.run_builder

        def fake_runner(
            _builder: Path,
            args: list[str],
            cwd: Path,
            _timeout: int,
        ) -> str:
            calls.append(list(args))
            require(args[0] != "print-oath", "smoke must never copy print-oath output")
            out_name = args[args.index("--out") + 1]
            (cwd / out_name).write_text("{}\n", encoding="utf-8")
            return ""

        try:
            three_core.run_builder = fake_runner
            three_core._build_cases(
                work / "builder.mjs",
                "https://www.trinityaccord.org",
                work,
                10,
                readbacks=loaded,
            )
        finally:
            three_core.run_builder = original_runner

        require(len(calls) == 3, "three-core smoke must build exactly three cases")
        for args, expected in zip(calls, readbacks.values()):
            require(
                args[args.index("--readback") + 1] == expected,
                "smoke must relay each participant-provided readback unchanged",
            )

    previous_bundle = os.environ.pop("TRINITY_CONTEXTUAL_READBACK_BUNDLE", None)
    try:
        try:
            load_contextual_readbacks(None, three_core.CORE_RECORD_TYPES)
        except ReadbackBundleError:
            pass
        else:
            raise AssertionError("missing participant bundle must fail closed")
    finally:
        if previous_bundle is not None:
            os.environ["TRINITY_CONTEXTUAL_READBACK_BUNDLE"] = previous_bundle

    signature = inspect.signature(lifecycle.build_current_canary_payloads)
    require(
        "readbacks" in signature.parameters
        and signature.parameters["readbacks"].default is inspect.Parameter.empty,
        "write lifecycle canary must require participant-generated readbacks",
    )
    phase3_source = (
        ROOT / "scripts/run_phase3_live_serial_hash_ots_canary.py"
    ).read_text(encoding="utf-8")
    three_core_block = phase3_source.split("three_core_cmd = [", 1)[1].split(
        "]",
        1,
    )[0]
    require(
        '"--site"' in three_core_block
        and "args.site" in three_core_block
        and '"--timeout"' in three_core_block
        and "str(args.timeout)" in three_core_block,
        "phase3 runner must forward its selected site and timeout to three-core preflight",
    )


def test_injector_refuses_policy_only_upgrade() -> None:
    injector = load_module(
        ROOT / "scripts/inject_oath_into_builder.py",
        "inject_oath_review_regression",
    )
    policy = json.loads(
        (ROOT / "api/record-chain-oath-policy.v1.json").read_text(encoding="utf-8")
    )
    require(
        not injector.verify_existing_builder_runtime(
            (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8"),
            policy,
        ),
        "current Builder must satisfy the injector runtime compatibility contract",
    )
    with tempfile.TemporaryDirectory(prefix="trinity-injector-regression-") as temp:
        temp_root = Path(temp)
        builder = temp_root / "builder.mjs"
        policy_path = temp_root / "policy.json"
        old_runtime = (
            'const OATH_POLICY = {\n  "version": "1.1.0"\n};\n'
            'const OATH_POLICY_SHA256 = "' + ("a" * 64) + '";\n'
            "// print-oath exists, but contextual helpers do not\n"
        )
        policy["oath_policy_sha256"] = "0" * 64
        original_policy_text = json.dumps(policy)
        builder.write_text(old_runtime, encoding="utf-8")
        policy_path.write_text(original_policy_text, encoding="utf-8")
        injector.BUILDER = builder
        injector.OATH_POLICY = policy_path
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                injector.main()
            except SystemExit as exc:
                require(int(exc.code or 0) != 0, "incompatible upgrade must exit non-zero")
            else:
                raise AssertionError("policy-only upgrade of old Builder must be refused")
        require(
            "refusing policy-only synchronization" in stderr.getvalue(),
            "injector must explain that the existing helper runtime is incompatible",
        )
        require(
            builder.read_text(encoding="utf-8") == old_runtime,
            "injector must not partially rewrite an incompatible Builder",
        )
        require(
            policy_path.read_text(encoding="utf-8") == original_policy_text,
            "injector must not partially rewrite policy metadata before runtime validation",
        )


def test_pages_deploy_orders_gateway_before_public_builder() -> None:
    pages = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
    manual = (
        ROOT / ".github/workflows/render-manual-deploy.yml"
    ).read_text(encoding="utf-8")
    for marker in (
        "deploy-gateway-before-pages:",
        "- deploy-gateway-before-pages",
        "Deploy exact Gateway source and wait for live",
        '--commit-id "$SOURCE_SHA"',
        "--wait",
        "Refuse stale source if main moved after verification",
    ):
        require(marker in pages, f"Pages rollout contract missing: {marker}")
    for marker in ('--commit-id "$source_sha"', "--wait"):
        require(marker in manual, f"manual Render workflow missing: {marker}")


def test_public_recovery_guidance_preserves_contextual_authorship() -> None:
    helper = json.loads(
        (ROOT / "api/record-chain-field-helper.v1.json").read_text(encoding="utf-8")
    )
    diagnostic_help = helper["diagnostic_code_help"]
    for code in (
        "MISSING_CLIENT_OATH_READBACK",
        "OATH_CANONICAL_HASH_MISMATCH",
        "OATH_READBACK_MISSING",
        "OATH_READBACK_MISMATCH",
    ):
        fix = str(diagnostic_help[code]["fix"])
        require(
            "active context" in fix
            or "active-context" in fix
            or "contextual oath process" in fix
            or "contextual readback" in fix,
            f"{code} recovery must preserve the participant active-context process",
        )
        require(
            "then include it as client_oath_readback" not in fix,
            f"{code} must not instruct a submission tool to copy print-oath output",
        )


def main() -> int:
    tests = [
        test_policy_downgrade_is_bound_to_immutable_history,
        test_gateway_rolling_policy_is_exact_and_bounded,
        test_gateway_published_policy_fetch_is_single_flight_cached,
        test_smokes_only_relay_participant_bundle,
        test_injector_refuses_policy_only_upgrade,
        test_pages_deploy_orders_gateway_before_public_builder,
        test_public_recovery_guidance_preserves_contextual_authorship,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print("PASS: all contextual-oath post-merge review regressions are closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
