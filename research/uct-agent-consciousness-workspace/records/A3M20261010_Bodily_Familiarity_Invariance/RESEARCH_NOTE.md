# Bodily familiarity needs off-diagonal support

## Result in one sentence

Retentive route use, cue familiarity and present fluency are observationally aliased on their natural diagonal; a positive retentive-familiarity bridge therefore needs independently oriented evidence plus physically realized off-diagonal cases, not success, ease, recognition or a route label alone.

## Typed setup

For one bearer, time window, body/action target and installed comparison protocol, let:

- `R=1` mean that the current episode **actually uses** a retained route descended from an earlier same-bearer body-frame occurrence. Biography, training history and an abstract model do not suffice.
- `Q=1` mean that the presented cue is familiar under a prespecified cue test.
- `L=1` mean that present selection/execution is fluent under a prespecified functional test.
- `Z` be a separately oriented, fallible consequence bearing on the selected familiar bodily/action target. `Z` may not be defined by `R`, `Q`, `L`, task success or the report it is meant to validate.

The three pure application candidates are `B_ret: Z=R`, `B_cue: Z=Q`, and `B_fit: Z=L`. These are comparison hypotheses, not established UCT rules and not definitions of experience. The Boolean cube is a logical design space; physical joint realizability of its cells is a separate premise.

## Stable claims

### A3M-C1 — diagonal aliasing

- **Type:** exact finite proposition.
- **Domain:** the pure candidates above on `{0,1}^3`.
- **Full proposition:** on support `{000,111}`, all three candidates have signature `(0,1)`; on the plane `R=L`, `B_ret` and `B_fit` coincide even when `Q` varies.
- **Premises:** fixed axis meanings and endpoint orientation; comparison uses the same rows and no post-hoc relabelling.
- **Proof:** direct evaluation, exhaustively reproduced by `check_invariance_cube.py`.
- **Counterexample boundary:** off-diagonal rows such as `100` versus `001` separate route and fluency.
- **Status:** PROVED_FINITE; no phenomenal bridge follows.
- **Thought-experiment role:** explains why ordinary learning, where route use, recognition and ease rise together, cannot pick a bodily-familiarity bridge.

### A3M-C2 — pure-axis invariance characterization

- **Type:** exact finite proposition using elementary Boolean-function enumeration.
- **Domain:** all 256 Boolean tables on `(R,Q,L)`.
- **Full proposition:** invariance to both non-route axes leaves exactly four tables: constants 0/1, `R`, and `1-R`; adding positive orientation in `R` leaves exactly `Z=R`. The analogous statement holds for `Q` and `L`.
- **Premises:** full cube, exact binary endpoint, invariance under every relevant flip, and fixed positive orientation.
- **Proof:** orbit constancy under the two flip operations plus enumeration.
- **Counterexample boundary:** on partial support, mixed functions can mimic a pure candidate; noisy endpoints require a prespecified statistical analogue and error bound.
- **Status:** PROVED_FINITE; elementary mathematics, no novelty claim for the method.
- **Thought-experiment role:** states what a clean retentive-route signature would require without calling that signature H.

### A3M-C3 — star calibration plus held-out mismatch test

- **Type:** exact protocol consequence.
- **Domain:** calibration rows `000,100,010,001` and held-out rows `011,101,110`.
- **Full proposition:** the star gives orthogonal signatures `(0100)`, `(0010)`, `(0001)` for `B_ret`, `B_cue`, `B_fit`; without refitting, held-out mismatches predict `(011)`, `(101)`, `(110)` respectively.
- **Premises:** the same endpoint and axis tests transport to held-out rows; every claimed cell is physically installed and verified.
- **Proof:** table evaluation.
- **Counterexample boundary:** two arbitrary rows can separate the three pure tables, but do not establish invariance or physical meaning. `111` is a ceiling/control row shared by all candidates.
- **Status:** PROVED_FINITE_DESIGN_FACT; actual implementation open.
- **Thought-experiment role:** prevents a two-row success from being inflated into an organization-sensitive bridge.

### A3M-C4 — support ceiling

