# UCT-GD-2026-01 v1.1.0 — final preprint preparation

Date: 13 October 2026. Human author of record: Hongju Liu, independent researcher, Shenzhen, China. Substantial analysis, mathematical derivation, code, execution, review and drafting assistance: ChatGPT / GPT-6 Astra Pro.

## Manuscript and exact publication state

**Learning What to Preserve Without Silencing the Body: Adaptive Organization, Mutable Evaluation, and Reference-Calibrated Regulation.** English theoretical/computational preprint, 22 pages, 16 references. Same work as the prepared v1.0.0, not a new independent paper. The original v1.0.0 archive is retained unchanged.

The user asked to refine the final DOI manuscript. No DOI was reserved, no Zenodo draft was created or published, and no OTS or Arweave operation occurred in this revision. The paper is not independently peer reviewed. The title, abstract, author/disclosure, version, proposed metadata, code/results, source-access ledger, claim review and file identities are prepared. Human line-by-line approval is not invented. No PR or requested CI run. No published paper or official UCT map is amended.

**Persistence boundary:** This GitHub directory preserves a detailed final-review handoff and, if the following upload succeeds, the actual validated safeguards module. It does NOT mirror the complete manuscript, PDF, full experiment code, raw outputs or ZIP. The complete final artifacts are downloadable in the originating conversation. Obtain and verify those actual files rather than reconstructing them from this summary. Local paths below are not durable public URLs.

## What survived and what changed

The original scalar radial recovery, predetermined-gain count, exact non-Gaussian moment construction and executed numerical comparison survived review within their declared assumptions. Original code and five primary numerical outputs were reproduced byte-for-byte. The new results close specific misuse routes, not the general consciousness problem.

### GD25: shared path and known sensitivity are not sufficient under directional distortion

The original contract is Pr(no alarm | x,t)=s exp(-t r ||x||^2), with fixed physical coordinates and a centered Gaussian body. The revision explicitly states that a common wire is not proof that every direction has the same sensitivity.

For a generalized held SPD sensor metric G, q(t)=s det(I+2t Sigma G)^(-1/2), and a reference vector v gives ell(v)=log(q0/qv)=v^T G v.

Exact same-path twin: (Sigma1,G1)=(I,I) and (Sigma2,G2)=(diag(1,4),diag(1,1/4)), with common reference e1. Every relative body gain and the reference match, although the physical traces are 2 and 5. The radial scalar formula returns 2 for both if misapplied. This does not refute the original theorem: it exposes violation of the isotropic transduction premise.

Stronger known-metric twin: G=diag(1,4) is identical and known, while Sigma_a=diag(1,2) and Sigma_b=diag(8,1/4). Both weighted spectra are {1,8}; every body gain and every same-device reference match, yet physical traces are 3 and 33/4. Learning G more accurately does not supply covariance orientation from radial data.

Theorem 6: reference matrices vv^T spanning the real symmetric matrices are necessary and sufficient for universal exact identification of G from these fixed quadratic reference readings over the open SPD family. Sufficiency is linear injectivity; necessity uses a nonzero symmetric matrix orthogonal to all vv^T and a small SPD-preserving perturbation. The n(n+1)/2 vectors e_i and e_i+e_j give G_ii=ell(e_i) and G_ij=[ell(e_i+e_j)-ell(e_i)-ell(e_j)]/2.

After reconstruction, a PHYSICALLY implemented input transform H=G^(-1/2) gives H^TGH=I and restores the centered-Gaussian radial trace protocol in unchanged physical coordinates. Postprocessing stored radial bits does not implement H. Directional references, held calibration, a non-feedback evaluation path, and verified actuation are additional physical resources. Singular G cannot be inverted. The theorem is exact-population calibration, not a noisy high-dimensional optimal estimator.

For imperfect equalization K=H^TGH, independent bounds 0<k_L I<=K<=k_U I imply J/k_U<=tr(Sigma)<=J/k_L, where J=tr(K Sigma) comes from the weighted determinant polynomial. A zero lower sensitivity bound gives no finite upper body-deviation bound. This retains implementation error rather than silently setting it to zero.

Polarization, rank arguments, matrix inverse roots and quadratic-measurement recovery are classical. Chen, Chi and Goldsmith (2015), DOI 10.1109/TIT.2015.2429594, is added as relevant prior work. Global priority for this application is not certified.

### GD26: confidence over all candidates is materially stricter than point estimates

The existing 96 selection runs were reanalyzed without drawing new samples. Each seed/environment uses 21 settings and four columns: 84 columns in one decision family. Two-sided Clopper–Pearson tails are alpha/(2*84), alpha=.05. Trials must be independent within each column; dependence between columns is allowed. Confidence is per decision family, not a single 95% claim over all 96 validation families.

