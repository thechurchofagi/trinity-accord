"""Serialize the auditor's completed reading and authored compatibility judgments.

This script is NOT a semantic checker. It supplies exact IDs, hashes and a
machine-readable record of work already performed through manual reading.
Unreviewed nested contracts and source proofs remain explicitly unreviewed.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from functools import lru_cache
import csv
import json

HERE = Path(__file__).parent
ROOT = HERE.parents[1] / "uct_repo/research/uct-agent-consciousness-workspace"
BASE = HERE / "baseline"
GRAPH = json.loads((BASE / "UCT_EFFECTIVE_GRAPH.json").read_text())
OLD = json.loads((BASE / "REVIEW_LEDGER.json").read_text())
OLD_BY_ID = {r["item_id"]: r for r in OLD["items"]}
NODE_FIELDS = ("id", "kind", "label", "statement", "domain", "scope", "quantifiers",
    "proof", "proof_or_definition", "proof_or_evidence", "proof_locator", "proof_location",
    "proof_source", "source", "boundary", "limits", "counterexamples_and_limits", "premises", "all_premises", "amendment")
RULE_FIELDS = ("id", "all_of", "conclusion", "statement", "kind", "scope", "proof", "proof_sketch",
    "proof_locator", "proof_location", "source", "instance_obligations", "binding", "guard",
    "inline_premise_contracts", "same_instance_required", "limits")
CONTEXT_FIELDS = ("id", "from", "to", "source", "target", "from_id", "to_id", "external_source",
    "source_reference", "relation", "reason", "statement", "type", "kind", "deductive", "from_type", "to_type", "source_type", "target_type")
SUPPLEMENTARY_SEMANTIC_FIELDS = {
    "caveats", "purpose", "excluded_inferences", "evidence_records", "instance_obligation_status",
    "semantic_override_source", "effective_override_source", "historical_statement_preserved",
    "source_review_rationale", "proof_review_rationale", "proof_source", "premise_semantics",
    "all_of_semantics", "alternative_route_semantics", "alternative_routes", "bindings_required",
    "instance_binding", "semantic_binding", "comparison_bindings", "definition_component_import",
    "premise_mode", "replaces", "may_infer", "no_assumption_promotion"
}


@lru_cache(maxsize=None)
def digest_file(path):
    return sha256(path.read_bytes()).hexdigest()


def digest_record(row):
    return sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


FAMILY = {
"A": "C1 relates the complete constitutive organization of independently admitted actual tokens, with every relevant physical parameter transported. U1 is unchanged by source equality, success, prediction, use, report or self labels. Source/intake distinctions in a selected model neither count subjects nor automatically prove complete-type or macroprocess differences. Product, persistence and continuity clauses retain their separate actual premises.",
"B": "The BAC/target-faithful translation contracts and each rival-specific bridge stay conditional. The source protocol identifies a declared mechanism within a finite interface, not a reduction of another theory or the actuality of its physiological realization. A recurrence or stability calculation still does not supply a new basal-experience gate.",
"C": "Capability J retains one task, policy, time, resource and port contract. Nominal success is one selected output and is weaker than complete J equality. Source-observation fibers instantiate existing factorization reasoning; a split selected relation does not by itself prove an actual full experiential-type difference. The finite probability and optimization identities keep their simultaneous law/support premises.",
"D": "Continuation variables, bearer identity, reward-relevant consequence and valence stay distinct. SCU supplies no actual continuation preference, fear or valence evidence. Existing rank, payoff and Frechet arguments rely on their own coherent joint laws; apparent scalar witnesses must not be detached from those laws, as the R201 correction demonstrates.",
"R126": "A view closes only when successor and output laws are constant on its fibers under the declared operations. Adding independently addressed source probes refines an observation contract; it does not retroactively make a prior coarse view complete, nor select an actual process from a mathematical quotient.",
"R127": "A prequery encoder and supported answer family jointly determine the exact information bound. The SCU binary source code uses a different intervention role and cannot infer ancestry or occurrence identity from codeword recovery. Joint cuts must still include background B; selected success is not a physical mediation certificate.",
"N128": "Marginal kernel closure does not imply joint closure; the hidden-coupling countermodel keeps one finite transition kernel and operation family. SCU's OR versus pure-route contrast similarly changes the response class explicitly. It supplies no new proof that an empirical joint kernel is closed.",
"R131": "Expected linear probes identify a probability law only under the fixed probe matrix, normalization and rank conditions. Source columns identify roots only under their separate pure-route response law. Neither statement licenses a zero-effect observation as absence of actual consumption.",
"R132": "Joint scheduling/enabledness and next-summary/output constraints cannot be reconstructed by pasting individually feasible choices. Hall-style bottlenecks are inherited local-to-global obstructions. The SCU deterministic protocol likewise must use one schedule policy valid for every admissible hidden route pair.",
"R133": "A decision cell requires a common successful action, and a persistent-model policy cannot switch the hidden world across time. Same-root testing is target-specific decision sufficiency, not complete identification of the route pair. Source interventions must remain available under one legal model contract.",
"R134": "The attainable policy profile is one shared vector over hidden states, not separate per-coordinate optima. The SCU adaptive lower bound uses one all-zero response branch for every compatible rival and does not choose a hidden-root-aware algorithm. No finite-error randomization optimum is imported into its exact deterministic claim.",
"R135": "Target guarantee regions and common legal policies remain more informative than one scalar score. The new logarithmic or linear probe cost measures its declared equality decision only; it neither orders intelligence generally nor supplies actual coupling and enabledness premises for the older transfer results.",
"R136": "Blackwell-style garbling and causal simulation keep one common channel and prefix nonanticipation. The SCU late sensory echo reinforces the inherited distinction between available final information and a timely installed predictor. Value equality alone does not supply an online access path.",
"R137": "Common randomized decoder weights, legal-action zeros, joint transitions and the chosen seed-coupling convention remain simultaneous. Stable source routes across repeated probes are a comparable protocol premise; synchronized readout marginals do not identify hidden paths or path laws.",
"R145": "Logical feedback equivalence is restricted to descending operations. A diagnostic reset or changed source wire may leave that class, while a full conjugate relabeling transports all ports and maps. The SCU source probe is an explicitly stronger operational contract, not passive coordinate renaming.",
"R146": "Equivariant centered reference does not require a unique uncentered owner. A public duplicate-label problem and local self-target prediction remain different observations. Same-root equality in SCU neither identifies bearer membership nor turns a report or an external label into a mineness fact.",
"R147": "This is a direct predecessor: tau-inverse-sigma can preserve exact command prediction while beta-relative physical attachment changes. Synchronized sources hide rewiring. SCU inherits this underdetermination and adds scoped intervention budgets; it must retain beta/source/carrier identities when it claims an actual comparison.",
"TA15": "The source's composition, factorization and observation-fiber statements remain relative to fixed domains and error assumptions. The new source-column fiber characterization is an application of that inherited logic. It introduces neither an actual support selector nor a new general representation theorem.",
"TA16": "Selected functional cut, recoding and wrapper results retain their implementation and incompatible-mode limits. The earlier RRH whole-target gate cannot become a basal-experience necessity under current U1. Source confluence adds no such gate and does not make mutually exclusive routes simultaneously realized.",
"TA17": "Functional descendant sets, mutual information, intervention dependence and numerical occurrence identity are different relations. Common source ancestry or two equal copy values cannot establish one intake occurrence, and a cardinality of source sites is not an amount of experience.",
"TA18": "Selected-germ bridges retain their explicit separation/isomorphism/null assumptions. The unrestricted bridge countermodel cannot also be treated as a countermodel within current complete C1-OI. SCU output twins are partial-signature twins; complete organizational clones retain complete experiential type under C1.",
"TA19": "Automorphism and monodromy obstructions concern equivariant singleton selectors or continuous sections under stated hypotheses. They neither prohibit centered reference nor decide subject count. The source equality protocol asks a finite relational question, not the selection of one privileged owner.",
"R149": "The complete-type kernel criterion and selected-target factorization criterion are different strengths. SCU correctly characterizes fibers for its declared readout and target. Those fibers are not complete physical or experiential signatures, and no new general fiber theorem is claimed.",
"R155": "The installed attribution updater, latent truth, threshold consumer and independently interpreted mineness target remain separate. A perfectly consistent source code or a Bayesian posterior is not an independently correct self label. Finite representation limits and positive-likelihood errors retain their original domains.",
"R156": "Equal current values can omit an installation parameter that changes actual intervention-dependent use. This is an inherited antecedent of the source/consumer distinction. A probe recovering functional R still does not recover a named ownership/familiarity endpoint.",
"R157": "Grounded K-formulas transport only with correct sorts and all physical parameters under one complete actual binding. Formula definability is not autonomous substructure; report measures remain partial outside their evidence domain. The source relation can have a conditional structural counterpart without gaining the name H.",
"R158": "A necessary-conjunct refutation needs an admitted target-positive witness, and definable selected sets need not be closed under functions. Ownership and agency targets are separately defined, not freely independent bits. SCU's actual-binding premise respects these limits and does not promote a source label into an admitted experiential part.",
"R159": "Anchor, internal reference frame, carrier binding and external anatomical referent are separately grounded. An externally located or remotely driven source may participate in a fixed internal relation, but external-source or local-source labels alone do not establish ownership or familiar mineness.",
"R160": "An intervention profile requires independently grounded ports, metrics, error bounds and complete estimands. Cross-trial contrasts are not automatically a relation in one actual token. SCU supplies an exact mathematical contract but no physiological fidelity or empirical h-to-H bridge.",
"R161": "Physical and measurement fidelity precede statistical profile classification; confirm, exclude and unresolved retain a simultaneous interval family. Exact code execution supplies no participant evidence and closes none of these application gates. These are evidence requirements, not basal-experience requirements.",
"R162": "Unpaired component data leave cross covariance unidentified, and planwise conditional coverage is needed after independent pilot freezing. The R202 repair is consistent with this insistence on one coherent joint law. SCU's source matrix contains no human sampling or covariance data.",
"R163": "Bounded finite-design outcomes, independent participant vectors and declared missing outcomes govern the finite-sample bounds. The source probes neither establish these premises nor replace latent outcomes with clipped or randomized-mixture targets. Mathematical exactness does not create empirical coverage.",
"R164": "The betting/variance constructions preserve the specified mean target through predictable residual and pilot premises. A deterministic source-code bound has no bearing on missing endpoints or rare-spike uncertainty. Identification and sampling uncertainty remain separate.",
"R165": "Menu selection, residual transport and feasibility certificates require their own budgets and target bindings. A synthetic intervention that is executable in the model is not a physical apparatus feasibility result. Invalid, inconclusive, infeasible and unresolved statuses remain distinct.",
"R166": "W1-W6 actual installation requirements jointly bind bearer, interval, signature, occurrences, physical grounding and path discrimination. Neither a source-code success nor an event log alone discharges the application conjunction. This is central to the C8 guard and leaves actual application open.",
"R167": "Contextual potential influence can be exposed only when the declared backup and compensation context is controlled. It is different from an executed intake event, present unmasked effect and diagnostic evidence. OR and cancellation models reinforce this distinction without redefining the older criterion as episode-level read occurrence.",
"R168": "Amplitude, affected mass and hidden-fiber coverage have different quantifiers. No-hit samples do not certify universal absence; finite source enumeration is complete only for its stated response class and cube. It does not certify actual hidden contexts or physiological regularity.",
"R169": "Local channel budgets compose only on an independently inventoried actual route graph with metric and calibration control. A matrix of experimental source codes is not that actual graph. SCU supplies none of the unmeasured edges or held-out calibration obligations.",
"R170": "Any nonempty unbounded remainder preserves the worst-case cap even when its measure is tiny. Complete checking of a finite declared source class does not close an open physical remainder. Mean/mass and universal amplitude claims retain separate certificates.",
"R171": "Direct total-range and inductively reachable certificates are alternative actual-application routes, not a conjunction of both. The completed effective replacements retain this repair. SCU's specified full binary control is an abstract premise and cannot self-discharge an actual range certificate through a program PASS.",
"R172": "Use certificates require independently grounded interfaces and a same-instance evidence-to-role bridge. The effective phi_path interpretation controls over historical theta_EBA wording. The source protocol does not turn matching output or a write event into an actual comparator, and it closes none of the corrected actual-role obligations.",
"R173": "The effective retained-history relation requires actual earlier occurrence, continuing lineage/carrier and current consumer use. Present source equality, copied values or a reset do not supply those facts. Suspended raw independence and unadmitted history-twin claims remain unavailable; B_fam is still open.",
"R174": "The shared/criterion/hidden-bypass rivals are distinguished only by jointly specified source and mediator probes, timings and scale. Finite support leaves hidden-context extensions possible. SCU's source-versus-node/edge distinction is a restricted application, not a universal path recovery or B_order result.",
"R175": "Effective replacements preserve the admitted explicit history twin and AgencyLoop-to-Avail constraint. At most six Boolean valuations is not realizability of all six, and held-out correspondence completion is not a new named phenomenal prediction. The new reflex comparison must not resurrect the suspended stronger claims.",
"R176": "The corrected closure packages retain every premise of the admitted comparison and do not fill independent actual-history or semantic obligations. Adding a new source coordinate does not bypass the effective rule repairs or establish all combinations of self-related labels.",
"R177": "The familiar-mineness/retention boundary remains a selected semantic problem; a structural relation or model distinction alone does not provide its named interpretation. SCU offers exact organizational targets while keeping H and the existing review-controlled application obligations open.",
"TE20261008": "Retiming and faithful replacement relays preserve selected relations only under explicit dynamic, source and actual-temporal grounding. A changing carrier material can preserve provenance, while distinct copies remain distinct occurrences. SCU inherits this source/path logic and does not infer token identity from matching values.",
"TO20261008": "Reference routing and global clock compatibility require coherent pairwise timing constraints on one actual interval. Reports and nonreport consumers remain separate routes. R194's anchor repair illustrates a general compatibility caution but does not change this completed temporal proof; a final copied value does not establish predictive chronology.",
"BR20261008": "Role refinement and joint mapping constrain selected organization only with actual role grounding and compatible target mappings. Different coordinates cannot choose contradictory correspondences independently. Source/intake relations add no independent phenomenal names or empirical bridge by themselves.",
"IA20261008": "The source-to-use trace DAG and source-set invariance under faithful relays/retiming are direct predecessors. Actual trace membership and C1 counterpart require their own same-instance P/I/K grounding. New protocol budgets concern observation of a restricted root relation, not the invention of source provenance or a unique experiential owner.",
"CORE20261008": "Inclusion-minimal support, least support, required intersection and monotone hitting-set duality differ. Redundant OR consumers can hide individual effects without removing actual intake. SCU's n-probe theorem is relative to the OR class and does not imply monotonicity of arbitrary physical intervention success.",
"EI20261008": "A joint cut, query timing and selected recovery target govern the support bound. Different arithmetic implementations need not share complete organization or attainable core families. Source probe counts are not universal substrate counts, and actual and named bridges remain separate.",
"OO20261008": "Linear/nonlinear readout access and later queries depend on the exact encoder/readout class and persistent source premise. Equal channel dimension or equal nominal values need not supply the same use. The new source protocol neither changes those access bounds nor ranks basal experience by storage.",
"RU20261008": "Average score, posterior equality, task-specific loss and actual wiring are separate targets. The new known-root shortcut changes available independent information and hence its decision problem, not a general intelligence law. The actual J-difference and persistence guards remain unfilled.",
"RC20261008": "Pointwise answer plausibility need not come from a common coherent reconstruction or shared joint sampler. This same quantifier discipline prevents SCU from mixing source assignments or residual values across one conclusion. Actual complete-type consequences still need the independent comparison package.",
"IE": "The fixed-organization experience-off switch remains inadmissible under C1/U1. Compensation and timely queries concern selected roles, not existence of experience. SCU's cancellation and sensory echo examples change or omit organizational coordinates and do not posit a consciousness-free complete clone.",
"TH20261009": "Storage, route recovery and physical handoff are distinct; fresh masks and reused masks have different joint laws. Duplicate cancellation already shows rank-one storage with zero XOR readout. The concurrent R205 subtraction example and SCU redundant OR example inherit that boundary while keeping their response classes and occurrence identities separate.",
"RB20261009": "The top-k cut bound and its tightness need the same target law and helper access; a wrong reader or late key fails those premises. No source intervention grants uncounted decoder/context access. Timing and target controls remain essential, and code success is not a named-experience test.",
"OL20261009": "Source-kick observability, correction spans and readout horizon determine the claimed gap. A compensated or unobserved source can have no selected output effect without being absent. Coordinate metrics and actual physical reduct/C1 guards remain independent of SCU's finite interface construction.",
"HOM": "Short observation equality does not close higher-order interaction possibilities outside the stipulated closure class. SCU's exhaustive cube is exhaustive only for the fixed pure or OR model. It makes no all-architecture or actual-completeness claim, and adds no basal gate.",
"UI20261009": "Order contrast obstructs independently updating product realizations only under the shared preparation, readout and update contract. Commutation is not sufficient for product structure. The sensorimotor source distinction similarly makes only a declared-class inference; it does not count carriers, subjects or degrees of experience.",
"CM20261009": "Compensation can remove a source's observed effect while its contribution remains physically present. Reconstruction requires the kernel/monitor contract and independently bounded errors; exogenous probe independence is separate. Cancellation and source testing do not establish actual causal clamping or complete-type nonisomorphism without their guards.",
"R183": "Target-relative unavoidable relations and disjunctive minimal supports concern selected capability preservation under one actual intervention policy. U1 remains outside these success conditions. Source equality or OR subset recovery can refine a selected target but is not a new gate or a named-experience relevance proof.",
"R184": "Equal resumption can use internal memory, a continuing external cue or redundant priority routes. A conflict input separates the stipulated policies; a reflex label does not identify feeling. SCU's route distinction inherits this lesson and does not prove actual retention or formation lineage from resumption alone.",
"R185": "One grounded occurrence may belong to multiple actual tokens; equal copies and synchronizers do not thereby become the same occurrence. SCU's shared/separate relay construction is directly compatible and prior-covered at this general level. Its node write needs additional physical targeting, and no cross-token numerical experience identity follows.",
"R187": "All-policy indistinguishability is relative to the common intervention interface. A constituent write, a readout-edge rewrite and a write erased before observation are different operations. SCU C6 uses this distinction with a nontrivial pre-read node write; source-only probes alone cannot justify it or recover past lineage.",
"R188": "Encoder access, source/context roles, late feedback and one-shot scoring determine the exact optimum. The classical coding ancestry is already represented; SCU must claim its application and response-class comparison rather than general coding priority. Actual J and complete-type grounding remain separate application obligations."
}

families_present = {r["id"].split(":")[0] for r in GRAPH["nodes"]}
assert families_present == set(FAMILY), (families_present-set(FAMILY), set(FAMILY)-families_present)
with (HERE / "MANUAL_ITEM_RATIONALES.tsv").open() as stream:
    manual = {row["id"]: row["rationale"] for row in csv.DictReader(stream, delimiter="\t")}


def item_family(record, item_type):
    if item_type == "node":
        return record["id"].split(":")[0]
    if item_type == "rule":
        return record.get("conclusion", "").split(":")[0]
    for key in ("from", "source", "from_id", "to", "target", "to_id"):
        value = record.get(key)
        if isinstance(value, str) and value.split(":")[0] in FAMILY:
            return value.split(":")[0]
    return None


def provenance(record):
    direct = {key: record[key] for key in ("source", "proof_source", "proof_location", "proof_locator",
        "source_provenance", "source_record_sha256", "original_source_record_sha256", "source_sha256", "origin_file") if key in record}
    anchors = {}
    for key, value in record.items():
        if key.startswith("formal_contract") and isinstance(value, dict):
            for subkey in ("source_anchor", "proof_source", "proof_or_evidence", "source", "proof_locator"):
                if subkey in value:
                    anchors[key + "." + subkey] = value[subkey]
    return {"direct_proof_source_fields": direct,
            "nested_source_locators_extracted_for_provenance_only": anchors,
            "nested_locator_extraction_is_not_full_contract_reading": True,
            "frozen_proof_source": "UCT-MAP-v1.1.2 capsule / UCT_EFFECTIVE_GRAPH.json and REVIEW_LEDGER.json",
            "fresh_full_historical_source_proof_reconstruction": False}


rows = []
unread_raw_contracts = []
unread_supplementary = []
for group, kind, fields in (("nodes", "node", NODE_FIELDS), ("rules", "rule", RULE_FIELDS), ("context_links", "context", CONTEXT_FIELDS)):
    for record in GRAPH[group]:
        item_id = record["id"]
        original = OLD_BY_ID[item_id]
        family = item_family(record, kind)
        formal_keys = sorted(key for key in record if key.startswith("formal_contract"))
        other_unread = sorted(key for key in record if key in SUPPLEMENTARY_SEMANTIC_FIELDS and key not in fields)
        if formal_keys:
            unread_raw_contracts.append({"item_id": item_id, "item_type": kind, "unreviewed_full_fields": formal_keys})
        if other_unread:
            unread_supplementary.append({"item_id": item_id, "item_type": kind, "unreviewed_full_fields": other_unread})
        old_semantic = original.get("semantic_review", {})
        inherited_assessment = old_semantic.get("assessment", old_semantic.get("review_reason"))
        read_record = {key: record[key] for key in fields if key in record}
        if kind == "node":
            relation_review = "Reviewed the displayed definition/statement with its declared domain, limits and graph-contained proof text where present. Its source proof is reused at the frozen version; no inference from candidate source-test success to actual or named phenomenal premise truth is accepted."
        elif kind == "rule":
            relation_review = "Reviewed this exact all_of list, conclusion, graph-contained argument and displayed same-instance/guard fields. The rule is a conditional schema: all premises must concern one appropriately bound instance. Later disabled modules are not additional satisfied premises, and declared availability does not discharge an actual relation."
        else:
            relation_review = "Reviewed the precise endpoints and relationship text as nondeductive context. The link records the stated conceptual correspondence; it neither supplies an all_of premise nor transfers actual truth, target semantics or proof status between its endpoints."
        rows.append({
            "item_id": item_id, "item_type": kind,
            "frozen_effective_record_sha256_from_release": original.get("effective_record_sha256"),
            "audit_serialized_record_sha256": digest_record(record),
            "fresh_read_scope": list(read_record), "freshly_read_semantic_card": read_record,
            "scope_level": "STATEMENT_PREMISE_RELATION_COMPATIBILITY",
            "new_compatibility_assessment": {"individual_manual_rationale": manual.get(item_id),
                "family": family, "family_rationale_authored_for_R190_R205_SCU": FAMILY.get(family, "The external reference remains contextual and does not import proof or actuality into the graph."),
                "relation_review": relation_review},
            "inherited_review_reused_without_fresh_reproof": {
                "source": "baseline/REVIEW_LEDGER.json", "source_sha256": digest_file(BASE / "REVIEW_LEDGER.json"),
                "source_review_locator": original.get("source_review"),
                "frozen_item_review_sha256": digest_record(old_semantic),
                "assessment": inherited_assessment},
            "proof_provenance": provenance(record),
            "unreviewed_full_raw_contract_fields": formal_keys,
            "unreviewed_supplementary_semantic_fields": other_unread,
            "review_outcome": "NO_NEW_STATEMENT_LEVEL_CONTRADICTION_IDENTIFIED_WITHIN_REVIEWED_SCOPE",
            "full_source_and_raw_contract_audit": "AUDIT_INCOMPLETE",
            "actual_premises_discharged": False, "phenomenal_target_validated": False,
            "open_reviews_preserved": ["QC10", "IA-QC11", "QC12", "QC13"]
        })

for item_id in GRAPH["suspended_historical_rule_ids"]:
    original = OLD_BY_ID[item_id]
    semantic = original["semantic_review"]
    rows.append({"item_id": item_id, "item_type": "suspended_historical_rule",
        "scope_level": "FROZEN_HISTORICAL_STATEMENT_PREMISES_AND_SUSPENSION_REASON",
        "freshly_read_semantic_card": {key: semantic.get(key) for key in
            ("historical_statement_read", "historical_premises_read", "review_reason")},
        "new_compatibility_assessment": semantic.get("review_reason"),
        "inherited_review_source": "baseline/REVIEW_LEDGER.json",
        "inherited_review_source_sha256": digest_file(BASE / "REVIEW_LEDGER.json"),
        "frozen_item_review_sha256": digest_record(semantic),
        "active_inference_permitted": False, "review_outcome": "RETAIN_SUSPENDED_NONEXECUTABLE",
        "full_historical_source_proof_read": False, "full_source_and_raw_contract_audit": "AUDIT_INCOMPLETE",
        "actual_premises_discharged": False, "phenomenal_target_validated": False,
        "open_reviews_preserved": ["QC10", "IA-QC11", "QC12", "QC13"]})

assert len(rows) == 1608 and len({r["item_id"] for r in rows}) == 1608
raw_by_type = Counter(r["item_type"] for r in unread_raw_contracts)
raw_fields = sum(len(r["unreviewed_full_fields"]) for r in unread_raw_contracts)
unread = {"schema": "uct-exact-unread-scope/1", "status": "AUDIT_INCOMPLETE",
    "base_graph_sha256": digest_file(BASE / "UCT_EFFECTIVE_GRAPH.json"),
    "statement_premise_relationship_unread_ids": [],
    "unreviewed_full_raw_contract_item_count": len(unread_raw_contracts),
    "unreviewed_full_raw_contract_field_count": raw_fields,
    "unreviewed_full_raw_contract_counts_by_type": dict(raw_by_type),
    "unreviewed_full_raw_contract_ids": sorted(r["item_id"] for r in unread_raw_contracts),
    "unreviewed_full_raw_contract_fields_by_id": unread_raw_contracts,
    "unreviewed_supplementary_semantic_item_count": len(unread_supplementary),
    "unreviewed_supplementary_semantic_field_count": sum(len(r["unreviewed_full_fields"]) for r in unread_supplementary),
    "unreviewed_supplementary_semantic_counts_by_type": dict(Counter(r["item_type"] for r in unread_supplementary)),
    "unreviewed_any_raw_or_supplementary_semantic_item_count": len({r["item_id"] for r in unread_raw_contracts+unread_supplementary}),
    "unreviewed_any_raw_or_supplementary_semantic_field_count": raw_fields + sum(len(r["unreviewed_full_fields"]) for r in unread_supplementary),
    "unreviewed_supplementary_semantic_fields_by_id": unread_supplementary,
    "full_historical_proof_source_not_independently_reconstructed_ids": sorted(r["item_id"] for r in rows if r["item_type"] != "context"),
    "explanation": "All semantic cards were manually read, including all 424 active all_of lists and displayed binding/guard fields. Nested formal_contract fields are conservatively counted as not FULLY reread, even where excerpts or equivalent inline guards were consulted. Exact historical proofs remain frozen-source reuse. This distinction prevents a statement-level review from being reported as a complete proof reconstruction."}
(HERE / "EXACT_UNREAD_SCOPE.json").write_text(json.dumps(unread, ensure_ascii=False, indent=2) + "\n")

ledger = {"schema": "uct-independent-semantic-compatibility-review/1", "audit_id": "SCU20261010-MAP-AUDIT-v0.1.0",
    "reviewer": "parallel internal AI auditor /root/map_semantic_audit", "not_independent_human_peer_review": True,
    "base_map": "UCT-MAP-v1.1.2", "base_graph_sha256": digest_file(BASE / "UCT_EFFECTIVE_GRAPH.json"),
    "frozen_release_ledger_sha256": digest_file(BASE / "REVIEW_LEDGER.json"),
    "counts": dict(Counter(r["item_type"] for r in rows)),
    "statement_premise_relation_read_count": len(rows), "statement_level_unread_ids": [],
    "full_source_and_raw_contract_audit": "AUDIT_INCOMPLETE",
    "freshly_authored_high_risk_individual_node_rationales": len(manual),
    "freshly_authored_family_compatibility_rationales": len(FAMILY),
    "method": "The auditor manually read every displayed semantic card in manageable batches, reread truncated items, examined all active all_of lists and contexts, and reviewed all ten suspension reasons. This script only serializes that reading, authored rationales, inherited exact proof provenance and explicit unread fields. No program PASS is used as a semantic judgment.",
    "new_actual_premises_discharged": False, "new_phenomenal_validation": False,
    "completed_map_version_change_authorized_by_this_review": False,
    "open_reviews_preserved": ["QC10", "IA-QC11", "QC12", "QC13"],
    "items": rows}
(HERE / "PER_ITEM_SEMANTIC_REVIEW.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
(HERE / "FAMILY_REVIEW_NOTES.json").write_text(json.dumps(FAMILY, ensure_ascii=False, indent=2) + "\n")
progress = {"node_semantic_cards_read": [x["id"] for x in GRAPH["nodes"]],
    "active_rule_semantic_cards_read": [x["id"] for x in GRAPH["rules"]],
    "context_relationship_cards_read": [x["id"] for x in GRAPH["context_links"]],
    "suspended_statement_premise_reason_cards_read": GRAPH["suspended_historical_rule_ids"],
    "unread_rule_cards": [], "scope_notice": "All card-level reading complete; full raw contracts/source proofs remain AUDIT_INCOMPLETE; see EXACT_UNREAD_SCOPE.json."}
(HERE / "READ_SCOPE_PROGRESS.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n")

with (HERE / "PER_ITEM_REVIEW_INDEX.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["item_id", "item_type", "review_scope", "review_outcome", "raw_contract_full_fields_unreviewed", "actual_premises_discharged"])
    for row in rows:
        writer.writerow([row["item_id"], row["item_type"], row["scope_level"], row["review_outcome"],
                         " | ".join(row.get("unreviewed_full_raw_contract_fields", [])), False])
print(json.dumps({"reviewed_cards": len(rows), "types": ledger["counts"],
    "raw_contract_items_not_fully_reread": len(unread_raw_contracts), "raw_contract_fields_not_fully_reread": raw_fields,
    "statement_level_unread_ids": [], "full_audit_status": "AUDIT_INCOMPLETE"}))
