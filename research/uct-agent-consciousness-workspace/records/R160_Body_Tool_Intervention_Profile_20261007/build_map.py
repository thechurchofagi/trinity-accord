#!/usr/bin/env python3
"""Build the scoped R160 extension from the exact R159 parent graph."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = Path(__file__).resolve().parent
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
NOTE_REL = "records/R160_Body_Tool_Intervention_Profile_20261007/Body_Tool_Intervention_Profile_v0_1.md"
NOTE = ROOT / NOTE_REL


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


parent_graph_hash = sha(GRAPH)
note_hash = sha(NOTE)
g = json.loads(GRAPH.read_text())
assert g["revision"] == "R159-v1.0"
assert len(g["nodes"]) == 418 and len(g["rules"]) == 200
assert parent_graph_hash == "d14e7e845e5c122bf3e12d55a078e06be1307cb1f091c7c5d5d2be5388daf32e"

common = {
    "object_domain": "Finite preregistered human upper-limb/tool-use trial family with independently grounded intervention and readout roles; actual execution is not claimed.",
    "quantifiers": "For each fixed protocol Pi, candidate slot family k, declared normalized effect/error model and epsilon>0; no universal necessity, sufficiency, anatomical-membership or F_O equivalence.",
    "bearer_time_signature": "Each trial fixes its own actual P_omega,I_omega,complete K_omega,D_omega,Phi_omega,h_omega. Participant lineage does not identify complete organizations across trials. Internal tokens and external referents retain different sorts.",
    "source_anchor": {"path": NOTE_REL, "sha256": note_hash, "locator": "§§2–8"},
    "purpose": "Give the R159 body-slot/tool-slot gap a falsifiable relative causal profile while preserving semantic and phenomenal limits.",
    "thought_experiments": NOTE_REL + " §7",
    "open_obligations": ["F153-09", "F153-10", "F153-11", "F153-12", "F153-17", "R160-G1", "R160-G2", "R160-G5"],
    "machine_formalized": False,
}


def node(id_, kind, label, statement, domain, status, proof, limits, routes):
    contract = dict(common)
    contract["premise_routes"] = routes
    return {
        "id": id_, "kind": kind, "label": label, "statement": statement,
        "domain": domain, "scope": domain, "source": NOTE_REL,
        "source_lineage": NOTE_REL, "status": status, "proof": proof,
        "counterexamples_and_limits": limits, "formal_contract_R160": contract,
    }


new_nodes = [
    node(
        "R160:INTERVENTION_PROFILE_CONTRACT",
        "DEFINITION_AND_ASSUMPTION_PACKAGE",
        "Intervention Profile Contract",
        "Fix Pi, actual trial tokens P_omega/I_omega, internal slot family k, independently physically grounded J_B and J_T, tool-absent body readouts Y_B and tool-specific readouts Y_T, preregistered normalized effect bounds L/U and epsilon>0. Let a=delta(Y_B;J_B), x=delta(Y_B;J_T), b=delta(Y_T;J_B), y=delta(Y_T;J_T). Undefined or noncommensurable effects block classification rather than count as zero. Reports do not define these roles.",
        "Declared finite protocol only; J_B/J_T fidelity, readout semantics, normalization, error bounds and admissibility are simultaneous premises.",
        "DECLARED_PROTOCOL_RELATIVE_PHYSICAL_WITNESS_CONTRACT",
        "Typed definition and preregistration package. The rational grid establishes abstract consistency only.",
        "No actual dataset or selective intervention is supplied; behavioral names do not ground pathways; unsafe interventions excluded.",
        [],
    ),
    node(
        "R160:FOUR_WAY_PROFILE",
        "CONDITIONAL_CLASSIFICATION_RESULT",
        "Four-Way Body/Tool Profile",
        "Under the full profile contract, define B_Pi(k) iff L(a)>epsilon and L(a)-U(x)>epsilon; define T_Pi(k) iff L(y)>epsilon and L(y)-U(b)>epsilon. Exactly one Boolean pair (1,0),(0,1),(1,1),(0,0) holds, interpreted only as body-dominant, tool-dominant, overlap or neither in Pi. Positive off-diagonal effects are compatible with every class.",
        "Exactly one fixed Pi/effect/error model satisfying every R160 profile premise.",
        "MANUAL_BOOLEAN_CLASSIFICATION_WITH_EXACT_FINITE_CHECK",
        "Boolean exhaustiveness gives four cases. The 3/4,1/4,1/4,3/4 matrix at epsilon=1/4 witnesses overlap with positive cross-effects; 625 exact grid matrices show all four classes, including under positive off-diagonals.",
        "A category is not anatomical membership, complete mechanism, external-reference correctness or F_O. Grid counts are not population frequencies.",
        [{"rule": "r160_four_way_profile", "all_of": ["R160:INTERVENTION_PROFILE_CONTRACT"]}],
    ),
    node(
        "R160:LATENT_LABEL_NONIDENTIFICATION",
        "CONDITIONAL_LIMIT_THEOREM",
        "Latent Label Nonidentification",
        "For any finite latent input/output model and any bijection pi of its latent carrier, transporting the initial law, each intervention kernel and the emission kernel by pi leaves every finite observable input/output law unchanged. Hence an ungrounded latent name body/tool is not identified by the observable profile alone.",
        "Finite latent-state models with transported initial, transition and emission laws; semantic/anatomical predicates not included among observed grounded variables.",
        "STANDARD_RELABELING_ARGUMENT_WITH_EXACT_INSTANCE_CHECK",
        "Change variables z_t to pi(z_t) in the finite path sum. The verifier checks 1,024 deterministic two-state/two-input/binary-output length-three instances.",
        "Independent physical grounding can identify protocol-relative causal roles; it still does not yield anatomy, complete organization or phenomenal ownership. Standard mathematics, no historical novelty claim.",
        [],
    ),
    node(
        "R160:TOKENWISE_APPLICATION_BOUNDARY",
        "CONDITIONAL_SCOPE_RESULT",
        "Tokenwise C1 Application Boundary",
        "Given R159 frame-relation transport separately for each admitted trial and the R160 trial-family contract, each trial's grounded internal relation transports under its own h_omega. The cross-trial matrix S_Pi and its class do not thereby become one within-token experiential relation or an F_O contrast; a cross-trial correspondence, measurement bridge and fixed selected target are additional premises.",
        "Same declared trial family and per-trial bindings; no common K,D,Phi,h is presumed across different interventions/times.",
        "MANUAL_SCOPE_AND_BINDING_DEDUCTION",
        "Instantiate R159 tokenwise in each trial. Its quantifiers do not bind a single h across different actual tokens. Cross-trial causal contrasts therefore require an added comparison bridge.",
        "Does not deny cross-trial science; it blocks an illicit object/time/signature substitution. No report-to-F or C1 verification follows.",
        [{"rule": "r160_tokenwise_application_boundary", "all_of": ["R159:FRAME_RELATION_TRANSPORT", "R160:INTERVENTION_PROFILE_CONTRACT"]}],
    ),
]

new_rules = [
    {
        "id": "r160_four_way_profile",
        "all_of": ["R160:INTERVENTION_PROFILE_CONTRACT"],
        "conclusion": "R160:FOUR_WAY_PROFILE",
        "statement": new_nodes[1]["statement"],
        "proof_sketch": new_nodes[1]["proof"],
        "source": NOTE_REL + " §§2–3",
        "kind": "DEFINITIONAL_CLASSIFICATION",
        "review": "MANUAL_ALL_PREMISES_AND_EXACT_GRID_CHECK",
        "formal_contract_R160": {
            "premise_connective": "AND",
            "bindings_required": ["same Pi,k,normalized metric,error bounds,epsilon", "J_B/J_T and Y_B/Y_T independently grounded before target outputs", "undefined effects do not default to zero"],
            "quantification": "Each jointly admissible protocol instance; no universal body/F_O theorem.",
            "proof_location": NOTE_REL + " §§2–3",
            "source_sha256": note_hash,
            "machine_proof": False,
        },
    },
    {
        "id": "r160_tokenwise_application_boundary",
        "all_of": ["R159:FRAME_RELATION_TRANSPORT", "R160:INTERVENTION_PROFILE_CONTRACT"],
        "conclusion": "R160:TOKENWISE_APPLICATION_BOUNDARY",
        "statement": new_nodes[3]["statement"],
        "proof_sketch": new_nodes[3]["proof"],
        "source": NOTE_REL + " §5",
        "kind": "CONDITIONAL_SCOPE_DEDUCTION",
        "review": "MANUAL_OBJECT_TIME_SIGNATURE_AUDIT",
        "formal_contract_R160": {
            "premise_connective": "AND",
            "bindings_required": ["same trial family Pi", "R159 transport instantiated with each trial's own P_omega,I_omega,K_omega,D_omega,Phi_omega,h_omega", "no silent common h or report/F bridge"],
            "quantification": "All admitted trials individually; cross-trial conclusion only with additional declared bridge.",
            "proof_location": NOTE_REL + " §5",
            "source_sha256": note_hash,
            "machine_proof": False,
        },
    },
]

ids = {n["id"] for n in g["nodes"]}
rids = {r["id"] for r in g["rules"]}
assert not ids.intersection(n["id"] for n in new_nodes)
assert not rids.intersection(r["id"] for r in new_rules)
g["nodes"].extend(new_nodes)
g["rules"].extend(new_rules)

amended = []
for n in g["nodes"]:
    if n["id"] == "R159:SELECTED_OWNERSHIP_APPLICATION":
        n["formal_contract_R160"] = {
            "amends": "Application status only; inherited statement/contracts retained.",
            "effective_reading": "R160 supplies a protocol-relative causal dominance discriminator and its nonidentification limit. It partially advances the body/tool grounding obligation but does not close physical selectivity, complete realization, B_min or F_O measurement.",
            "source_anchor": {"path": NOTE_REL, "sha256": note_hash, "locator": "§§2–5,8–9"},
            "machine_formalized": False,
        }
        amended.append(n["id"])
assert amended == ["R159:SELECTED_OWNERSHIP_APPLICATION"]

g["revision"] = "R160-v1.0"
g["date"] = "2026-10-07"
g["research_R160"] = {
    "start_head": "36e73dda56acb6036d87f20a598e63c3793f24e2",
    "first_checkpoint": "97fbb37dfe45c2b88cbf10e35fcfe9acf90ed25e",
    "parent_graph_sha256": parent_graph_hash,
    "note": NOTE_REL,
    "new_nodes": 4,
    "new_rules": 2,
    "status": "PROTOCOL_RELATIVE_BODY_TOOL_DISCRIMINANT_AND_NONIDENTIFICATION_BRIDGE_OPEN",
    "contract": "formal_contract_R160 for four new nodes, two rules and one explicit R159 application amendment only",
    "actual_experiment": False,
    "empirical_F_witness": False,
    "global_semantic_proof": False,
}

all_ids = [n["id"] for n in g["nodes"]]
all_rids = [r["id"] for r in g["rules"]]
assert len(all_ids) == len(set(all_ids)) == 422
assert len(all_rids) == len(set(all_rids)) == 202
idset = set(all_ids)
for r in g["rules"]:
    assert r["conclusion"] in idset
    assert all(x in idset for x in r["all_of"])

# Kahn acyclicity over deductive rules.
succ = {x: [] for x in idset}
indeg = {x: 0 for x in idset}
for r in g["rules"]:
    for p in r["all_of"]:
        succ[p].append(r["conclusion"])
        indeg[r["conclusion"]] += 1
q = [x for x in idset if indeg[x] == 0]
seen = 0
while q:
    x = q.pop()
    seen += 1
    for y in succ[x]:
        indeg[y] -= 1
        if indeg[y] == 0:
            q.append(y)
assert seen == len(idset)

dump(GRAPH, g)
dump(REC / "MAP_EXTENSION.json", {"revision": "R160-v1.0", "parent_graph_sha256": parent_graph_hash, "note_sha256": note_hash, "nodes": new_nodes, "rules": new_rules, "amended_nodes": amended})

proofs = {
    "schema": "UCT_R160_PROOF_LEDGER/v1",
    "note_sha256": note_hash,
    "entries": [{
        "id": n["id"], "kind": n["kind"], "statement": n["statement"],
        "domain": n["domain"], "all_premises": n["formal_contract_R160"]["premise_routes"],
        "proof_or_source": n["proof"], "counterexamples_and_limits": n["counterexamples_and_limits"],
        "status": n["status"], "thought_experiment_role": n["formal_contract_R160"]["thought_experiments"],
    } for n in new_nodes],
    "historical_novelty": "Boolean classification and latent relabeling are established mathematics; novelty claimed only for the typed project application/repair.",
}
dump(REC / "PROOF_LEDGER.json", proofs)

gaps = {
    "schema": "UCT_R160_GAP_LEDGER/v1",
    "gaps": [
        {"id": "R160-G1", "location": "Profile contract J_B/J_T", "impact": ["R160:INTERVENTION_PROFILE_CONTRACT", "R160:FOUR_WAY_PROFILE", "R159:SELECTED_OWNERSHIP_APPLICATION"], "counterexample": "A nominal proprioceptive manipulation also changes attention or tool feedback; a nominal tool perturbation changes biological afference.", "repaired": "Independent intervention-fidelity checks made simultaneous premises; names alone rejected.", "unresolved": "No concrete selective human intervention pair or fidelity data supplied."},
        {"id": "R160-G2", "location": "Effect normalization/error model", "impact": ["R160:FOUR_WAY_PROFILE"], "counterexample": "Kinematic latency and crossmodal interference in different units cannot be subtracted without a declared normalization.", "repaired": "Predeclared dimensionless effects, bounds and epsilon required; undefined is not false.", "unresolved": "No empirically calibrated common normalization or power analysis supplied."},
        {"id": "R160-G3", "location": "Cross-trial C1 use", "impact": ["R160:TOKENWISE_APPLICATION_BOUNDARY"], "counterexample": "Different intervention trials need not share complete K,D,Phi,h even for one participant.", "repaired": "Per-trial h_omega and an explicit additional cross-trial bridge required.", "unresolved": "No complete actual trial-token correspondence established."},
        {"id": "R160-G4", "location": "Latent body/tool naming", "impact": ["R160:LATENT_LABEL_NONIDENTIFICATION", "R160:FOUR_WAY_PROFILE"], "counterexample": "Transport every latent kernel/emission through a state permutation; all finite observations stay fixed while names swap.", "repaired": "Only independently grounded intervention/readout roles receive protocol-relative labels.", "unresolved": "Anatomical membership, external-reference truth and complete constitutive boundaries remain separate."},
        {"id": "R160-G5", "location": "Selected ownership bridge", "impact": ["R159:SELECTED_OWNERSHIP_APPLICATION", "R160:TOKENWISE_APPLICATION_BOUNDARY"], "counterexample": "Tool use changes a body-only kinematic measure without establishing familiar felt ownership; tool RHI drift and report can also diverge.", "repaired": "Classifier excludes ownership reports and explicitly refuses F_O equivalence.", "unresolved": "Independent B_min semantics and fallible no-report measurement remain open."},
        {"id": "R160-G6", "location": "Primary-source scope", "impact": ["R160:INTERVENTION_PROFILE_CONTRACT"], "counterexample": "One tool effect can admit body-schema, task-learning or attention explanations.", "repaired": "Competing Holmes attention account and source-specific scopes retained.", "unresolved": "No raw-data reanalysis, exhaustive literature review or unified factorial study."},
        {"id": "R160-G7", "location": "Formal verification level", "impact": ["all R160 nodes/rules"], "counterexample": "Acyclic references and finite enumerations can pass while physical premises or prose semantics are wrong.", "repaired": "Machine checks and manual arguments labeled separately.", "unresolved": "No proof-assistant certification, independent review or global semantic consistency proof."},
    ],
}
dump(REC / "GAP_LEDGER.json", gaps)

sources = {
    "schema": "UCT_R160_SOURCE_LEDGER/v1",
    "fixed_A": {"path": "records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md", "sha256": "2e4469afbd1d1862463cc36396dd6e2b50c418f22d6f0fd584bbae33bfedc6f4", "scope": "§§8.11–8.14,10.1–10.3,11,14.7–14.10"},
    "primary_sources": [
        {"id": "S1", "citation": "Cardinali et al. 2009", "doi": "10.1016/j.cub.2009.05.009", "scope": "Metadata plus later primary-paper descriptions; PubMed record had no abstract; no raw/full-text claim."},
        {"id": "S2", "citation": "Cardinali et al. 2011", "doi": "10.1016/j.neuropsychologia.2011.09.033", "scope": "PubMed abstract: tactile-dependent access/localization result; no raw reanalysis."},
        {"id": "S3", "citation": "Martel et al. 2019", "doi": "10.1038/s41598-019-41928-1", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6445103/", "scope": "Full primary methods/results windows on blindfolded tool use, free-hand transport/grip kinematics and stated controls."},
        {"id": "S4", "citation": "Maravita et al. 2002", "doi": "10.1016/S0010-0277(02)00003-3", "pmid": "11869727", "scope": "Primary abstract only; crossed-tool visuotactile-interference result."},
        {"id": "S5", "citation": "Holmes et al. 2007", "pmcid": "PMC1885399", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1885399/", "scope": "Full primary discussion/methodological windows; alternative spatial-attention account and confounds."},
        {"id": "S6", "citation": "Weser et al. 2017", "doi": "10.1016/j.concog.2017.07.002", "scope": "PubMed abstract plus publisher abstract: chopsticks/teacup contrast, skill/recent-use modulation; no raw reanalysis."},
        {"id": "S7", "citation": "Martel et al. 2016", "doi": "10.3389/fnhum.2016.00272", "url": "https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2016.00272/full", "scope": "Full case-report methods/results windows; single deafferented patient, longitudinal kinematics."},
    ],
    "failed_or_limited": ["PubMed pages for S2/S4 intermittently returned reCAPTCHA on open; search-index abstracts retained.", "S1 full article not retrieved; no unsupported method detail imported.", "No raw datasets or supplements downloaded; no exhaustive priority search."],
    "new_neural_mechanism_claim": False,
    "raw_data_analysis": False,
    "human_experiment_executed": False,
}
dump(REC / "SOURCE_LEDGER.json", sources)

audit = {
    "schema": "UCT_R160_MAP_AUDIT/v1", "revision": "R160-v1.0",
    "counts": {"nodes": 422, "rules": 202, "new_nodes": 4, "new_rules": 2},
    "structure": {"unique_node_ids": True, "unique_rule_ids": True, "all_endpoints_present": True, "deductive_graph_acyclic": True, "inherited_nodes_rules_retained": True, "context_links_retained": len(g["context_links"])},
    "manual_checks": {
        "concept_quantifier_scope": "PASS_WITH_PROTOCOL_RELATIVITY",
        "all_of_simultaneous_premises": "PASS",
        "joint_satisfiability": "PASS_ABSTRACT_RATIONAL_WITNESS_ONLY",
        "object_time_signature_actuality": "PASS_PER_TRIAL_COMMON_H_NOT_ASSUMED",
        "evidence_level": "PASS_EXACT_CHECKS_SEPARATED_FROM_EMPIRICAL_EVIDENCE",
        "direction": "PASS_NO_REPORT_OR_PROFILE_TO_C1_FO_OR_BASAL_GATE",
        "unlinked_concept_consistency": "PASS_ANATOMY_REFERENCE_BODY_IMAGE_AGENCY_CONCEPTUAL_I_REPORT_REMAIN_SEPARATE",
        "purpose": "PASS_DIRECTLY_ADVANCES_R159_BODY_TOOL_GROUNDING_GAP",
    },
    "not_established": ["actual selective intervention pair", "complete neural organization", "anatomical membership from profile", "B_min or empirical F_O witness", "C1", "global semantic proof", "proof-assistant certification"],
    "direction_checks": {"after_topic": "PASS", "after_result": "PASS_WITH_OPEN_BRIDGE", "before_save": "PENDING_FINAL_REREAD"},
}
dump(REC / "MAP_AUDIT.json", audit)
dump(REC / "AMENDMENTS.json", {"schema": "UCT_R160_AMENDMENTS/v1", "amendments": [{"node": "R159:SELECTED_OWNERSHIP_APPLICATION", "kind": "additive_application_status", "effect": g["nodes"][all_ids.index("R159:SELECTED_OWNERSHIP_APPLICATION")]["formal_contract_R160"]}], "historical_text_preserved": True})

print(json.dumps({"revision": g["revision"], "nodes": len(g["nodes"]), "rules": len(g["rules"]), "note_sha256": note_hash, "parent_graph_sha256": parent_graph_hash, "dag": True}, indent=2))
