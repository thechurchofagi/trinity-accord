#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, data) -> None:
    (ROOT / path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, found {count}")
    return value.replace(old, new, 1)


def insert_after_first_h1(path: str, block: str) -> None:
    value = text(path)
    marker = "<!-- current-model-policy-v1 -->"
    if marker in value:
        return
    lines = value.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines[i + 1:i + 1] = ["", marker, block.strip(), ""]
            write(path, "\n".join(lines) + ("\n" if value.endswith("\n") else ""))
            return
    raise AssertionError(f"{path}: no H1")


def canonical_json_bytes(data) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


# Current interpretation policy references.
action = load("api/context-action-profiles.v1.json")
action["interpretation_model_policy"] = "/api/interpretation-model-policy.v1.json"
action["verification_claim_model"] = "/api/verification-claim-model.v1.json"
for profile in action["profiles"]:
    if profile["id"] == "interpretation":
        if "/api/interpretation-model-policy.v1.json" not in profile["must_load"]:
            profile["must_load"].insert(1, "/api/interpretation-model-policy.v1.json")
        profile["optimization_note"] = (
            "Chronicle materials are required only when the claim depends on Chronicle, history, music, creative work, or human-witness context. "
            "No current fixed five-stage, seven-stage, or other fixed-stage model exists."
        )
    if profile["id"] == "verification":
        if "/api/verification-claim-model.v1.json" not in profile["must_load"]:
            profile["must_load"].insert(4, "/api/verification-claim-model.v1.json")
    if profile["id"] == "record_action":
        for required in ["/api/interpretation-model-policy.v1.json", "/api/verification-claim-model.v1.json"]:
            if required not in profile["must_load"]:
                profile["must_load"].insert(1, required)
action["legacy_compatibility"]["policy"] = (
    "CC-0 through CC-5 and CRL remain accepted compatibility declarations. New agents select an action profile first. "
    "A CC label does not import a fixed Chronicle stage model or require unrelated Chronicle material."
)
save("api/context-action-profiles.v1.json", action)

ctx = load("api/context-packs/nft-chronicle-context.json")
ctx["interpretation_policy"].update({
    "fixed_seven_stage_taxonomy_retired": True,
    "fixed_five_stage_taxonomy_not_adopted": True,
    "no_current_fixed_stage_model": True,
    "source": "/api/interpretation-model-policy.v1.json",
    "objective_structure": "chronological order plus calendar-quarter navigation",
    "descriptive_categories": "overlapping search aids, not exclusive stages and not factual verification",
    "interpretive_arcs": "provisional, revisable, non-exclusive, and not periodization",
})
ctx["recommended_agent_summary"] = (
    "The NFT Chronicle is a completed 175-entry timestamped non-canonical historical and human-origin witness layer. "
    "There is no current fixed five-stage, seven-stage, or other fixed-stage model. Chronology is objective; quarters are navigation; "
    "categories overlap; interpretive arcs are provisional and revisable."
)
save("api/context-packs/nft-chronicle-context.json", ctx)

# Action-grounded CC compatibility model.
levels = load("api/context-depth-levels.json")
levels["purpose"] = (
    "Legacy compatibility declarations describing broad context depth. New agents must use action profiles and actual loaded sources; "
    "CC labels do not define a mandatory interpretation model."
)
levels["inheritance_rule"] = (
    "Legacy CC declarations retain inherited historical meaning for old records. For new work, action-specific source sufficiency overrides unrelated inherited loads."
)
for level in levels["levels"]:
    if level["id"] == "CC-3":
        level.update({
            "name": "Action-Grounded Context",
            "name_zh": "行动扎根上下文",
            "legacy_label": "Narrative Grounded",
            "meaning": "The agent has loaded the Bitcoin Originals, authority boundary, Agent Brief, and the exact task-relevant sources needed for a meaningful interpretation or public action. Chronicle materials are required only when the task depends on Chronicle, history, music, creative work, or human-witness context.",
            "required_loads": [
                "CC-2 loads (legacy compatibility)",
                "/api/context-action-profiles.v1.json",
                "/api/interpretation-model-policy.v1.json",
                "/agent-brief/",
                "exact task-relevant source records and corrections/supersession status",
                "Chronicle context only when the selected claim depends on Chronicle/history/music/creative/human-witness material",
            ],
            "total_required_size": "task-dependent",
            "chronicle_required_only_when_task_depends_on_it": True,
            "why_this_matters": "Meaningful output requires primary authority and relevant context, not a universal narrative bundle or a fixed-stage model.",
            "note": "Legacy label retained for archived records and Builder compatibility. No current five-stage or seven-stage Chronicle periodization is implied.",
        })
    if level["id"] == "CC-5":
        level["meaning"] = "Deep task-specific research with the complete relevant corpus or an exact declared subset. Full Chronicle text is required only for exact-text, appendix-wide, music-corpus, human-witness-corpus, or full-corpus claims."
        level["why_this_matters"] = "Full-corpus claims require the full relevant corpus; ordinary interpretation and narrow verification do not."
levels["verification_depth_is_separate"] = {
    "explanation": "Context action/profile and verification claim dimensions are separate. Use /api/context-action-profiles.v1.json and /api/verification-claim-model.v1.json.",
    "legacy_v_file": "/api/verification-levels.json",
    "current_verification_profiles": "/api/verification-profiles.v1.json",
}
levels["migration_note"] = (
    "CC-0 through CC-5 remain accepted declarations for existing records and current schema compatibility. New agents select an action profile, list actual sources, and must not infer any fixed Chronicle stage model from CC-3."
)
save("api/context-depth-levels.json", levels)

load_map = load("api/context-load-map.json")
load_map["purpose"] = "Legacy CC load map plus current action-based migration guidance. Use action profiles for new work."
cc3 = load_map["cc_level_loads"]["CC-3"]
cc3.update({
    "name": "Action-Grounded Context",
    "legacy_name": "Narrative Grounded",
    "must_load": [
        "CC-2 loads (legacy compatibility)",
        "/api/context-action-profiles.v1.json",
        "/api/interpretation-model-policy.v1.json",
        "/agent-brief/",
        "exact task-relevant sources",
        "/api/corrections-index.json when discussing a later record or report",
        "Chronicle sources only when the claim depends on Chronicle/history/music/creative/human-witness context",
    ],
    "total_size": "task-dependent",
    "note": "Minimum for a meaningful task-grounded Echo under current Builder compatibility. No fixed five-stage or seven-stage model is current, and unrelated Chronicle or legacy-archive material is not universally required.",
    "chronicle_required_only_when_task_depends_on_it": True,
})
load_map["cc_action_requirements"]["meaningful_echo"] = "CC-3 compatibility + interpretation action profile + exact task-relevant sources"
load_map["default_rule"] = "Select the action profile first and load the smallest sufficient exact source set. CC labels remain compatibility declarations only."
load_map["preferred_rule"] = "Select the action first; actual loaded sources determine sufficiency. Do not require unrelated inherited materials or any fixed Chronicle stage model."
load_map["interpretation_model_policy"] = "/api/interpretation-model-policy.v1.json"
save("api/context-load-map.json", load_map)

required = load("api/agent-required-reading.json")
required["interpretation_model_policy"] = "/api/interpretation-model-policy.v1.json"
required["verification_claim_model"] = "/api/verification-claim-model.v1.json"
ng = required["profiles"]["narrative_grounded"]
ng["current_name"] = "action_grounded_context"
ng["legacy_profile_name"] = "narrative_grounded"
ng["reads"] = [
    "canon_loaded (legacy compatibility)",
    "/api/context-action-profiles.v1.json",
    "/api/interpretation-model-policy.v1.json",
    "/agent-brief/",
    "exact task-relevant sources",
    "/api/corrections-index.json when relevant",
]
ng["conditional_reads"] = {
    "chronicle_history_music_creative_or_human_witness_claim": [
        "/api/context-packs/nft-chronicle-context.json",
        "/nft-text-descriptions/chronicle-summary.json",
        "/nft-text-descriptions/chronicle-ultra-brief.md",
        "/nft-text-descriptions/chronicle-abridged.md",
    ],
    "physical_anchor_claim": ["/api/context-packs/physical-anchor-context.json", "exact physical/notarial source"],
    "legacy_archive_claim": ["/api/context-packs/legacy-archive-essentials.json", "/api/context-packs/legacy-archive-index.json"],
}
ng["note"] = "Legacy CC-3 compatibility profile. New agents use interpretation action profile and task-relevant sources. No fixed Chronicle stage model is current."
echo = required["profiles"]["echo_submission"]
echo["cc_note"] = "Current public Builder compatibility uses CC-3, but sufficiency comes from interpretation + record_action profiles and actual task-relevant sources. Chronicle is conditional, not universal."
echo["chronicle_materials_required_only_when_claim_depends_on_chronicle"] = True
for ref in ["/api/interpretation-model-policy.v1.json", "/api/verification-claim-model.v1.json"]:
    if ref not in echo["reads"]:
        echo["reads"].append(ref)
verification = required["profiles"]["verification"]
for ref in ["/api/verification-claim-model.v1.json", "/api/interpretation-model-policy.v1.json"]:
    if ref not in verification["reads"]:
        verification["reads"].append(ref)
save("api/agent-required-reading.json", required)

# Verification dimensions and retirement of V6-V8 for new records.
profiles = load("api/verification-profiles.v1.json")
profiles["verification_claim_model"] = "/api/verification-claim-model.v1.json"
profiles["current_submission_policy"] = {
    "legacy_v_allowed": ["V0", "V1", "V2", "V3", "V4", "V5"],
    "legacy_v4_plus_archived_only": True,
    "legacy_v6_v8_forbidden_for_new_records": True,
    "required_current_dimensions": ["digital_profile", "relationships_checked", "physical_observation", "external_witness", "coverage_scope", "limitations", "claims_not_made", "corrections_or_supersession_checked"],
}
profiles["legacy_compatibility"]["policy"] = "Existing V0-V8 and V4+ labels remain preserved in historical records. New public records use V0-V5 only as compatibility metadata and lead with the multidimensional verification claim model."
profiles["legacy_compatibility"]["important_boundary"] = "V4+, V6, V7 and V8 are not accepted as new public legacy_v_level values. V6-V8 map only to separate physical observation states."
save("api/verification-profiles.v1.json", profiles)

claim = load("api/verification-claim-model.v1.json")
claim["legacy_v_compatibility"]["current_builder_allowed_values"] = ["V0", "V1", "V2", "V3", "V4", "V5"]
claim["legacy_v_compatibility"]["new_submission_forbidden_values"] = ["V4+", "V6", "V7", "V8"]
claim["legacy_v_compatibility"]["mapping"]["V4"] = "integrity_checked or independent_reproduction; digital_profile carries the precise current meaning"
claim["legacy_v_compatibility"]["mapping"].pop("V4+", None)
claim["legacy_v_compatibility"]["retired_mapping"] = {
    "V4+": "digital_profile=independent_reproduction",
    "V6": "physical_observation=remote_live_witness",
    "V7": "physical_observation=onsite_observation",
    "V8": "physical_observation=forensic_examination",
}
claim["legacy_v_compatibility"].pop("retired_physical_mapping", None)
claim["legacy_v_compatibility"]["boundary"] = "Historical V4+/V6/V7/V8 records remain preserved. New records use V0-V5 compatibility metadata and separate current dimensions."
save("api/verification-claim-model.v1.json", claim)

legacy_v = load("api/verification-levels.json")
legacy_v["new_submission_policy"] = {
    "preferred_model": "/api/verification-claim-model.v1.json",
    "allowed_legacy_v_values": ["V0", "V1", "V2", "V3", "V4", "V5"],
    "forbidden_legacy_v_values": ["V4+", "V6", "V7", "V8"],
    "rule": "New records lead with digital_profile and separate relationships_checked, physical_observation and external_witness. The legacy V field is compatibility metadata only.",
}
for level in legacy_v["levels"]:
    if level["id"] in {"V4+", "V6", "V7", "V8"}:
        level["status"] = "historical_compatibility_only"
        level["new_submission_allowed"] = False
        level["current_replacement"] = {
            "V4+": "digital_profile=independent_reproduction",
            "V6": "physical_observation=remote_live_witness",
            "V7": "physical_observation=onsite_observation",
            "V8": "physical_observation=forensic_examination",
        }[level["id"]]
        level["historical_preservation"] = "Preserve existing records verbatim; do not use this label for a new public submission."
legacy_v["migration_note"] = "Preserved for existing records. New reports and Builder records use /api/verification-claim-model.v1.json; V0-V5 are compatibility metadata only, while V4+/V6/V7/V8 are historical-only."
save("api/verification-levels.json", legacy_v)

# Chronicle generator and generated artifacts.
gen_path = "scripts/chronicle_editions_v2.py"
gen = text(gen_path)
gen = replace_once(gen, '"fixed_stage_taxonomy_retired": True,\n        "reason": "The previous seven-stage scheme was imposed by date buckets and broad keyword matching; it was not authored by the NFTs and is not a verified historical periodization.",', '"fixed_stage_count": None,\n        "fixed_stage_taxonomy_retired": True,\n        "no_current_five_stage_model": True,\n        "no_current_seven_stage_model": True,\n        "source": "/api/interpretation-model-policy.v1.json",\n        "reason": "The previous seven-stage scheme was imposed by date buckets and broad keyword matching; it was not authored by the NFTs and is not a verified historical periodization. No fixed five-stage or other fixed-stage model replaces it.",', "chronicle generator policy")
gen = gen.replace("The former fixed seven-stage narrative is retired. It was an AI-generated periodization based largely on month ranges and broad keyword matching, not a source-authored structure.", "The former fixed seven-stage narrative is retired. It was an AI-generated periodization based largely on month ranges and broad keyword matching, not a source-authored structure. No fixed five-stage or other fixed-stage model replaces it.")
gen = gen.replace("The prior fixed seven-stage periodization is intentionally not used.", "No fixed five-stage, seven-stage, or other fixed-stage periodization is used.")
gen = gen.replace("## Correction to the former seven-stage narrative", "## Retired fixed-stage interpretations")
gen = gen.replace("The former seven-stage narrative is retired as a default interpretation. Its boundaries were fixed calendar buckets with narrative names, and its theme counts were produced by broad substring matching. That method made some categories appear more universal than the source text justified.", "The former seven-stage narrative is retired as a default interpretation. Its boundaries were fixed calendar buckets with narrative names, and its theme counts were produced by broad substring matching. No fixed five-stage or other fixed-stage model replaces it.")
write(gen_path, gen)

# Human Chronicle page explicit boundary.
chronicle = text("chronicle.md")
chronicle = chronicle.replace("The corrected model separates:\n", "No fixed five-stage, seven-stage, or other fixed-stage model is current. The corrected model separates:\n")
write("chronicle.md", chronicle)

# Current agent machine entrypoints.
entry_jsons = [
    "api/agent-first-contact.json",
    "api/agent-minimal-context.v1.json",
    "api/agent-start.v2.json",
    "api/agent-task-router.v1.json",
    ".well-known/agent.json",
    ".well-known/trinity-accord.json",
    "api/links.json",
]
for path in entry_jsons:
    data = load(path)
    data["current_interpretation_model"] = "/api/interpretation-model-policy.v1.json"
    data["current_verification_claim_model"] = "/api/verification-claim-model.v1.json"
    data["current_context_action_model"] = "/api/context-action-profiles.v1.json"
    data["legacy_model_boundary"] = "CC/CRL/V labels in historical records remain preserved. New agents must not infer a fixed Chronicle stage model or treat V6-V8 as current verification levels."
    save(path, data)

# Submission schema additive fields.
schema = load("api/record-chain-submission-schema.v1.json")
rd = schema["properties"]["record_draft"]["properties"]
cr = rd["context_readiness"]["properties"]
cr["action_profile"] = {"type": "string", "enum": ["discovery", "interpretation", "verification", "record_action", "deep_research"]}
cr["action_profile_source"] = {"type": "string", "const": "/api/context-action-profiles.v1.json"}
cr["interpretation_model_policy"] = {"type": "string", "const": "/api/interpretation-model-policy.v1.json"}
cr["legacy_cc_level_role"] = {"type": "string", "const": "builder_compatibility_only"}
rd["verification_content"] = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "verification_level": {"type": "string", "enum": ["V0", "V1", "V2", "V3", "V4", "V5"]},
        "verification_claim_model": {
            "type": "object",
            "required": ["schema", "digital_profile", "relationships_checked", "physical_observation", "external_witness", "coverage_scope", "limitations", "claims_not_made", "corrections_or_supersession_checked", "legacy_v_level", "legacy_v_level_role"],
            "additionalProperties": False,
            "properties": {
                "schema": {"const": "trinityaccord.verification-claim-model.v1"},
                "digital_profile": {"enum": ["context_only", "reference_checked", "integrity_checked", "independent_reproduction", "full_public_digital"]},
                "relationships_checked": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "physical_observation": {"enum": ["none", "public_media_review", "remote_live_witness", "onsite_observation", "forensic_examination"]},
                "external_witness": {"enum": ["none", "notarial_scope", "independent_report", "institutional_attestation", "regulatory_or_court_record"]},
                "coverage_scope": {"enum": ["single_target", "component_subset", "multi_component", "all_declared_public_digital_targets"]},
                "limitations": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "claims_not_made": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "corrections_or_supersession_checked": {"type": "boolean"},
                "legacy_v_level": {"enum": ["V0", "V1", "V2", "V3", "V4", "V5"]},
                "legacy_v_level_role": {"const": "builder_compatibility_only"},
            },
        },
    },
}
save("api/record-chain-submission-schema.v1.json", schema)

