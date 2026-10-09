# Five-port sustained control: independent certificate and proof review

**Review ID:** `ONLINE-AC-N5-INDEPENDENT-REVIEW-20261009`  
**Result:** `ONLINE-AC-RESULT-v0.2.0`; constructive component `ONLINE-AC-N5-CLOSED-20261009`.  
**Reviewer:** `/root/map_audit`, with independently implemented certificate checks by `/root/map_audit/online_trace_check`.  
**Disposition:** **PASS for the finite certificates, canonical transport, closed-family induction, and the stated optimal probe-budget comparison.**  
**Readiness:** a focused, complete technical working paper is justified by the specified result package. External priority, actual realization, and scientific-map integration remain separate and open. **PENDING_MAP is unchanged.**

**Final manuscript bound by this review:** `publication_audit_work/ONLINE_AC_PAPER.md`, `ONLINE-AC-PAPER-v0.1.0`, 39,779 bytes / 5,708 space-delimited words, SHA-256 `713c99e59d2abf6278a2f036dbb49514fafd89ee7f781be8bf5bc91bf1827b65`.

## 1. Result and review boundary

For five command/effect ports, known initial wiring, and identity or one arbitrary effect-port transposition before each round, a controller with **at most two full binary-vector probes per round** can attain the same prescribed net unit effect at every round deadline. The probes and terminal action physically alter the same persistent plant. The controller uses only its retained compatible-wiring set and returned effects.

The constructive proof preserves a family of singleton wiring sets and pairs differing by one transposition of two non-goal effects. Complete wiring identification need not occur on every successful branch. The previously reviewed one-probe obstruction rules out a uniform per-round cap of one, so the minimum sustainable cap for this five-port task is two. Complete current-wiring identification requires three probes under a matched timing and net-goal contract. The latter signature bound is inherited mathematics; the positive closed-family construction supplies the new specific separation.

This review includes the complete source of both independent five-port verifiers, the original 240-state certificate's metadata and verified state conditions, all 28 readable canonical table rows, the algebraic transport argument, and the manuscript's substantive claims and limits. It does not review the controller-discovery search as the basis of proof. Neither independent verifier reads, imports, or executes that search, its winning-state recursion, the extractor, or the formatter. Their provenance hashes are retained as declared source metadata rather than substituted for verification.

The original three-port/general one-probe checkpoint has its own frozen review, `publication_audit_work/ONLINE_AC_INDEPENDENT_REVIEW.md`, SHA-256 `5936df43cce324bb067f8f219520b90a3b279e0e9deea5ea40f539757dab477b`. This report adds the five-port construction and matched identification comparison. It does not rewrite that earlier checkpoint or reinterpret a previously open larger-port case as having been proved in the older version.

## 2. Contract continuity and information available to the controller

The action law is unchanged from the earlier checkpoint:

\[
x\leftarrow x\oplus P_\pi u.
\]

At the beginning of a round, \(\pi\) changes to \(\sigma\pi\), with \(\sigma\) identity or one of all ten effect-port transpositions. It stays fixed through both probes and the terminal command. Drift changes the action law only; it does not permute or reset the plant state.

A probe is any vector in \(\{0,1\}^5\), with its entire effect vector returned. The second probe may depend on the first returned vector. The terminal command may depend on both. Zero vectors are legal. Every command acts physically; the success condition is

\[
y_1\oplus y_2\oplus z=e_g,
\qquad x_{\rm end}\oplus x_{\rm start}=e_g.
\tag{1}
\]

The known initial wiring and the timing and observation assumptions are retained. The changes are the explicit value \(n=5\) and the allowed probe cap of two. This is a new point in the same parameterized model, not a claim that the one-probe and two-probe resource contracts are identical capability evaluations for an experiential inference.

A belief in this proof is the **exact set of current or old wirings compatible with the controller's history**, not a probability distribution. No uniform prior is needed for the five-port result. Each possible old wiring and every fresh legal change must be handled. A representative \(\rho\) is selected from a known belief by a predetermined rule; it is never supplied as the actual hidden wiring.

