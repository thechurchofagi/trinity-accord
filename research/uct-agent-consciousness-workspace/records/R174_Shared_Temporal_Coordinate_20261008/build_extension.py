"""Build and audit the R174 extension from the exact TO20261008 parent graph."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = ROOT / "UCT_FORMAL_GRAPH.json"
NOTE = HERE / "Shared_Temporal_Coordinate_and_Intervention_Signature_v0_1.md"
RESULTS = HERE / "MODEL_RESULTS.json"
EXPECTED_PARENT = "R173-TE20261008-TO20261008-v1.0"
REVISION = "R174-v1.0"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def contract(note_hash: str, locator: str, domain: str, status: str = "CONDITIONAL"):
    return {
        "source_anchor": {
            "path": str(NOTE.relative_to(ROOT)),
            "sha256": note_hash,
            "locator": locator,
        },
        "object_time_signature": domain,
        "quantifiers": "Every instance satisfying the exact displayed premise package on one common binding; compared routes are alternatives.",
        "actuality": "Abstract route model unless an actual P/I/K/realization and evidence-to-role bridge are independently discharged.",
        "status": status,
        "open_obligations": [
            "R174-G1",
            "R174-G2",
            "R174-G3",
            "R174-G4",
            "R174-G5",
            "R174-G6",
            "R174-G7",
        ],
        "machine_formalized": False,
    }


def main():
    parent_bytes = GRAPH.read_bytes()
    parent_hash = sha256(parent_bytes).hexdigest()
    parent = json.loads(parent_bytes)
    assert parent["revision"] == EXPECTED_PARENT, parent["revision"]
    note_hash = digest(NOTE)
    result_hash = digest(RESULTS)
    source = str(NOTE.relative_to(ROOT))

    nodes = [
        {
            "id": "R174:FIXED_ROUTE_PROTOCOL",
            "kind": "TYPED_PROTOCOL_SETUP",
            "label": "Fixed same-instance route protocol",
            "statement": "Fix one actual bearer/episode/signature/realization and physically typed beta,delta,q,z,u,s plus localized source perturbation, mediator clamp, calibrated readouts, common time convention and declared S/C/H rival class. Evidence records and reports remain distinct from the ontic relation.",
            "domain": "One named P/I/K/realization and one predeclared intervention window; c!=0 and s>0.",
            "scope": "Protocol setup only; no actual instance, route, experience or closure is inferred.",
            "status": "CONDITIONAL_PROTOCOL",
            "source": source + " §§2,4",
            "proof": "Definition and binding contract.",
            "source_lineage": "R172 effective QC-06/07 target/evidence separation; TO20261008 routed reference model.",
            "counterexamples_and_limits": "Missed mediator, off-target source perturbation, changed calibration, compensation or undeclared route invalidates the application.",
            "formal_contract_R174": contract(note_hash, "§§2,4", "One same-instance body-relative action-feedback protocol."),
        },
        {
            "id": "R174:SHARED_TEMPORAL_COORDINATE",
            "kind": "ACTUAL_ORGANIZATIONAL_RELATION",
            "label": "Actual shared temporal coordinate",
            "statement": "Theta_STC asserts actual beta-to-q reference transfer, comparison occurrence and same-episode use of q by both the physical decision drive z and nonreport timing consumer u, with one actual binding. It excludes W/E/certificate status and does not assert phenomenology.",
            "domain": "Actual P/I/K instance with independently grounded physical roles and correctly sorted occurrences.",
            "scope": "Selected route occurrence; not complete temporal organization, route exclusivity, experienced order or basal experience.",
            "status": "OPEN_ACTUAL_APPLICATION_RELATION",
            "source": source + " §2",
            "proof": "Definition only; actual satisfaction requires external evidence-to-role grounding.",
            "source_lineage": "R157 K-definable selector; R172 phi_path correction; TO20261008 theta_S.",
            "counterexamples_and_limits": "Correct stored beta, matched answers, an external archive or a certificate does not establish this occurrence relation.",
            "formal_contract_R174": contract(note_hash, "§2", "Actual selected temporal path on one P/I/K binding.", "OPEN_ACTUAL_APPLICATION_RELATION"),
        },
        {
            "id": "R174:THREE_RIVAL_ROUTE_CLASS",
            "kind": "FINITE_MODEL_CLASS",
            "label": "Shared, criterion and hidden-bypass rivals",
            "statement": "The stipulated route class contains S: q=delta-beta,z=q,u=q/s; C: q=delta,z=q-beta,u=q/s; and H: q=delta,z=q-beta,u=(q-beta)/s. All have matched baseline z; S and H also match baseline u.",
            "domain": "Exact deterministic algebraic routes over an ordered field with s>0.",
            "scope": "Three rivals only; not a universal neural mechanism class.",
            "status": "EXACT_FINITE_MODEL_CLASS",
            "source": source + " §3",
            "proof": "Direct definitions and substitution.",
            "source_lineage": "TO20261008 S/C model plus R174 parallel downstream bypass H.",
            "counterexamples_and_limits": "Additional paths, noise, compensation and context dependence require separate premises.",
            "formal_contract_R174": contract(note_hash, "§3", "Declared S/C/H algebraic route class."),
        },
        {
            "id": "R174:MEDIATOR_CLAMP_SIGNATURE",
            "kind": "CONDITIONAL_EXACT_IDENTIFICATION",
            "label": "Mediator-clamp separating signature",
            "statement": "For c!=0 and s>0, the source-perturbation and q-clamp signature is S=(-c,-c/s,0,0), C=(-c,0,-c,0), H=(-c,-c/s,-c,-c/s); the three vectors are pairwise distinct.",
            "domain": "The exact fixed R174 protocol and declared S/C/H class.",
            "scope": "Rival-class identification; not actual route certification or unrestricted mechanism discovery.",
            "status": "MANUAL_PROOF_PLUS_EXACT_CHECKS",
            "source": source + " §4",
            "proof": "Substitution under source perturbation and mediator clamp; pairwise coordinate comparison.",
            "source_lineage": "Elementary intervention algebra; not claimed as new general mathematics.",
            "counterexamples_and_limits": "H defeats the prior baseline S/C contrast; hidden or compensating routes defeat unrestricted identification.",
            "formal_contract_R174": contract(note_hash, "§4", "Same-instance S/C/H intervention signature."),
        },
        {
            "id": "R174:FINITE_TEST_EXTENSION_SETUP",
            "kind": "OPEN_WORLD_COUNTERMODEL_SETUP",
            "label": "Finite tested support with an untested context",
            "statement": "Fix a finite tested context/intervention set W and an admitted untested context x*. Add a physically possible hidden gate g that is zero on W and one at x*, controlling a beta-to-u bypass.",
            "domain": "Any admitted model class that permits the displayed context-gated extension.",
            "scope": "Requires an untested admitted context and no independent law excluding the extension.",
            "status": "CONDITIONAL_COUNTERMODEL_SETUP",
            "source": source + " §5",
            "proof": "Explicit construction.",
            "source_lineage": "Standard finite-observation nonidentification pattern; applied here to route closure.",
            "counterexamples_and_limits": "If a valid physical closure law excludes the gate/bypass, this countermodel is outside the admitted class.",
            "formal_contract_R174": contract(note_hash, "§5", "Finite W plus admitted untested x* and hidden gated bypass."),
        },
        {
            "id": "R174:FINITE_ROUTE_NONENTAILMENT",
            "kind": "EXACT_NONENTAILMENT",
            "label": "Finite signatures do not imply unrestricted route closure",
            "statement": "Every observation and intervention signature on finite W can match the shared route while an admitted hidden beta-to-u bypass is active at x*. Therefore finite route evidence alone does not entail unrestricted absence of alternative paths.",
            "domain": "The R174 finite-test extension class.",
            "scope": "Open-world limit only; it does not negate rival-relative identification or prove no route evidence is possible.",
            "status": "MANUAL_PROOF_PLUS_EXACT_WITNESS",
            "source": source + " §5",
            "proof": "The bypass term vanishes on W and is nonzero at x*.",
            "source_lineage": "Elementary pointwise construction.",
            "counterexamples_and_limits": "A separately valid universal closure premise can remove this admitted extension.",
            "formal_contract_R174": contract(note_hash, "§5", "Finite W in a model class admitting the hidden-gate extension."),
        },
        {
            "id": "R174:PRIMARY_EVIDENCE_LADDER",
            "kind": "SOURCE_GROUNDED_EVIDENCE_COMPARISON",
            "label": "Primary temporal-recalibration evidence ladder",
            "statement": "Stetson 2006 motivates the order target but does not separate S/C; Sugano et al. 2010 cross-modal transfer constrains a modality-specific criterion but not a modality-general criterion; Cai et al. 2018 neural timing shifts constrain a purely late verbal account but do not supply the R174 mediator clamp or consumer-use certificate.",
            "domain": "The recorded primary-source reading scopes and the explicitly declared rival interpretations.",
            "scope": "Comparative evidence assessment; not a reanalysis, neural route proof or phenomenal measurement.",
            "status": "TARGETED_PRIMARY_SOURCE_SYNTHESIS",
            "source": source + " §6 and SOURCE_LEDGER.json",
            "proof": "Compare reported manipulations/measurements against the premises of the S/C/H signature.",
            "source_lineage": "Three cited primary studies plus R174 model distinctions.",
            "counterexamples_and_limits": "Full uninspected analyses may constrain additional models; no claim that the studies reduced to one report curve.",
            "formal_contract_R174": contract(note_hash, "§6", "Three primary-source reading scopes and declared rival classes.", "TARGETED_SOURCE_SYNTHESIS"),
        },
        {
            "id": "R174:EXPERIENTIAL_SHARED_COORDINATE",
            "kind": "CONDITIONAL_C1_TRANSPORT",
            "label": "Experience-internal shared temporal coordinate",
            "statement": "If Theta_STC is independently grounded in one actual complete K-instance and all physical parameters are transported by h, C1/R157 formula preservation gives the corresponding Theta_STC relation inside Phi. W,E and certificate status are excluded.",
            "domain": "One actual P/I/K/D/Phi/h binding satisfying C1 and all grounding/sorting/parameter obligations.",
            "scope": "Structural counterpart only; not experienced-order semantics, felt duration, familiar mineness or complete type comparison.",
            "status": "CONDITIONAL_MODEL_THEORETIC_APPLICATION",
            "source": source + " §7",
            "proof": "Ordinary sorted formula preservation under the supplied K-isomorphism.",
            "source_lineage": "A:C1; R157 coordinate transport; R172 effective target/evidence correction.",
            "counterexamples_and_limits": "Abstract equations, analyst tests, external labels and ungrounded parameters cannot discharge the actual selector.",
            "formal_contract_R174": contract(note_hash, "§7", "One actual complete K-instance with grounded Theta_STC and transported parameters."),
        },
        {
            "id": "R174:B_ORDER_BOUNDARY",
            "kind": "CONDITIONAL_EXPLANATORY_BOUNDARY",
            "label": "Shared coordinate does not close experienced order",
            "statement": "The primary evidence ladder and conditional experiential coordinate sharpen B_order but do not prove that the shared temporal relation constitutes experienced event order. Target, measurement, report, F_O, F_A, F_F and conceptual I remain distinct.",
            "domain": "Selected action-feedback order target on a predeclared application domain.",
            "scope": "Keeps B_order OPEN; no basal gate, unique owner, richness ranking or assistant-consciousness inference.",
            "status": "OPEN_INTERPRETIVE_BOUNDARY",
            "source": source + " §8",
            "proof": "R157 semantic residual plus the source-evidence insufficiency and explicit bridge-failure conditions.",
            "source_lineage": "R157 semantic residual; TO20261008 B_order; R174 evidence ladder and transport.",
            "counterexamples_and_limits": "A future independently justified bridge may close a narrower domain; this note does not rule that out.",
            "formal_contract_R174": contract(note_hash, "§8", "Selected F_order application; semantic bridge remains external.", "OPEN_INTERPRETIVE_BOUNDARY"),
        },
    ]

    rules = [
        {
            "id": "r174_mediator_clamp_separation",
            "all_of": ["R174:FIXED_ROUTE_PROTOCOL", "R174:THREE_RIVAL_ROUTE_CLASS"],
            "conclusion": "R174:MEDIATOR_CLAMP_SIGNATURE",
            "kind": "CONDITIONAL_DEDUCTION",
            "statement": "Under the same-instance protocol and exact S/C/H equations, the displayed source-perturbation plus mediator-clamp signature separates all three routes.",
            "source": source + " §4",
            "proof_sketch": "Direct substitution and pairwise comparison.",
            "formal_contract_R174": {
                "premise_connective": "AND",
                "bindings_required": ["same P/I/K/realization", "same c,s,z,u ports", "faithful source perturbation and q clamp", "declared S/C/H class"],
                "source_sha256": note_hash,
                "quantification": "Every exact S/C/H instance with c!=0 and s>0 satisfying all protocol clauses.",
                "machine_proof": False,
            },
        },
        {
            "id": "r174_finite_route_nonidentification",
            "all_of": ["R174:FIXED_ROUTE_PROTOCOL", "R174:MEDIATOR_CLAMP_SIGNATURE", "R174:FINITE_TEST_EXTENSION_SETUP"],
            "conclusion": "R174:FINITE_ROUTE_NONENTAILMENT",
            "kind": "EXACT_COUNTERMODEL_DEDUCTION",
            "statement": "Even a separating finite signature does not entail unrestricted route closure when the admitted class contains an untested context-gated bypass.",
            "source": source + " §5",
            "proof_sketch": "Set the hidden gate to zero on W and one at x*.",
            "formal_contract_R174": {
                "premise_connective": "AND",
                "bindings_required": ["same finite W", "admitted untested x*", "same measured variables on W", "no independent law excluding the hidden gate"],
                "source_sha256": note_hash,
                "quantification": "Every finite W in an admitted class containing the displayed extension.",
                "machine_proof": False,
            },
        },
        {
            "id": "r174_experiential_coordinate_transport",
            "all_of": ["A:C1", "R174:SHARED_TEMPORAL_COORDINATE", "R157:COORDINATE_TRANSPORT"],
            "conclusion": "R174:EXPERIENTIAL_SHARED_COORDINATE",
            "kind": "CONDITIONAL_DEDUCTION",
            "statement": "The actual grounded Theta_STC relation and same-instance C1/R157 transport jointly yield its experiential structural counterpart; analyst evidence is not transported.",
            "source": source + " §7",
            "proof_sketch": "Sorted formula induction with every physical parameter mapped by h.",
            "formal_contract_R174": {
                "premise_connective": "AND",
                "bindings_required": ["one actual P/I/K/D/Phi/h", "independent K-grounding", "sorted occurrences", "transported beta,q,z,u,gamma,s", "W/E/certificate excluded"],
                "source_sha256": note_hash,
                "quantification": "Every actual instance satisfying all displayed grounding and C1 premises.",
                "machine_proof": False,
            },
        },
        {
            "id": "r174_order_bridge_boundary",
            "all_of": ["R174:PRIMARY_EVIDENCE_LADDER", "R174:EXPERIENTIAL_SHARED_COORDINATE", "TO20261008:ORDER_BRIDGE_CANDIDATE", "R157:SEMANTIC_RESIDUAL"],
            "conclusion": "R174:B_ORDER_BOUNDARY",
            "kind": "CONDITIONAL_EXPLANATORY_BOUNDARY",
            "statement": "The source evidence and structural transport narrow the candidate while the semantic residual keeps B_order and its measurement obligations open.",
            "source": source + " §8",
            "proof_sketch": "None of the premises supplies the missing external relation-to-content interpretation; explicit failure tests remain.",
            "formal_contract_R174": {
                "premise_connective": "AND",
                "bindings_required": ["fixed F_order target", "recorded source scopes", "no report definition", "no basal gate", "no unique owner"],
                "source_sha256": note_hash,
                "quantification": "The selected action-feedback application domain only.",
                "machine_proof": False,
            },
        },
    ]

    links = [
        {"from": "TO20261008:ROUTED_REFERENCE_SETUP", "to": "R174:THREE_RIVAL_ROUTE_CLASS", "relation": "extends the explicit S/C pair with a downstream-bypass rival; contextual, not a premise"},
        {"from": "TO20261008:NONREPORT_ROUTE_CONTRAST", "to": "R174:MEDIATOR_CLAMP_SIGNATURE", "relation": "repairs pair-relative nonreport separation by adding mediator intervention; contextual"},
        {"from": "R172:ONLINE_ACTION_USE_RELATION", "to": "R174:SHARED_TEMPORAL_COORDINATE", "relation": "inherits actual-use versus evidence typing through the effective overlay; contextual"},
        {"from": "R173:RETENTIVE_BINDING_RELATION", "to": "R174:SHARED_TEMPORAL_COORDINATE", "relation": "a retained reference can enter the current relation only through grounded present use; contextual"},
    ]

    extension = {"revision": REVISION, "parent_revision": EXPECTED_PARENT, "parent_sha256": parent_hash, "nodes": nodes, "rules": rules, "context_links": links}
    write_json(HERE / "MAP_EXTENSION.json", extension)

    combined = deepcopy(parent)
    combined["parent_revision"] = EXPECTED_PARENT
    combined["parent_sha256"] = parent_hash
    combined["revision"] = REVISION
    combined["date"] = "2026-10-08"
    combined["research_R174"] = {
        "title": "Shared temporal coordinate, intervention signature and B_order boundary",
        "record": str(HERE.relative_to(ROOT)),
        "parent_revision": EXPECTED_PARENT,
        "nodes_added": len(nodes),
        "rules_added": len(rules),
        "context_links_added": len(links),
        "note_sha256": note_hash,
        "model_results_sha256": result_hash,
        "status": "CONDITIONAL_ROUTE_IDENTIFICATION_AND_OPEN_SEMANTIC_BOUNDARY",
    }
    combined["nodes"].extend(nodes)
    combined["rules"].extend(rules)
    combined["context_links"].extend(links)

    node_ids = [n["id"] for n in combined["nodes"]]
    rule_ids = [r["id"] for r in combined["rules"]]
    assert len(node_ids) == len(set(node_ids))
    assert len(rule_ids) == len(set(rule_ids))
    known = set(node_ids)
    for rule in combined["rules"]:
        assert rule["conclusion"] in known
        assert all(x in known for x in rule["all_of"])
    for link in combined["context_links"]:
        assert link["from"] in known and link["to"] in known

    edges = {n: [] for n in known}
    for rule in combined["rules"]:
        for premise in rule["all_of"]:
            edges[premise].append(rule["conclusion"])
    visiting, done = set(), set()

    def visit(node):
        if node in visiting:
            raise AssertionError("cycle at " + node)
        if node in done:
            return
        visiting.add(node)
        for nxt in edges[node]:
            visit(nxt)
        visiting.remove(node)
        done.add(node)

    for node in known:
        visit(node)

    write_json(GRAPH, combined)
    graph_hash = digest(GRAPH)

    model_results = json.loads(RESULTS.read_text())
    expected_new = {n["id"] for n in nodes}
    expected_rules = {r["id"] for r in rules}
    expected_links = {(x["from"], x["to"], x["relation"]) for x in links}
    checks = [
        ("exact_parent_nodes", combined["nodes"][:-len(nodes)] == parent["nodes"]),
        ("exact_parent_rules", combined["rules"][:-len(rules)] == parent["rules"]),
        ("exact_parent_context_links", combined["context_links"][:-len(links)] == parent["context_links"]),
        ("exact_new_nodes", {n["id"] for n in combined["nodes"][-len(nodes):]} == expected_new),
        ("exact_new_rules", {r["id"] for r in combined["rules"][-len(rules):]} == expected_rules),
        ("exact_new_context_links", {(x["from"], x["to"], x["relation"]) for x in combined["context_links"][-len(links):]} == expected_links),
        ("unique_ids", len(node_ids) == len(set(node_ids)) and len(rule_ids) == len(set(rule_ids))),
        ("all_endpoints_resolve", True),
        ("rule_graph_acyclic", len(done) == len(known)),
        ("note_hash_matches", digest(NOTE) == note_hash),
        ("model_hash_matches", digest(RESULTS) == result_hash),
        ("model_checks_pass", all(x["pass"] for x in model_results["checks"])),
        ("actual_relation_not_inferred_from_certificate", not any("R174:PRIMARY_EVIDENCE_LADDER" in r["all_of"] and r["conclusion"] == "R174:SHARED_TEMPORAL_COORDINATE" for r in rules)),
        ("semantic_bridge_has_no_deductive_closure", not any(r["conclusion"] == "TO20261008:ORDER_BRIDGE_CANDIDATE" for r in rules)),
        ("c1_rule_excludes_evidence_parameters", "W/E/certificate excluded" in rules[2]["formal_contract_R174"]["bindings_required"]),
    ]
    assert all(ok for _, ok in checks)
    audit = {
        "status": "SCOPED_R174_INTEGRATION_CHECK_ONLY",
        "parent_revision": EXPECTED_PARENT,
        "parent_graph_sha256": parent_hash,
        "graph_sha256": graph_hash,
        "counts": {"nodes": len(combined["nodes"]), "rules": len(combined["rules"]), "context_links": len(combined["context_links"])},
        "checks": [{"name": name, "pass": ok} for name, ok in checks],
        "not_established": ["Actual route realization", "Intervention fidelity or unrestricted mechanism closure", "C1 or B_order empirical truth", "Independent review closure", "Global semantic consistency"],
    }
    write_json(HERE / "MAP_AUDIT.json", audit)

    proof_ledger = {
        "round": "R174",
        "source_sha256": note_hash,
        "entries": [
            {"id": "R174-P1", "type": "exact counterexample", "claim": "The previous baseline nonreport contrast separates S from C but not S from H.", "domain": "Declared S/C/H equations.", "all_premises": ["same delta,beta,s", "s>0", "fixed z,u definitions"], "argument": "Direct substitution: all z match; u_S=u_H!=u_C for beta!=0.", "counterexample_or_limit": "Only the declared three routes; no actual system.", "status": "PROVED_IN_MODEL", "thought_experiment_role": "Shows why a mediator intervention is needed."},
            {"id": "R174-P2", "type": "conditional theorem", "claim": "The source-perturbation plus mediator-clamp signature separates S,C,H.", "domain": "Same-instance declared rival class.", "all_premises": ["R174:FIXED_ROUTE_PROTOCOL", "R174:THREE_RIVAL_ROUTE_CLASS", "c!=0", "s>0"], "argument": "Displayed algebra in §4; 21 exact regressions include boundary values.", "counterexample_or_limit": "Off-target clamp, hidden paths or compensation invalidate application.", "status": "MANUAL_PROOF_PLUS_EXACT_CHECKS", "thought_experiment_role": "Definition and identification test."},
            {"id": "R174-P3", "type": "nonidentification theorem", "claim": "Finite route evidence does not imply unrestricted route closure when an untested gated bypass is admitted.", "domain": "Finite W plus admitted x* extension.", "all_premises": ["finite W", "x* not in W", "gate zero on W and one at x*", "bypass admitted"], "argument": "The added term vanishes on W and is nonzero at x*.", "counterexample_or_limit": "A valid universal physical closure law can exclude the extension.", "status": "PROVED_BY_CONSTRUCTION", "thought_experiment_role": "Stops overgeneralization from finite PASS."},
            {"id": "R174-P4", "type": "source synthesis", "claim": "The three primary studies successively constrain criterion variants but do not provide the complete R174 mediator-clamp certificate.", "domain": "Recorded source scopes.", "all_premises": ["study manipulations/results as read", "declared S/C/H and C_mod/C_gen contrasts", "no unreported route intervention inferred"], "argument": "Compare the reported evidence with each required route premise.", "counterexample_or_limit": "No raw-data reanalysis; Cai scope is abstract; full studies may constrain more models.", "status": "TARGETED_SOURCE_COMPARISON", "thought_experiment_role": "Connects the model to a real evidence ladder without overclaiming."},
            {"id": "R174-P5", "type": "conditional C1 application", "claim": "A grounded actual Theta_STC relation has an experiential structural counterpart.", "domain": "One actual complete P/I/K/D/Phi/h instance.", "all_premises": ["A:C1", "R174:SHARED_TEMPORAL_COORDINATE", "R157:COORDINATE_TRANSPORT", "K grounding", "sorted occurrences", "all physical parameters transported", "W/E/certificate excluded"], "argument": "Ordinary isomorphism preservation for the grounded K-formula.", "counterexample_or_limit": "Does not name experienced order or validate C1.", "status": "CONDITIONAL_MODEL_THEORETIC_ARGUMENT", "thought_experiment_role": "Places the positive coordinate inside experience."},
            {"id": "R174-P6", "type": "semantic boundary", "claim": "The evidence ladder and structural counterpart do not entail B_order.", "domain": "Selected action-feedback experienced-order target.", "all_premises": ["R174:PRIMARY_EVIDENCE_LADDER", "R174:EXPERIENTIAL_SHARED_COORDINATE", "R157:SEMANTIC_RESIDUAL", "TO20261008:ORDER_BRIDGE_CANDIDATE"], "argument": "No premise supplies the external relation-to-content interpretation; explicit failure conditions remain.", "counterexample_or_limit": "A future independently justified narrower bridge is not ruled out.", "status": "OPEN_INTERPRETIVE_BOUNDARY", "thought_experiment_role": "Prevents report or control from defining experience."},
        ],
    }
    write_json(HERE / "PROOF_LEDGER.json", proof_ledger)

    source_ledger = {
        "round": "R174",
        "reading_date": "2026-10-08",
        "sources": [
            {"id": "A/I-v1.2", "type": "fixed UCT source", "location": "records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md", "sha256": digest(ROOT / "records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md"), "scope_read": "§§2.5,3.5,C1,6.4,8.11-8.14,14.7", "use": "token/signature/physical-witness/C1/self boundaries"},
            {"id": "R157", "type": "project source", "location": "records/R157_Structural_Coordinate_and_Mineness_20261007/Structural_Coordinate_and_Mineness_v0_1.md", "sha256": digest(ROOT / "records/R157_Structural_Coordinate_and_Mineness_20261007/Structural_Coordinate_and_Mineness_v0_1.md"), "scope_read": "complete note", "use": "formula transport and semantic residual"},
            {"id": "R172-effective", "type": "mandatory effective overlay", "location": "records/R172_Interface_Composition_and_Action_Use_20261008/REVIEW_AMENDMENTS.json", "sha256": digest(ROOT / "records/R172_Interface_Composition_and_Action_Use_20261008/REVIEW_AMENDMENTS.json"), "scope_read": "complete file", "use": "actual role/evidence/parameter separation"},
            {"id": "R173", "type": "project source", "location": "records/R173_Familiar_Mineness_and_Retentive_History_20261008/Familiar_Mineness_Retentive_History_v0_1.md", "sha256": digest(ROOT / "records/R173_Familiar_Mineness_and_Retentive_History_20261008/Familiar_Mineness_Retentive_History_v0_1.md"), "scope_read": "complete note", "use": "retentive history and F_O/F_A/F_F separation"},
            {"id": "TO20261008", "type": "project source", "location": "records/TO20261008_Temporal_Reference_and_Order/Temporal_Reference_and_Represented_Order_v0_1.md", "sha256": digest(ROOT / "records/TO20261008_Temporal_Reference_and_Order/Temporal_Reference_and_Represented_Order_v0_1.md"), "scope_read": "complete note", "use": "S/C model, P2/P3, B_order"},
            {"id": "Stetson2006", "type": "primary human study", "citation": "Stetson C, Cui X, Montague PR, Eagleman DM. Neuron 51:651-659.", "doi": "10.1016/j.neuron.2006.08.006", "url": "https://pubmed.ncbi.nlm.nih.gov/16950162/", "scope_read": "Current round: PubMed abstract; inherited TO20261008 documents targeted full-article reading of results, discussion and behavioral methods. No raw-data reanalysis.", "use": "motivates experienced-order target; does not identify S/C"},
            {"id": "Sugano2010", "type": "primary human study", "citation": "Sugano Y, Keetels M, Vroomen J. Exp Brain Res 201:393-399.", "doi": "10.1007/s00221-009-2047-3", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2832876/", "scope_read": "Abstract, introduction, methods/design and discussion passages concerning cross-modal transfer and criterion alternative; no raw-data reanalysis.", "use": "constrains modality-specific criterion, not modality-general criterion"},
            {"id": "Cai2018", "type": "primary human study", "citation": "Cai C et al. NeuroImage 172:654-662.", "doi": "10.1016/j.neuroimage.2018.02.015", "url": "https://pubmed.ncbi.nlm.nih.gov/29428581/", "scope_read": "PubMed abstract only; no full-text or raw-data analysis.", "use": "neural timing evidence that constrains a purely late verbal account but does not establish mediator routing"},
        ],
        "novelty_limit": "No new general algebra, causal-identification theorem or neuroscience priority is claimed; contribution is the project-specific typed synthesis and countermodel.",
    }
    write_json(HERE / "SOURCE_LEDGER.json", source_ledger)

    gaps = {
        "round": "R174",
        "record_type": "RESEARCH_SELF_CHECK_NOT_INDEPENDENT_REVIEW",
        "items": [
            {"id": "R174-G1", "severity": "HIGH", "location": "§§2,7 / SHARED_TEMPORAL_COORDINATE", "impact": "Blocks actual satisfaction and C1 application.", "counterexample": "A correct stored beta or analyst diagram with no executed beta-to-q-to-consumer occurrences.", "repaired": "Ontic Theta_STC is separated from evidence and reports.", "unresolved": "No actual human, neural or hardware instance has been grounded.", "status": "OPEN"},
            {"id": "R174-G2", "severity": "HIGH", "location": "§4 / MEDIATOR_CLAMP_SIGNATURE", "impact": "Blocks empirical route identification.", "counterexample": "Clamp misses q, perturbs beta, changes calibration or recruits compensation.", "repaired": "Same-instance fidelity/locality/window premises and failure conditions are explicit.", "unresolved": "No intervention package has been executed or validated.", "status": "OPEN"},
            {"id": "R174-G3", "severity": "HIGH", "location": "§5 / FINITE_ROUTE_NONENTAILMENT", "impact": "Prevents unrestricted no-alternative-path claims.", "counterexample": "A hidden gate is silent on W and activates a beta-to-u bypass at x*.", "repaired": "Positive identification is limited to the declared rival/intervention class.", "unresolved": "Any broader physical closure law must be independently justified.", "status": "OPEN"},
            {"id": "R174-G4", "severity": "MEDIUM", "location": "§4 / z,u readout", "impact": "Binary report and noisy consumer observations may not recover the algebraic signature.", "counterexample": "A small z shift stays on the same side of a binary threshold; noise or recalibration hides u change.", "repaired": "Requires calibrated physical z/u readout or a separately justified response-law inference.", "unresolved": "Measurement/calibration and no-compensation evidence remain application-specific.", "status": "OPEN"},
            {"id": "R174-G5", "severity": "HIGH", "location": "§8 / B_order", "impact": "Blocks the claim that the transported coordinate is experienced order or familiar mineness.", "counterexample": "Same independently warranted F_order inside one Theta_STC fiber, or changed Theta_STC with invariant F_order where sensitivity is claimed.", "repaired": "Target, measurement, report, F_O, F_A, F_F and conceptual I are separated with explicit failure tests.", "unresolved": "No independent relation-to-content bridge or no-report measurement is established.", "status": "OPEN"},
            {"id": "R174-G6", "severity": "MEDIUM", "location": "§6 / primary evidence ladder", "impact": "Limits claims about existing human evidence.", "counterexample": "Cross-modal transfer can be reproduced by a modality-general criterion; neural correlation need not be shared causal use.", "repaired": "Each primary source is assigned only its recorded scope and rival exclusion strength.", "unresolved": "Stetson full text was not independently reread this round; Cai reading is abstract-only; no raw-data reanalysis.", "status": "OPEN"},
            {"id": "R174-G7", "severity": "MEDIUM", "location": "REVIEW_SUPERVISION QC-06/07", "impact": "Independent reviewer closure cannot be claimed.", "counterexample": "A self-reported PASS or new derived node does not resolve reviewer-controlled status.", "repaired": "R174 uses the effective overlay and preserves the actual/evidence firewall.", "unresolved": "QC-06/07 remain pending reviewer assessment.", "status": "OPEN"},
        ],
    }
    write_json(HERE / "GAP_LEDGER.json", gaps)
    print(json.dumps({"revision": REVISION, "counts": audit["counts"], "checks": len(checks), "graph_sha256": graph_hash}, ensure_ascii=False))


if __name__ == "__main__":
    main()
