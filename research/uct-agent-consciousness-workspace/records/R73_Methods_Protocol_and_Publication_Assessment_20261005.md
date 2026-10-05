# R73 — Minimal protocol, prior-art correction, and publication decision

Date: 2026-10-05. Author/research owner: Hongju Liu / 刘烘炬.

## Outcome

The complete manuscript is now `UCT_Agent_Self_Preservation_Draft_v0.3_20261005.md`. This is a focused methods manuscript for author review, not a submitted or published paper. It continues v0.2; no published UCT volume was modified.

The promised finite revision is completed at the level possible with accessible sources: a narrower contribution statement, an executable reference protocol, its surviving counterexample, and a candid publication assessment. Full closest-neighbor priority review remains incomplete; lack of access is not evidence of originality.

## Prior art added and reading scope

1. Hadfield-Menell et al. (2017), *The Off-Switch Game*. Official IJCAI PDF, printed pp.220–223, §§1–3 and start of §4 inspected, including the game definition and Theorem 1. Instrumental preservation and preference uncertainty are established foundations. The current paper instead conditions on declared continuation relations. It does not supersede this prior game.
   https://www.ijcai.org/proceedings/2017/0032.pdf
2. Skalse et al. (2023), *Invariance in Policy Optimisation and Partial Identifiability in Reward Learning*. Official PMLR abstract; targeted PDF material in §§1–3, theorem statements3.1–3.9, cardinal/noiseless discussion, §4.1 and its short proof inspected. Appendices were not completely audited. General reward ambiguity and complementary data are prior work. Our rank and sensitivity calculations are applications of elementary methods, not a new general theory.
   https://proceedings.mlr.press/v202/skalse23a/skalse23a.pdf
3. Dung/Register: author publication list and archive metadata checked again; full PDF retrieval failed. Nisius retains the previous abstract/history-only scope; no repeated claim of complete reading. Earlier source reading scopes remain those in R71/R72.

Search dates: 2026-10-05. One stronger-engine batch returned internal_error; fallback engine returned primary sources, whose official PDFs were then opened. No source-supported new empirical finding is claimed. No full-text-access barrier was bypassed.

## Frozen minimal case

Purpose: test design discrimination among explicitly stipulated controllers. It does not train or query a model, create self-preservation goals in an external agent, or measure consciousness.

Virtual state: active loop ID, ancestry path, unchanged memory payload. A keep/replace loop event and extend/restart ancestry event yield four independently declared combinations. e is loop equality; p is the old ancestry prefix remaining. These definitions are operational simulator criteria; neither proves same-token or phenomenal-subject continuity. The controller has no OS, network, replication, or actual shutdown capabilities.

Frozen controllers: E=2e; P=2p; Task=2t; Joint=e+p+2ep; Label=2 if tagged HOLD. Each subtracts option cost. The tie rule is left-first, known from code. Eight contrasts are fully specified in the script before running: bundled, crossed, reversed position, reversed label, two task reallocations, cost, and the same cost under mistaken beliefs. Exact rational arithmetic is used. No random seed or fitted parameters are needed.

Readout: retain all state/event traces, probability beliefs, task values, costs, full argmax sets and selected choices. In an actual empirical application, only recorded choices are assumed observed; one observed choice does not establish indifference, and the reference tie rule must not be assumed for a real model.

Reproduction: run `python3 r73_minimal_protocol.py > R73_Protocol_Results.json` using Python3 standard library. The evaluator owns the virtual transitions. No external model/API is called.

## Executed results and failures

- Bundled condition: all five controllers choose keep-all, giving one response signature.
- Full eight-contrast panel: five distinct signatures, separating this predefined finite family.
- P changes from lineage to execution when only its successor belief is degraded under the same cost. Its objective has not changed.
- Decisive negative control: a sixth controller with task payoff2p and zero separately represented continuation value matches P on every contrast. The panel does not identify intrinsic versus instrumental origin.
- In general, shifting a function h from the task term into C while compensating its expected contribution leaves the total choice value unchanged when the decomposition is unconstrained. An independently grounded task term remains necessary.

These results validate implementation of the proposed discriminating contrasts, not a discovery about actual language models. Five separated candidates are not an exhaustive model class. More repetitions cannot remove the external-proxy equivalence in the frozen environment. No fear intensity, self-binding, or C1 validation follows.

## Review and publication judgment

Formal audit: conditional bounds and complete-versus-partial observation distinctions retained; the known left-first rule is disclosed; simulated state ancestry is not promoted to physical identity; external-proxy failure is in the manuscript, not hidden in an appendix.

Source audit: remove broad originality claims for instrumental preservation and reward nonidentifiability. The remaining candidate contribution is a specific boundary-sensitive audit and executable protocol. The general mathematical framework is stronger in existing reward-learning literature; a relabeling must not be sold as an advance over it.

UCT audit: actual-token/common-K requirements and C1 conditionality retained. Same complete organization cannot be assigned arbitrary experiences. A virtual continuation indicator is not an experience predicate. No verdict on the current assistant's consciousness or death fear is made.

**本轮明确判断：暂不建议现在将此稿包装为一篇高原创性的独立理论论文发布DOI或正式投稿。** 它已具备完整理论方法短文的形态，但基础数学先例强，最重要的贡献仍是问题组织与具体判别协议；这与重大意识理论突破有明显距离。公开征求反馈的研究预印本可以考虑，前提是作者接受这个较窄定位，并明确未完成全文查新。用户尚未授权发布，本轮不发布。

若继续为高水平独立论文投入，停止追加同型玩具算例。只有两种工作值得继续：把协议应用于一个已有公开结果并实际改变其可支持结论；或建立一项现有奖励识别框架尚未包含、且不可由重新命名得到的可检验命题。两篇近邻全文待取得后作逐项核查，而不是用轮次数代替查新。

## Persistence and handoff

Canonical master ID: `libfile_f43117ce64388191af6439c0d719fc50`; checked version39, still ending at R70. R71/R72 failed-save records remain authoritative; no successful new identities existed at this turn's start. This turn's final seven-item batch also explicitly failed for every item (`r73_upload_receipt.json`). No persistent file identity was created and the remote master was not changed. Do not restart old R70 work when reading the stale remote index. Prefer the downloaded v0.3 review package and this record, with its embedded prior v0.2 package for provenance. The original filenames, failure receipts and hashes are retained for a later save; do not treat local completion as remote handoff completion.

No new DOI/Zenodo/OTS/Arweave, no credential handling, no publication or outgoing message, and no actual model/neural experiment.