The verifiers separate environment and controller. The environment owns the true wiring and mutable plant. The controller receives the known belief/state identifier and its effect observations. No actual wiring, drift label, true plant value, or success flag is passed as a decision input. Initial belief identity is a stipulated, public initial condition; the construction does not establish that an arbitrary unknown initial wiring can be calibrated with the same budget.

On a successful leaf,

\[
z=e_g\oplus y_1\oplus y_2.
\tag{2}
\]

The terminal effect is therefore constant over the complete leaf. Full terminal feedback is available and is not being withheld to produce a limitation. It adds no distinction within a leaf on which net-goal success is guaranteed. No assertion requires a correct plant value immediately after either probe, and no extra correction occurs before the same deadline.

## 3. Independent verification of the 240-state certificate

The verifier reconstructs the complete set of 120 permutations and the complete 11-member drift family independently. It validates each decimal bit-mask state identifier against its explicit wiring membership, checks the initial belief is exactly identity, and requires every leaf to name an existing state.

For each state it expands **every old-wiring/fresh-drift pair**, retains all labelled worlds even when they produce duplicate current wirings, and derives the exact first and second observation cells. It rejects missing or extra branches. Each terminal command is common to its two-observation history. Its net command must have the required effect under every compatible wiring. Each successor must equal the complete compatible-current-wiring set, not merely contain selected witnesses. Full terminal feedback is explicitly included when checking that this set remains exact.

The verifier also executes a separate observable controller in every labelled world from all 32 plant starting states. The same mutable plant is toggled by both probes and the terminal command. The inverse-port effect calculation and the forward physical coordinate update are independently expressed in the program and required to agree.

| Verified property | Count |
|---|---:|
| Wiring basis | 120 permutations |
| Fresh drift choices | 11 |
| Controller states | 240 |
| States reachable from identity | 240 |
| Singleton states / pair states | 120 / 120 |
| Labelled old-wiring/drift worlds | 3,960 |
| Distinct current-wiring/state pairs | 3,720 |
| First-effect cells | 1,920 |
| Exact-posterior terminal leaves | 3,360 |
| Directed state edges | 3,360 |
| Persistent-plant cases | 126,720 |
| Physically applied commands | 380,160 |

Every verified case satisfied (1). Breadth-first reachability confirmed that every state in this particular extracted certificate is reachable. The accepted source hash is fixed in the result receipt. No claim rests on the extractor's heuristic lookahead value or on extrapolating the earlier horizon-one-to-six search.

### Why the finite check proves every finite horizon

Initially the actual old wiring lies in the exact initial belief. If this invariant holds before a round, the actual next wiring belongs to the verifier's exhaustive fresh-drift expansion. The actual returned effects therefore follow one checked branch. Its common terminal action meets (1), and the exact successor belief contains precisely the possible current wirings, including the actual one. The successor is another verified controller state.

Induction gives one fixed controller that meets every round deadline at every finite horizon. The result is a safety statement about all finite prefixes of every legal run. It is not an empirical demonstration of an infinitely operating physical device.

## 4. Two canonical templates and the closed family

For a fixed goal port \(g\), define

\[
\mathcal F_g=
\{\{\rho\}:\rho\in S_5\}
\cup
\{\{\rho,(rs)\rho\}:\rho\in S_5,\ r<s,\ r,s\ne g\}.
\tag{3}
\]

Every unordered pair has two possible representatives. There are therefore

\[
120+\frac{120\binom42}{2}=480
\]

distinct beliefs: 120 singletons and 360 pairs. These numbers describe an invariant proof family, not a collection of 480 discoveries or a minimum-memory theorem.

The two templates use \(g=0\), with old beliefs \(\{I\}\) and \(\{I,(34)\}\). Their first probes are respectively \(\{0,1\}\) and \(\{0,3\}\). They cover all allowed fresh changes:

| Template | Labelled old/drift worlds | Distinct current wirings | First-effect cells | Terminal leaves |
|---|---:|---:|---:|---:|
| Known identity | 11 | 11 | 7 | 10 |
| Identity or \((34)\) | 22 | 20 | 9 | 18 |
| Total | 33 | 31 | 16 | 28 |

