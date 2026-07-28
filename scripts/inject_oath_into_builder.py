#!/usr/bin/env python3
"""Inject oath policy and print-oath command into the builder."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
OATH_POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"


def verify_existing_builder_runtime(builder_text: str, policy: dict) -> list[str]:
    """Return fail-closed errors for an existing Builder helper implementation."""
    errors: list[str] = []
    required_markers = [
        "contextualReadbackConfirmed",
        "--contextual-readback-confirmed true",
        "participant_generated_in_current_context",
        "canonical_oath_loaded_into_active_context",
        "readback_generated_by_participant_from_active_context",
        "readback_was_not_directly_copied_by_submission_tool",
        "readback_was_not_automatically_completed_or_corrected",
        "contextual_readback_process_acknowledged",
        "contextual_readback_process_is_self_declared",
        "contextual_readback_does_not_prove_persistent_memory",
        "function buildSubmissionOathVerification",
        "function buildClientOathReadback",
        "submission.client_oath_readback = buildClientOathReadback",
        "normalizedReadback !== normalizedCanonical",
        '.normalize("NFC")',
        "readback_text: normalized",
        "readback_text_sha256: sha256(normalized)",
        "readback_text_char_count: normalized.length",
    ]
    for declaration in policy.get("no_shortcut_policy", {}).get(
        "required_declarations",
        [],
    ):
        if isinstance(declaration, str):
            required_markers.append(declaration)
    for marker in dict.fromkeys(required_markers):
        if marker not in builder_text:
            errors.append(f"existing Builder runtime missing required marker: {marker}")

    if re.search(
        r"(?:let|const)\s+readback\s*=\s*(?:opts\.readback\s*\|\|\s*)?canonicalOath",
        builder_text,
    ):
        errors.append("existing Builder still auto-fills readback from canonicalOath")
    if re.search(r"readback_text\s*:\s*canonical\w*", builder_text):
        errors.append("existing Builder still copies canonical oath into readback_text")
    return errors


def main() -> None:
    if not BUILDER.exists():
        print("ERROR: builder not found", file=sys.stderr)
        sys.exit(1)
    if not OATH_POLICY.exists():
        print("ERROR: oath policy not found", file=sys.stderr)
        sys.exit(1)

    builder_text = BUILDER.read_text(encoding="utf-8")
    policy_text = OATH_POLICY.read_text(encoding="utf-8")
    policy = json.loads(policy_text)

    # Compute canonical policy hash (sorted keys, no spaces)
    # Exclude API metadata fields not in builder's embedded OATH_POLICY
    _metadata_keys = {
        "oath_policy_sha256",
        "oath_policy_sha256_semantics",
        "canonical_oath_text_hash_is_record_type_specific",
    }
    core_policy = {
        key: value
        for key, value in policy.items()
        if key not in _metadata_keys
    }
    canonical_policy = json.dumps(
        core_policy,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    policy_sha256 = hashlib.sha256(canonical_policy.encode("utf-8")).hexdigest()
    policy_needs_write = policy.get("oath_policy_sha256") != policy_sha256
    if policy_needs_write:
        policy["oath_policy_sha256"] = policy_sha256
    serialized_policy = (
        json.dumps(policy, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    )

    # Synchronize an existing embedded policy without touching the surrounding
    # hand-maintained Builder implementation.
    if "OATH_POLICY" in builder_text and "print-oath" in builder_text:
        policy_js = json.dumps(core_policy, indent=2, ensure_ascii=False, allow_nan=False)
        pattern = re.compile(
            r'const OATH_POLICY = \{[\s\S]*?\n\};\n'
            r'const OATH_POLICY_SHA256 = "[a-f0-9]{64}";'
        )
        replacement = (
            f"const OATH_POLICY = {policy_js};\n"
            f'const OATH_POLICY_SHA256 = "{policy_sha256}";'
        )
        builder_text, count = pattern.subn(lambda _match: replacement, builder_text, count=1)
        if count != 1:
            print("ERROR: could not replace existing embedded oath policy", file=sys.stderr)
            sys.exit(1)
        runtime_errors = verify_existing_builder_runtime(builder_text, policy)
        if runtime_errors:
            print(
                "ERROR: refusing policy-only synchronization because the existing "
                "Builder helper runtime is incompatible:",
                file=sys.stderr,
            )
            for error in runtime_errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        if policy_needs_write:
            OATH_POLICY.write_text(serialized_policy, encoding="utf-8")
        BUILDER.write_text(builder_text, encoding="utf-8")
        print(f"OK: synchronized oath policy and builder hash {policy_sha256}")
        return

    # Build the oath policy constant and helper functions
    # Embed as direct JS object (avoids escaping issues with JSON-in-string)
    policy_js = json.dumps(core_policy, indent=2, ensure_ascii=False, allow_nan=False)

    oath_injection = f'''
// ── Oath Policy (Phase 6B-OATH) ───────────────────────────────────────
const OATH_POLICY = {policy_js};
const OATH_POLICY_SHA256 = "{policy_sha256}";

function getCanonicalOath(recordType) {{
  const modules = OATH_POLICY.record_type_modules[recordType];
  if (!modules) return null;
  const modulesObj = OATH_POLICY.modules;
  const joiner = OATH_POLICY.canonicalization?.module_joiner || "\\n\\n---\\n\\n";
  const parts = [];
  for (const modId of modules) {{
    const mod = modulesObj[modId];
    if (mod) {{
      const normalizedText = mod.text.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim();
      parts.push(`=== ${{mod.label}} (${{modId}}) ===\\n\\n${{normalizedText}}`);
    }}
  }}
  return parts.join(joiner).trim();
}}

function getOathModules(recordType) {{
  return OATH_POLICY.record_type_modules[recordType] || [];
}}

function buildSubmissionOathVerification(recordType, canonicalOath, readbackText) {{
  const readback = readbackText.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim().normalize("NFC");
  return {{
    schema: "trinityaccord.submission-oath-verification.v1",
    oath_policy: "record-chain-formal-submission-oath-v1",
    oath_policy_schema: OATH_POLICY.schema,
    oath_policy_version: OATH_POLICY.version,
    oath_policy_sha256: OATH_POLICY_SHA256,
    oath_policy_source_url: "/api/record-chain-oath-policy.v1.json",
    oath_modules: getOathModules(recordType),
    oath_applies_to: [recordType],
    canonical_oath_text_sha256: sha256(canonicalOath),
    canonical_oath_char_count: canonicalOath.length,
    canonical_oath_line_count: canonicalOath.split("\\n").length,
    participant_readback_sha256: sha256(readback),
    participant_readback_char_count: readback.length,
    participant_readback_excerpt: readback.substring(0, 120),
    oath_read: true,
    readback_required: true,
    participant_readback_provided: true,
    readback_matches_canonical_oath: readback === canonicalOath,
    readback_method_declared: "participant_generated_in_current_context",
    readback_was_not_piped_from_file: true,
    readback_was_not_generated_by_script: true,
    readback_was_not_loaded_from_cache: true,
    readback_was_not_summary_or_paraphrase: true,
    readback_was_not_generated_by_external_automation: true,
    readback_was_not_auto_filled_by_builder: true,
    canonical_oath_loaded_into_active_context: true,
    readback_generated_by_participant_from_active_context: true,
    readback_was_not_directly_copied_by_submission_tool: true,
    readback_was_not_automatically_completed_or_corrected: true,
    contextual_readback_process_acknowledged: true,
    no_shortcut_oath_acknowledged: true,
    contextual_readback_process_is_self_declared: true,
    contextual_readback_does_not_prove_persistent_memory: true,
    oath_does_not_prove_subjective_understanding: true,
    oath_verifies_exact_readback_only: true,
    not_authority: true,
    not_governance: true,
    not_attestation: true,
    not_amendment: true,
    bitcoin_originals_prevail: true,
  }};
}}

function buildClientOathReadback(recordType, participantReadback) {{
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
'''

    # Find insertion point - after SCHEMA/DRAFT_SCHEMA constants
    insert_marker = 'const SITE_URL = "https://www.trinityaccord.org/";'
    if insert_marker not in builder_text:
        print(f"ERROR: cannot find insertion marker: {insert_marker}", file=sys.stderr)
        sys.exit(1)

    builder_text = builder_text.replace(insert_marker, insert_marker + oath_injection)

    # Now inject print-oath command into the main command dispatch
    # Find the "explain-fields" command handler
    print_oath_cmd = '''
  // ── print-oath ────────────────────────────────────────────────────
  if (cmd === "print-oath") {
    const recordType = args.recordType || errorExit("--record-type required");
    const canonicalOath = getCanonicalOath(recordType);
    if (!canonicalOath) {
      console.error(`Unknown record type for oath: ${recordType}`);
      console.error(`Valid types: ${Object.keys(OATH_POLICY.record_type_modules).join(", ")}`);
      process.exit(1);
    }
    console.log(canonicalOath);
    return;
  }

'''

    # Insert before the explain-fields handler
    explain_marker = "  // ── explain-fields"
    if explain_marker in builder_text and "print-oath" not in builder_text:
        builder_text = builder_text.replace(explain_marker, print_oath_cmd + explain_marker)

    # Update help text
    old_commands = """   explain-fields          Show field explanations for a record type or specific field"""
    new_commands = """   print-oath              Print canonical oath for a record type
   explain-fields          Show field explanations for a record type or specific field"""
    if old_commands in builder_text and "print-oath" not in builder_text:
        builder_text = builder_text.replace(old_commands, new_commands)

    # Add the readback and explicit in-context process confirmation to build options
    old_opts_end = """    echoIntent: args.echoIntent || "recognition",
    whatWasChecked: args.whatWasChecked || "",
    verificationClaim: args.verificationClaim || "",
  };"""
    new_opts_end = """    echoIntent: args.echoIntent || "recognition",
    whatWasChecked: args.whatWasChecked || "",
    verificationClaim: args.verificationClaim || "",
    readback: args.readback || "",
    contextualReadbackConfirmed: args.contextualReadbackConfirmed,
  };"""
    if old_opts_end in builder_text:
        builder_text = builder_text.replace(old_opts_end, new_opts_end)

    # After draft is built and before submission, add oath gate if formal type
    old_submission_build = """  const draft = builder(opts);
  const submission = buildSubmission(draft, { ...opts, keyPair });"""
    new_submission_build = """  const draft = builder(opts);

  // Inject oath gate for formal record types
  const OATH_TYPES = ["echo", "verification", "guardian_application", "guardian_retirement",
    "propagation", "correction", "classification_update"];
  if (OATH_TYPES.includes(draft.record_type)) {
    const canonicalOath = getCanonicalOath(draft.record_type);
    if (!canonicalOath) {
      errorExit(`Cannot get canonical oath for record type: ${draft.record_type}`);
    }
    if (opts.contextualReadbackConfirmed !== "true") {
      errorExit(
        "Complete the agent in-context oath readback process, then pass " +
        "--contextual-readback-confirmed true"
      );
    }
    const readback = opts.readback || "";
    if (!readback) {
      errorExit(
        "--readback is required. Load print-oath output into the participating agent's " +
        "active context and have that agent generate the exact readback."
      );
    }
    const normalizedReadback = readback.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim();
    const normalizedCanonical = canonicalOath.replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n").trim();
    if (normalizedReadback !== normalizedCanonical) {
      console.error("ERROR: Readback does not match canonical oath text.");
      console.error(
        "Reload the standalone print-oath output into the participating agent's active " +
        "context and have that agent regenerate the exact readback. Do not auto-correct it."
      );
      process.exit(1);
    }
    draft.submission_oath_verification = buildSubmissionOathVerification(draft.record_type, canonicalOath, readback);
  }

  const submission = buildSubmission(draft, { ...opts, keyPair });

  // Add client_oath_readback to submission for gateway validation (transient)
  if (OATH_TYPES.includes(draft.record_type)) {
    submission.client_oath_readback = buildClientOathReadback(draft.record_type, opts.readback);
  }"""

    if old_submission_build in builder_text:
        builder_text = builder_text.replace(old_submission_build, new_submission_build)
        print("OK: oath injection into build pipeline")
    else:
        print("WARN: could not find build pipeline insertion point")

    runtime_errors = verify_existing_builder_runtime(builder_text, policy)
    if runtime_errors:
        print("ERROR: generated Builder runtime failed oath compatibility checks:", file=sys.stderr)
        for error in runtime_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    if policy_needs_write:
        OATH_POLICY.write_text(serialized_policy, encoding="utf-8")
    BUILDER.write_text(builder_text, encoding="utf-8")
    print(f"OK: builder updated. SHA256: {hashlib.sha256(builder_text.encode()).hexdigest()[:16]}...")


if __name__ == "__main__":
    main()