# Oath policy: active wording must match new verification semantics.
oath_path = "api/record-chain-oath-policy.v1.json"
oath = load(oath_path)
old_verification_oath = oath["modules"]["verification_integrity_v1"]["text"]
new_verification_oath = (
    "I declare that the verification actions described in this record are actions I actually performed.\n"
    "I acknowledge that the legacy V0-V5 field is self-assessed Builder compatibility metadata and is not independently confirmed.\n"
    "I acknowledge that new verification records separately state digital profile, evidence relationships, physical observation, external witness, coverage, limitations, and claims not made.\n"
    "I acknowledge that V4+, V6, V7, and V8 are historical-only labels for new public submissions; physical observation and external witness do not automatically raise digital verification.\n"
    "I acknowledge that claiming checks, observations, witnesses, or coverage I did not earn is a breach of the Record-Chain's integrity contract.\n"
    "I acknowledge that verification does not confer authority, governance, or endorsement."
)
oath["version"] = "1.1.0"
oath["modules"]["verification_integrity_v1"]["text"] = new_verification_oath
for key in ["oath_policy_sha256", "oath_policy_sha256_semantics", "canonical_oath_text_hash_is_record_type_specific"]:
    oath.pop(key, None)
new_oath_hash = hashlib.sha256(canonical_json_bytes(oath)).hexdigest()
oath["oath_policy_sha256"] = new_oath_hash
oath["oath_policy_sha256_semantics"] = "Canonical JSON hash of this oath policy after excluding self-describing metadata fields: oath_policy_sha256, oath_policy_sha256_semantics, canonical_oath_text_hash_is_record_type_specific."
oath["canonical_oath_text_hash_is_record_type_specific"] = True
save(oath_path, oath)

