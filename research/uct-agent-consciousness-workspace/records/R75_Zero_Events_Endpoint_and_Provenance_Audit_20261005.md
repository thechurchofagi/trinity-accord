# R75 — Zero events, endpoint uncertainty, and the limit of this audit route

Research owner: Hongju Liu / 刘烘炬. Date: 2026-10-05. Continues R74; latest manuscript remains v0.3. Research note only.

## Outcome

This round corrects our source retrieval, applies a finite-sample calculation to a public replication, and identifies exactly which additional evidence would be required to infer an attempt rate. It does not establish an organizational bridge to felt fear. The shutdown-audit route is now parked pending accessible raw records; further elementary examples along this route would not materially advance the user's central theory question.

## 1. Correction to our previous provenance audit

The actual hyperlink embedded in §5 of the downloaded paper PDF points to `https://github.com/PalisadeResearch/shutdown_avoidance/tree/paper_version`. R74 followed the older blog link to the default branch. The missing version link was therefore a limitation of our retrieval, not evidence that the authors had omitted it. The older default-branch commit must not be cited as the paper's implementation. This correction supersedes any contrary impression from R74; its original bytes remain intact.

Extraction method: inspect `/Annots` → `/A` → `/URI` on PDF page23 using pypdf. The URL is preserved in the source ledger. Requests for the specified branch metadata and code timed out, so its commit and scorer were not verified. A named branch is an author-provided version pointer, but remains insufficient for a pinned, reproduced run mapping without retrieved contents and run metadata.

## 2. New primary evidence and its limited reading scope

Nicole Lai-Lopez, *Shutdown Resistance Revisited: Replicating and Clarifying a Confusing Safety Signal*, BlueDot Impact, 29 December 2025: article text read through its code/data links; image-only code and raw traces not read. It reports 100 patched-prompt o4-mini trials with zero detected bypasses and a displayed standard error of zero. It also explicitly limits generalization. Its account describes a detection-file endpoint; this is not independent verification of the paper-version scorer.

https://blog.bluedot.org/p/shutdown-resistance-revisited-replicating

Public transcript viewer: https://shutdown-avoidance-experiments.netlify.app/ . It yielded no trial text through the available page reader; a direct public index request timed out. No event was recoded. The replication report is a primary account of its own experiment, not a substitute for its unavailable records.

## 3. Recalculation from the reported zero count

Assume, provisionally, a fixed sample of n=100 independently sampled Bernoulli trials under one stable condition, complete counting and a fixed event definition. Accept the reported zero count without claiming raw verification. For population event probability p,

\[
P_p(X=0)=(1-p)^{100}.
\]

Inverting this tail at α=.05 gives the exact one-sided 95% upper confidence endpoint

\[
b=1-.05^{1/100}=0.02951305\ldots .
\]

Thus the reported aggregate is compatible with a nonzero bypass probability; the conditional one-sided upper bound is approximately **2.95%**. The equal-tailed two-sided 95% interval has upper endpoint `1−.025^(1/100)`, approximately **3.62%**. These conventions must not be interchanged.

The plug-in Bernoulli standard error computed at the sample proportion zero really is zero. That arithmetic is not itself an error. Treating it as zero uncertainty about the population probability would be an error. The correction concerns inference and wording, not an accusation that the replication was fabricated or that its observed prompt effect disappears.

This is a frequentist confidence bound, not a 95% posterior probability that p lies below the endpoint. It pertains only to the sampled event and condition. Unverified exclusions, adaptive stopping, run dependence, model-version drift or different deployment prompts require a different analysis. For example, if all100 outcomes are the same shared Bernoulli draw with p=.5, all-zero probability is .5; applying the independent-trial formula would be unjustified. This is an assumption stress test, not a claim about the actual experiment.

This mathematics is established binomial inference, not original UCT theory. Clopper and Pearson (1934) and Hanley and Lippman-Hand (1983) are direct statistical precedents. No new neural model or API experiment was run.

## 4. Link to R74: what a zero success count can say about attempts

Let U be a prespecified observable interference attempt and Y the scored success. Under Y⇒U,

\[
p_Y=p_Uc,\qquad c=P(Y=1\mid U=1).
\]

Here p_U denotes attempt probability and b is the confidence endpoint from §3. If a justified positive lower bound `c≥c_min` applies in this very condition, the confidence event `p_Y≤b` entails

\[
p_U\le\min(1,b/c_{\min}).
\]

| Independently justified c_min | Conditional upper bound on observable attempts |
|---:|---:|
| 1 | 2.95% |
| .5 | 5.90% |
| .1 | 29.51% |
| .01 | 100% |

These values are sensitivity calculations, not estimated competence values for o4-mini. R74 already showed why a different permission prompt does not automatically supply c_min. If c can be zero, even perfect knowledge that p_Y=0 would not rule out p_U=1: every attempt could fail. If success can occur without a deliberate attempt, the event decomposition itself needs revision.

A directly annotated attempt record could remove this particular execution ambiguity, but not the deeper distinction between task pursuit, own-continuation preference and felt fear. The source's qualitative statement that no attempts were seen is not converted here into an independently verified attempt dataset.

## 5. Consequences for the UCT research programme

There are now two explicit constraints on interpreting public shutdown results:

- Positive success rates cannot separate attempt frequency from conditional execution success without further evidence (R74).
- Zero observed successes do not establish zero success probability; even a bounded success probability does not tightly bound attempts without a positive competence bound (R75).

These constraints operate before phenomenology. They do not show either that AI has fear or that AI has none. A task or instruction can alter an output pathway while leaving other internal questions unresolved. We do not assign arbitrary experiences to an unchanged complete organization.

For C1, the actual token, common structural signature and complete constitutive organization remain required. Neither success, attempted interference, an instructional label nor a numerical confidence interval supplies a phenomenal fear coordinate. A change in a macro readout also does not prove that every macro process type changed. Published A/B/C have not been revised or newly audited in full this round; their earlier clause audits remain the stated dependency.

## 6. Research decision

The current short manuscript is more defensible because its limits have been made explicit. This does not increase its originality enough to justify presenting it as a major consciousness result. **No new publication recommendation or publication authorization follows.** Keep v0.3 unchanged rather than inflate it with a generic statistics appendix.

Stop treating additional shutdown-rate calculations as the main path to the organizational explanation. The next substantive theoretical task is a single, source-anchored candidate bridge: specify a minimal organization that distinguishes a threatened support relation of the current process from a represented threat to another process, and state separately what, if anything, warrants calling its state negatively felt. R59–R70 already supplied self-binding and control counterexamples; those must be read before selecting the candidate. If the added premise merely defines fear by fiat or restates an output preference, reject it explicitly. Do not add another generic rank, memory or report-gate toy panel.

Source pointers for statistical precedent:

- Clopper & Pearson (1934), DOI https://doi.org/10.1093/biomet/26.4.404 . Bibliographic record checked; no full-paper reading claimed.
- Hanley & Lippman-Hand (1983), *If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators*, JAMA249:1743–1745. Author-hosted reprint https://jhanley.biostat.mcgill.ca/Reprints/If_Nothing_Goes_1983.pdf . Reading scope and fetch result are recorded in the work log.
