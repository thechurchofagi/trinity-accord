"""Record actual candidate text review, source versions, and bounded rederivations."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json
import subprocess

HERE = Path(__file__).parent
REPO = HERE.parents[1] / "uct_repo"
ROOT = REPO / "research/uct-agent-consciousness-workspace"
RECORDS = ROOT / "records"
MODEL = HERE.parent / "model"
BASE = json.loads((HERE / "baseline/UCT_EFFECTIVE_GRAPH.json").read_text())


def file_sha(path):
    return sha256(path.read_bytes()).hexdigest()


def record_sha(row):
    return sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


MODULE_REVIEWS = {
"R190": "The four PC/BDCC profiles are witnessed alternatives under one selected target, not universal physiological independence. Deliberate/reflex label swaps retain the modeled routes and therefore cannot identify a feeling. Actual bearer/endpoint/consumer/timing grounding is not supplied by the finite rows.",
"R191": "The precommit consumer separates post-hoc use from authorization, and generic formation history does not exclude an adaptive reflex. Definition availability must not be read as actual PCBDCC implying OCCA, or generic RetBind plus OCCA implying a specific conflict-driven revision. The latter graph typing remains an OPEN normalization obligation, not a new source theorem.",
"R192": "Complete K* twins preserve every isomorphism-invariant grounded predicate and, under C1, complete experiential type. A selected projection twin defeats only bridges factoring through that projection. Actual historical expansion can split that projection but does not orient familiar mineness.",
"R193": "The finite H_hist/U/E/R contrast package reduces 65536 Boolean tables to an unoriented conjunction/complement pair. One independent positive anchor selects its numerical pole; target naming remains open. Here H means actual retained history and must not be identified by letter with later H_fam.",
"R194": "The unanchored global-complement symmetry remains valid. The displayed general component count must additionally handle contradictory anchors in one component; the correction overlay returns zero for cycle OR anchor/path inconsistency. The seven-vertex single-anchor examples are unaffected.",
"R195": "The latent complement simultaneously changes Z, marker signs and the consequence kernel, retaining every declared do(Q) law. Functional Y ordering can orient a structural pole only by adding its full-table bridge; it is not independently familiar-mineness direction. No sensorimotor protocol supplies that semantic bridge.",
"R196": "A-sensitive/V-invariant Boolean markers leave exactly two complements, while two-axis-sensitive outcomes give XOR/XNOR. The structural and outcome dissociation removes a value confound but does not choose a phenomenal pole. Any historical requirement that an endpoint be nonverbal is superseded by R197's modality-neutral correction.",
"R197": "Signed fallible reliability orients an independently fixed target by a contrast sign; modality alone is irrelevant. Equal marginals do not preserve class-conditional direction across domains. Reports can be evidence without defining the target, and no endpoint premise is needed for U1.",
"R198": "The 166 monotone endpoint-fixed four-bit functions show an underdetermined aggregate within the stated Boolean profile family. O/G/H_fam target coordinates remain separate from organizational C; the profile is not an exhaustive ontology. Orientation cannot select the coordinate it is meant to orient.",
"R199": "Identical current controlled state/kernel/readout/exogenous coupling yields identical future trace laws by induction. A difference rejects the clone package but does not uniquely identify RetBind or lineage. Complete operational equality is not silently equated with complete historical organization.",
"R200": "Unsigned proxy batteries remain invariant under a latent complement and conditional-law swap. Signed calibration and class-specific transport are distinct premises; formation-by-use interactions can remain positive with fixed H_fam through confounding. Actual use and use evidence remain separate.",
"R201": "The sufficient strict-margin theorem survives under one coherent calibration/transport law. The rho=1,b>0 witnesses are impossible and withdrawn; coherent rho=1/2 examples replace them without arbitrary-budget sharpness. The strict-margin all_of premise must be removed from the equality/below-threshold witness rule.",
"R202": "The exact mixture inversion survives under conditional independence or independently zero aggregate residual. A bound on nonzero conditional dependence yields one shared residual feasible set, not point identification. The coherent R203 twin reverses the naive inferred direction. Reporting-domain recovery still does not transport itself to nonreporting T.",
"R203": "The total-covariance identity retains the prevalence, signed endpoint, residual and actual-use contract in one law. A defended residual budget can orient Delta when K exceeds it; a trivial universal covariance cap is uninformative. Fixed-sample concentration does not make audit missingness ignorable or validate H_fam.",
"R204": "S, prediction agreement K and actual writer gate U can vary independently for n>=2. State change is U AND mismatch in the stated update model; a matched feedback result is not evidence of no use. Error-gated and unconditional writers can share every prediction-state trace while write events differ. No RetBind/H_fam follows.",
"R205": "The concurrent two-source location/correspondence square preserves nominal success/alignment, and isolated probes recover selectors only in the fixed injective single-read class. The modular cancellation model consumes two branches while every whole-source assignment has the direct predictor's output. It attacks extension beyond that class, not its conditional theorem. The two-probe construction is sufficient, not a minimum-query result."
}

SPECIAL = {
"R194:COMPONENT_COUNT": "CORRECTION_REQUIRED: joint anchor/path consistency omitted for general anchored graphs.",
"R194:r_component_count": "CORRECTION_REQUIRED: use the fixed anchor map in the same graph and reject conflicts before 2^c.",
"R194:RELATIVE_ALIGNMENT": "CORRECTION_REQUIRED: add joint consistency when supplied anchors are part of the design.",
"R201:STRICTNESS_COUNTERMODELS": "WITHDRAW_ORIGINAL_DISPLAYED_WITNESSES: scalar tuples violate their joint-probability interpretation; coherent replacements supplied.",
"R201:r_strictness_witnesses": "CORRECTION_REQUIRED: strict-margin instance cannot also be equality/below-margin; alternative witness worlds need their own domain.",
"R202:CONDITIONAL_NONDIFFERENTIALITY": "CORRECTION_REQUIRED: separate exact independence from bounded departure route.",
"R202:AUDIT_INVERSION_RESULT": "CORRECTION_REQUIRED: exact rates require zero common residual; otherwise retain joint feasible rates.",
"R202:r_audit_inversion": "CORRECTION_REQUIRED: add coherent same-law positivity and strict independence/zero-residual branch.",
"R191:r_occa": "OPEN_NORMALIZATION: conditional definition availability is not an actual-instance implication from PCBDCC.",
"R191:r_history": "OPEN_NORMALIZATION: generic retention is not specific conflict-driven revision; retain a definition schema or add the actual specialization premises.",
"R193:DOMAIN": "SYMBOL_TYPE_GUARD: H here denotes H_hist, not later H_fam; no cross-module identification by bare letter.",
"R196:INDEPENDENT_ENDPOINT": "READ_WITH_R197_CORRECTION: independent signed reliability is the relevant premise; nonverbal modality is not necessary or sufficient."
}

modules, candidate_rows = [], []
for number in range(190, 206):
    prefix = "R" + str(number)
    directory = next(RECORDS.glob(prefix + "_*"))
    path = directory / "MAP_EXTENSION.json"
    graph = json.loads(path.read_text())
    modules.append({"module": prefix, "map_path": str(path.relative_to(ROOT)), "map_sha256": file_sha(path),
                    "note_path": str((directory/"RESEARCH_NOTE.md").relative_to(ROOT)), "note_sha256": file_sha(directory/"RESEARCH_NOTE.md"),
                    "source_note_read_scope": "Full RESEARCH_NOTE.md body, including model, proofs/arguments, scope and limits.",
                    "map_read_scope": "All node statements/scopes/quantifiers, all rule premises/conclusions/bindings and all context relationship texts. Historical checker source not fully reread or rerun by this auditor.",
                    "assessment": MODULE_REVIEWS[prefix]})
    for group, kind in (("nodes", "node"), ("rules", "rule"), ("context_links", "context")):
        for row in graph[group]:
            candidate_rows.append({"item_id": row["id"], "item_type": kind, "module": prefix,
                "source_record_sha256": record_sha(row),
                "freshly_read_statement": row.get("statement"), "scope": row.get("scope"),
                "quantifier": row.get("quantifier", row.get("quantifiers")),
                "all_of": row.get("all_of", []), "conclusion": row.get("conclusion"),
                "binding": row.get("binding"), "alternative_route_semantics": row.get("alternative_route_semantics"),
                "context_endpoints": {k: row[k] for k in ("from", "to", "source", "target") if k in row} if kind=="context" else None,
                "individual_finding": SPECIAL.get(row["id"]), "module_compatibility_assessment": MODULE_REVIEWS[prefix],
                "review_outcome": "REQUIRES_CORRECTION_OR_OPEN_NORMALIZATION" if row["id"] in SPECIAL else "SCOPED_TEXT_REVIEWED_KEEP_DISABLED",
                "actual_premises_discharged": False, "promoted_to_completed_map": False})

SCU_REDERIVATIONS = {
"C1": "For each nominal target t, every source x_i=t, so the pure consumers both output t regardless of (a,b). Induct over an arbitrary finite word. A calibrated identity forward row remains identical under matched replacement, whether or not a write event occurred. The statement is nominal, not all-intervention equality.",
"C2": "Under a fixed k-row schedule W, the actuator and predictor read columns c_a and c_b. Full-output preimages are the product of the two equal-column classes; mismatch-only preimages solve c_i XOR c_j=d. For restricted allowed inputs U, equivalent coordinates on every u in U cannot be separated. Distinct columns decide equality but mismatch symmetry does not identify the ordered pair.",
"C3": "An injective binary code of length ceil(log2 n) makes zero mismatch equivalent to a=b. For any deterministic adaptive exact protocol, follow its all-zero mismatch branch. If fewer probes are used, two source columns agree by pigeonhole, so their unequal pair follows that same branch as every equal pair. The algorithm cannot correctly decide both. This is classical separation applied to the stated model.",
"C4": "For independently known motor root a, choose x_a=0 and every other source 1. Motor output is 0; a pure predictor agrees exactly for root a. For a nonempty OR subset B, it agrees exactly when B={a}. At n>=2 zero observations leave both cases possible. This is a different information contract, not a violation of C3.",
"C5": "For arbitrary nonempty OR source sets A,B, unit input e_i gives mismatch exactly when i lies in their symmetric difference, so n units suffice. Along the adaptive all-zero branch compare (N,N) to each (N,N minus {i}); their only distinguishing input is e_i. Every i must be queried; n>=2 keeps each alternative nonempty. The four-source code alias is a counterexample to extrapolating the pure-route class, not to C3.",
"C6": "In a faithful-copy DAG, the output functions depend on the composite root-to-consumer map, not its relay factorization. One shared relay and two copies therefore match all source assignments. Under the corrected all-zero preparation, independently targeted 0-to-1 node write before both reads with no intervening overwrite yields shared (1,1), separate (0,1). Predictor-edge replacement yields (0,1) in both. The node/edge target and timing capability are new premises, not inferred from the result.",
"C7": "A postconsequence copy returns the same numerical root value as a pure predictor for every source assignment, so value-only readouts leave their timing fiber unresolved. Independently recorded read/consequence order distinguishes the roles. Neither a role name nor exact numerical agreement proves preconsequence prediction.",
"C8": "Given independent actual admission and complete same-instance P/I/K role grounding, C1 and correctly transported formula parameters yield the structural counterpart of the selected relation. C1-C7 or code output do not supply ACTUAL_BINDING. Formula transport does not automatically select a closed experiential substructure, RetBind, H_fam, conceptual self, report validity, local membership or a unique owner; U1 is unchanged."
}

scu_path = MODEL / "MAP_EXTENSION.json"
scu = json.loads(scu_path.read_text())
all_ids = {r["id"] for group in ("nodes", "rules", "context_links") for r in BASE[group]}
all_ids |= {r["item_id"] for r in candidate_rows}
all_ids |= {r["id"] for group in ("nodes", "rules", "context_links") for r in scu[group]}
scu_rows = []
for group, kind in (("nodes", "node"), ("rules", "rule"), ("context_links", "context")):
    for row in scu[group]:
        claim = row.get("claim_id", "").rsplit("-", 1)[-1]
        if not claim and row["id"].split(":")[-1] in SCU_REDERIVATIONS:
            claim = row["id"].split(":")[-1]
        note = SCU_REDERIVATIONS.get(claim)
        if kind == "context":
            note = "Reviewed this exact nondeductive link. " + row["statement"] + " It is provenance/compatibility context, not an actual-premise discharge or a new mathematical theorem."
        if note is None:
            note = "This node supplies the explicit " + row["kind"] + " required by the corresponding source protocol. Its statement and scope are retained as simultaneous conditional premises, not truths established by the checker: " + row["statement"]
        scu_rows.append({"item_id": row["id"], "item_type": kind, "source_record_sha256": record_sha(row),
                         "fresh_read_scope": "Complete node/rule/context record, including all_of, guard/binding and limits where present.",
                         "record_reviewed": row, "independent_semantic_assessment": note,
                         "status": "SCOPED_MODEL_REVIEW_COMPLETED_KEEP_DISABLED",
                         "actual_premises_discharged": False, "H_or_RetBind_inferred": False})

missing = []
for row in scu["rules"]:
    for ref in row["all_of"] + [row["conclusion"]]:
        if ref not in all_ids:
            missing.append({"from": row["id"], "missing": ref})
for row in scu["context_links"]:
    for key in ("from", "to"):
        if row[key] not in all_ids:
            missing.append({"from": row["id"], "missing": row[key]})

result = {"schema": "uct-cumulative-candidate-audit/1", "status": "CANDIDATES_REVIEWED_NOT_PROMOTED",
    "base_map": "UCT-MAP-v1.1.2", "source_snapshot": "a22ad487b2a072293de2ecb55b4f2cc2a2c0dafc",
    "completed_map_full_raw_contract_and_source_proof_audit": "AUDIT_INCOMPLETE",
    "R190_R205_counts": dict(Counter(r["item_type"] for r in candidate_rows)),
    "R190_R205_statement_level_unread_ids": [], "modules": modules, "items": candidate_rows,
    "SCU": {"map_sha256": file_sha(scu_path), "counts": dict(Counter(r["item_type"] for r in scu_rows)),
            "local_reference_resolution_bookkeeping_only": {"missing_refs": missing, "semantic_certification_by_program": False},
            "all_claim_proofs_manually_reconstructed_in_declared_model": True,
            "code_fully_independently_reviewed_by_this_auditor": False,
            "finite_enumeration_scope": "The 5045 matrix/route checks explicitly cover the zero-mismatch/equal-column criterion; complete nonzero fibers are algebraic, and the independent optimizer checks only finite nonadaptive minima. The adaptive lower bounds are manual proofs.",
            "mathematical_priority_claim": "No new general coding theorem or historical priority is established by this audit.",
            "items": scu_rows},
    "open_reviews_preserved": ["QC10", "IA-QC11", "QC12", "QC13"],
    "actual_premises_discharged": False, "new_phenomenal_validation": False}
(HERE / "CUMULATIVE_CANDIDATE_REVIEW.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


def pinned_source(path, scope, revision="90a542d697d923aa484f2bd5a4484a438125325a"):
    relative = str(path.relative_to(REPO))
    process = subprocess.run(["git", "show", revision + ":" + relative], cwd=REPO, capture_output=True, check=True)
    return {"repository_path": relative, "revision": revision, "sha256": sha256(process.stdout).hexdigest(), "actual_read_scope": scope}


read_sources = [
    pinned_source(REPO / "research/AGENTS.md", "Full file."),
    pinned_source(ROOT / "RESEARCH_MASTER_GUIDE.md", "Full guide, including both initial and remainder batches."),
    pinned_source(ROOT / "AGENTS.md", "Header/current instructions lines 1-100 and lines 485-end; intervening historical body not fully read by this auditor."),
    pinned_source(ROOT / "CURRENT_STATE.json", "Full initial current-state snapshot; later root-managed navigation updates are not the same source."),
    pinned_source(ROOT / "FORMAL_MAP_REVIEW_POLICY.json", "Full v2.4 policy."),
    pinned_source(ROOT / "REVIEW_SUPERVISION.md", "Lines 1-34, 264-306, 330-405, 477-506 and heading inventory; remaining historical review body not fully read."),
    pinned_source(ROOT / "UCT_FORMAL_MAP.md", "Full descriptor overview; restored v1.1.2 capsule used for exact item audit."),
    pinned_source(ROOT / "UCT_FORMAL_GRAPH_MODULES.json", "Descriptor/navigation fields inspected; whole initial output had a small truncated tail, so full-file reading is not claimed."),
    pinned_source(RECORDS / "R153_Complete_Formal_Map_20261007/FORMAL_FOUNDATION.md", "Lines 1-79 and 101-138. P01-P05 and P10-P12 proof sections were read; P06-P09 full sections at lines 80-100 were not read."),
    pinned_source(RECORDS / "R154_All_Rule_Proof_Review_20261007/RULE_REVIEW.md", "Headings and proof locators only; the full historical proof corpus was not reread."),
    pinned_source(RECORDS / "R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md", "Lines 81-204 (actual-token criteria) and 357-427 (C1/C1-OI/C1-W/U1). Full paper not claimed by this auditor.")
]
manifest = {"schema": "uct-audit-source-read-scope/1", "scope_is_auditor_specific": True,
    "not_a_claim_about_other_agents_reading": True,
    "frozen_map": {"version": "UCT-MAP-v1.1.2", "graph_sha256": file_sha(HERE / "baseline/UCT_EFFECTIVE_GRAPH.json"),
                   "review_ledger_sha256": file_sha(HERE / "baseline/REVIEW_LEDGER.json"),
                   "source_location_index_sha256": file_sha(HERE / "baseline/SOURCE_LOCATIONS.json"),
                   "read_scope": "All 1608 semantic cards; full nested-contract and historical-proof exceptions are enumerated in EXACT_UNREAD_SCOPE.json."},
    "governance_and_foundation_sources": read_sources,
    "pending_note_and_map_sources": modules,
    "current_SCU_sources": [{"path": str(path), "sha256": file_sha(path), "actual_read_scope": scope}
        for path, scope in [
            (MODEL / "RESEARCH_NOTE.md", "Full main note read; final scope corrections on 5045 zero-fiber checks, concurrent R205 and node/edge semantics inspected separately."),
            (MODEL / "CLAIM_LEDGER.json", "All 8 claims, quantifiers, all_of, proof locators, predecessors and limits."),
            (scu_path, "All 23 nodes, 8 rules and 16 nondeductive contexts; corrected nontrivial node-write guard reread."),
            (RECORDS / "SCU20261010_Source_Consumer_Protocols/Matched_Behavior_and_Source_Use_v1.0.0.md", "Final sections 2, 7, 9-10 reread, including corrected predictor/process notation, carrier timing, complete clones and all three older corrections. Abstract/introduction/conclusion/references were read in the first review version. This is not a full independent manuscript proof/citation review.")]],
    "other_exact_prior_reasoning_consulted": [
        {"module": "R147", "scope": "Source locator/headings and route algebra from the frozen graph and R153 P11; full original source note not independently reread."},
        {"module": "R174", "scope": "Declared S/C/H source-and-mediator equations, separating table and finite-context counterextension as retained in the graph; no claim of full empirical-source review."},
        {"module": "IA20261008", "scope": "Actual source/consumer trace-DAG definitions and relay/retiming invariance from the retained source section and graph; broader adaptive-observer proof corpus reused."}],
    "full_historical_source_proof_reconstruction": False,
    "actual_application_or_H_validation": False}
(HERE / "SOURCE_READ_SCOPE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"pending": result["R190_R205_counts"], "SCU": result["SCU"]["counts"],
                  "SCU_unresolved_refs": missing, "family_review_count": len(json.loads((HERE / "FAMILY_REVIEW_NOTES.json").read_text()))}))
