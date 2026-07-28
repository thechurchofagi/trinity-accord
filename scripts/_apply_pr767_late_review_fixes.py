#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_chain() -> None:
    path = "scripts/trinity_record_chain.py"
    text = read(path)
    old = '''HISTORICAL_OATH_POLICY_BY_RECORD_RANGE = (
    (1, 32, "1.0.0", "7ecc6908c9ac147d8d6d493f750c94d6117929e7dff2d18bcbc4c70527886ea4"),
    (33, 43, "1.0.0", "9356e8c0955d7f17814dff1a93300cb271acfa21cfe39da63a7b5201364cb820"),
    (44, 82, "1.0.0", "6327c8fbf16cb859d951c42f77c7e185c453df5f05cd648ff94c7eca4d3caf7d"),
    (83, 102, "1.1.0", "27a2f8ce244542e6ca76e9f75f6e4c95745b0e5e007d274a6b4b3228b67f6b51"),
)
'''
    new = old + '''
# Exact predecessor identities that the Gateway may admit only while the public
# Builder still publishes that policy during a bounded rollout. Append and final
# verification must preserve those already-accepted drafts instead of reclassifying
# them solely because their append-assigned record index is post-activation.
ROLLING_PREDECESSOR_OATH_POLICY_IDENTITIES = frozenset({
    ("1.1.0", "27a2f8ce244542e6ca76e9f75f6e4c95745b0e5e007d274a6b4b3228b67f6b51"),
})
'''
    text = replace_once(text, old, new, "insert rolling predecessor identities")

    old = '''def record_requires_contextual_readback(record: dict[str, Any]) -> bool:
    """Fail closed unless the record is provably from the pre-v1.2 history."""
    index = _record_index_from_identity(record)
    return index is None or index >= CONTEXTUAL_READBACK_ACTIVATION_RECORD_INDEX
'''
    new = '''def record_requires_contextual_readback(
    record: dict[str, Any],
    oath: dict[str, Any] | None = None,
) -> bool:
    """Select the oath contract from immutable history or an exact rollout identity.

    New records normally require the current contextual-readback policy. The only
    exception is a draft carrying an exact predecessor identity that the Gateway was
    allowed to accept while that same policy was still publicly published. Unknown
    or participant-invented identities continue to fail closed as contextual.
    """
    index = _record_index_from_identity(record)
    if index is not None and index < CONTEXTUAL_READBACK_ACTIVATION_RECORD_INDEX:
        return False
    if isinstance(oath, dict):
        identity = (
            str(oath.get("oath_policy_version") or ""),
            str(oath.get("oath_policy_sha256") or ""),
        )
        if identity in ROLLING_PREDECESSOR_OATH_POLICY_IDENTITIES:
            return False
    return True
'''
    text = replace_once(text, old, new, "replace contextual policy selector")

    old = '''    if record_requires_contextual_readback(record):
        return (
            oath.get("oath_policy") == CURRENT_OATH_POLICY_ID
            and oath.get("oath_policy_schema") == CURRENT_OATH_POLICY_SCHEMA
            and version == CURRENT_OATH_POLICY_VERSION
            and policy_hash == CURRENT_OATH_POLICY_SHA256
        )
    index = _record_index_from_identity(record)
'''
    new = '''    requires_contextual = record_requires_contextual_readback(record, oath)
    if requires_contextual:
        return (
            oath.get("oath_policy") == CURRENT_OATH_POLICY_ID
            and oath.get("oath_policy_schema") == CURRENT_OATH_POLICY_SCHEMA
            and version == CURRENT_OATH_POLICY_VERSION
            and policy_hash == CURRENT_OATH_POLICY_SHA256
        )
    if (version, policy_hash) in ROLLING_PREDECESSOR_OATH_POLICY_IDENTITIES:
        return (
            oath.get("oath_policy") == CURRENT_OATH_POLICY_ID
            and oath.get("oath_policy_schema") == CURRENT_OATH_POLICY_SCHEMA
        )
    index = _record_index_from_identity(record)
'''
    text = replace_once(text, old, new, "allow exact rolling predecessor identity")

    old = '''def _required_oath_true_fields_for_record(
    record: dict[str, Any],
) -> tuple[str, ...]:
    """Return the exact declaration set applicable to this immutable identity."""
    if record_requires_contextual_readback(record):
        return CURRENT_OATH_REQUIRED_TRUE_FIELDS
'''
    new = '''def _required_oath_true_fields_for_record(
    record: dict[str, Any],
    oath: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Return declarations for current, historical, or exact rollout policy."""
    if record_requires_contextual_readback(record, oath):
        return CURRENT_OATH_REQUIRED_TRUE_FIELDS
'''
    text = replace_once(text, old, new, "make required fields policy-aware")

    text = replace_once(
        text,
        '        requires_contextual = record_requires_contextual_readback(record)\n',
        '        requires_contextual = record_requires_contextual_readback(record, oath)\n',
        "guardian activation policy selector",
    )
    text = replace_once(
        text,
        '        for field in _required_oath_true_fields_for_record(record):\n',
        '        for field in _required_oath_true_fields_for_record(record, oath):\n',
        "guardian activation declarations",
    )
    text = replace_once(
        text,
        '        requires_contextual = record_requires_contextual_readback(obj)\n',
        '        requires_contextual = record_requires_contextual_readback(obj, oath)\n',
        "final oath policy selector",
    )
    text = replace_once(
        text,
        '        required_bools.extend(_required_oath_true_fields_for_record(obj))\n',
        '        required_bools.extend(_required_oath_true_fields_for_record(obj, oath))\n',
        "final oath declarations",
    )
    write(path, text)