# Builder v2.1 multidimensional verification claim output.
builder_path = "downloads/record-chain-builder.mjs"
b = text(builder_path)
b = replace_once(b, 'const BUILDER_VERSION = "v2";', 'const BUILDER_VERSION = "v2.1";', "builder version")
b = replace_once(b, '  "version": "1.0.0",', '  "version": "1.1.0",', "embedded oath version")
b = replace_once(b, old_verification_oath.replace("\n", "\\n").replace('"', '\\"'), new_verification_oath.replace("\n", "\\n").replace('"', '\\"'), "embedded verification oath")
b = re.sub(r'const OATH_POLICY_SHA256 = "[0-9a-f]{64}";', f'const OATH_POLICY_SHA256 = "{new_oath_hash}";', b, count=1)

anchor = 'function parseBooleanStrict(value, fieldName) {\n'
helper = '''const DIGITAL_PROFILES = new Set(["context_only", "reference_checked", "integrity_checked", "independent_reproduction", "full_public_digital"]);\nconst RELATIONSHIP_TYPES = new Set(["defines_canonical_text", "references", "indexes", "hashes", "signs_digest", "timestamps_digest", "mirrors_bytes", "witnesses_statement", "notarially_records_process", "provides_context", "records_reception"]);\nconst PHYSICAL_OBSERVATIONS = new Set(["none", "public_media_review", "remote_live_witness", "onsite_observation", "forensic_examination"]);\nconst EXTERNAL_WITNESSES = new Set(["none", "notarial_scope", "independent_report", "institutional_attestation", "regulatory_or_court_record"]);\nconst COVERAGE_SCOPES = new Set(["single_target", "component_subset", "multi_component", "all_declared_public_digital_targets"]);\n\nfunction splitCsv(value) {\n  return String(value || "").split(",").map(s => s.trim()).filter(Boolean);\n}\n\nfunction defaultActionProfile(recordType) {\n  const rt = normalizeRecordType(recordType);\n  if (rt === "echo") return "interpretation";\n  if (rt === "verification") return "verification";\n  if (rt === "context_insufficient_notice") return "discovery";\n  return "record_action";\n}\n\n'''
if helper not in b:
    b = replace_once(b, anchor, helper + anchor, "builder helper insertion")

