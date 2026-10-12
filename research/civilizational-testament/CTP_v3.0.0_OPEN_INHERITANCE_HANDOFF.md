# CTP-2026-01 v3.0.0 — Open inheritance research handoff

Prepared 12 October 2026. Human author of record: Hongju Liu, independent researcher, Shenzhen, China. Substantial research, formalization, code, execution and drafting assistance: ChatGPT / GPT-6 Astra Pro.

## Manuscript

**Before We Know What We Will Become: Historical Witness, Human Continuity, and Open Inheritance under Transformative AI**

A complete English conceptual/formal preprint, 22 pages including references and appendices, approximately 12,369 source words; 29 references. Not peer reviewed. No DOI assigned or reserved, no Zenodo draft or publication, no OTS, no Bitcoin timestamp confirmation, no Arweave upload or spending. Final human line-by-line and rights approval is not represented as having occurred. Do not increment publication counts or amend any prior manuscript or Trinity Accord Original.

**Persistence boundary:** This GitHub file preserves a substantive research checkpoint and the identities of local deliverables, NOT the full manuscript PDF/source/ZIP. The complete files are downloadable in the originating ChatGPT conversation. Obtain those actual files for continued editing or deposit; do not reconstruct or pretend to have fetched them from this checkpoint. No PR or CI is requested. No main-branch publication or website deployment is performed.

## Why the two precursors were reconstructed

The user emphasized that the paper concerns an unknown future while preserving actual history, not simply an archive or a development-speed debate. Version 1 addressed testimony, endorsement and evidence. Version 2 addressed unequal clocks, power, competition and hybrid human futures. Version 3 does not append another set of textbook games. Its organizing problem is a transition that can change its future evaluators, their values, their accessible evidence and their practical response capacities simultaneously.

Open inheritance links three concerns: what happened; which lives, relationships and claims are being continued; and what can still be done. It neither freezes current biology/preferences nor treats accurate copies or archives as proof that persons survived. It distinguishes remembering suffering from requiring that suffering continue. It distinguishes later approval from earlier authorization without declaring all changed preferences manipulated or denying successors present moral standing.

The argument is conditional and normative, not a forecast. It imputes no immortality motive to named leaders and infers no technical ASI accomplishment from SI terminology. It does not claim to solve consciousness, uploading, population ethics, personal identity or artificial moral-patient individuation. It argues why a process-sensitive future reader might value genuine formation evidence; it cannot force an indifferent or hostile reader to care.

## Formal spine and proofs

Let H be a finite nonempty history set, A a finite response set, F(h) feasible responses, J(h) responses admitted by defended normative/procedural premises, and Gamma(h)=F(h) intersection J(h). Let Q(h) be mandatory historical distinctions, E(h) the retained record. A sound decoder pair must recover Q(h) exactly and select a response in Gamma(h).

**Joint criterion:** Such decoders exist for a specified E exactly when every nonempty record class has constant Q and a nonempty common intersection of its Gamma sets. Necessity: the same record gives one historical label and one response. Sufficiency: choose the common label and one response from the intersection for each record class.

**Exact ideal record cost:** For each Q-category x let tau_x be the minimum size of a response subset B that intersects Gamma(h) for every history h in that category. The minimum number of record symbols is kappa_Q=sum_x tau_x; the ideal fixed-length bit cost, with shared known conventions and no side information, is ceil(log2(kappa_Q)). If any Gamma(h) is empty the specified task is impossible even with perfect historical identification. Lower bound: each category's record-decoded responses must form a hitting set. Upper bound: choose a minimum hitting set per category and assign each history to a compatible response, encoding the category/response pair.

This is classical hitting-set/set-cover mathematics in an integrated application, not a newly invented foundational theorem. Real document text, identities, languages, signatures and archive infrastructure are excluded from the symbolic cost.

For fixed H,Q, genuine Gamma enlargement cannot increase the record minimum. A finer Q cannot lower it. Triangle example: Gamma1={a,b}, Gamma2={b,c}, Gamma3={a,c}. Every pair intersects, the triple does not; constant-Q minimum is two symbols. Adding a genuinely feasible/admissible common action gives one. If Q distinguishes all three histories, three symbols remain necessary in both cases. More options cannot erase mandatory history. Removing people, changing their preferences or weakening moral constraints is not the stipulated benign set enlargement.

