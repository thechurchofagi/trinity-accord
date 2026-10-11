# Exact proof — finite public challenges and prechallenge read-policy commitment

## Setup

Let `J` be a finite set of labelled Boolean port assignments `j=(u_j,v_j)` and let `b:J->{0,1}` be any target response. A one-port polarity mode is `(i,a)` with `i in {u,v}` and `a in {0,1}`; on row `j` it returns `x_i(j) XOR a`. A challenge-indexed policy chooses a mode separately for each `j`. A committed cue-blind policy chooses one mode before the independently drawn row and uses it on every row.

## A4Y-T1 — finite public-challenge mimicry

For every finite `J` and every Boolean target `b`, a challenge-indexed one-port polarity policy reproduces `b` exactly on all rows.

**Proof.** For each row choose port `u` and polarity `a_j=b(j) XOR u_j`. Then `u_j XOR a_j=b(j)`. The same construction works with port `v`. Therefore each row has two matching modes, and a labelled suite of `n` distinct rows has `2^n` matching policies among `4^n` policies. For the four A4X rows there are 16 exact mimics among 256. QED.

The construction may leave both live port occurrences and a dual-input monitor unchanged. It changes which occurrence the named consumer uses. Thus apparent lineage/log evidence and output tables do not close A4X `READ_i` or hidden-mode exclusion.

## A4Y-T2 — bounded separation under PBRW

Within `T_1`, if BEFORE, BLIND and BOUND all hold, a one-port policy uses one fixed mode across the full factorial. No such mode equals AND or OR on all four rows.

**Proof.** BEFORE places the policy selection before an independent challenge draw. BLIND removes every admitted post-selection challenge-index path except the named port values. BOUND makes the selected state determine the actual consumer policy rather than a sidecar. Hence a one-port rival in `T_1` is one of the four fixed modes `u`, `not u`, `v`, `not v`. None equals AND or OR on all four rows; direct enumeration verifies zero matches. This is also A4X-T3's projection separation with the polarity complements included. QED.

This theorem excludes only `T_1`. It neither proves the physical premises nor closes a controller that reads both named ports, changes the boundary, forges the witness, or lies outside the declared inventory.

## A4Y-T3 — componentwise drop-one countermodels

Each PBRW clause blocks a distinct exact mimic in the declared evidence model.

1. **Without BEFORE:** let the record be produced after challenge disclosure and bind it to the adaptively selected matching mode. BLIND can hold after this late record, while all four rows are mimicked.
2. **Without BLIND:** before the draw commit a fixed meta-program containing the entire challenge-indexed dispatch table. The record is timely and bound to the consumer, but the later cue selects one of the 16 exact policies.
3. **Without BOUND:** record a timely isolated sidecar state that is blind to the challenge; let the actual consumer use an unbound adaptive dispatcher. The evidence record remains unchanged while the table is mimicked.

The countermodels prove componentwise necessity for this contract's advertised exclusion. They do not prove logical uniqueness among all possible experimental designs.

## A4Y-C1 — no snapshot-only sufficiency

There is no inference from `recorded_state(z)` alone to a challenge-independent consumer read policy in the declared family. T3 supplies three completions of the same generic state-record proposition with adaptive consumer behavior. Therefore an independently recorded state value must be accompanied by time order, cue isolation and consumer binding before it can address A4X-G03.

## Scope

The proof is finite and elementary. It is not a cryptographic security proof, a general theorem of adaptive data analysis, a remote-attestation theorem, a universal account of mechanism identity, a physical installation, complete-signature evidence or a phenomenal result.