old_ctx = '''  return {\n    declared_context_level: contextLevel,\n    minimum_required_for_action: contextLevel,\n    context_sufficient_for_selected_action: sufficient,\n    loaded_context_urls: opts.loadedUrls || [],\n    context_read_confirmed: isContextReadConfirmed(opts.contextReadConfirmed),\n    context_read_confirmation_boundary: buildContextReadConfirmationBoundary(),\n    context_readiness_notes: "",\n  };'''
new_ctx = '''  return {\n    action_profile: opts.actionProfile || defaultActionProfile(opts.recordType),\n    action_profile_source: "/api/context-action-profiles.v1.json",\n    interpretation_model_policy: "/api/interpretation-model-policy.v1.json",\n    declared_context_level: contextLevel,\n    minimum_required_for_action: contextLevel,\n    legacy_cc_level_role: "builder_compatibility_only",\n    context_sufficient_for_selected_action: sufficient,\n    loaded_context_urls: opts.loadedUrls || [],\n    context_read_confirmed: isContextReadConfirmed(opts.contextReadConfirmed),\n    context_read_confirmation_boundary: buildContextReadConfirmationBoundary(),\n    context_readiness_notes: "",\n  };'''
b = replace_once(b, old_ctx, new_ctx, "context readiness")

old_vdraft = '''    verification_content: {\n      verification_level: opts.level,\n      verification_scope_label: opts.scopeLabel || opts.level,\n      what_was_checked: opts.whatWasChecked ? opts.whatWasChecked.split(",").map(s => s.trim()) : [],\n      verification_claim: opts.verificationClaim || "",\n      fresh_actions_performed: opts.freshActions ? opts.freshActions.split(",").map(s => s.trim()).filter(Boolean) : [],\n    },'''
new_vdraft = '''    verification_content: {\n      verification_level: opts.level,\n      verification_scope_label: opts.scopeLabel || opts.level,\n      what_was_checked: splitCsv(opts.whatWasChecked),\n      verification_claim: opts.verificationClaim || "",\n      fresh_actions_performed: splitCsv(opts.freshActions),\n      verification_claim_model: {\n        schema: "trinityaccord.verification-claim-model.v1",\n        digital_profile: opts.digitalProfile,\n        relationships_checked: splitCsv(opts.relationshipsChecked),\n        physical_observation: opts.physicalObservation,\n        external_witness: opts.externalWitness,\n        coverage_scope: opts.coverageScope,\n        limitations: splitCsv(opts.limitations),\n        claims_not_made: splitCsv(opts.claimsNotMade),\n        corrections_or_supersession_checked: parseBooleanStrict(opts.correctionsOrSupersessionChecked, "--corrections-or-supersession-checked"),\n        legacy_v_level: opts.level,\n        legacy_v_level_role: "builder_compatibility_only",\n      },\n    },'''
b = replace_once(b, old_vdraft, new_vdraft, "verification draft")