The fixed incumbent is p=1. Accept a candidate only when its upper trace bound is strictly below the incumbent's lower bound; otherwise retain the incumbent. Upstream: 4/32 runs certified a mean improvement, 28 retained baseline. Downstream and low-noise: 0/32 each; those incumbents are already population-optimal. All 2,016 finite trace intervals covered simulator truth in this audit and no certificate was false, but this observed count is NOT a universal 100% guarantee. Existing actual point-estimate improvements are preserved, not erased; the new result distinguishes their truth from the amount of available evidence.

This is an application of the already stated interval rule, not a new confidence theorem. It is not a combined online mutable-evaluator learner, a transient-cost analysis, a minimax efficiency claim, or a safety/survival certificate. More efficient interval/likelihood methods remain unexecuted future work.

### GD27: a shifted body is not just covariance

For X~N(mu,Sigma), q(t)=s det(I+2tr Sigma)^(-1/2) exp[-tr mu^T(I+2tr Sigma)^(-1)mu]. The physical total is tr(Sigma)+||mu||^2. The explicit example mu=(1,0), Sigma=diag(.2,.4), r=.5, s=.8 has total 1.6 but returns about .97363 under misapplication of the centered reconstruction. Do not remove a real setpoint error by unobserved recentering. The independently moment-bounded non-Gaussian interval alternative applies to total energy without a zero-mean assumption.

## Actual execution and review scope

All three original calibration/selection/precision programs were freshly executed, and their five primary files matched v1.0 bytes. The added final-revision verifier was executed twice, producing three matching primary files. Eight final output files therefore have exact repeat receipts.

New checks: symbolic anisotropic and known-metric twins; 400 metric reconstructions across dimensions 2–6; 1,200 equalized body-probability comparisons; 400 residual-metric bounds; five reference-span designs; 500 valid probability boxes; 13 malformed inputs and two abstention/inconsistency cases; all 2,016 archived candidate settings. Maximum metric-entry error 3.33e-16, equalization error 3.33e-15 and 2D trace error 2.67e-15. General statements rest on the written proofs, not these finite counts.

The GD v0.3 online experiment was NOT freshly rerun in this revision. Its immutable archive and prior v1.0 re-execution receipt are retained as older evidence, not relabeled as a new execution. An initial streaming-shell request failed because that mode was unavailable; all counted runs were synchronous. No scientific assertion failed in them.

All 22 PDF pages were rendered and reviewed; the added theorem and final conclusion were inspected enlarged. All fonts are embedded, no out-of-page text or overfull boxes were detected, and no font files are distributed. Publication metadata, CFF software-package/preferred-manuscript citation, BibTeX and file manifest distinguish preparation from release.

The full historical UCT semantic map was not re-audited. Official completed map UCT-MAP-v1.1.2 remains unchanged; candidates GD18–GD27 stay disabled as automatic UCT premises. C1/U1 are theory-relative assumptions; no regulation, reference, learned score or successful calibration is made an experience-existence gate. No body ownership, pain, self count, biological lineage or empirical consciousness measure is identified.

## Final artifact SHA-256 identities

Originating final package directory: /mnt/data/Adaptive_Consequence_Calibration_v1.1.0/

- Learning_What_to_Preserve_v1.1.0.pdf: 410208 bytes; 20671c736396b95070ccd7be1af989de4e8ceef987bc6ae531ca1d5dda003f16
- manuscript.md: 70093 bytes; b909666f526dada17c5cedd1f7b87f2c83a411a64d1c37b51727c7a3176093bb
- code/calibration_safeguards.py: 5526 bytes; b468645c8e323b94227d78273885bfe138045e878c2fe778d67adee9b2a32ccb
- code/verify_final_revision.py: 11154 bytes; a4a24c522f8cf16fd379a06b5db5a23cdfd7ded2b77ab4f1de0c429186d720c0
- results/FINAL_REVISION_RESULTS.json: 3592 bytes; 2aa6df2cc0e493bd3a8c0486b31a734bf96f7d9a48a0adeeb0a3da07bfe2d36f
- review/FINAL_SCIENTIFIC_REVIEW.md: 9708 bytes; defe24945efe7a4ddeb4f6d7f67fb7ba1ebd91e95f1f821bfd90181dc3a46feb

Public-facing local download names: Learning_What_to_Preserve_v1.1.0.pdf; Learning_What_to_Preserve_v1.1.0.md; Learning_What_to_Preserve_Final_Review_v1.1.0.md; Adaptive_Consequence_Calibration_DOI_Preparation_v1.1.0.zip.

## Next operational step

Obtain the complete final package and verify its manifest. Inspect the proposed author/rights/abstract/version metadata; no invented ORCID, funding or journal acceptance. With actual publication authorization, deposit the frozen files without overwriting another paper. An actual DOI inserted before publication changes the byte freeze and requires fresh hashes and review. Verify anonymous exact-byte readback after publication, then follow repository DOI -> OTS -> verified Bitcoin proof -> Arweave, with existing budget/reserve/idempotency safeguards. Never use this handoff or a metadata template as evidence that a remote publication succeeded.
