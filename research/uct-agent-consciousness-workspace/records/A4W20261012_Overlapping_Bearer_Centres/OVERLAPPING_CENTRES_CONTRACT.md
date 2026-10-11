# Overlapping bearer-centres contract

Version: `A4W-OCF-v0.1.0`  
Status: disabled application contract; no actual physical installation or phenomenal calibration.

## 1. Fixed binding

Fix one admitted candidate process `P`, interval `I`, complete-signature obligation `K`, event `e`, target activity `tau`, target coordinate `x`, two current live bearer anchors `a_1,a_2`, route occurrences `r_1,r_2`, local consumers `c_1,c_2`, and a downstream consumer `m`. The two routes may share `P,I,e,tau` and `m`; they need not be disjoint. Numerical equality of anchor values, route values, outputs, labels, or logs does not identify these occurrences or their live bindings.

## 2. Concurrent bearer-centre family

Define the disabled relation

```text
ConcurrentBCR2(P,I,K,e,tau;a1,r1,c1;a2,r2,c2) :=
  SAME-BINDING
  AND BCR(P,I,K,e,tau;a1,r1,c1)
  AND BCR(P,I,K,e,tau;a2,r2,c2)
  AND SIMULTANEOUS
  AND DISTINCT-LIVE-ROLES.
```

Each `BCR` expands to A4V's eight simultaneous premises:

```text
BIND AND ANCHOR AND ENCODE AND USE
AND A-CONTRAST AND R-CONTRAST AND JOINT AND ORDER.
```

`DISTINCT-LIVE-ROLES` distinguishes the two bound anchor/route occurrences. It does not require distinct values, disjoint substrates, anatomical membership, or distinct subjects. `SIMULTANEOUS` requires both local routes to exist and be consumed in the same declared event window; merely having two available schemas is insufficient.

## 3. Target-indexed participation, not an owner selector

`ConcurrentBCR2` alone says that two local bearer-centred relations coexist. It does **not** entail that both organize the downstream target `tau`. For that stronger statement define a non-exclusive actual-use predicate:

```text
Participates_tau(r_i,m,e) := m actually reads/uses the occurrence descending
from r_i in forming or sustaining tau during e.

JointlyCentred_tau := ConcurrentBCR2
  AND Participates_tau(r_1,m,e)
  AND Participates_tau(r_2,m,e).
```

`Participates_tau` may hold for zero, one, or multiple routes. It is not a function from a target to one owner and is not a subject selector. A projection merger supplies the counterexample to inferring both participations from two local BCRs. A direct bypass supplies the counterexample to inferring either participation from correct output.

## 4. Exact finite witness

For `x,a,b in {0,1}` let

```text
r_1 = x XOR a,   u = r_1 XOR a = x,
r_2 = x XOR b,   v = r_2 XOR b = x,
z = h(u,v).
```

Both local routes meet the A4V contrast and joint-compensation pattern. Their partial overlap consists of a common target, event, organization, and downstream consumer; their live anchors and route occurrences remain typed separately.

Among all 16 Boolean mergers `h`, normal operation reaches only `(u,v)=(0,0)` and `(1,1)`. Exactly four mergers satisfy `z=x` on every `x,a,b`: projection to `u`, projection to `v`, AND, and OR. The two projections implement one-route target participation; AND and OR are symmetric two-input mergers. Hence correct normal output neither requires an exclusive selector nor identifies joint participation. Off-manifold branch challenges `(0,1)` and `(1,0)`, together with an independently grounded consumer mechanism, are required to discriminate them.

## 5. Conditional UCT placement

If every conjunct is independently grounded in one complete actual `K` organization, C1 plus R157 transports both local BCR relations and any grounded `Participates_tau` relations to experience-internal structural counterparts. Ordinary first-order relation transport is pointwise and does not become inconsistent when the selected set has two members.

The open bridge `B_pc^family` interprets the transported family as multiple practical bearer-relative coordinates available within one experience. The stronger interpretation that one selected activity is *jointly organized from both coordinates* additionally requires both non-exclusive participation relations. Neither claim determines a unique subject count, an exclusive owner, `H_cf`, agency, ownership, conceptual self, or report.

## 6. Stop conditions

Stop before a phenomenal or actual-installation claim if any of the following is absent: one actual `P/I/K/e` binding, two live anchors, actual local consumption, the relevant downstream participation relation, an independently fixed phenomenal target, or a separate fallible measurement bridge. Code success and diagonal output equality discharge none of these obligations.
