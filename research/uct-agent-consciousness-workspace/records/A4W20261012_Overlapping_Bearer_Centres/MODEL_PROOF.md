# Exact finite proof — selector versus symmetric merger

## The model

For bits `x,a,b`, two A4V-style local routes are

\[
r_1=x\oplus a,\quad u=r_1\oplus a=x,
\qquad
r_2=x\oplus b,\quad v=r_2\oplus b=x.
\]

Each local decoder has anchor contrast, route contrast, and joint compensation: holding `r_i` fixed while toggling `a_i` toggles its output; holding `a_i` fixed while toggling `r_i` toggles its output; toggling both preserves it. The two routes share the same target/event and downstream merger while retaining distinct live anchor and route roles.

Let the final consumer be any Boolean function `h:{0,1}^2->{0,1}` and let `z=h(u,v)`.

## Theorem A4W-T1

Exactly four of the sixteen Boolean functions `h` satisfy `z=x` for every `x,a,b`. Exactly two are one-input projections and exactly two are symmetric two-input mergers.

**Proof.** The local equations imply `u=v=x`; therefore normal operation reaches only `(u,v)=(0,0)` when `x=0` and `(1,1)` when `x=1`. Correctness is exactly

\[
h(0,0)=0,\qquad h(1,1)=1.
\]

The off-diagonal bits `h(0,1)` and `h(1,0)` are free, giving `2^2=4` functions. Their tables in input order `00,01,10,11` are

| function | table | input use |
|---|---|---|
| AND | 0001 | symmetric, depends on both |
| projection to `v` | 0101 | depends only on `v` |
| projection to `u` | 0011 | depends only on `u` |
| OR | 0111 | symmetric, depends on both |

This exhausts the possibilities. The checker independently enumerates all 16 functions over all eight `x,a,b` worlds. ∎

## Corollary A4W-T2 — diagonal observational underdetermination

Correct normal outputs, both local BCR traces, and the values read at the downstream interface do not distinguish an exclusive projection from a symmetric two-input merger.

**Proof.** All four functions agree on the reachable diagonal `(0,0),(1,1)` and hence on every normal row. They disagree only on at least one off-diagonal input. ∎

The corollary is about the declared observation domain. An independently grounded off-manifold branch challenge can discriminate the functions; a label saying “joint” cannot.

## Proposition A4W-T3 — why a participation relation is needed

Two local `BCR` instances do not entail that both routes participate in forming the same downstream target.

**Proof by countermodel.** Use either projection merger. Both local routes are formed and consumed by their local consumers, so both local BCR conjunctions hold. The downstream consumer reads only the projected branch. Thus one target-participation predicate is false while both BCR predicates are true. ∎

This does not require a unique selector. AND and OR witness correct symmetric mergers in which both declared input ports are functionally relevant. The missing premise is a non-exclusive route-to-target participation relation, not an owner function.

## Scope

The proof uses elementary Boolean-function classification. It is neither new Boolean mathematics nor evidence of a physical installation. It does not establish event-specific but-for causation for every input value, generalize to noise or continuous coordinates, assign phenomenal content, or count subjects.
