# UCT-RC-2026-01 — final manuscript revision v1.1.0

Date: 12 October 2026. Author: Hongju Liu. Work: What the Whole Adds Without Erasing Its Parts: Local Persistence, Overlap, and Relational Completion in Structural Accounts of Experience.

## Status and persistence scope

The author requested another deep scientific review and a final manuscript, not a DOI transaction. The final English PDF is 25 pages with 18 references. This is the same work as supplied v1.0.0, which was preserved unchanged. A complete v1.1.0 package was prepared as a downloadable conversation artifact, containing PDF, Markdown, LaTeX, three exact verifiers, results, claim ledger, source-access ledger, review, and proposed deposit metadata.

THIS GITHUB RECORD IS A RESEARCH HANDOFF AND FINGERPRINT RECORD, NOT A FULL BACKUP OF THE PDF OR PACKAGE. Do not claim the complete manuscript, binary PDF, or reproduction files were uploaded by this commit. Retrieve the v1.1.0 conversation artifacts and verify these fingerprints before publication. No DOI was reserved or published; no OTS or Arweave submission was made. No PR was opened or CI deliberately run. The official UCT map and its CURRENT_STATE were not changed.

## Preserved core and corrections

RC1–RC2 retain the finite completion and temporal-consistency constructions. RC3 now states an exact-overlap premise: commuting embeddings agree on declared shared occurrences but do not alone exclude accidental extra identifications. Require e_i[D(P_i)] intersect e_j[D(P_j)] = e_i a_ij,i[D(O_ij)]. A bijective structural identity h_W transports that exact intersection. Example: P={a,b}, Q={b,c}; mapping a,c to 0 and b to 1 commutes on b but wrongly collapses distinct outer events. A bare intersection is not automatically an actual experience-bearing process token. C1/U1 must not be applied without that premise.

The single-parity memory construction remains explicitly inherited from Rosas et al. (2020), Reconciling emergences, DOI 10.1371/journal.pcbi.1008289, Example 1. No novelty is claimed for binary coupling, higher-order dependence, Markov projection, or common-drive organization themselves.

RC6 retains the overlapping model. For three bits x, S=(-1)^(x1+x2), T=(-1)^(x2+x3), R=ST=(-1)^(x1+x3), with declared patches {1,2} and {2,3}, define

L_(alpha,beta,gamma)(y|x) = [1+alpha S(x)S(y)+beta T(x)T(y)+gamma R(x)R(y)]/8.

Feasibility is -1+|alpha+beta| <= gamma <= 1-|alpha-beta|. Both full separate local trajectory laws remain fixed when only gamma changes. Under this closed, fresh-innovation Markov family, the three stationary correlations are alpha^k, beta^k, gamma^k. For nonnegative local rates, max |gamma|=1-|alpha-beta|. The outer relation is cover-relative: registers 1 and 3 suffice to read it. It is NOT an irreducible three-body consciousness measure or a unique-subject result.

## RC7: what survives without Markov closure

For arbitrary sign processes with R=ST and any fixed lag k, write A_k=E[S_t S_(t+k)], B_k=E[T_t T_(t+k)], C_k=E[R_t R_(t+k)]. Then

-1+|A_k+B_k| <= C_k <= 1-|A_k-B_k|.

Proof: U=S_t S_(t+k), V=T_t T_(t+k) have four probabilities [1+A_k u+B_k v+C_k uv]/4, which must be nonnegative. This is sharp at one lag, not a claim that independently chosen feasible moments at all lags form a realizable process. These are raw moments; centered normalized correlation language additionally requires unbiased signs. No exponential envelope follows without the extra dynamical premises.

## RC8: uniform positivity is stronger than strict positivity

A fixed transition floor L(y|x)>=rho/8, with z=1-rho, is equivalent to

-z+|alpha+beta| <= gamma <= z-|alpha-beta|.

For feasible nonnegative local rates, max |gamma|=z-|alpha-beta|. Thus a fixed rho>0 bounds the exponential time even at equal local rates. The equal-local-rate unbounded sequence in RC6 approaches zero minimum transition probability. This is process noise, not sensor noise or a universal thermodynamic constraint.

## RC9: fully positive hidden-mediator witness

Set alpha=3/4, beta=1/4, q=1/4, d=1/5, and 1/2<=lambda<1. Add a mediator sign H with retention lambda. Set c(x,h)=q+d h R(x), which takes values 1/20 and 9/20, strictly within [0,1/2]. Use the 16-state transition