def patch_app() -> None:
    path = "apps/record_chain_intake_gateway/app.py"
    text = read(path)
    text = replace_once(text, "import hashlib\n", "import asyncio\nimport hashlib\n", "import asyncio")
    old = "    diagnostics = validate_submission(body)\n"
    if text.count(old) != 2:
        raise RuntimeError(f"async validation: expected 2 calls, found {text.count(old)}")
    text = text.replace(
        old,
        "    diagnostics = await asyncio.to_thread(validate_submission, body)\n",
    )
    write(path, text)


def patch_canary_workflow() -> None:
    path = ".github/workflows/site-agent-write-lifecycle-canary.yml"
    text = read(path)
    text = replace_once(
        text,
        '''      confirm_live_canary:
        description: "Required exact phrase for write modes"
        required: false
        default: ""
  schedule:
    - cron: "17 6 * * *"
''',
        '''      confirm_live_canary:
        description: "Required exact phrase for write modes"
        required: false
        default: ""
      contextual_readback_bundle_b64:
        description: "Base64-encoded participant-generated contextual readback bundle JSON"
        required: true
        type: string
''',
        "replace unsatisfiable schedule with explicit participant bundle input",
    )
    text = replace_once(
        text,
        '  INPUT_CONFIRM_LIVE_CANARY: ${{ github.event.inputs.confirm_live_canary || \'\' }}\n',
        '  INPUT_CONFIRM_LIVE_CANARY: ${{ github.event.inputs.confirm_live_canary || \'\' }}\n  INPUT_CONTEXTUAL_READBACK_BUNDLE_B64: ${{ github.event.inputs.contextual_readback_bundle_b64 }}\n',
        "add bundle env",
    )
    text = replace_once(
        text,
        '''      - name: Run external write lifecycle canary
        run: |
          python3 scripts/smoke_external_agent_write_lifecycle_canary.py \\
            --site "$INPUT_SITE_URL" \\
            --mode "$INPUT_MODE" \\
            --route "$INPUT_ROUTE" \\
            --confirm-live-canary "$INPUT_CONFIRM_LIVE_CANARY"
''',
        '''      - name: Run external write lifecycle canary
        run: |
          set -euo pipefail
          bundle_path="$(mktemp)"
          trap 'rm -f "$bundle_path"' EXIT
          printf '%s' "$INPUT_CONTEXTUAL_READBACK_BUNDLE_B64" | base64 --decode > "$bundle_path"
          python3 scripts/smoke_external_agent_write_lifecycle_canary.py \\
            --site "$INPUT_SITE_URL" \\
            --mode "$INPUT_MODE" \\
            --route "$INPUT_ROUTE" \\
            --confirm-live-canary "$INPUT_CONFIRM_LIVE_CANARY" \\
            --readback-bundle "$bundle_path"
''',
        "pass participant bundle to canary",
    )
    write(path, text)


def patch_injector() -> None:
    path = "scripts/inject_oath_into_builder.py"
    text = read(path)
    text = replace_once(
        text,
        '''function buildSubmissionOathVerification(recordType, canonicalOath, readbackText) {{
  const readback = readbackText.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim();
''',
        '''function buildSubmissionOathVerification(recordType, canonicalOath, readbackText) {{
  const readback = readbackText.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim().normalize("NFC");
''',
        "normalize injected signed readback",
    )
    text = replace_once(
        text,
        '''function buildClientOathReadback(recordType, participantReadback) {{
  return {{
    schema: "trinityaccord.client-oath-readback.v1",
    record_type: recordType,
    oath_policy_sha256: OATH_POLICY_SHA256,
    oath_modules: getOathModules(recordType),
    readback_text: participantReadback,
    readback_text_sha256: sha256(participantReadback),
    readback_text_char_count: participantReadback.length,
    readback_method_declared: "participant_generated_in_current_context",
  }};
}}
''',
        '''function buildClientOathReadback(recordType, participantReadback) {{
  const normalized = participantReadback.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim().normalize("NFC");
  return {{
    schema: "trinityaccord.client-oath-readback.v1",
    record_type: recordType,
    oath_policy_sha256: OATH_POLICY_SHA256,
    oath_modules: getOathModules(recordType),
    readback_text: normalized,
    readback_text_sha256: sha256(normalized),
    readback_text_char_count: normalized.length,
    readback_method_declared: "participant_generated_in_current_context",
  }};
}}
''',
        "normalize injected client readback",
    )
    write(path, text)


