# R137 validation and review scope

7 October 2026. General proofs were reviewed by the same assistant that developed them. This is not independent peer review or proof-assistant certification.

## Completed exact checks

All 12 named checks in check_feedback_interfaces.py passed:

- 6561 three-state binary-row families: common feasibility agrees with all one/two-state tests, as the two-action Helly bound requires.
- 6561 two-state menu-constrained interval comparisons, with explicit incompatible legal-menu and hidden-state oracle examples.
- 501 proper subsets of the sharp obstruction families for m=2,...,8, and 780 rational action mixtures.
- 32 translated joint rows in a genuine controlled hidden-state model.
- 556 exact adaptive feedback path-law comparisons and 2224 approximate comparisons through horizon three. Native actions affect both visible and hidden state; abstract requests select hold versus random-update dynamics.
- Eight horizons for the persistent-seed versus fresh-randomness path-law counterexample.

Arithmetic is exact integer/Fraction arithmetic. No Monte Carlo, numerical optimization, biological data or trained model was used. The general LP characterization and obstruction proof are handwritten; small checks do not certify all finite models.

## Development corrections retained

The first checker execution stopped at a coverage-count assertion written as “more than 1000 rational mixtures.” The specified finite grids actually contain exactly 780. The assertion was corrected to the exact count; no mathematical inequality failed. During this review, interval inputs supplied as integers were explicitly converted to Fraction at entry, so every later division follows the exact arithmetic contract. The final script was rerun successfully. No failed empirical result was discarded.

## Graph and publication identity

All 112 map/source checks passed. Current graph: 328 nodes and 157 rules. All 315 prior nodes and 150 rules remain field-for-field unchanged. Four publication snapshots retain their byte counts, SHA-256 and Git blob identities. The full ledger exports every node/rule field, including all 105 explicit node scope fields; every rule has a review entry.

All seven new mathematical results are independent of C1. Existing R135 experiential interpretation retains its actual-support/common-signature premise. C1/U1 and the published paper bytes are unchanged.

## Manual premise audit

- Decoder information is the supplied visible alpha(s) and requested u, not the hidden concrete state. One common distribution is used over every state in a visible fiber.
- Physical Markov state includes persistent mechanism/memory/resources where relevant. A persistent random seed cannot be omitted and then replaced by a fresh conditional action law.
- The joint next-visible-state/output row is matched. Matching marginals alone is not claimed sufficient.
- Decoder weights vanish on every incompatible state's illegal actions. Allowing TV error does not relax legality.
- The abstract policy has a legal extension to every projected history, including nominally impossible histories reached after approximation mismatch.
- Exact completeness concerns the declared memoryless randomized action-decoder class and all represented start states. Arbitrary history-dependent, diagnostic and multi-step refinement remain outside this theorem.
- The Helly argument uses dimension m-1 of a fixed m-action simplex; its finite state witness is not a finite empirical sample certificate.
- Projected payoffs omit hidden action/cost quantities unless these have explicitly been included in the comparison.

## Reading, attribution and remaining scope

Pinned A's identity/type-equivalence clauses, B §2/§2.1, C §5.2/§5.3, D §4, R132 closure and R135–R136 interface limits were checked. Reissig/Weber/Rungger's primary feedback-refinement preprint was read at its introduction, definitions and controller-refinement theorem/proof passages. Khaled/Zhang/Zamani and Nadali/Trivedi/Zamani abstracts identify direct output-feedback and stochastic-transfer prior art; their full technical comparison is still open.

Feedback refinement, Helly/Radon geometry and TV coupling are standard. The opposite-action witness is reused from R134 with explicit attribution. No historical priority, algorithmic superiority or new UCT constitutive theorem is claimed.

No experiment, model training, DOI, release, PR or CI action was initiated. T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN. Next target: explicitly observable finite-memory interfaces. Remote save verification is recorded separately in the deliverable's save receipt.
