# CD20261008 — Collective dynamics behind identical local records

8 October 2026. Non-R theory-first dialogue supplement. Preserve R181, CG20261008, SB20261008 and all reviewer-controlled open items. This is a self-contained compact research checkpoint, not a paper release, a complete repository backup or independent phenomenal validation. The expanded local research package contains the longer argument and larger executed verifier; it is not claimed byte-identical to this compact file.

## 1. Question and prior-art correction

The author's goal is to understand experience, intelligence, self and overlapping organization through first-principles reasoning and thought experiments, with concrete progress feedback. The question here is whether local temporal descriptions identify a whole, and whether collective information identifies dynamical indivisibility or one subject.

The persistent-parity example is NOT new: Rosas et al. (2020), Example 1, explicitly construct it and also recognize partition-relative emergence. We generalize the construction to an arbitrary finite macro Markov kernel, prove a restricted adaptive-observation statement, and distinguish two independent encoded memory layers from a four-cycle. These use established sharing, lumpability, lifting and linear algebra. No historical-priority claim or completed general novelty audit is made.

## 2. Actuality and scope

Let n>=2 sampled registers take values in a finite abelian group G of order q>=2. Set c(x)=sum_i x_i in G, with x in G^n. For binary words, this sum is bitwise XOR. Fix the sampling step, register identity, admissible ports and treatment of fresh randomness.

These are mathematical register variables, not every actual physical component of a brain or implementation. Random sources, clock, intermediate computation and boundary relations may be constitutive. Same sampled stochastic laws do NOT establish the same complete local open mechanisms. No macrovariable is an actual experiential process merely because an analyst names it.

## 3. Arbitrary macro dynamics, identical proper projections

For ANY row-stochastic q-state transition matrix Q define m=q^(n-1) and

    L_Q(x,x') = Q(c(x),c(x')) / m.                       (1)

Implementation schema: determine c(x); sample s' from Q(c(x),.); draw n-1 independent uniform new shares; set the last share so that their sum is s'. Intermediate operations belong to a physical implementation and cannot be omitted when claiming its complete organization.