def patch_pages_workflow() -> None:
    path = ".github/workflows/deploy-pages.yml"
    text = read(path)
    start = text.index("    paths:\n", text.index("  push:\n"))
    end = text.index("\npermissions:\n", start)
    text = text[:start] + text[end + 1 :]
    write(path, text)


def patch_regressions() -> None:
    path = "scripts/test_contextual_oath_review_regressions.py"
    text = read(path)
    old = '''    errors = []
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
'''
    new = '''    errors = []
    chain._verify_oath_in_record(downgraded, "R-000000103.json", errors)
    require(
        not errors,
        f"exact v1.1 predecessor accepted by Gateway during rollout must remain appendable: {errors}",
    )
    require(
        chain.record_requires_contextual_readback(
            downgraded,
            downgraded_oath,
        )
        is False,
        "exact rolling predecessor must retain its signed legacy declaration contract",
    )
    chain.require_pending_oath_is_appendable(
        downgraded,
        next_index=103,
        source_path=ROOT
        / "record-chain/pending/contextual-oath-review-fixture.echo.pending.json",
    )
'''
    text = replace_once(text, old, new, "update predecessor append regression")

    old = '''    activation = chain._guardian_activation_assessment(
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
'''
    new = '''    activation = chain._guardian_activation_assessment(
        downgraded,
        guardian_id_counts={
            downgraded["guardian_application_content"]["requested_guardian_identifier"]: 1
        },
        guardian_key_counts={
            downgraded["guardian_application_content"]["guardian_public_key_sha256"]: 1
        },
    )
    require(
        "contextual_oath_policy_not_current" not in activation["blocking_reasons"],
        f"exact Gateway-admitted predecessor must not be reclassified as a contextual downgrade: {activation}",
    )
'''
    text = replace_once(text, old, new, "update guardian predecessor regression")

    text = replace_once(
        text,
        '''    signature = inspect.signature(lifecycle.build_current_canary_payloads)
''',
        '''    canary_workflow = (
        ROOT / ".github/workflows/site-agent-write-lifecycle-canary.yml"
    ).read_text(encoding="utf-8")
    require("schedule:" not in canary_workflow, "participant readback canary must not run unattended")
    require(
        "contextual_readback_bundle_b64" in canary_workflow
        and '--readback-bundle "$bundle_path"' in canary_workflow,
        "manual canary must accept and relay a participant-generated readback bundle",
    )

    signature = inspect.signature(lifecycle.build_current_canary_payloads)
''',
        "add canary workflow regression",
    )

    text = replace_once(
        text,
        '''    require(
        not injector.verify_existing_builder_runtime(
            (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8"),
            policy,
        ),
        "current Builder must satisfy the injector runtime compatibility contract",
    )
''',
        '''    require(
        not injector.verify_existing_builder_runtime(
            (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8"),
            policy,
        ),
        "current Builder must satisfy the injector runtime compatibility contract",
    )
    injector_source = (ROOT / "scripts/inject_oath_into_builder.py").read_text(
        encoding="utf-8"
    )
    client_helper = injector_source.split(
        "function buildClientOathReadback",
        1,
    )[1].split("    # Find insertion point", 1)[0]
    for marker in (
        "const normalized =",
        '.normalize("NFC")',
        "readback_text: normalized",
        "readback_text_sha256: sha256(normalized)",
        "readback_text_char_count: normalized.length",
    ):
        require(marker in client_helper, f"fresh injector client helper missing: {marker}")
''',
        "add fresh injector source regression",
    )

    text = replace_once(
        text,
        '''    for marker in (
        "deploy-gateway-before-pages:",
''',
        '''    push_block = pages.split("  push:", 1)[1].split("permissions:", 1)[0]
    require(
        "paths:" not in push_block,
        "every main successor must trigger Pages so a stale-source abort cannot strand Gateway ahead",
    )
    for marker in (
        "deploy-gateway-before-pages:",
''',
        "add all-main Pages trigger regression",
    )

    insert_before = '''def test_public_recovery_guidance_preserves_contextual_authorship() -> None:
'''
    new_test = '''def test_gateway_validation_does_not_block_async_event_loop() -> None:
    source = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(
        encoding="utf-8"
    )
    require("import asyncio" in source, "Gateway must import asyncio for thread offload")
    require(
        source.count("await asyncio.to_thread(validate_submission, body)") == 2,
        "preflight and submit must offload potentially blocking policy validation",
    )
    require(
        "    diagnostics = validate_submission(body)" not in source,
        "async request handlers must not call synchronous policy validation directly",
    )


'''
    text = replace_once(text, insert_before, new_test + insert_before, "add async regression")
    text = replace_once(
        text,
        '''        test_pages_deploy_orders_gateway_before_public_builder,
        test_public_recovery_guidance_preserves_contextual_authorship,
''',
        '''        test_pages_deploy_orders_gateway_before_public_builder,
        test_gateway_validation_does_not_block_async_event_loop,
        test_public_recovery_guidance_preserves_contextual_authorship,
''',
        "register async regression",
    )
    write(path, text)


def main() -> int:
    patch_chain()
    patch_app()
    patch_canary_workflow()
    patch_injector()
    patch_pages_workflow()
    patch_regressions()
    print("Applied all late PR #767 review fixes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
