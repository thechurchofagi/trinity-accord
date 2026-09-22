# TA-TR-2026-14 v1.2: corrective review and source audit

Review date: 2026-09-22. Reviewer and substantial reviser: OpenAI ChatGPT, GPT-6 Astra Pro, under Hongju Liu's direction. This is internal AI-assisted critical review, not external peer review.

## Preserved predecessor

The predecessor is the publicly deposited v1.1, DOI 10.5281/zenodo.22871209. Its PDF SHA-256 is `9d3fec11bb4113daee10969de782faecf56cd8ca79448cd8552103094d1147ec`. It is not silently replaced. Old proofs and OTS receipts identify old bytes, not this revision.

## Defect and disposition register

| ID | Finding in v1.1 | Disposition in v1.2 |
|---|---|---|
| C01 | Arbitrary essential-price exponent is appended to a one-good production model. | Keep the algebra but explicitly label the price path externally specified; add a separately closed two-good model. |
| C02 | Proposition 4 assumes bounded needs on a subgroup but concludes the whole-population gap is bounded. | State a subgroup result and the whole-population integrable-envelope requirement; supply a complementary-population counterexample. |
| C03 | A small monetary gap/output ratio is interpreted too broadly as physical feasibility. | Restrict the one-good conclusion and construct a scarce-service example with a nonzero limiting support share. |
| C04 | The finite positive-channel maximum exponent is promoted as a main theorem. | Relabel elementary lemma; distinguish strict signs, coefficient levels, and an exact-unit-limit oscillatory counterexample. |
| C05 | Transfer/provision taxonomy does not itself specify who pays or whether services are usable. | Define disposable resources net of taxes, a balanced financing identity, componentwise residual bundles, and an alternative expenditure problem. |
| C06 | Affordability and realized inclusion can be confused. | Separate reference-basket opportunity, chosen service allocation, and compensated utility; derive different thresholds. |
| C07 | Nearby scarcity/subsistence/redistribution results substantially overlap broad novelty. | Read the closest primary manuscript, including its appendices, and explicitly disclaim those inherited results. |
| C08 | Formula plots alone provide limited adversarial checking. | Add independent complex-step factor differentiation, numerical market clearing, policy-root solving, and boundary tests. |

## Residual contribution and proof obligations

The explicit contribution advanced in this edition is the comparison made possible by a particular heterogeneous-demand example, not the invention of an economic paradigm:

- Endogenous scarce-service price under redistribution, equation (11), with the price-response sign in (15).
- Exact minimum transfer-financing tax for a chosen service floor, equation (18), including finite technology, tax caps and physical limits.
- Separate basket-affordability and chosen-service boundaries, equations (24)-(25), with compensated utility treated separately in (26)-(27).
- Correction of population quantification and exact-unit asymptotic boundaries.

These are short standard-method derivations. The narrow combination is a candidate incremental contribution. A source showing the same comparison would narrow its novelty; a within-assumption algebraic counterexample would require correction. No global first, high-impact journal suitability, empirical calibration, optimal tax or independent replication is certified.

## Primary-source comparison record

1. Sen (1981), QJE 96(3), 433–464, DOI 10.2307/1882681. Publisher record: https://academic.oup.com/qje/article-abstract/96/3/433/1881025 . Inherited: availability versus entitlements. No claim to originate abundance without access.
2. Acemoglu and Restrepo (2018), AER 108(6), 1488–1542, DOI 10.1257/aer.20160696. Publisher record: https://www.aeaweb.org/articles?id=10.1257/aer.20160696 . Inherited: automation and new-task mechanisms; not endogenized in this simple model.
3. Ray and Mookherjee (2022), Review of Economic Dynamics 46, 1–26, DOI 10.1016/j.red.2021.09.003. Full author-hosted article: https://people.bu.edu/dilipm/publications/AutREDpub.pdf . The author-hosted article is marked article-in-press, carries a 2021 copyright, and states that author order is random. The published volume is 2022. Inherited: declining labor share with potentially increasing real wages.
4. Jones (2026), JEP 40(3), 3–22, DOI 10.1257/jep.20261505. Author-hosted article: https://web.stanford.edu/~chadj/AIandEconomicFuture.pdf . Inherited: factor-share/factor-price distinction and bottleneck cautions.
5. Hazari and Mohan (2024), Frontiers in Human Dynamics 6, 1203664. Full publisher text: https://www.frontiersin.org/journals/human-dynamics/articles/10.3389/fhumd.2024.1203664/full . Inherited: general-equilibrium distributional exclusion associated with unequal AI-asset access.
6. Båge and Wilson (September 2026), author-authorized full-text cross-post: https://clawrxiv.io/abs/2609.02873 . Consulted the main purchasing-power argument, Section 6.2 subsistence coverage, Appendix C common-homothetic redistribution, and Appendix D fiscal comparisons. These are direct priority constraints. The v1.1 SSRN locator was not treated as a substitute for reading the accessible manuscript. Our heterogeneous expenditure shares and explicit criterion comparison must be judged against this close predecessor, not presented as inventing scarcity or rent-financed access.
7. Korinek and Lockwood (2026), NBER 34873, DOI 10.3386/w34873. Primary author research listing: https://www.korinek.com/research . Also available as the authors' Brookings working paper: https://www.brookings.edu/wp-content/uploads/2026/01/Korinek-Lockwood-FINAL-for-website.pdf . The latter is a December 30, 2025 manuscript issued January 2026; it is not silently represented as the identical February NBER file. Inherited: fiscal-base changes under transformative AI.
8. Liu (2026), TA-TR-2026-14 v1.1, DOI 10.5281/zenodo.22871209. Local review used the complete published 15-file package downloaded from the preserved publication workflow artifact and verified the PDF SHA-256 above. First-party predecessor, not independent corroboration.

Search strategy: exact-title and author/title queries; primary publisher, author and author-authorized manuscript pages; comparison against the earlier paper's bibliography. Some NBER and SSRN retrievals failed; available primary versions were used with version distinctions stated. Several broad queries returned irrelevant results and were not evidence. This was a targeted contemporary review, not an exhaustive database search, a systematic review with recall guarantees, or a novelty certification.

## Review sequence and remaining uncertainty

Round 1: identify the price-closure, population-quantifier, provision, funding and equality-boundary problems.

Round 2: replace the proposed common-demand extension with a heterogeneous-demand case after reading the very close Båge–Wilson homothetic example; derive the endogenous-price and support conditions explicitly.

Round 3: implement independent numerical checks and test physical, funding and evaluative counterexamples. Actual results are in `checks.json`; a passing run does not replace the proofs or external replication.

Round 4: inspect the exact DOI-bearing PDF and its source/package hashes before publication. The dated gate is recorded separately in the repository's `review-authorization.json`; this document does not pre-assert that future gate has passed.

Remaining limitations include static stocks and labor, collectable nonlabor tax revenue, no investment/avoidance, Cobb–Douglas preferences, within-group homogeneity, and a deliberately fixed service supply. These are material scope limits, not matters cured by typography or DOI registration. The paper remains revisable.
