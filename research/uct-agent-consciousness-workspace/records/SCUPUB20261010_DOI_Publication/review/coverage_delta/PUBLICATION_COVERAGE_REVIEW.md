# Bounded review of UCT-PUB-v1.0.21

**Final decision: required corrections verified and closed; bounded coverage review complete.** The initial delta assigned the stable historical IDs R204-C2 and R204-C3 the wrong content and body locations. The root corrected both, narrowed C3, clarified R205:C2, retained the partial R205:C4 status, and explicitly separated frozen-base counts from the SCU increment. I checked those final edits against delta SHA-256 `e3c76a81c2a5779014038e0806f78b416f25ac45d11d8441dabf55a08a7903c8`. The discussion below preserves the initial findings and their rationale. No change to the frozen SCU publication was required. This is a disclosure review, not a new proof review, map promotion, or worldwide publication census.

## Evidence and read scope

I directly inspected the actual released `matched-behavior-and-source-use-v1.0.1.md` and the contents of `reproducibility-v1.0.1.zip` under `records/SCUPUB20261010_DOI_Publication/release/`. In this bounded pass, the fresh body reading covered §§2–7.4 and the later interpretation, coverage, and reference discussion; the provenance paragraph in §8 was separately inspected. I read all eight published SCU claim records, the published R204 and R205 source code and exact result files, the original R204 research note, and the original R205 claim ledger. The three correction overlays were read and compared to the coverage rows at the field level.

The exact input hashes and checks are saved in [REVIEW_RECEIPT.json](REVIEW_RECEIPT.json). The release ZIP contains **41 members**. The coverage delta contains **42 distinct IDs**, comprising eight SCU claims, five R204 claims, five R205 claims, sixteen correction records, and eight later DVC claims/evidence entries. All 42 new index pointers and coverage statuses agree with the inspected delta. No release artifact was modified and no scientific code was rerun during this bounded review.

## Required corrections: historical R204 IDs

The original R204 note explicitly labels §3 as **R204-C1: separation and a successful-output quartet**, §4 as **R204-C2: a probe with an explicit failure condition**, and §5 as **R204-C3: port covariance and gradual organization**. These source labels control the identity of the claims.

| Claim | Current discrepancy | Required effective location and limit |
|---|---|---|
| R204-C1 | Its existing location is correct but describes only the separation portion. | Published §3.1 includes the successful-output quartet as well. Adding that phrase improves traceability. |
| R204-C2 | The delta assigns the successful-output quartet, which belongs to C1. | Published §3.2: natural/null-update ambiguity and the forced-mismatch inference with joint port, writer, exclusivity, and carrier-readout premises. |
| R204-C3 | The delta assigns forced mismatch, which belongs to C2. | Finite covariance/mixture witnesses are in the published R204 code/results; §7.4 is general transport background and §8 reports the inherited check counts. Use a partial-body-plus-executable-witness status. |

The published R204 code checks **333,088** input/output-port relabelings for mismatch/alignment invariance using permutations on domains of size 2, 3, and 4. It also checks **6,776** exact rational mixtures under uniform action weighting and eleven values of λ, from 0 to 1 in steps of 1/10. The general historical claim additionally discusses transported controllers and success, nonuniform support weights, and the formula for every real λ in [0,1]. Those larger narrative scopes must not be credited solely because a related finite executable family was published. The SCU body reports the counts but does not reproduce the full historical covariance/mixture derivation.

Suggested replacements are provided in [PROPOSED_LOCATION_CORRECTIONS.json](PROPOSED_LOCATION_CORRECTIONS.json). This finding corrects my preliminary message that the R204 locations were sound; that preliminary judgment preceded comparison with the original stable source IDs.

R204-C4's guarded UCT interpretation is located in §§2 and 9, and R204-C5's all-sequence comparator/reflex state equivalence is explicitly developed in §3.3. Neither location establishes actual H, human consumer identity, or an empirical instantiation.

## SCU and R205 coverage

All **eight SCU statements and scope arrays match the published claim ledger exactly**. Their coverage status deliberately permits the formal supplement to carry parts not fully narrated in the body. The disclosed scope retains pure versus nonempty-OR domains, unknown versus independently known source identity, deterministic intervention schedules, internal targeting assumptions, chronology, and guarded same-instance UCT interpretation. Formal disclosure does not discharge those premises or promote the disabled candidate map.

The five R205 rows distinguish inherited workspace work from this turn's increment. The original two-probe recovery implementation is disclosed in `reproduction/baseline_R205/exact_probe.py` and its results; the current C2 row now names those files. The published code covers 608 single-read installations on domain sizes 2–5. Main §§4–5 give the broader pure-selector framework, rather than an identical full narrative of the historical two-probe table.

**R205:C4 is correctly limited to `PARTIAL_BODY_PLUS_EXECUTABLE_WITNESS_NOT_FULL_NARRATIVE_PROOF`.** Section 7.4 supplies general transport discussion; the attached code records 38,224 compensated-recoding episodes on sizes 2–4. The complete historical claim should not be treated as fully narrated in the article. C1's source-locality/coherence square, C3's cancellation construction, and C5's guarded interpretation have their stated body locations. None of these records equates matched behavior, recoding, consumption, agency, ownership, or familiar self-feeling.

## Published correction overlays

The ZIP contains the R194, R201, and R202 effective correction overlays and their associated evidence. **All sixteen coverage records match their published overlay replacement fields or node/rule statements.** Every inspected historical-record hash agrees with the overlay's expected-original hash. The fields preserving history, disabling scientific promotion, and excluding these repairs from the paper's principal contribution are appropriate.

This verifies exact disclosure of the correction objects. It does not newly certify all historical proofs or mark each original historical record as wholly published. The root must preserve the overlays as non-destructive effective corrections.

## Inventory counts and remaining boundaries

The ledger and inventory count fields agree: **29 research works, 39 work/version-label pairs, 40 research DOI records, and one separate editorial DOI**, yielding 41 publication DOI records including that editorial. Their `incremental_audit_scope` explicitly describes a frozen previously verified census plus the separately verified SCU publication. That is the correct interpretation; I did not freshly inspect all account drafts or enumerate worldwide records.

The initial inherited counting-decision sentence explained the **28-work base** without explicitly marking its provenance. The root has now prefixed the inherited decisions as frozen v1.0.0 provenance and added the SCU arithmetic: 28+1 works, 38+1 version-label pairs, 39+1 research DOI records, and one separate editorial DOI. Both final count explanations were checked. The duplicate DOI/version and separate editorial distinctions remain useful. The eight DVC entries correctly avoid retroactively importing this later research into the frozen SCU paper. Their noncoverage status is specific to this published version, not a claim about every possible venue or private draft.

**Closeout verified:** the two R204 ID/location corrections and C3 scope limit are present; R205:C4 remains partial; the incremental-census qualification is explicit; all 42 final index pointers and coverage statuses agree. The receipt retains initial input hashes and appends the final verification separately. No additional scientific experiment or alteration of the released paper is required by this review.