The independent transport verifier compares all 28 extracted JSON rows, field by field, with the original state `1` and state `3` trees. It then independently executes all 33 worlds and reconstructs each exact observation cell. I also read the complete human-readable table and checked its cycle notation against the explicit permutation tuples.

There are exactly three nonsingleton leaves across the two templates:

\[
\{I,(34)\},\qquad
\{I,(24)\},\qquad
\{(34),(234)\}.
\]

The third pair differs by the non-goal transposition \((23)\), since \((234)=(23)(34)\). All other leaves are singletons. Each leaf has one common inverse-goal port, and its terminal command is the XOR of both probes with that inverse-goal unit command. Thus all three nonsingleton outcomes retain the family form in (3), and their physical terminal correction is valid.

## 5. Independent transport proof

Let \(B=\{\rho,(rs)\rho\}\in\mathcal F_g\). Select a representative \(\rho\) from the known set, and choose an effect bijection \(f\) satisfying

\[
f(0)=g,\qquad f(3)=r,\qquad f(4)=s.
\]

The remaining two canonical labels can be assigned bijectively to the remaining effects. Put

\[
c=\rho^{-1}f.
\tag{4}
\]

The canonical old-wiring set is

\[
f^{-1}Bc=\{I,(34)\}.
\]

For a current actual wiring \(\pi'=\sigma\pi\), the canonical current wiring is

\[
\lambda=f^{-1}\pi'c
=(f^{-1}\sigma f)(f^{-1}\pi c).
\tag{5}
\]

Conjugation by \(f\) preserves identity and the complete transposition family. The transformed problem is therefore exactly the canonical template's admitted drift problem.

To issue a canonical vector \(u\), the controller uses actual vector \(P_cu\). Its returned actual effect is

\[
P_{\pi'}P_cu=P_fP_\lambda u.
\tag{6}
\]

Applying \(P_{f^{-1}}\) to that returned vector supplies the canonical observation. The same relation holds for the adaptive second probe and the terminal command. Since canonical net effect is \(e_0\), the actual net effect is \(P_fe_0=e_g\).

This changes the controller's choice of command ports and interpretation of returned vectors. It does **not** physically relabel or move the existing plant state, change the fixed actual goal port, or reveal which old belief member is real.

A canonical leaf wiring \(\eta\) maps back to \(f\eta c^{-1}\). If a canonical leaf is \(\{\eta,(ab)\eta\}\) with \(a,b\ne0\), its actual posterior is

\[
\{f\eta c^{-1},\ (f(a)\ f(b))f\eta c^{-1}\}.
\tag{7}
\]

Both transposed effects differ from \(g\), so this set lies in \(\mathcal F_g\). Singleton leaves stay singleton. For a singleton old belief, any \(f\) with \(f(0)=g\), together with (4), reduces it to the known-identity template. The observation transport is bijective, so exact compatible sets, not only correctness, are preserved.

Choosing \(\rho,f,c\) deterministically from the returned belief gives one observation-based controller. Recanonicalization after each round preserves (3). A known initial wiring is a singleton in that family, so induction proves the sustained-control theorem.

### Independent execution over the full family

The transport verifier independently generated all 480 beliefs, normalized each by (4), and checked every allowed old-wiring/drift world. It used only the two template trees and permutation data; the other 238 original controller trees were not used in the transport construction.

| Full-family check | Count |
|---|---:|
| Beliefs checked | 480 |
| Labelled old-wiring/fresh-drift worlds | 9,240 |
| Distinct current-wiring/belief pairs | 8,520 |
| First-effect cells | 4,080 |
| Exact terminal leaves / directed edges | 7,680 |
| Singleton / pair posterior leaves | 6,840 / 840 |
| Transported physical trajectory cases | 9,240 |
| Transported physical commands | 27,720 |

Each world was physically executed from nonzero plant state 21, with both probes and terminal acting on that same plant. All net effects were \(e_0\). The algebra establishes translation independence from the starting plant value; the separate 240-state verifier had already checked all 32 starting values. Including the 33 canonical-template cases, the transport run executed 9,273 physical trajectories. This is a five-port computation at \(g=0\); equations (4)–(7) provide the proof for every fixed goal label.

### Keep the three state counts separate

The independently implemented canonicalization chooses the lexicographically smallest belief member, then assigns the remaining effect labels in sorted order. It reaches **260** beliefs from identity: 120 singletons and 140 pairs. The other 220 members of \(\mathcal F_0\) belong to the verified closed family but are unreachable under this particular deterministic choice.

The earlier **240** states belong to the original extracted controller. The **260** states belong to this transported implementation. The **480** states form the invariant family. These are different correct counts of different objects. None has been proved to be a minimal memory count, and closure does not require every member of a chosen invariant family to be reachable.

## 6. Exact sustainable cap and the matched identification comparison

The old general-\(n\) two-round theorem forbids a controller with a uniform per-round cap of one from guaranteeing two deadlines, including unlimited memory and full terminal feedback. The five-port construction supplies a cap of two for every finite horizon. Hence

\[
k_{\rm sustainable}^{*}(n=5)=2.
\tag{8}
\]

This is a **worst-case per-round cap**. It does not say that every branch needs two nonzero probes, that every round must spend two useful probes, that an average cost of two is minimal, or that the total optimum over \(H\) rounds is \(2H\).

For complete current-wiring identification, take a completely known old \(\rho\) and the same allowed fresh drift family. Follow the adaptive branch whose fresh drift is identity. Across \(k\) selected probes, each old effect port receives a \(k\)-bit inclusion signature, measured at its known inverse command port.

If \(2^k<n\), two effect ports have identical signatures. A fresh transposition of those two effects preserves every probe observation on the identity branch. By induction over observations the adaptive controller chooses the same later probes, and both the returned effects and actual plant values remain the same. Identity and that legal transposition are indistinguishable. Therefore complete identification before choosing the terminal action needs

\[
k\ge\lceil\log_2 n\rceil.
\tag{9}
\]

The same lower bound holds if identification is required at a deadline that also retains guaranteed net-goal success: equation (2), generalized to all \(k\) probes, makes terminal feedback a function of the preceding probe effects and the fixed goal. It cannot distinguish the unresolved pair on a successful leaf. If the terminal action is instead a free extra identification query and the net-goal requirement is removed, this is a different task and different query accounting.

Distinct command signatures attain (9). The observations reconstruct the current wiring; a terminal vector equal to the XOR of all probe vectors and the identified inverse-goal command compensates their physical effects. The upper construction works in the same old-known, identity-or-transposition setting. Independent randomization cannot evade the finite zero-error signature lower bound.

Thus, on five ports, the exact comparison is **two probes for sustained selected-goal control versus three for complete current identification**, with matched initial knowledge, drift family, physical probe law, and the stated identification deadline. The argument does not make the complete-identification task start from less knowledge.

The binary-signature principle is classical and already explicit in the AC predecessor. This review accepts its narrowed identity-branch application as an inherited comparison lemma. The new positive work is the safe partial-belief construction that attains (8). No universal two-probe controller for \(n\ge6\) or general formula for sustained-control budgets has been proved here.

## 7. Manuscript and reuse readiness

The substantive manuscript review covered its model, Theorems 1–4, the identification comparison, verification account, inheritance table, applications, limitations, and reproducibility interface. It found no mathematical blocker. The author was asked to make three small scope clarifications: say zero-vector probes when padding slots; refer to the two first-round histories in the two-round proof; define beliefs as compatible sets without probabilities and state that the optimum is a uniform worst-case per-round cap. These changes are present in the final manuscript identified above.

The completed manuscript includes both tables and no table placeholder. A final independent semantic parsing check translated its math-formatted vector sets, cycle notation, and net-port entries back into the canonical JSON fields. All ten Table A rows and all eighteen Table B rows matched, including their inferred physical terminal commands. Raw Markdown equality is not expected because the manuscript uses mathematical delimiters and compact cycle notation. Its new 9,240-world/7,680-leaf transport counts and the distinction between the 260-state transported controller and 240-state extracted controller were also checked against the frozen receipts.

The paper is now justified as a **focused technical working paper** because it contains a common problem contract, a negative information result, an exact three-port benchmark, a five-port construction, a matching lower bound for its resource cap, and a clear comparison with complete identification. The two small decision tables and transport proof make the positive result independently understandable without trusting an opaque discovery search. The full certificates and separate verifiers support exact reuse.

This assessment is about the incremental content, not the number of nodes, rows, states, checks, or publication artifacts. The general distinction between present capability and future dynamical sufficiency is already published in UCT III §6.4, Proposition 6, with a circuit witness in §7.2. Static calibration, task factorization, binary signatures, common belief-state control, and invariant induction remain inherited. The five-port invariant and exact budget separation are the specific new project results accepted here. An independent finite verification is not external peer review.

The preferred claim boundaries are:

| Content | Treatment |
|---|---|
| Two canonical templates and their closed non-goal-pair family | Specific constructive five-port result |
| Sustainable cap two | Corollary of the construction and the earlier one-probe obstruction |
| Same-contract complete-ID cap three | Inherited signature method specialized to the matched observation/drift contract |
| 240/260/480 state counts | Distinct implementation and proof-domain facts, not memory lower bounds or separate discoveries |
| General belief recursion, factorization, covariance, and closure induction | Credited inherited methods |
| Full scientific-map integration, biological/AI realization, fixed-J experiential use, named feelings, personal identity | Not established by these results |

A future AI can cite the precise impossibility conditions, implement the two templates, verify the compatible-set invariant, or use the benchmark to detect an information leak in a proposed controller. It should retain the physical probe effects, same net goal, observation law, known initial wiring, full drift support, and within-round timing. These exact interfaces make the work useful as durable knowledge.

Historical priority for the exact package remains unverified by this review. The separate predecessor/reuse review records the targeted external searches and what was actually read. A complete working manuscript is appropriate; a claim to invent adaptive control, dynamic abstraction, or a foundational theory of experience is not supported. The manuscript remains a working paper with no new DOI or published-work count supplied by this review.

## 8. Frozen source and verification hashes

The following paths are relative to `publication_audit_work/next_probe_n5/` in the shared workspace.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `CLOSED_CONTROLLER.json` | 784,009 | `2d5ba3fb65730620c2ef1308d1236aa08360f79623fb202899cd9f11af6db0fe` |
| `verify_closed_controller_independent.py` | 18,857 | `c275352f0177f1935dd192231b36fe83a0d52d7920ab5150fa63122d57f4d7d0` |
| `CERTIFICATE_INDEPENDENT_VALIDATION.json` | 87,848 | `285e4a993abac070eebbc3c13d4321d744ca09f5077b9d83585383d176670416` |
| `CANONICAL_TEMPLATES.json` | 11,013 | `149bcada929b4dd92236f10734eb3b6f19ac929970207b8475dc02c7d5076bb7` |
| `CANONICAL_TABLES.md` | 1,860 | `39011dab4817d96e7618ce466ece6ce8cd1b9a9e98a573c5e5cba5a776211471` |
| `canonical_transport_independent.py` | 24,657 | `9a2d29db9ca0f3c978e37aeaef8b90477fcbb281b000c5a817d521cd35f1d632` |
| `CANONICAL_TRANSPORT_INDEPENDENT_VALIDATION.json` | 16,357 | `3fe8b00e208d0bd93be02f805aa328052ad554c805a6aa0517f168516781eefd` |

The original certificate verifier's normalized transition-row hash is `737ec9a0ab85f7a503d74ba2a4b7c5d8808c632f2770ab933164aa5e7d326e81`. The full-family transport verifier's normalized transition-row hash is `8708a12279f0089b8f5114c23263208c9bcfa17a3601ddafe3526fd90756db97`. They identify different implementations and are not expected to agree.

The effective v1.1.2 graph and review ledger remain the previously frozen objects with hashes `0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612` and `0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687`. No scientific-map version is created by this local review. AC and IL remain separately pending, suspended rules are not reactivated, and actual or named-experience obligations are not closed.