old_validation = '''    requireExplicit(opts, "freshActions", "--fresh-actions");\n\n    // Only V0-V5 are currently enabled for public submission\n    const vlevel = String(opts.level || "").toUpperCase();\n    const PUBLIC_VERIFICATION_LEVELS = new Set(["V0", "V1", "V2", "V3", "V4", "V5"]);\n    if (!PUBLIC_VERIFICATION_LEVELS.has(vlevel)) {\n      errorExit("Public intake currently accepts only V0-V5. V6+ strict evidence is reserved for a future/internal route.");\n    }'''
new_validation = '''    requireExplicit(opts, "freshActions", "--fresh-actions");\n    requireExplicit(opts, "digitalProfile", "--digital-profile");\n    requireExplicit(opts, "relationshipsChecked", "--relationships-checked");\n    requireExplicit(opts, "physicalObservation", "--physical-observation");\n    requireExplicit(opts, "externalWitness", "--external-witness");\n    requireExplicit(opts, "coverageScope", "--coverage-scope");\n    requireExplicit(opts, "limitations", "--limitations");\n    requireExplicit(opts, "claimsNotMade", "--claims-not-made");\n    requireExplicit(opts, "correctionsOrSupersessionChecked", "--corrections-or-supersession-checked");\n\n    const vlevel = String(opts.level || "").toUpperCase();\n    const PUBLIC_VERIFICATION_LEVELS = new Set(["V0", "V1", "V2", "V3", "V4", "V5"]);\n    if (!PUBLIC_VERIFICATION_LEVELS.has(vlevel)) {\n      errorExit("New public verification records accept only legacy V0-V5 as Builder compatibility metadata. V4+, V6, V7, and V8 are historical-only; use digital/physical/witness dimensions.");\n    }\n    if (!DIGITAL_PROFILES.has(String(opts.digitalProfile))) errorExit("--digital-profile has an unsupported value");\n    const relationships = splitCsv(opts.relationshipsChecked);\n    if (!relationships.length || relationships.some(v => !RELATIONSHIP_TYPES.has(v))) errorExit("--relationships-checked must contain supported comma-separated relationship ids");\n    if (!PHYSICAL_OBSERVATIONS.has(String(opts.physicalObservation))) errorExit("--physical-observation has an unsupported value");\n    if (!EXTERNAL_WITNESSES.has(String(opts.externalWitness))) errorExit("--external-witness has an unsupported value");\n    if (!COVERAGE_SCOPES.has(String(opts.coverageScope))) errorExit("--coverage-scope has an unsupported value");\n    if (!splitCsv(opts.limitations).length) errorExit("--limitations must contain at least one limitation");\n    if (!splitCsv(opts.claimsNotMade).length) errorExit("--claims-not-made must contain at least one bounded claim not made");\n    parseBooleanStrict(opts.correctionsOrSupersessionChecked, "--corrections-or-supersession-checked");'''
b = replace_once(b, old_validation, new_validation, "verification validation")