Every macro fiber has m members, so the kernel normalizes and

    sum_{x':c(x')=s'} L_Q(x,x') = Q(c(x),s').            (2)

Thus c(X_t) follows Q for every initial distribution. For any proper coordinate subset A, k=|A|<n, fixed a and every full previous x,

    Pr[X_(t+1)^A=a | X_t=x] = q^(-k).                  (3)

Proof: at a fixed s', there are q^(n-k-1) compatible next states with X'^A=a; sum Q over s'. This gives (3), independently of Q and x.

If pi is stationary for Q, pi_L(x)=pi(c(x))/m is stationary. If Q is doubly stochastic the FULL one-time register distribution is uniform. Full snapshots therefore match across many different dynamics; uniform snapshots are not asserted for arbitrary Q.

## 4. Restricted adaptive-transcript theorem

At each step a protocol may choose pre-update overwrites and one proper next-readout subset using its previous readouts and independent randomness. The interventions provide no extra state information. It cannot pool enough subsets to reconstruct the same unrefreshed full state, inspect masks/update intermediates, or change the refresh law. Given common initial accessible information, its finite transcript law is identical for every Q.

Proof: condition on the history, chosen subset and intervention. Whatever the altered hidden current-state distribution, (3) makes the next readout uniform. The common policy then acts on identically distributed histories; induction finishes. Controlled families Q_u also satisfy the statement when every installed controlled kernel retains (1).

This is not a statement about all possible experiments. Joint contemporaneous readouts, mask observations/control, different sampling, or changed mechanisms can distinguish the models. A local record is not the full physical organization.

## 5. Positive temporal reconstruction and invariants

Let R[x,s]=1[c(x)=s] and B[s,x]=1[c(x)=s]/m. Then BR=I, L_Q=RQB, and for k>=1,

    L_Q^k=R Q^k B,
    trace(L_Q^k)=trace(Q^k),
    rank(L_Q^k)=rank(Q^k).                              (4)

Proof: cancel BR in products; use cyclicity of trace. The ambient vector space is im(R) direct-sum ker(B); on the former L acts as Q, and on the latter as zero. The spectrum is that of Q plus q^n-q zero eigenvalues. This linear decomposition is not itself a physical partition or subject selector.

For n=3 and G=(F_2)^2 compare Q_H=I_4, the four-cycle Q_C:00->01->10->11->00, and Q_F=J_4/4. They share all admitted proper temporal records and the full uniform instantaneous distribution. The lag-1 through lag-4 traces are:

    hold     4,4,4,4
    cycle    0,0,0,4
    forget   1,1,1,1.

These kernels cannot be conjugate at the same one-step clock. The four-step return is a MACRO statement: L_C^4=RB, not I_64. The random microstate need not return exactly. Larger trace is not more consciousness.

## 6. Collective coding does not establish dynamical indivisibility

Write each register as two independently addressable bits, and S=(S_1,S_2) as the two parity coordinates. Under Q_H:

    S_1'=S_1; S_2'=S_2.

The full holding kernel factors into two binary parity-memory kernels after regrouping the physically admitted bit-level parts. Every three-register proper view is blind to the collective symbol, yet there are two autonomous encoded memory layers. Collective coding relative to a device split does not imply nonfactorization under every justified split.

In contrast, the four-state macro cycle cannot be a product of two nontrivial deterministic binary dynamics under any macro state bijection. A bijective product forces both binary maps to be bijections; each has order at most two, so the product has order at most two, contradicting the cycle's order four. This concerns a specified 2x2 macro factorization, not all physical grain choices or subjective centers. At a four-step sampling interval the cycle becomes identity, illustrating why the clock must remain declared.

All 24 macro labelings and all 16 pairs of binary update functions were checked in the expanded verifier: identity has 24 product realizations, cycle zero. The holding lift's bit-plane product was checked entrywise.

## 7. A fixed-task capability relation, not an experience scale

Set Q_rho=rho I+(1-rho)J/q, 0<=rho<=1. Then

    Q_rho^k=rho^k I+(1-rho^k)J/q.                       (5)

Prepare a uniform unknown initial collective symbol with uniform masks and apply no intervening writes. Proper-readout transcripts contain no information about that symbol: optimal recall is 1/q. An actually installed joint decoder of final c(X_k) achieves

    p_correct(k)=[1+(q-1)rho^k]/q.                     (6)

Proof: use (3) for local records and Bayes' rule for the symmetric stationary kernel (5). Diagonal posterior mass is (6), off-diagonal mass (1-rho^k)/q; masks add no information conditional on c(X_k). For q=4, rho=1, joint recall is 1 and local recall 1/4; rho=1/2 at lag one gives joint recall 5/8. The advantage vanishes continuously as rho tends to zero. This is a specified recall capability, not general intelligence, basal experience, or valence.

An analyst's offline decoding does not demonstrate an internal consumer or self. Actual installation/use must be independently supplied to attribute capability to the whole system.

## 8. What can positively follow for UCT

UCT I v1.2 already distinguishes full organization, finite views, nonproduct comparison and subject selection. Under C1, justified full organizational-type differences give experiential structural-type differences. A useful inherited asymmetry is that one grounded invariant DIFFERENCE can establish nonisomorphism, while invariant equality generally cannot establish isomorphism.

Consequently, one need not reconstruct every microscopic detail to establish a type difference, provided the differing invariant belongs to the SAME actual token and is preserved by the common physically justified comparison. Here traces qualify only when the sampled kernel, clock, ports and noise treatment are an admitted reduct of the organization. An arbitrary graph or unverified fitted model does not suffice.

Neither the resulting type difference nor the collective-memory construction identifies a named feeling, intensity, pain, fear, familiar mineness or subject count. Two independent macro bits are not two proved subjects; a macro four-cycle is not one proved subject. C1 is still an interpretive axiom, not inferred from a working circuit. Continuing lower processes are not deleted, and no report/memory/integration threshold for basal experience is added.

The project increment is a constructive family separating (i) matched local observations, (ii) actual joint temporal organization, (iii) split-relative dynamical factorization, and (iv) joint task capacity, with a conditional C1 type consequence. It is not a solved phenomenal-unity bridge.

## 9. Executed verification and map attachment

Expanded local script check_collective.py was actually run successfully: 28 exact matrix cases (q=2,3,4; declared n=2,3,4 combinations; four kernels each), every proper subset in those cases, quotient/power/trace identities, an adaptive three-step protocol with 64 equally likely transcripts under four laws, binary-product checks and 25 rational retention/Bayes cases. Integer or Fraction arithmetic proves the finite equalities; only displayed information logarithms use floats. No human/animal/LLM experiment or raw dataset was performed.

Affected inherited nodes: C1; actual token and common signature; finite scientific views; UCT I §6 split-relative product; UCT III capability/type; CG interaction-complete composition. No canonical graph nodes/rules edited, no global-map proof claimed. QC10, IA-QC11, QC12 and QC13 actual/phenomenal application remain open. This auxiliary result must not be used to bypass R181's body/action-reference task.

Failures explicitly preserved: claiming parity memory as novel; confusing macro return with microstate return; confusing sampled marginals with full open mechanisms; treating collective information or factorization as a proved subject count.

Next bounded question: compare independently addressable versus coupled temporal reference roles at equal joint recall in one actually specified action-feedback assembly. Require a fixed physical consumer, bearer/time and a predeclared target consequence; do not rename the result felt trying without an independent bridge. HOLD DOI/OTS/Arweave and paper release.

## 10. Primary sources and read scope

- Rosas FE et al. (2020), PLOS Computational Biology 16:e1008289, DOI 10.1371/journal.pcbi.1008289. Publisher fundamental examples and partition-relativity discussion read. Direct parity/collective-dynamics antecedent, not UCT novelty. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008289
- Geiger BC, Wu Y (2016), Higher-Order Kullback-Leibler Aggregation of Markov Chains, arXiv:1608.04637v1. Primary abstract/metadata only; full HTML failed. Established lifting/aggregation background, not a theorem-level novelty clearance. https://arxiv.org/abs/1608.04637
- Bayne T, Chalmers DJ, What is the Unity of Consciousness?, author-hosted manuscript §§3–5: access and phenomenal unity distinguished. https://consc.net/papers/unity.html
- Lopez A (2025), A layered unity model of split-brain consciousness, Philosophical Studies 182:2159–2190; DOI 10.1007/s11098-025-02339-3, published 12 June 2025. Transitivity/duplicate-experience alternatives inspected, no raw-data reanalysis. https://link.springer.com/article/10.1007/s11098-025-02339-3
- UCT I v1.2, DOI 10.5281/zenodo.23131575, frozen source blob 7a980c86b8f94ce787d358dab3529903eb822f8f, §§6–7 read. CG checkpoint blob d216112697b10efade409ca99e81b56aff0e0f8d read. R181/SB handoff and map notices inspected. No exhaustive entire-repository prior-art audit claimed.

## 11. Compact independent core verifier

This smaller standard-library verifier reproduces the principal exact construction and factorization claims. It is not the byte-identical expanded local verifier or a claim to reproduce its entire 28-case output.

```python
from itertools import product, combinations, permutations
from fractions import Fraction as F

q,n=4,3
xs=list(product(range(q),repeat=n))
def c(x): return x[0]^x[1]^x[2]
m=q**(n-1)
kernels={
 'hold':[[F(int(i==j)) for j in range(q)] for i in range(q)],
 'cycle':[[F(int(j==(i+1)%q)) for j in range(q)] for i in range(q)],
 'forget':[[F(1,q) for j in range(q)] for i in range(q)]}
traces={}
for name,Q in kernels.items():
 L=[[Q[c(x)][c(y)]/m for y in xs] for x in xs]
 assert all(sum(row)==1 for row in L)
 assert all(sum(L[i][j] for i in range(len(xs)))==1 for j in range(len(xs)))
 for k in range(n):
  for A in combinations(range(n),k):
   for a in product(range(q),repeat=k):
    inds=[j for j,y in enumerate(xs) if tuple(y[i] for i in A)==a]
    assert all(sum(L[i][j] for j in inds)==F(1,q**k) for i in range(len(xs)))
 for i,x in enumerate(xs):
  for s in range(q):
   assert sum(L[i][j] for j,y in enumerate(xs) if c(y)==s)==Q[c(x)][s]
 Qk=[[F(int(i==j)) for j in range(q)] for i in range(q)]
 traces[name]=[]
 for k in range(1,5):
  Qk=[[sum(Qk[i][r]*Q[r][j] for r in range(q)) for j in range(q)] for i in range(q)]
  traces[name].append(sum(Qk[i][i] for i in range(q)))
assert traces=={'hold':[4,4,4,4],'cycle':[0,0,0,4],'forget':[1,1,1,1]}
pairs=list(product((0,1),repeat=2)); maps=pairs
counts={}
for name,step in [('hold',(0,1,2,3)),('cycle',(1,2,3,0))]:
 count=0
 for h in permutations(pairs):
  for f,g in product(maps,repeat=2):
   if all(h[step[s]]==(f[h[s][0]],g[h[s][1]]) for s in range(4)): count+=1
 counts[name]=count
assert counts=={'hold':24,'cycle':0}
print('CORE PASS',traces,counts)
print('Mathematical kernels only; no phenomenal variable measured.')
```
