"""Serialize reviewer-authored corrections; hashes/closures are bookkeeping only."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json

HERE = Path(__file__).parent
WORKSPACE = HERE.parents[1] / "uct_repo/research/uct-agent-consciousness-workspace"
RECORDS = WORKSPACE / "records"
SCU = "SCU20261010:"


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def record_hash(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def module(prefix):
    directory = next(RECORDS.glob(prefix + "_*"))
    path = directory / "MAP_EXTENSION.json"
    return directory, path, json.loads(path.read_text())


def provenance(prefix):
    directory, path, content = module(prefix)
    paths = [path, directory / "RESEARCH_NOTE.md"]
    return content, [{"path": str(p.relative_to(WORKSPACE)), "sha256": file_hash(p)} for p in paths]


def new_node(name, statement, scope, kind="CONDITIONAL_DECLARATION"):
    return {"id": SCU + name, "kind": kind, "statement": statement, "scope": scope,
            "status": "CANDIDATE_DISABLED", "enabled_as_established_premise": False,
            "actual_premises_discharged": False, "node_presence_is_premise_truth": False}


def new_rule(name, premises, conclusion, statement, binding):
    return {"id": SCU + name, "all_of": premises, "conclusion": conclusion,
            "statement": statement, "binding": binding,
            "same_instance_required": True, "kind": "CONDITIONAL_CORRECTION_RULE",
            "status": "CANDIDATE_DISABLED", "enabled_as_established_premise": False,
            "actual_premises_discharged": False,
            "proof_location": "EFFECTIVE_CORRECTIONS.md; EFFECTIVE_CORRECTION_EXACT_RESULTS.json"}


def override(content, target_id, fields, rationale):
    original = next(row for group in ("nodes", "rules") for row in content[group] if row["id"] == target_id)
    return {"target_id": target_id, "expected_original_record_sha256": record_hash(original),
            "hash_serialization": "UTF-8 JSON; sorted keys; ensure_ascii=false; separators comma/colon",
            "operation": "OVERLAY_FIELDS_WITHOUT_MODIFYING_HISTORICAL_SOURCE",
            "replacement_fields": {**fields, "enabled_as_established_premise": False,
                                   "actual_premises_discharged": False,
                                   "proof_location": "EFFECTIVE_CORRECTIONS.md; EFFECTIVE_CORRECTION_EXACT_RESULTS.json; verify_effective_corrections.py",
                                   "effective_correction_status": "CANDIDATE_DISABLED"},
            "rationale": rationale}


def base_overlay(name, prefix):
    content, sources = provenance(prefix)
    result = {"schema": "uct-disabled-effective-correction-overlay/1", "overlay_id": name,
        "base_completed_release": "UCT-MAP-v1.1.2",
        "review_snapshot_sha": "a22ad487b2a072293de2ecb55b4f2cc2a2c0dafc",
        "historical_source_version": content.get("result_version"), "sources": sources,
        "status": "PENDING_CHECKPOINT_DISABLED", "enabled_as_established_premise": False,
        "actual_premises_discharged": False, "phenomenal_validation": False,
        "completed_map_changed": False, "historical_files_changed": False,
        "proof_code": "verify_effective_corrections.py",
        "exact_results": "EFFECTIVE_CORRECTION_EXACT_RESULTS.json",
        "effective_overrides": [], "nodes": [], "rules": [], "context_links": []}
    return content, result


g194, o194 = base_overlay("SCU20261010-CORR-R194-v0.1.0", "R194")
anchored_domain = SCU + "CORR_R194_ANCHORED_GRAPH_DOMAIN"
o194["nodes"].append(new_node("CORR_R194_ANCHORED_GRAPH_DOMAIN",
    "Fix one finite vertex set V, one undirected XOR-parity edge set E, and one partial anchor function eta:V->{0,1}. For vertices in one component, anchor values must agree with the parity of a connecting path for joint satisfiability. Multiple anchors are permitted and tested, not silently assumed compatible.",
    "Finite Boolean graphs; the original seven-vertex design is a subcase. This defines a mathematical family and does not assert any empirical anchor or phenomenal orientation."))
o194["effective_overrides"].append(override(g194, "R194:COMPONENT_COUNT", {
    "statement": "For a finite signed graph with a fixed partial binary anchor map, the compatible-labelling count is zero if an XOR-parity cycle is inconsistent or two anchors in one component disagree with path parity. Otherwise it is exactly 2^c, where c is the number of unanchored connected components. In particular one anchor per component gives a unique numeric labelling when all cycle constraints are consistent.",
    "scope": "All finite XOR graphs with fixed partial anchor assignments; consistency covers edges AND anchors on that same graph.",
    "quantifier": "For every fixed graph, parity assignment and partial anchor map in the declared domain."
}, "The old cycle-only premise is insufficient when multiple anchors are allowed. The two-vertex core embeds in the original seven-vertex domain; old one-anchor checks remain valid."))
o194["effective_overrides"].append(override(g194, "R194:r_component_count", {
    "all_of": ["R194:DOMAIN", "R194:SIGNED_GRAPH", anchored_domain, "R149:COMPATIBILITY", "R157:COORDINATE_TRANSPORT"],
    "statement": "Propagate parity from one root per component; reject cycle or anchor/path conflicts. Each remaining unanchored component has two root values and each compatible anchored component one.",
    "binding": "One V,E,edge-parity map, partial anchor map eta and coordinate interpretation are retained. The theorem evaluates all constraints jointly; an anchor from another graph or target cannot be pasted into this instance.",
    "alternative_route_semantics": "Conflicting cycles and conflicting anchors are two failure cases, not alternative positive proofs. The 2^c branch requires joint consistency."
}, "Adds the omitted anchor interface while keeping the theorem conditional rather than asserting that all graphs are consistent."))
o194["effective_overrides"].append(override(g194, "R194:RELATIVE_ALIGNMENT", {
    "statement": "Multiple populations, markers and known reversal relations can identify relative channel polarity and connect components when all edge constraints and any supplied anchors are jointly consistent.",
    "scope": "One fixed signed comparison design; same-target transport, edge truth and anchor/path compatibility remain simultaneous premises."
}, "A contradiction among anchored assignments is not a positive relative-alignment instance."))
o194["manual_affected_rederivation"] = [
    "R194:r_component_count: choose a root, propagate relative signs, test each cycle and each anchor against the same root. A conflict gives no labelling; otherwise multiply two choices over unanchored components.",
    "R194:r_relative_alignment: the repaired count leaves relative path parity intact within a jointly consistent component. Inconsistent anchored designs have no admitted positive alignment case.",
    "R194:r_global_complement: on each UNANCHORED consistent component, simultaneous complement still preserves every edge and evidence constraint. Added anchor checking does not orient an unanchored component.",
    "R194:r_anchor_taxonomy and R194:r_protocol: a conventional numeric anchor still does not warrant a familiar-mineness name. The correction adds consistency checking, not target evidence.",
    "R193's four-cell one-anchor construction remains unchanged. Its broader graph-language generalization should use the same joint edge/anchor consistency definition."
]

g201, o201 = base_overlay("SCU20261010-CORR-R201-v0.1.0", "R201")
witness_domain = SCU + "CORR_R201_COHERENT_WITNESS_DOMAIN"
o201["nodes"].append(new_node("CORR_R201_COHERENT_WITNESS_DOMAIN",
    "Fix a mathematical family of coherent binary calibration and target probability laws with supported H/J strata and explicit nuisance budgets. Each displayed equality, below-threshold, or unsigned-endpoint counterexample is a SEPARATE joint law satisfying its own retained premises. The strict positive-margin premise is deliberately not imposed on equality or below-threshold witnesses.",
    "Exactly the three rational witnesses in EFFECTIVE_CORRECTION_EXACT_RESULTS.json and their explicitly proved interpretation; no arbitrary-positive-budget sharpness claim and no actual endpoint validation."))
o201["effective_overrides"].append(override(g201, "R201:STRICTNESS_COUNTERMODELS", {
    "statement": "There exists a coherent equality example with rho=1/2, b=beta=1/10 and epsilon0=epsilon1=0 in which delta=1/10 and Delta_T=0. There exists a separate coherent below-threshold example with rho=1/2, b=beta=1/10, epsilon0=epsilon1=1/10, delta=3/20 and Delta_T=-1/10. Without independently positive endpoint sign, a separate reversed-endpoint example has delta=1 and Delta_C=-1. These witness failure of a general non-strict replacement and of unconstrained endpoint orientation; they do not prove sharpness at every nuisance-budget tuple.",
    "scope": "Coherent binary probability laws; original rho=1,b=1/10 scalar tuples are withdrawn as unrealizable probability witnesses.",
    "quantifier": "Existential: one coherent witness per displayed failure mode, with separate world and budget binding."
}, "rho=1 on supported J strata forces H=J almost surely and hence b=0. Replace impossible scalar tuples with actual joint laws."))
o201["effective_overrides"].append(override(g201, "R201:r_strictness_witnesses", {
    "all_of": ["R201:FIXED_CALIBRATION_TRANSPORT_DOMAIN", witness_domain],
    "statement": "Evaluate the three explicitly coherent rational probability witnesses under their own retained premises. Equality and below-threshold worlds are not required to satisfy the strict-margin certificate premise.",
    "binding": "Fix target meaning and variable sorts at schema level. Bind C,T,H,J,M,U=1, a single coherent joint calibration law, target conditionals and budgets separately inside each existential witness. Never combine a strict-margin instance with a different equality or reversal instance.",
    "alternative_route_semantics": "The three failure modes are alternative witnesses. Positive endpoint sign is retained in the first two and deliberately dropped in the third."
}, "Removes the invalid all_of ROBUST_MARGIN_PREMISE from the counterexample route; same_instance_required remains true within each witness."))
o201["manual_affected_rederivation"] = [
    "R201:r_source_lower_bound remains valid: delta=rho Delta_C+b, 0<rho<=1 and delta-beta>0 imply Delta_C=(delta-b)/rho>=delta-beta.",
    "R201:r_target_sign_certificate remains valid: apply both class-specific drift bounds in the same C-to-T instance to obtain Delta_T>=delta-beta-epsilon0-epsilon1>0.",
    "R201:r_strictness_witnesses is replaced by three coherent existential worlds. The original strict-margin premise cannot be used in the equality or below-threshold worlds.",
    "R202 marginal nonidentification and R203 total covariance do not use the rejected R201 witness as a deductive premise. Their own defects or scope conditions are reviewed separately."
]

g202, o202 = base_overlay("SCU20261010-CORR-R202-v0.1.0", "R202")
joint_guard = SCU + "CORR_R202_JOINT_AUDIT_LAW"
zero_guard = SCU + "CORR_R202_ZERO_RESIDUAL"
residual_guard = SCU + "CORR_R202_COMMON_RESIDUAL_BOUND"
set_result = SCU + "CORR_R202_COMMON_RESIDUAL_SET"
o202["nodes"] += [
    new_node("CORR_R202_JOINT_AUDIT_LAW", "Use one coherent binary joint law of H,M,J in V conditional on actual U=1, with the independently calibrated endpoint rates a=P(J=1|H=1), c=P(J=1|H=0), a>c, and c<j=P(J=1)<a. The audited m=P(M=1),j,r=P(M=1,J=1) must concern that same validation law after justified sampling correction.", "One frozen V,H,M,J,A,U=1 endpoint and audit interface; both H classes have positive mass. Probability coherence, calibration and sampling are simultaneous, not separate adjustable scalar inputs.", "JOINT_PROBABILITY_AND_POSITIVITY_PREMISE"),
    new_node("CORR_R202_ZERO_RESIDUAL", "The aggregate conditional covariance R=(1-pi)Cov(M,J|H=0)+pi Cov(M,J|H=1) is zero in the same validation law. Conditional independence J independent of M given H is sufficient; an asserted cancellation requires independent justification.", "One common residual in the fixed joint audit law. The observed fit does not establish R=0.", "OPEN_ZERO_RESIDUAL_PREMISE"),
    new_node("CORR_R202_COMMON_RESIDUAL_BOUND", "An independently justified kappa>=0 bounds the one common aggregate residual |R|<=kappa in the fixed validation law. H-specific component covariances obey a coherent binary joint law.", "One V,H,M,J,A,U=1 instance; nuisance uncertainty is shared by both recovered marker rates.", "OPEN_RESIDUAL_BOUND_PREMISE"),
    new_node("CORR_R202_COMMON_RESIDUAL_SET", "pi=(j-c)/(a-c), q1=(r-c*m-R)/(j-c), q0=(a*m-r+R)/(a-j), with the SAME R. Under |R|<=kappa retain all jointly coherent candidate laws and their rate pairs satisfying those equations. Marginal intervals qhat1 plus/minus kappa/(j-c) and qhat0 plus/minus kappa/(a-j), clipped to [0,1], are conservative outer intervals, not independent choices or a claim of arbitrary-budget sharpness.", "Fixed positive-support validation law and declared residual budget; no automatic transport from V to nonreporting T.", "CONDITIONAL_SENSITIVITY_RESULT")
]
o202["effective_overrides"].append(override(g202, "R202:CONDITIONAL_NONDIFFERENTIALITY", {
    "statement": "Within the same validation domain V and actual U=1, endpoint J is conditionally independent of marker M given H in both supported H classes. Bounded departures are a separate residual-sensitivity route and do not satisfy this exact-inversion premise.",
    "scope": "Exact nondifferential-error route only. Aggregate R=0 is an alternative sufficient premise in a separate rule."
}, "Separates exact point identification from merely bounded dependence; the original OR weakened its own exact premise."))
o202["effective_overrides"].append(override(g202, "R202:AUDIT_INVERSION_RESULT", {
    "statement": "Under the fixed coherent audit/endpoint/actual-use contract, positivity c<j<a, and zero aggregate residual R, recover pi=(j-c)/(a-c), q1=(r-c*m)/(j-c), q0=(a*m-r)/(a-j). Conditional independence is sufficient for R=0. A nonzero residual bound alone gives the separately defined common-residual feasible set, not these exact values.",
    "scope": "Only the same V,H,M,J,A,U=1 law and calibrated endpoint matrix; no V-to-T transport inference is included."
}, "Makes the exact inversion's sufficient condition and its scope explicit."))
o202["effective_overrides"].append(override(g202, "R202:r_audit_inversion", {
    "all_of": ["R202:FIXED_THREE_DOMAIN_CONTRACT", "R202:PROSPECTIVE_IGNORABLE_AUDIT", "R202:INFORMATIVE_SIGNED_ENDPOINT", "R202:CONDITIONAL_NONDIFFERENTIALITY", "R202:ACTUAL_USE_EVIDENCE_FIREWALL", joint_guard],
    "statement": "Conditional independence makes R=0; invert the same two-by-two mixture law at c<j<a to recover pi,q0,q1 exactly.",
    "binding": "One V,H,M,J,A,U=1 joint law, endpoint-error calibration, audit-selection contract, observed M/J law and positive-support condition are retained. A different dependence model cannot be substituted while keeping the zero-residual answer.",
    "alternative_route_semantics": "Use the separately guarded zero-aggregate-residual route if independence is absent; a nonzero bound invokes the sensitivity-set rule instead."
}, "Adds explicit joint probability/positivity binding and retains the exact independence route."))
shared = ["R202:FIXED_THREE_DOMAIN_CONTRACT", "R202:PROSPECTIVE_IGNORABLE_AUDIT", "R202:INFORMATIVE_SIGNED_ENDPOINT", "R202:ACTUAL_USE_EVIDENCE_FIREWALL", joint_guard]
binding = "All rates, audit inclusion, actual U=1, target meaning, endpoint calibration and nuisance terms concern the SAME V/H/M/J law. No residual is independently chosen for q0 and q1; transport to T remains a separate premise."
o202["rules"] += [
    new_rule("corr_r202_zero_residual_inversion", shared + [zero_guard], "R202:AUDIT_INVERSION_RESULT", "Invert the mixture equations with the independently supplied common R=0; conditional independence is not necessary if the aggregate zero is otherwise justified.", binding),
    new_rule("corr_r202_bounded_residual_set", shared + [residual_guard], set_result, "Retain the common-residual formulas and probability-coherent feasible laws; derive clipped marginal outer intervals by |R|<=kappa. Do not report unique rates from the bound alone.", binding)
]
o202["manual_affected_rederivation"] = [
    "E[J]=c+(a-c)pi identifies pi when a>c; positivity c<j<a keeps both class denominators nonzero.",
    "E[MJ]=a*pi*q1+c*(1-pi)*q0+R and E[M]=pi*q1+(1-pi)*q0 give q1=(r-cm-R)/(j-c) and q0=(am-r+R)/(a-j). The same R enters with opposite signs.",
    "R202:r_audit_inversion recovers its original point result only on the independence/zero-R branch. The coherent R203 dependent twin reverses the naive direction and is excluded only by this additional premise.",
    "R202:r_three_domain_stop remains a stopping rule: even exact V recovery does not provide V-to-T class-conditional transport. A residual set yields an even weaker V conclusion, never a stronger T conclusion.",
    "R203's covariance identity K=pi(1-pi)(a-c)Delta+R agrees algebraically with the repaired inversion and needs no correction to its core theorem."
]


def dependency_closure(seeds, all_nodes, all_rules, all_contexts):
    found = set(seeds)
    added_rules = set()
    changed = True
    while changed:
        changed = False
        for rule in all_rules:
            if rule["id"] in found or any(p in found for p in rule.get("all_of", [])):
                additions = {rule["id"], rule["conclusion"]} - found
                if additions:
                    found.update(additions)
                    changed = True
                added_rules.add(rule["id"])
    context_ids = []
    for context in all_contexts:
        ends = [context.get(k) for k in ("from", "to", "source", "target", "from_id", "to_id")]
        if any(isinstance(x, str) and x in found for x in ends):
            context_ids.append(context["id"])
    return {"seed_ids": sorted(seeds), "syntactic_forward_dependency_ids": sorted(found),
            "affected_node_ids": sorted(found & {r["id"] for r in all_nodes}),
            "affected_rule_ids": sorted(added_rules), "adjacent_nondeductive_context_ids": sorted(context_ids),
            "warning": "This is a syntactic over-approximation for review routing, not proof reconstruction or actual premise discharge. Context links never propagate deduction."}


baseline = json.loads((HERE / "baseline/UCT_EFFECTIVE_GRAPH.json").read_text())
all_nodes, all_rules, all_contexts = baseline["nodes"][:], baseline["rules"][:], baseline["context_links"][:]
for number in range(190, 206):
    _, _, content = module("R" + str(number))
    all_nodes.extend(content["nodes"])
    all_rules.extend(content["rules"])
    all_contexts.extend(content["context_links"])
baseline_ids = {row["id"] for group in ("nodes", "rules", "context_links") for row in baseline[group]}
for name, overlay in (("R194", o194), ("R201", o201), ("R202", o202)):
    seeds = {r["target_id"] for r in overlay["effective_overrides"]}
    overlay["affected_closure"] = dependency_closure(seeds, all_nodes, all_rules, all_contexts)
    overlay["affected_closure"]["completed_map_ids_requiring_replacement"] = sorted(seeds & baseline_ids)
    overlay["affected_closure"]["completed_map_forward_dependents"] = sorted(set(overlay["affected_closure"]["syntactic_forward_dependency_ids"]) & baseline_ids)
    target = HERE / (name + "_EFFECTIVE_CORRECTION_OVERLAY.json")
    target.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n")

manifest = {"schema": "uct-disabled-correction-index/1", "status": "PENDING_CHECKPOINT_DISABLED",
            "overlays": [{"path": f"{name}_EFFECTIVE_CORRECTION_OVERLAY.json", "sha256": file_hash(HERE / f"{name}_EFFECTIVE_CORRECTION_OVERLAY.json")}
                         for name in ("R194", "R201", "R202")],
            "exact_results_sha256": file_hash(HERE / "EFFECTIVE_CORRECTION_EXACT_RESULTS.json"),
            "proof_code_sha256": file_hash(HERE / "verify_effective_corrections.py"),
            "completed_map_changed": False, "actual_premises_discharged": False,
            "open_reviews_preserved": ["QC10", "IA-QC11", "QC12", "QC13"]}
(HERE / "EFFECTIVE_CORRECTION_INDEX.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"overlays": 3, "new_conditional_nodes": sum(len(o["nodes"]) for o in (o194, o201, o202)),
                  "new_rules": sum(len(o["rules"]) for o in (o194, o201, o202)),
                  "overridden_records": sum(len(o["effective_overrides"]) for o in (o194, o201, o202)),
                  "completed_map_changed": False}))