T((y,h')|(x,h)) = L_(alpha,beta,c(x,h))(y|x) (1+lambda h h')/2.

All 256 entries are positive. Each local patch remains Markov with its original law even conditional on the full past. The stationary law is pi(x,h)=[1+mu R(x)h]/16, where mu=d lambda/(1-q lambda). Visible X is uniform. Its complete stationary observational one-step table equals L_(alpha,beta,gamma_eff), gamma_eff=q+d mu. All these apparent tables even share the positive entry floor 59/2400.

Nevertheless, the actual stationary relation correlation is

C_k=w lambda^k+(1-w)q^k, w=d mu/(lambda-q), 0<w<1.

Proof: E[R'|X,H]=qR+dH, E[H'|H]=lambda H. Stationarity gives mu=lambda(q mu+d). Iteration gives E[R_(t+k)|X_t,H_t]=q^k R_t+d(lambda^k-q^k)H_t/(lambda-q). Multiply by R_t and average. The two-step defect is C_2-C_1^2=d mu(lambda-gamma_eff)>0.

As lambda approaches 1, w approaches 16/225, so the slow-tail time and 1+2 sum_(k>=1) C_k diverge despite fixed unequal local rates. At lambda=.9,.99,.999, C_8 is approximately .030777,.065635,.070558, whereas the incorrectly extrapolated RC6 envelope would be 1/256. This does not contradict RC6: visible X is not a closed Markov state. The full 16-state floor vanishes in this limit, so RC8 is not contradicted either.

IMPORTANT: equality of the one-step tables is stationary and observational, NOT equality of all interventional responses. Preparing R_0=r with otherwise uniform visible states and independently fair H_0 gives E[R_k]=q^k r. A long passive correlation tail does not by itself establish storage of a newly written bit. Writing H too would be a different protocol and declared carrier. Tail time, integrated autocorrelation time, and first 1/e crossing must remain distinct.

## RC10: matched-local preparation and generator intervention

In the closed L family, prepare M_r(x)=1{R(x)=r}/4. Both preparations induce the same complete trajectory law on each patch separately, but a noiseless outer-pair reader has mean contrast 2 gamma^k. A general observation channel W detects this contrast exactly through b_o^R=(1/8) sum_y R(y)W(o|y). Optimal balanced bit-decoding success is (1+|gamma|^k)/2. Independent calibrated noise on outer bits attenuates the contrast by (1-2eta_1)(1-2eta_3).

Replace innovation V physically at the generator with an independent sign of the same mean beta while retaining U's mean alpha. Then gamma becomes alpha beta, so the contrast becomes 2(alpha beta)^k, while both full separate local path laws remain fixed. This is not post-hoc trial shuffling, not preservation of actual individual trajectories, and not proof that complete local constitutive organizations or experiential contents stay identical. Use a non-feedback readout and independently audit the intervention and carrier.

## Verification actually executed

Three standard-library Python verifiers were executed twice synchronously. All primary result JSONs matched between the two runs byte for byte. The first two scripts and their main result bytes reproduce v1.0.0. New exact checks include 455 sign-pair tables, 3,645 floor parameter combinations (543 feasible), five positive mediator models, 640 local marginal equalities, 320 observational one-step equalities, 60 multi-lag identities, 10 complete three-time patch-law comparisons, 120 fresh-preparation checks, and 8,192 readout-distribution checks. All assertions passed. The general results depend on the written proofs, not the grid counts.

The 25-page PDF was rendered and reviewed; critical equations and tables were inspected at full render resolution. All fonts are embedded, no overfull boxes remain, and no standalone font files are distributed. This is internal author-directed, substantially AI-assisted review, not independent peer review, a hardware experiment, or empirical consciousness evidence.

## Exact artifact fingerprints — SHA-256

- manuscript.md: fd355578fd0d79911409c54ed929c0aed597f98ede0ecb84edf03a8654dbd1be
- What_the_Whole_Adds_v1.1.0.pdf: 68e2e3a80226f946ed40a0fa7a947a27c7af33431d373a456e1ba738bc3c24c7
- code/verify_revision.py: 3ac030f581091dfdff4a8be31d99c773fb16fb0cbe20619b63f9774b731eba93
- results/REVISION_RESULTS.json: a41ddad5ac3026a4bb576c92ac77182e20faac9a4e5330c4da0559fb6294f35d
- review/FINAL_SCIENTIFIC_REVIEW.md: acea731a5702ef31896e78aadc4235c4b80f9b8f26ffe09c9d309624e59c0ba5

## Map, coverage, originality, and next handoff

The current v2.3 research guide, CURRENT_STATE, and pinned UCT I v1.2 combination/subject-selection passages were re-read. The entire historical semantic map was NOT freshly re-audited. Candidate nodes stay disabled; no completed map version or independent empirical premise is promoted. Coverage is scoped to the supplied predecessor and relevant retrieved material, not every historical publication. C1/P3/U1 remain conditional UCT premises. Continuing local experience is not unchanged local experiential content. No IIT score, IIT refutation, unique subject count, or named phenomenal quality is established.

This is a final revision of the same paper, with a targeted primary-source priority review and no guarantee of global novelty. Before any separately authorized DOI deposit, retrieve and hash-check the full v1.1.0 artifacts, audit the proposed nested metadata, and follow the existing DOI -> OTS -> Arweave workflow. Do not treat this handoff alone as the manuscript or claim publication was completed.