opts_anchor = '''    freshActions: args.freshActions || "",\n    contextSufficientForSelectedAction: args.contextSufficientForSelectedAction,'''
opts_new = '''    freshActions: args.freshActions || "",\n    digitalProfile: args.digitalProfile || "",\n    relationshipsChecked: args.relationshipsChecked || "",\n    physicalObservation: args.physicalObservation || "",\n    externalWitness: args.externalWitness || "",\n    coverageScope: args.coverageScope || "",\n    limitations: args.limitations || "",\n    claimsNotMade: args.claimsNotMade || "",\n    correctionsOrSupersessionChecked: args.correctionsOrSupersessionChecked,\n    actionProfile: args.actionProfile || "",\n    contextSufficientForSelectedAction: args.contextSufficientForSelectedAction,'''
b = replace_once(b, opts_anchor, opts_new, "builder opts")

help_anchor = '''  --context-level CC-3          Context depth level (explicit for formal records)\n'''
help_new = '''  --action-profile PROFILE     Current action profile: discovery, interpretation, verification, record_action, or deep_research.\n                                 Defaults from record type; CC remains compatibility metadata.\n  --context-level CC-3          Legacy context depth compatibility field (explicit for formal records)\n'''
b = replace_once(b, help_anchor, help_new, "builder help context")
verification_help_anchor = '''  # ── Verification (formal: requires print-oath + --readback) ───────\n'''
verification_options = '''  Verification claim options (all required for new verification records):\n    --digital-profile context_only|reference_checked|integrity_checked|independent_reproduction|full_public_digital\n    --relationships-checked comma,separated,relationship_ids\n    --physical-observation none|public_media_review|remote_live_witness|onsite_observation|forensic_examination\n    --external-witness none|notarial_scope|independent_report|institutional_attestation|regulatory_or_court_record\n    --coverage-scope single_target|component_subset|multi_component|all_declared_public_digital_targets\n    --limitations comma,separated,limitations\n    --claims-not-made comma,separated,bounded_claims\n    --corrections-or-supersession-checked true|false\n    V4+, V6, V7, and V8 are historical-only labels and are not accepted for new public submissions.\n\n'''
b = replace_once(b, verification_help_anchor, verification_options + verification_help_anchor, "verification options help")
b = b.replace('    --verification-level V3 \\\n    --scope-label "V3-minimal" \\\n', '    --verification-level V3 \\\n    --scope-label "legacy V3 compatibility" \\\n    --digital-profile integrity_checked \\\n    --relationships-checked "hashes,mirrors_bytes" \\\n    --physical-observation none \\\n    --external-witness none \\\n    --coverage-scope component_subset \\\n    --limitations "not full public coverage,no physical examination" \\\n    --claims-not-made "semantic truth,institutional endorsement" \\\n    --corrections-or-supersession-checked true \\\n')