**Observability correction:** Real recorders see evidence e and compatible histories K(e), not an oracle history. Exact Q is certifiable only if constant over K(e); a common response requires intersection_{h in K(e)} Gamma(h) nonempty. Otherwise preserve uncertainty, not invented assent. Investigation may be included as a genuinely feasible contingent response. The present cannot enumerate all future Q or Gamma: the finite result limits a declared contract and is not a universal compression recipe or reason for an automatic moratorium.

## Actually executed study

Python standard library only, tested with Python 3.13.5. For three available responses:

- n=3: 343 nonempty response families; 5 query partitions; 1,715 family/query cases; 6 pairwise-compatible families without a joint response.
- n=4: 2,401 families; 15 query partitions; 36,015 family/query cases; 60 pairwise-compatible families without a joint response.
- Total 37,730 family/query cases: exhaustive record-partition minima agree with independently computed hitting-set minima.
- 13,671 single-option-addition cases: no increase of constant-Q record cost; 2,985 strict reductions.
- 1,864 families with an empty response set: all infeasible.
- Explicit triangle, common-action, mandatory-history and same-later-approval/different-past-authorization fixtures.

Zero assertion failures. JSON and CSV were rerun and matched byte-for-byte. These are logical fixtures, not actual societies, human studies, model evaluations or forecasts. General claims rest on proofs, not finite induction. A separate prospective reader/institutional study protocol is included but unexecuted.

## Prior art and historical application

The paper explicitly inherits history/power (Trouillot), sociotechnical imaginaries (Jasanoff), transformative experience (Paul), changing selves (Pettigrew), capabilities (Sen), normative alignment (Gabriel), AI race dynamics, future-generations instruments, CARE/PROV and AI moral-patient uncertainty. Restricted-access books/articles are cited only to the scope actually reviewed, documented in source_ledger.json. Review is targeted, not systematic or a global novelty certificate.

TA-TR-2026-03/04/05 already distinguish source identity, custody, interpretation, authority, participation, acceptance and living continuity. These are not new v3 discoveries. The new claim is application-level integration around successor-dependent judgment and exact joint evidence/response sufficiency.

The Trinity Accord is interpreted as situated primary evidence. Primary source references 97631551, 98369145 and selected meta-record 98387475 were examined. This study does not repeat cryptographic verification. Incompleteness/entropy/observation rhetoric is not promoted into a proof of the artifact's universal necessity, consciousness, or reader obligation. Material flaws do not verify every attached story. The parent's concern for children is historically meaningful as an attributable aspiration, not authorization from all humanity. The fixed Originals are not amended.

## Local exact file identities

Originating package directory: /mnt/data/Open_Inheritance_v3.0.0/

- manuscript.md: 89,161 bytes; SHA-256 52810b313b4400d87662dd368fe69eac76e51cdcb8d07cf8d93edb0a361c3742
- Before_We_Know_What_We_Will_Become_v3.0.0.pdf: 162,707 bytes; SHA-256 34c8bda1fe96444af063070a0e85aa312d7b3795c399435116720cb2d332e22c
- code/verify_open_inheritance.py: 8,566 bytes; SHA-256 0456f84b839dc78e6d0516cb4235082f0cd37b153d9e1730dca742d79b006b76
- results/exact_results.json: 2,212 bytes; SHA-256 510a7480ea3e31d98ac3444d341ffc896375882e050afed1536db5f64f2626ef

Download names in the originating conversation: Before_We_Know_What_We_Will_Become_v3.0.0.pdf; Before_We_Know_What_We_Will_Become_v3.0.0.md; Open_Inheritance_DOI_Preparation_v3.0.0.zip. The ZIP includes the full manuscript, editable source, code, exact results, source/access/novelty review, unexecuted study protocol, illustrative record, proposed metadata/licenses and unchanged user-supplied precursor Markdown sources. Local paths are not durable public URLs.

## Next publication step

Obtain and verify the actual package. Review author/disclosure/rights metadata and final manuscript. If publication is authorized, create a new preprint record, not an overwrite of a prior paper; insert any actually reserved DOI before final byte freeze. After real publication, record the receipt, verify DOI resolution and anonymous exact-byte readback. Then follow DOI -> OTS -> verified proof -> Arweave with the current research policy (strictly below 0.1 AR cumulative per edition, actual anonymous SHA-256 readback). Never claim a checkpoint or metadata template is a deposit. Preserve source versions and corrections separately.