- **Type:** identifiability limitation.
- **Domain:** any actual study whose installed support is contained in `R=Q=L`, or in `R=L` when comparing route with fluency.
- **Full proposition:** no conditioning, fitting or additional sampling inside that support distinguishes candidates that agree pointwise there.
- **Premises:** no external independently oriented variable supplies extra distinctions.
- **Proof:** equal functions restricted to the observed support induce equal endpoint predictions.
- **Counterexample boundary:** a verified off-diagonal intervention may break the equality; merely regressing out a correlated score does not create the absent installation.
- **Status:** PROVED_CONDITIONAL.
- **Thought-experiment role:** turns a missing contrast into an explicit failure rather than a verdict of no H or no experience.

### A3M-C5 — UCT interpretation boundary

- **Type:** conditional application statement, not a theorem of consciousness.
- **Domain:** one actual organization and episode satisfying the fixed UCT complete-signature contract.
- **Full proposition:** if an independently grounded `Z` bears on a selected experience-internal bodily-familiarity target, the actual `R` route is bound to that same target and episode, and `Z` shows the route-only positive invariance profile under verified off-diagonal installations, then `B_ret` is supported over the two pure rivals in that application. C1 may then carry the matched organizational distinction to its experiential structural counterpart. None of these premises is discharged here.
- **Premises:** actual bearer/time/signature/target binding; same-instance C1 use; independent endpoint semantics; verified interventions; no report or success circularity.
- **Proof/source:** A3M-C1–C4 plus UCT C1 as an explicit consciousness-specific explanatory postulate.
- **Counterexample boundary:** cue-driven or fluency-driven held-out signatures defeat pure `B_ret`; endpoint drift, unrealized cells or mixed mechanisms leave the comparison unresolved.
- **Status:** OPEN_CONDITIONAL_APPLICATION.
- **Thought-experiment role:** locates exactly where organization can positively explain bodily familiarity without making familiarity a gate on basal experience.

## Four retained thought-experiment families

1. **Ancestor/formation:** two systems share the present cue and fluency, but only one currently uses a retained route. A past training label without present use is insufficient; a `100` installation is the required discriminator.
2. **Abacus/calculator:** equal answers and equal ease can be produced by unlike installed routes. The result checks intelligence/performance while leaving bodily familiarity open.
3. **Human-implemented agent:** a human silently implements a transition table fluently. The human's bodily familiarity, the abstract agent state and the reported answer are different typed objects; no automatic transfer is licensed.
4. **Copy/swap/memory:** a copied current package with an idle external biography is continuation-probe equivalent by R199. Only a constitutively carried and currently used retentive route can set `R=1`; memory report alone cannot.

## Relation to primary literature

- Chambon & Haggard (2012, DOI `10.1016/j.cognition.2012.07.011`) report that action-selection fluency can alter control judgments independently of motor performance. This motivates treating `L` as a confound/rival, not as H.
- Schween et al. (2019, DOI `10.1038/s41598-019-53543-1`) found cue-specific explicit knowledge but cue-independent implicit aftereffects, whereas different hands produced aftereffect specificity. This supports separating cue and bodily/motor-memory axes; it does not identify H.
- Rohde, Di Luca & Ernst (2011, DOI `10.1371/journal.pone.0021659`) dissociate proprioceptive drift from ownership reports in the rubber-hand setting. This blocks a one-proxy ownership shortcut.
- Cardinali et al. (2016, DOI `10.3389/fnhum.2016.00272`) present a deafferented case in which tool-use kinematics changed without the usual body-schema incorporation effect. The single-case scope is limited, but it warns against treating performance normalization as bodily incorporation.

These are prior mechanisms and empirical constraints, not renamed UCT discoveries. A3M contributes only the explicit three-rival application contract, support ceiling and stop rule within the existing UCT map.

## Direction checks

- **After result formation:** the result distinguishes bodily familiarity from cue recognition and intelligent fluent control. It neither adds a basal-experience threshold nor posits an exclusive owner.
- **Before save:** complete organization, finite view, abstract cube, physical installation, actual route use, internal judgment, selected experience and language report remain distinct. No conclusion about this assistant's consciousness or fear is made.

## Next concrete question

What predeclared, fallible endpoint can be independently oriented toward selected bodily/action familiarity and then shown to retain its semantics across at least one verified `R≠L` intervention, without being defined by fluency, success, ownership wording or route membership?