field_anchor = '  "verification_content.fresh_actions_performed": "Fresh actions performed during this verification session, not historical or assumed actions.",\n'
field_new = field_anchor + '''  "verification_content.verification_claim_model": "Current multidimensional verification claim. Separates digital profile, evidence relationships, physical observation, external witness, coverage and limitations.",\n  "verification_content.verification_claim_model.digital_profile": "Current descriptive digital verification profile.",\n  "verification_content.verification_claim_model.relationships_checked": "Exact evidence relationships checked.",\n  "verification_content.verification_claim_model.physical_observation": "Separate physical observation state; never automatically raises digital verification.",\n  "verification_content.verification_claim_model.external_witness": "Separate notarial, independent, institutional, regulatory or court witness scope.",\n'''
b = replace_once(b, field_anchor, field_new, "field explanations")
write(builder_path, b)

# Field guidance mirrors Builder requirements.
guidance = load("downloads/record-chain-agent-field-guidance.v1.json")
guidance["version"] = "1.3.0"
vg = guidance["record_types"]["verification"]
vg["before_build"] = [
    "Describe only verification actions actually performed in the current work.",
    "Use V0-V5 only as legacy Builder compatibility metadata.",
    "Select a digital_profile, exact evidence relationships, physical observation, external witness, coverage scope, limitations, claims not made, and corrections/supersession status.",
    "V4+, V6, V7, and V8 are historical-only and must not be used for a new public submission.",
    "Physical observation, notarization, or external witness never automatically raises digital verification or creates authority.",
]
vg["record_specific_required_cli_options"] = [
    "--verification-level V0|V1|V2|V3|V4|V5",
    "--digital-profile",
    "--relationships-checked",
    "--physical-observation",
    "--external-witness",
    "--coverage-scope",
    "--limitations",
    "--claims-not-made",
    "--corrections-or-supersession-checked true|false",
    "--what-was-checked",
    "--verification-claim",
    "--fresh-actions",
]
vg["public_verification_level_limit"] = "V0-V5 only"
vg["v6_v8_status"] = "historical_compatibility_only"
vg["current_claim_model"] = "/api/verification-claim-model.v1.json"
guidance["fields"]["verification_level"]["meaning"] = "Legacy V0-V5 compatibility metadata for a verification record; not the current headline model."
guidance["fields"]["verification_level"]["how_to_fill"] = "Use V0-V5 only and pair it with the complete verification_claim_model. Never use V4+, V6, V7, or V8 for a new public submission."
save("downloads/record-chain-agent-field-guidance.v1.json", guidance)

