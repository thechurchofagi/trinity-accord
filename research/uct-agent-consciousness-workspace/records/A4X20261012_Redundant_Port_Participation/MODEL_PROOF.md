# Exact proof — contingent port relevance versus universal but-for necessity

## Theorem A4X-T1 — exact classification

For deterministic Boolean `h(u,v)` satisfying `h(0,0)=0` and `h(1,1)=1`, exactly two of the four satisfying functions depend functionally on both ports: AND and OR. The remaining two are the projections to `u` and `v`.

**Proof.** The diagonal constraints fix two table entries and leave `h(0,1),h(1,0)` free, so there are four tables. Enumerating the four free-bit assignments yields AND, projection to `v`, projection to `u`, and OR. Direct comparison of the two rows differing only in `u`, and then only in `v`, gives dual-port dependence exactly for AND and OR. The checker enumerates all sixteen Boolean tables and verifies the classification. QED.

## Corollary A4X-T2 — universal actual-row but-for is too strong

No diagonally correct Boolean consumer has both ports individually but-for necessary at both normal rows.

**Proof.** For AND at `(0,0)`, flipping either one input leaves output `0`; for OR at `(1,1)`, flipping either one input leaves output `1`. Each projection ignores one port at both rows. These four functions exhaust the correct family. QED.

This does not say that AND/OR inputs are actual causes under every general account. It proves only that the proposed universal per-row but-for requirement would wrongly exclude the two declared dual-port mechanisms.

## Theorem A4X-T3 — full-factorial separation from direct one-port projections

No Boolean function of `u` alone or `v` alone equals AND or OR on all four port assignments. When the possible projection port is not known beforehand, both off-diagonal rows are needed to distinguish either dual-port function from both projections.

**Proof.** A `u`-only function must be constant within each fixed-`u` pair; a `v`-only function must be constant within each fixed-`v` pair. AND and OR violate both conditions. AND differs from projection `u` at `(1,0)` and from projection `v` at `(0,1)`; OR differs from them on the opposite respective off-diagonal rows. Thus either single off-diagonal row leaves one projection observationally possible. QED.

## Proposition A4X-P1 — evidence does not back-propagate across a compiler

Suppose a two-port compiler `q(u,v)` sends one occurrence `w` to a one-port consumer `m`. Even if `q` is AND or OR and the final output equals `w`, `m` need not read `u` or `v`. Therefore dual-port dependence of the end-to-end function does not establish `SEPP_i` at `m`; it may establish a candidate at `q` only if the same-event binding, lineage, read, freeze and exclusion clauses are independently grounded.

**Countermodel.** Let `q=AND` and `m(w)=w`. Both routes matter to `q`, while `m` has only one input port. Re-labelling the composite as one box changes the tested boundary and is not an inference about the original `m`. QED.

## Scope

The proof is finite and exact for deterministic Boolean consumers. It does not handle noisy/graded mechanisms, establish physical reachability or intervention fidelity, prove full Halpern–Pearl actual causation, install a complete UCT token, calibrate `B_pc^family/H_cf`, or identify subjects.
