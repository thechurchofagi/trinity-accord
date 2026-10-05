# R72 / Manuscript v0.2 — targeted revision and handoff

Date: 2026-10-05. Research owner: Hongju Liu / 刘烘炬. This continues the R71 manuscript; it is not a new consciousness discovery or a new publication.

## Delivered revision

Entry point: `UCT_Agent_Self_Preservation_Draft_v0.2_20261005.md`. Preserve the v0.1 file as its unsaved local predecessor. Neither has an existing Library identity at the start of this turn. Released UCT I/II/III are untouched.

The main argument is now bundled-versus-crossed identification, extended to decision-relevant beliefs. Opposite preservation choices and mechanism ambiguity remain supporting limitations. The instrumental/intrinsic distinction is explicitly attributed to prior literature.

New manuscript-level deductions, using standard mathematics:

1. With known beliefs and calibrated exact continuation-value differences, the three coefficients are identifiable over an unrestricted parameter space iff the difference design has rank three. Physical crossing can coexist with belief collapse. The result does not apply directly to ordinal choices or certify internal beliefs from verbal answers.
2. A finite-range and approximate-choice sensitivity bound is derived: relative persistence contribution is at least cost difference minus task/nuisance advantage, regret, and value range times the sum of two total-variation errors. Without independently warranted bounds it can be vacuous.
3. A small exact witness shows that better consequence understanding can improve inference about an unchanged preservation contribution. This is a mechanism-level explanation of one way intelligence and inferred concern can dissociate; it measures no fear.

`r72_revision_checks.py` checks the determinant, belief collapse, the witness, and omitted-regret/unbounded-range failure cases. `R72_Exact_Results.json` and `R72_Run.log` retain results. These are limited formal checks, not an empirical model run. No large experiment was started.

## Source audit and overlap

Source access date: 2026-10-05. Primary sources only inform the comparison.

| Source | Actually inspected in this turn | Editorial consequence |
|---|---|---|
| Mullally, 2026, DOI 10.1007/s43681-026-00983-x | Publisher text §§2–7, especially §§4.2–4.6 | Instrumental/intrinsic distinction is prior work. Compare temporal evidence with the cessation criterion; retain precautionary scope. |
| Dung & Register, AI identity and self-concern | Author abstract, archive history (v1 2026-03-02; v2 2026-06-10), search-indexed PDF p.10 excerpt | Belief/desire and self-concern distinctions overlap. Do not claim first general framework; full-paper priority audit remains open. |
| Nisius, Who Is Interrupted? | Author abstract and archive history (v1 2026-08-14; SSRN posted 2026-08-18) | Multiple continuity grades are prior work. Detailed formal comparison is not yet established. |

Links:
- https://link.springer.com/article/10.1007/s43681-026-00983-x
- https://philpapers.org/rec/DUNAIA-3
- https://philpapers.org/versions/DUNAIA-3
- https://philpapers.org/archive/DUNAIA-3.pdf
- https://philpapers.org/versions/NISWII
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7285541

Failures retained: PhilArchive record/full PDF routes and direct public PDF requests returned access errors, including HTTP403. No login, captcha, or credential handling attempted. An arXiv HTML request for 2509.14260v2 failed; no new protocol audit of that empirical study is claimed. Search-indexed excerpts are not a full-text read. No absence of a search hit is treated as proof of originality. Sources already documented in R71 retain their earlier reading limits.

## Three revision checks

**Formal:** verified the sign of the robust bound, its dependence on the range M and regret eta, and the need for known belief rows. Rank refers to exact calibrated contrasts, not four observed choices. Restricting coefficients can alter necessity of full rank. A small singular value concerns stability in the stated known-X model, not all estimation problems.

**Source and novelty:** narrowed the main contribution; removed implied originality of the instrumental/intrinsic distinction. Full closest-neighbor review remains incomplete. The temporal contrast is our proposed evidential refinement, not a finding of actual agent fear or a wholesale refutation of SPT.

**UCT and experience:** retained actual-token/common-K conditions, no arbitrary experience changes at fixed complete organization, no macro-change inference from every micro-change. No fear score, intelligence-to-experience scaling law, or consciousness verdict about the current assistant. A general criterion connecting operational continuity to same-token continuity remains unresolved, and is exposed as an assumption.

## Storage and handoff status

Canonical master checked at version 39, still ending in R70. R71 files exist locally but previous writes failed. One recovery attempt in this turn also returned explicit transfer failures for all three. The final ordered batch of ten items likewise failed for every item; receipt: `r72_final_upload_receipt.json`. No new persistent identity or successful write was returned. The remote master was deliberately not replaced with pointers to unsaved files. The local master has tentative R71 direction text from the previous turn and is excluded from the review package to prevent mistaking it for the canonical update.

To resume elsewhere before storage recovers: provide `UCT_Agent_Manuscript_v0.2_Review_Package_20261005.zip`, read this handoff and the v0.2 manuscript first, then reconcile the canonical master by identity/version before replacing it. The package includes v0.1, v0.2, review records, exact checks/results/logs, and failed-save receipts. Do not restart from R70 just because the remote index is stale. Publication remains unauthorized.

## Conclusion and next action

结论：已形成更严谨的v0.2完整稿，核心从泛泛“智能体会不会自保”收紧到“延续目标能否识别、误解会使结论损失多少”。形式论证有实质修订，但基础数学不是新发现，全文查新尚未闭合，不能说已达到投稿终稿或取得重大意识突破。

下一步只处理两项明确缺口：取得两篇近邻全文以判断具体识别命题的重合；给选定架构的延续关系提供独立操作定义。若全文持续无法取得，维持原创性保留并准备供作者审阅的稿件，不用额外玩具轮次掩盖缺口。先补存当前成品和索引，再接续。不得发布DOI/Zenodo/OTS/Arweave或覆盖已发表论文。