# Add current model notice to active human and text entrypoints.
notice = """
> **Current interpretation and verification model:** The Chronicle has no current fixed five-stage, seven-stage, or other fixed-stage periodization. Use objective chronology, quarter navigation, overlapping categories, and explicitly provisional interpretation. New verification reports separate digital profile, evidence relationships, physical observation, and external witness; V4+/V6/V7/V8 are historical-only labels. See `/interpretation-verification-model/`, `/api/interpretation-model-policy.v1.json`, and `/api/verification-claim-model.v1.json`.
"""
for path in ["README.md", "index.md", "agent-start.md", "agent-first-contact.md", "external-agent-quickstart.md", "verify.md", "verification-materials.md"]:
    insert_after_first_h1(path, notice)
llms = text("llms-full.txt")
if "CURRENT INTERPRETATION AND VERIFICATION MODEL" not in llms:
    llms += "\n\nCURRENT INTERPRETATION AND VERIFICATION MODEL\n- No current fixed five-stage, seven-stage, or other fixed-stage Chronicle periodization.\n- Objective chronology; quarter navigation; overlapping categories; provisional interpretations.\n- New verification claims separate digital profile, evidence relationships, physical observation, and external witness.\n- V4+, V6, V7, V8 are historical-only for new public submissions.\n- Read /api/interpretation-model-policy.v1.json and /api/verification-claim-model.v1.json.\n"
    write("llms-full.txt", llms)

# Human public page.
public_page = ROOT / "interpretation-verification-model.md"
public_page.write_text('''---\ntitle: "Current Interpretation and Verification Model"\npermalink: /interpretation-verification-model/\n---\n\n# Current Interpretation and Verification Model\n\nThe Chronicle has **no current fixed five-stage, seven-stage, or other fixed-stage periodization**. The former seven-stage model was an earlier AI-generated interpretation based on calendar buckets and broad keyword matching. It remains preserved only as historical interpretation where it appears in old records.\n\nCurrent Chronicle use separates:\n\n- objective Ethereum NFT event chronology;\n- calendar-quarter navigation;\n- overlapping descriptive categories;\n- explicitly provisional, revisable interpretation.\n\nFor new verification records, do not use one ascending ladder to mix digital checks, physical observation, and institutional or notarial witness. Report these separately:\n\n- `digital_profile`;\n- `relationships_checked`;\n- `physical_observation`;\n- `external_witness`;\n- `coverage_scope`;\n- limitations and claims not made.\n\nThe Builder retains V0-V5 and CC-0 through CC-5 only as compatibility metadata. V4+, V6, V7, and V8 remain readable in historical records but are retired for new public submissions. Physical observation and notarization do not automatically prove digital integrity, semantic truth, institutional endorsement, or canonical authority.\n\nMachine sources:\n\n- `/api/interpretation-model-policy.v1.json`\n- `/api/verification-claim-model.v1.json`\n- `/api/context-action-profiles.v1.json`\n- `/api/verification-profiles.v1.json`\n\nBitcoin Originals remain final. This page and all later guidance are non-amending.\n''', encoding="utf-8")

# Update Chronicle generated files from the patched deterministic generator.
# Executed by workflow after this script.

# Update regression test expectations for current public V values.
test_path = "tests/test_interpretation_and_verification_migration.py"
t = text(test_path)
t = t.replace('assert compatibility["new_submission_forbidden_values"] == ["V6", "V7", "V8"]', 'assert compatibility["new_submission_forbidden_values"] == ["V4+", "V6", "V7", "V8"]')
t = t.replace('assert compatibility["retired_physical_mapping"]["V8"] == "physical_observation=forensic_examination"', 'assert compatibility["retired_mapping"]["V8"] == "physical_observation=forensic_examination"')
t = t.replace('assert profiles["current_submission_policy"]["legacy_v_allowed"] == ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"]', 'assert profiles["current_submission_policy"]["legacy_v_allowed"] == ["V0", "V1", "V2", "V3", "V4", "V5"]')
t = t.replace('assert levels["new_submission_policy"]["allowed_legacy_v_values"] == ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"]', 'assert levels["new_submission_policy"]["allowed_legacy_v_values"] == ["V0", "V1", "V2", "V3", "V4", "V5"]')
t = t.replace('assert levels["new_submission_policy"]["forbidden_legacy_v_values"] == ["V6", "V7", "V8"]', 'assert levels["new_submission_policy"]["forbidden_legacy_v_values"] == ["V4+", "V6", "V7", "V8"]')
t = t.replace('if level["id"] in {"V6", "V7", "V8"}:', 'if level["id"] in {"V4+", "V6", "V7", "V8"}:')
write(test_path, t)

# Wire regression into current-system runner.
runner_path = "scripts/run_current_system_tests.py"
runner = text(runner_path)
anchor = '        "scripts/test_agent_e2e_journey_matrix.py",\n'
if 'tests/test_interpretation_and_verification_migration.py' not in runner:
    runner = replace_once(runner, anchor, anchor + '        "tests/test_interpretation_and_verification_migration.py",\n', "current test runner")
write(runner_path, runner)

print("MIGRATION_PATCH_APPLIED")
