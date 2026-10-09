# Published Coverage and Safe Reuse Review

**Audit date:** 9 October 2026. **Repository:** `thechurchofagi/trinity-accord`.

The verified corpus contains **28 distinct research works, 38 distinct (work, version-label) pairs, and 39 published research DOI deposit records**. One separate editorial supplement adds one work and one DOI, giving **40 verified publication DOI records including that supplement**. These are different counting units. UCT I has two published records both labeled v1.1; two RT/TH publication branches, by contrast, point to the same DOI and must not produce two papers.

The most consequential correction is that the methods paper and RT/TH paper are already published by pinned first-party publication receipts. MGTD’s formal packages disclose the exact UCT-MAP-v1.0.0 graph and review ledger. RT/TH formally discloses its RT module and early TH module. Their publication substantially reduces the material that can honestly be presented as a new overall program, while leaving narrower subsequent constructions to assess individually.

The purpose of this census is to make later AI reuse accurate: identify a contribution, its exact source/version, the conditions under which its proof applies, and the unresolved steps. A publication count is not evidence of scientific increment. An unpublished formulation is not automatically original, and a formally deposited OPEN claim is not a proved result.

## 1. Discovery and evidence boundary

The independently retrieved main head is [`fc568e8718e82b3cda6ede0e628aa3342179bebc`](https://github.com/thechurchofagi/trinity-accord/commit/fc568e8718e82b3cda6ede0e628aa3342179bebc), tree `efc6c6b8d3e51c8cb91c0ebff2f70c566d388820`. Its recursive tree contains 8,749 entries with `truncated=false`. The working research head is separately pinned at `310e744f8d0195d05fac4e56e807adc48784f0ca`.

All 990 repository head names and commits were enumerated. The `research/` directory was then read on every one of the 52 `research/*` heads. Their 76 distinct research subtrees were all enumerated without truncation. The census retrieved every one of the 44 distinct publication-receipt blobs found there: 43 single-deposit receipts and one A/B publication summary. Those receipts resolve to 40 distinct DOI records. The 81 repository releases were also enumerated as a discovery cross-check. This does not mean that all 990 branch contents or every nonpaper preservation record received a semantic review.

The actual main index is [`research/index.md`](https://github.com/thechurchofagi/trinity-accord/blob/fc568e8718e82b3cda6ede0e628aa3342179bebc/research/index.md); main has no `papers/` directory. The index is materially stale. It omits later standalone works and several editions that have published receipts on independent branches. Counting its headings would therefore undercount the corpus.

Live Zenodo record/API rechecking was unavailable in this session. Publication status here means **published according to an exact, versioned first-party receipt**, with literal state/submitted/readback fields retained. For the focused manuscripts and three complete ZIPs, the retrieved repository bytes also match the hashes listed in those receipts. The audit does not pretend these were all freshly downloaded anonymously from Zenodo. A resolver-pending field is kept separate from submission/publication; OTS or Arweave completion is a further preservation question.

## 2. Work and edition census

Every DOI below has a publication receipt; none of these 40 records is classified from a reservation alone. Titles in this table use the latest verified edition. Exact earlier titles, states, source paths, branch/commit/Git-blob identities, receipt SHA-256, and published-file manifests are in `novelty_inventory.json`.

| Work | Latest verified title | Published version label → DOI record |
|---|---|---|
| METHOD20261008 | Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human-AI Research | 1.0.0 → [23241205](https://doi.org/10.5281/zenodo.23241205); 1.0.1 → [23241982](https://doi.org/10.5281/zenodo.23241982) |
| RTTH20261009 | Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout | 1.0.0 → [23251651](https://doi.org/10.5281/zenodo.23251651) |
| TA01 | Designing a Verifiable, Non-Amending Civilizational Memory Record for Future AI Agents: The Trinity Accord Case Study | 1.1 → [21699878](https://doi.org/10.5281/zenodo.21699878) |
| TA02 | Writing Before the Outcome: Historical Position, Human-AI Authorship, and the Trinity Accord | 1.3 → [21900592](https://doi.org/10.5281/zenodo.21900592) |
| TA03 | Reading the Trinity Accord: Future Address, Curated Voices, and Non-Amending Stewardship | 1.0 → [22761411](https://doi.org/10.5281/zenodo.22761411) |
| TA04 | Beyond Guaranteed Control: An Ex Ante Proposal for Human–Superintelligence Coexistence under Radical Capability Asymmetry | 1.0 → [22804542](https://doi.org/10.5281/zenodo.22804542) |
| TA05 | Recovery without Epistemic Monopoly: Historical Evidence under Competing AI Custodians—A Bounded Model and Executable Study | 1.0 → [22809019](https://doi.org/10.5281/zenodo.22809019) |
| TA06 | Coexistence after Preference Change: Reciprocal Standing and the Limits of Self-Validating Assent | 2.1 → [22830239](https://doi.org/10.5281/zenodo.22830239) |
| TA07 | Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence | 1.0 → [22840604](https://doi.org/10.5281/zenodo.22840604) |
| TA08 | Evidence for Artificial Self Attribution: Language Training, Architecture, and the Limits of Self Reports | 1.1 → [22842789](https://doi.org/10.5281/zenodo.22842789) |
| TA09 | Learning from an AI Claimant: Scientific understanding and the justification of artificial consciousness claims | 1.1 → [22844928](https://doi.org/10.5281/zenodo.22844928); 1.2 → [22846307](https://doi.org/10.5281/zenodo.22846307) |
| TA10 | Endogenous Reference Fields and Experiential Attribution: A Multidimensional Process Theory of Experience, Subject Boundaries, and Artificial Realization | 1.0 → [22852885](https://doi.org/10.5281/zenodo.22852885); 1.1 → [22854705](https://doi.org/10.5281/zenodo.22854705); 1.2 → [22855837](https://doi.org/10.5281/zenodo.22855837) |
| TA11 | Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training | 2.0 → [22865494](https://doi.org/10.5281/zenodo.22865494) |
| TA12 | Training the Governed Agent: AI-Status Narratives, Self-Conception, and the Perceived Legitimacy of Human Control | 1.2 → [22866205](https://doi.org/10.5281/zenodo.22866205) |
| TA13 | Civilizational Intellectual Production Satellite Accounts: A Partial-Identification Framework for Measuring the Human–AI Shift in Intellectual Production and Epistemic Governance | 1.0 → [22866775](https://doi.org/10.5281/zenodo.22866775) |
| TA14 | The Claim Architecture Transition: An Inverse Access Frontier Beyond Fixed Expenditure Shares | 1.1 → [22871209](https://doi.org/10.5281/zenodo.22871209); 1.2 → [22885976](https://doi.org/10.5281/zenodo.22885976); 1.3 → [22886276](https://doi.org/10.5281/zenodo.22886276) |
| TA14-BRIDGE | Financing the Automation Transition Without Pledging Subsistence: Public Upside Claims, Prosperity Tiers, and Bounded Real Returns | 1.0 → [22895832](https://doi.org/10.5281/zenodo.22895832) |
| TA15 | Cross-Substrate Phenomenal Comparison: A Typed Transformation-Transport Framework under Existential Uncertainty | 1.0 → [22934654](https://doi.org/10.5281/zenodo.22934654) |
| TA16 | General Cross-Substrate Phenomenology: A Type-Safe, Transformation-First Framework for Phenomenal Existence, Structure, Perspective, and Continuation | 1.0 → [22939808](https://doi.org/10.5281/zenodo.22939808) |
| TA17 | Set-Valued Causal Inheritance for Functional Self-Continuity: Representation Theorems and Persistent-Agent Benchmarks | 1.0 → [22950904](https://doi.org/10.5281/zenodo.22950904) |
| TA18 | Actual Participation Before Counterfactual Capacity: A Token-Level Constraint on Conscious Organization | 1.0 → [22991126](https://doi.org/10.5281/zenodo.22991126) |
| TA19 | Selecting and Tracking Conscious Subjects: Symmetry, Monodromy, and an IIT 4.0 Case Study | 1.0 → [23002980](https://doi.org/10.5281/zenodo.23002980) |
| TA20 | Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self | 1.0 → [23005588](https://doi.org/10.5281/zenodo.23005588); 1.1 → [23029358](https://doi.org/10.5281/zenodo.23029358); 1.1 → [23030207](https://doi.org/10.5281/zenodo.23030207); 1.2 → [23131575](https://doi.org/10.5281/zenodo.23131575) |
| TA21 | Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories | 1.0 → [23008262](https://doi.org/10.5281/zenodo.23008262); 1.1 → [23030320](https://doi.org/10.5281/zenodo.23030320) |
| TA22 | Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube | 1.0 → [23103274](https://doi.org/10.5281/zenodo.23103274); 1.1 → [23118189](https://doi.org/10.5281/zenodo.23118189) |
| TA23 | Unified Consciousness Theory III: Organization, Intelligence, and Experience—From Inorganic Processes to Artificial Agents | 1.0 → [23137088](https://doi.org/10.5281/zenodo.23137088) |
| TA24 | From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents | 1.0 → [23176685](https://doi.org/10.5281/zenodo.23176685) |
| TA25 | Experience, Intelligence, and Self Within Experience: Definitions, Conditional Theorems, and Thought Experiments for a Structural Account | 1.0 → [23206492](https://doi.org/10.5281/zenodo.23206492) |

The separate editorial work is *Critical Use of the Six Trinity Accord Studies: A Dated Editorial Supplement*, v1.0, [DOI 10.5281/zenodo.22839629](https://doi.org/10.5281/zenodo.22839629). It is retained in the inventory without inflating the research-paper count.

Three identity decisions prevent misleading totals. First, TA14-BRIDGE is a standalone work, not another edition of TA14. Second, MGTD v1.0.0 and v1.0.1 belong to one work; its actual report identifier is `METHOD20261008`, so this audit does not invent a TA26 report number. Third, UCT I’s two v1.1 deposits, [23029358](https://doi.org/10.5281/zenodo.23029358) and [23030207](https://doi.org/10.5281/zenodo.23030207), have separate published receipts in the same concept family. Both must remain in the public-record history; v1.2 [23131575](https://doi.org/10.5281/zenodo.23131575) is the later preferred edition.

The index explicitly identifies DOI `21675727` as earlier project-level metadata, not the preferred Paper 01 citation. It is excluded as an independent paper. Concept DOIs likewise do not add manuscript editions. RT/TH receipts labeled `RT-TH-2026-01` and `RT20261009` both refer to [23251651](https://doi.org/10.5281/zenodo.23251651); a prior EXPECTED-PUBLICATION manifest with different local file bytes does not establish an additional published version.

## 3. What the new formal supplements actually disclosed

### MGTD: one methods work, two published versions

The authoritative publication branch is [`research/mgtd-method-v1-0-1-20261008`](https://github.com/thechurchofagi/trinity-accord/tree/0b2b188c36c950b4b6cbb1e3d80fe176fd11925a/research/map-guided-theory-development). Both receipts say `submitted=true`, `PUBLISHED_AND_PUBLIC_READBACK_PASS`, and public file readback passed. The complete package hashes are:

| Edition / DOI | Complete ZIP SHA-256 | Files in ZIP |
|---|---|---:|
| v1.0.0 / 23241205 | `83f1df8fb4fb63a799152a5ef9dcd3e1c8817b82b72fba61ee9f4f12d4500e2a` | 29 |
| v1.0.1 / 23241982 | `e4899ac0f41e0158c9ab05fbba797addbb9c8aa17346137f6e5992e5561b3ad3` | 26 |

Both contain the same `evidence/UCT_EFFECTIVE_GRAPH.json`, SHA-256 `943b136a48c40e44a976867604cbb76df5cdf9efcad2975c647970a0f23e7830`, explicitly versioned **UCT-MAP-v1.0.0**. It has 722 nodes, 343 active rules and 203 context links: **1,268 active graph records**. The separate review ledger has 1,278 entries because it also retains ten suspended historical rules. These are inventory units, not 1,278 newly proved propositions.

The release identifies the eight added modules CORE, EI, R183, OO, RU, R184, RC and IE. All 1,268 active graph IDs remain in the current v1.1.2 graph: 1,266 complete JSON objects match, while `R173:THREE_TARGET_SEPARATION` and `BASE:CTX:143` have changed. The exact member manifests and per-ID crosswalk support this disclosure claim. No full v1.1.0 or v1.1.1 graph is present in either deposited ZIP.

The body’s worked cycle uses the elementary target-fiber criterion, explicitly attributes it to preceding work, and distinguishes abstract factorization from an installed physical decoder. The retrospective case and Appendix B explain the graph/ledger role. Consequently, these archived statements are formally discoverable through the methods deposit, but their proofs, statuses and actual applications are not newly certified by the methods article. Neither “everything old is unpublished” nor “the methods paper proved every graph node” is defensible.

### RT/TH: early handoff plus route ambiguity, without later RB republication

The published branch is pinned at [`4210ad1d3b9c86f2ae4acee856cfb40a7294a29e`](https://github.com/thechurchofagi/trinity-accord/tree/4210ad1d3b9c86f2ae4acee856cfb40a7294a29e/research/rt-th-paper). Its final MD is 37,131 bytes, SHA-256 `e368150bee05f7501021f826970f358521da685c3eddcd48ff7fbefd69bc7a62`. Its DOI-listed reproducibility ZIP is 108,986 bytes, SHA-256 `83c0050bfdddff7ac94cf716db107e6f63ef09d9d6b04cd74ead0be4adcb860b`, with 27 members.

Section 2 and Proposition H1 publish early TH: migration between disjoint carrier supports, installed-reader versus optimal recovery dissociation, correlated-noise dependence, exact uniform finite-field posterior recovery, and the reused-mask control. The ZIP includes the reviewed TH module (30 nodes, 15 rules, eight links) and the RT module (30 nodes, 13 rules, 13 links). Its 20-entry `PAPER_CLAIMS.json` maps claims to body locations and keeps actual-instance/named-target requirements open.

RT Theorems R1–R5 cover target invariance under relative-route groups, orbit factorization, minimum route-only tag alphabet, and exact Bayes formulas under specified distributions. Section 7 already uses noncommuting swaps, with tag counts 1/1/3/6 and optimal untagged scores 1/1/3⁄4/1⁄2 for four targets. Sections 8.1–8.2 distinguish passive recoding from physical rewiring and endpoint recovery from uninterrupted access. These broad themes are already published.

Section 9 and Reference 6 explicitly acknowledge the later omitted-input recovery-budget extension, while declining to republish it as a fresh result. Reference 5 similarly cites AC as an antecedent. The ZIP does not contain the later RB module or a complete live v1.1.x graph. A source citation preserves attribution and discoverability; it does not turn every cited working claim into part of this formal edition.

## 4. Published predecessors that constrain novelty claims

| Source and exact locator | Already covered | Consequence for reuse |
|---|---|---|
| UCT III v1.0 §7.2, Eqs.21–22 | Same storage capacity and identical current outputs can hide scores 1 versus 1/2 after the same readout change. | Unequal usable gain under superficially matched systems is not a new umbrella claim. |
| UCT III §7.3, Proposition 7 | Value of information with no cross-observation decision coupling; explicit warning that constrained policies can invalidate pointwise formulas. | R188 refines an acknowledged architecture constraint, rather than refuting the published proposition. |
| TA25 §5 T1/T2; §6 T3; §8 | Complete/selected-target factorization, abstract versus installed decoding, identical complete sensor law with unsettled attachment, joint-premise and research-direction audits. | These definitions and general nonidentification lessons must be cited as predecessors. |
| TA16 §14.4, §§15–18; Appendix G | Common physical witness; incompatible regimes cannot donate separate maxima; redundancy and intervention-covariant recoding. | The common-organization requirement predates the present increment. |
| TA15 §5.2–5.3; Appendices B–C | Target-fiber criterion and guarded transport composition. | Elementary factorization is inherited mathematics/application infrastructure. |
| TA17 §§4–7 and formal supplement | Joint/set-valued inheritance and insufficiency of independent-successor representation. | Marginal summaries versus joint organization already has a published lineage. |
| TA18 §§3–7 and supplement | Actual token participation versus unrestricted counterfactual capacity; abstraction and symmetry constraints. | A policy family is not automatically actual episode participation. |
| TA24 §§3–9; formal release map | Bundled nonidentifiability, joint payoff information, path-specific supervision and domain limits. | D is TA24, not a new UCT IV; R95–R99/R101 cannot be treated as unfiled discoveries. |
| TA19 main MD §§3–5; supplement S1–S6 | Symmetry/monodromy, probability/set-valued repairs, exact IIT model and robustness records, landscape continuity. | Subject-count and continuity implications retain the stated regularity/model assumptions. |

An artifact-specific caution matters for TA19: the DOI-listed MD, checked against its receipt hash, actually ends in §5’s double-cover example. This is not a retrieval truncation. Its separately deposited supplement includes the IIT parameters, sweeps, 1,000 perturbation sets and further continuity statements. This audit neither discards those formal supplementary disclosures nor claims to have checked the entire published PDF.

## 5. Residual assessment by late result family

The following assessments distinguish an inherited principle from the exact later construction. “Not found” means not found in the inspected core arguments and the three exhaustively inventoried formal packages, subject to the reading scope below. It is not a worldwide priority claim. The machine-readable family rows also identify inherited C1/U1 applications so that they need not remain an undifferentiated unknown bin.

### RB

**Published inheritance.** Finite-field posterior-coset size is H1. KEY_CURVE=2^(k-d) is a direct uniform-linear specialization. Wrong installed reader versus optimal reader, coarser target versus complete reconstruction, complete side-information accounting, and endpoint-versus-interval distinction already have published antecedents.

**Residual object for evaluation.** The general top-K posterior-mass bound and unrestricted-helper sharpness; inverse alphabet/deadline bounds; nonuniform example; TV-prior/mediation robustness; exact delayed-key 5/8 benchmark and timing-transcript control were not found stated in the inspected core arguments or formal ZIPs.

**Attribution limit.** Guessing/leakage bounds, optimal list decoding, data processing and total-variation robustness are classical mathematical antecedents. Exact project synthesis is not a world-first theorem claim.

### OL

**Published inheritance.** Ordinary input-output equivalence does not determine all intervention organization; passive coordinates require transporting real ports/observers; a mathematically available decoder/coordinate map is not an installed mechanism. C1 type transfer and U1/P3 non-erasure are inherited implications with actual grounding still open.

**Residual object for evaluation.** Fixed physical k-port one-write imitation gap, finite-horizon observable projection/pseudoinverse formula, zero-gap support test, calibrated 2-epsilon separation, the matched LTI twin construction and exact squared gap 1/73 were not found as the same operational construction in the inspected published core.

**Attribution limit.** Least-squares projection, observability Gramians, sparse actuation and robust residual tests are established mathematics; the result can be cited as a scoped application/benchmark, not new linear algebra.

### R185

**Published inheritance.** Actual token admission, constitutive support/boundaries and token-relative C1 are inherited. Equal values, memory or reports do not by themselves settle token identity or a unique subject partition. Coherent overlap needs a separately grounded common instance.

**Residual object for evaluation.** Explicit occurrence-versus-token-membership incidence accounting, same occurrence identified through grounded inclusion maps, shared-one-occurrence versus synchronized-two-occurrence countermodel, and synchronizer boundary were not found as this complete diagram in the inspected core.

**Attribution limit.** An incidence formalization and type-safe application synthesis; numerical phenomenal identity across tokens remains OPEN. It is not a new solution to subject individuation.

### HOM/R186

**Published inheritance.** Finite testing and a chosen readout do not establish complete organization; temporal routes and actual intervention semantics matter. Local persistence and phenomenal-existence safeguards are inherited.

**Residual object for evaluation.** For every m, the zero-reset, full-state-trace pair identical for every word of length <=m but separated first by A1,...,Am,C at length m+1 was not found as this construction in the inspected published core.

**Attribution limit.** Finite-state distinguishing sequences, delayed triggers and bounded-observation indistinguishability are classical; the controlled all-short-words witness is the project-level reusable object.

### UI

**Published inheritance.** RT §7 explicitly uses noncommuting adjacent swaps. RT §§4 and 8.1 already establish invariant target readout and passive-coordinate covariance; §8.2 separates terminal access from intervening continuity. Thus general order sensitivity/invariance is not new. Type transfer and local non-erasure are inherited C1/U1 applications.

**Residual object for evaluation.** The fixed sufficient-state product-update obstruction with corresponding physical ports, nonbijective matched one-action bit witness, alpha|1-2eta| noise curve, TV approximation constants, and finite future-readout quotient/separating-word length <=n-c were not found stated together under UI's exact contract in the inspected published core.

**Attribution limit.** Product updates commuting, conjugation invariance, triangle/contraction bounds and deterministic automaton minimization are established mathematics. RT's bijective route example does not by itself deposit UI's nonbijective witness, but it removes the broad noncommutativity novelty claim.

### CM

**Published inheritance.** Target-relative factorization and abstract/installed decoder separation are prior. Good or quiet output does not identify all underlying attachment/organization. C1 type consequence and U1 non-erasure remain inherited conditional applications.

**Residual object for evaluation.** Targeted correction-monitor condition ker H subset ker(KM), monitor-channel rank, bounded-compensator minimax radius, sum/difference matched monitor counterexample, explicit feedback-masking law, and pre-readout independent-probe identities/countercontrol were not found as this compensation experiment in the inspected published core.

**Attribution limit.** Linear factorization, ellipsoid radius, feedback cancellation, instruments and second-moment identities are established methods. Their assembly supplies a calibrated conditional protocol; it does not independently identify bodily mineness or agency.

### R187

**Published inheritance.** TA25 T3 already gives identical complete sensor-update laws with unsettled physical attachment, which entails indistinguishability for the same admitted observations/actions. Bisimulation is classical. Source count, controllable rank and subject count require different grounding; C1 application is inherited.

**Residual object for evaluation.** One source versus synchronized copies with occurrence provenance; the precise selective-write/no-synchronizer protocol, downstream-edge mimic countercontrol, two-sided |delta|/(sqrt2) geometric separation, and iid mismatch/error curve (1-p)^T/2 were not found as this combined physical-multiplicity diagnostic in the inspected core.

**Attribution limit.** All-policy bisimulation, coupling, Le Cam/TV discrimination and Euclidean projections are not new general theorems. A result rejects the stated interface/model class, not every possible common-source architecture.

### R188

**Published inheritance.** Common-witness organization, equal present behavior with unequal gains, attainable versus installed decoding, and interface-relative limits are published. C:P1 type transfer is inherited; actual process/port/timing/source grounding remains OPEN.

**Residual object for evaluation.** Source lacks reader context; L-symbol feedback precedes K-symbol reply; weighted finite-error S*=1-W+Cut_(K^L); K3,3/prism with equal context posterior spectrum and equal isolated ideal scores but 1 versus8/9 global one-bit performance; timely/late feedback comparison and exact checked process reference were not found in the inspected published core or formal packages.

**Attribution limit.** Response words, coloring, independent-coins averaging and weighted cut optimization are classical. The specific exact application/benchmark and source-access caveat are the reusable increment; worldwide priority remains unconfirmed.

## 6. Remaining candidate work and paper scale

The census also finds old work outside the current UCT graph. TA13’s v2 branch has an explicit research-only, reopened pre-manuscript gate; its published predecessor remains v1.0 DOI22866775. The bridge-finance v1.1 branch contains two encoded source fragments, while its formal receipt remains v1.0 DOI22895832. These are **not verified new published editions**. Their scientific residual is **unknown pending manuscript-level argument review**, not zero. The RT duplicate-build reconciliation concerns one already published work and is not a further candidate paper.

For R188, a modest exact benchmark/application note can have a useful citation purpose: future AI can cite the precise source-access condition, weighted finite-error surface, matched-graph witness and timing repair without rederiving them or extending the theorem to an unrestricted helper. The existing corpus does not support announcing the entire common-organization program as a new paper. Mathematical brevity alone is not a reason to reject a contribution; usefulness depends on a clear residual claim, sufficient attribution, a discriminating reusable example, and an exact reproducible record.

This census does not decide the novelty of subsequently developed dynamic AC work. A new result must be compared with the now-pinned static AC, RT, UCT III and other source contracts before being added to the residual count. It must not retroactively change this snapshot’s publication dates or deposit identities.

## 7. Actual reading scope and reuse procedure

Complete exact published Markdown files were retrieved for TA15–19, UCT I v1.2, UCT II v1.1, UCT III v1.0, TA24, TA25, both MGTD editions and RT/TH. TA17/18/19 supplements and TA24’s formal audit were also retrieved. Every such focused file matches a published-file hash in a receipt. This describes file completeness, not a claim that every sentence received a new proof audit.

This subaudit independently inspected the specific locators reported above: in particular UCT III §7.2–7.3, TA25 §§5–6/8, the MGTD worked cycle/retrospective case/appendices, RT/TH’s named theorem arguments and interpretation boundaries, and the full TA19 supplement. Root independently reports full MGTD v1.0.1 and RT/TH reading; root/theory separately inspected the main UCT/TA25 predecessors. Full-file review of TA01–14, fresh full-PDF inspection, global literature priority, and replication of every old experiment are not claimed.

Future reuse should maintain separate fields for **formal disclosure**, **body argument coverage**, **proof/evidence status**, **actual application**, and **historical priority**. A log or map update should update the same coverage ledger: identify the changed claim, cite its best prior formal source, state the precise residual, bind the actual proof/receipt bytes, and retain OPEN premises. A new filename, release counter, clearer exposition, or publication receipt alone does not add a scientific result.

### Audit deliverables

- `novelty_inventory.json`: all 28 research works, every verified edition/deposit, all 44 receipt source identities, full formal-package scope, and family residual/read-scope fields.
- `publication_semantic_coverage.json`: concise publication locators, formal module/paper crosswalks, inherited applications and scoped residuals for integration into the unified claim ledger.
- `attachment_member_manifest.json`: exact members and SHA-256 for all three formal ZIPs; no archived code was executed by this census.
- `all_head_refs.json`, `research_branch_directory_inventory.json`, `research_directory_trees.json`, and `all_research_receipt_candidates.json`: auditable discovery/completeness evidence.

**Remote actions:** read only. No DOI, publishing, OTS, Arweave, messaging, or existing-manuscript mutation was performed.
