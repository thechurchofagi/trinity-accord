# R134 validation and limits

## Executed exact mathematics

`python3 check_quantitative_control.py` passed all 14 named checks, using Python Fraction throughout, without sampling, floating-point LP thresholds, training or neural/biological data.

- All 2025 binary families with signal probabilities on the five-point quarter grid and four conditional survival probabilities in {0,1/2,1} were checked. Primal attainable-hull calculations agree with an independent dual line-envelope calculation and the diagnostic sum-of-maxima formula. The opportunity-weighted upper bound holds; the optional-probe convex union never loses its available blind baseline.
- The asymmetric closed forms were checked at 22 distinct rational survival levels, including the 2/3 threshold and 7/10 witness. Probe weight 20/27 and dual weight 13/27 both certify exactly 14/27. The forced-probe optimum is 7/15.
- 144 dynamic cases compare all exact pure-policy vectors from direct evaluation against the continuation-profile recursion: two signal laws, four survival probabilities, six initial supports and horizons 0–2. Horizon two has 193 observable policy trees including early stopping. Eight root dynamic models also agree with independently built probe-decision hulls.
- Equal TV with different robust accuracy, same-support useful signals, and the distinction between coordinatewise maxima and attainable mixtures were checked explicitly.

The 2D primal routine examines vertices and segment crossings of the diagonal; the dual independently minimizes the upper envelope of affine model-weighted values. Both return rational values. These are small bounded checks, not proofs for arbitrary model families.

## Graph and source checks

`python3 validate_formal_map.py`: 112 checks passed. Current graph: 290 nodes and 135 rules. Every one of the 276 earlier nodes and 127 earlier rules is retained field-for-field; all four pinned source byte counts, SHA-256 hashes and Git blob identities match. All 67 explicit scope fields are present in the readable proof ledger. Prior C1/U1 separation, source-fidelity and forbidden-inference checks remain in force.

## Manual proof review

| Question | Resolution |
|---|---|
| Does the same policy generate every model coordinate? | Yes; pure trees are shared, mixed-tree weights are independent of the hidden model |
| Is the hidden model persistent during backups? | Yes; kernel entries between different model labels are zero |
| Does the controller get a hidden model or free menu oracle? | No; actions must be common-enabled on the exact observation support |
| Does a support-indexed vector set imply a support-only policy? | No; this distinction and a strict same-support example are explicit |
| Can nature see the private coin before selecting a model? | No; changing this order changes the game and invalidates the mixing guarantee |
| Does TV alone give the robust value? | No; it gives the stated equal-weight bound, with symmetric equality and asymmetric strictness |
| Does optional probing equal the maximum of two separately optimized robust scores? | Not generally; the 14/27 example is a strict counterexample |
| Does opportunity survival represent every kind of cost? | No; it is a specified probability of completing this task; additive utility costs need a different model |
| Is this new control theory or a UCT-specific constitutive theorem? | Neither is established; direct prior art and unresolved UCT-specific contribution are recorded |

This is a manual review by the same assistant, not independent peer review or proof-assistant certification. General validity rests on the stated finite-domain proofs. No failed check was discarded. Full-text retrieval of the recent hidden-model paper was blocked; its abstract was read, and a full technical comparison remains open. Earlier Takahashi reading scope remains unchanged.

T2 OPEN, C3 intervention transport NOT_TESTED, valence OPEN. Storage verification appears separately in the downloadable package save receipt after remote commit creation.
