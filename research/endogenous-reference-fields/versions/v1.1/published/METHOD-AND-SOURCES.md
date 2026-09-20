# Method, source and final review — TA-TR-2026-10 v1.1

Source: user-supplied 内生参照场_终稿交付(3).zip. SHA-256: cf83bdd4a84c84464e9554c8e0e1022ab9b95240edefc36408fea862e4f3cc42. The uploaded manuscript is the substantive base; this is a reviewed revision, not a verbatim deposit of its PDF.

## Evidence and changes

All three original programs were executed. Nine models were fully retrained with the original code and all 171 numeric results reproduced exactly on Python 3.12 / NumPy 2.3.5. Accuracy was 100% in all nine fixed 2000-sequence tests. No seeds were discarded. Raw results.json is byte-preserved. Original trained weights/environment were not supplied; the deposited weights are from this rerun. No claim of preregistration or absence of earlier exploratory tuning is made.

The original numerical algorithms have no detected result-changing bug. The measure.py entry point now avoids overwriting the raw results and prints scientific notation. A portable reproduce.py adds comparison and post-hoc diagnostics. Full retraining used the original computational functions; the final measure.py functions were separately checked with the same weights and reproduce the same numbers.

The revised paper separates theoretical suprema m_i(s) from finite-probe means, total-variation persistence from norm retention, and content feedback from the supplied event-flip metric. It retains T2 seed 0's nonzero modulation, T3's nonzero tail, both unequal channels, every seed, and the effects of the 1e-12 norm denominator. Appendix C specifies T3's whole-prompt-history reversal and its common continuation inputs. The no-switch window is a deliberate intervention, not a natural test distribution. Independent random streams are used for training, task testing, and organizational probes.

Theoretical corrections retain the discriminating constructions while adding their necessary conditions: compatible shared interventions; real update effects rather than graph paths alone; invariant protocol for the symmetry proof; no claim excluding all macroscopic grains; no general refutation of IIT 4.0 or all functionalism; no claim that one unfolded intervention requires N interventions; no automatic inference from broadcasting to zero modulation. Necessity and sufficiency are both bridging conjectures. P3 principally tests sufficiency. Support persistence is not decay speed; division by zero content duration is not used.

The finite verification program enumerates 8 controller states and 8 × 4^4 restricted input prefixes for the slow construction, extending the last input afterward. It samples 300 initial states for the rings/torus and 500 parity trajectories. It does not exhaust all ring states or all length-12 input sequences. Algebra, not finite sampling, supports the all-horizon statements. The training experiment measures organization only and does not establish complete ERF criteria or machine consciousness.

## Citation-to-claim review

- Albantakis et al. (2023), PLOS DOI 10.1371/journal.pcbi.1011465: IIT 4.0 axioms and causal commitments, not a computed IIT result for the submitted toy model.
- Aaronson (2014), https://scottaaronson.blog/?p=1799 and the exchange at https://scottaaronson.blog/?p=1823: historical XOR-grid dispute. The exchange links Tononi's response; the DOCX itself was unavailable to direct extraction in this review. The statement is retained as historical discussion, not a new IIT calculation.
- Aru et al. (2020), DOI 10.1016/j.tics.2020.07.006: Dendritic Information Theory and cellular integration. Suzuki & Larkum (2020), DOI 10.1016/j.cell.2020.01.024: anesthetic dendrite/soma decoupling in mice. Neither directly validates ERF's three criteria.
- Phillips et al. (2015), DOI 10.1016/j.neubiorev.2015.02.010, and Salinas & Sejnowski (2001), DOI 10.1177/107385840100700512: contextual/gain modulation. The latter publisher metadata prefixes its title with “Book Review”; authors, pages and abstract identify the cited gain-modulation article.
- Dehaene & Changeux (2011), DOI 10.1016/j.neuron.2011.03.018: conscious processing/global workspace; a copying bus is not the full theory.
- Doerig et al. (2019), DOI 10.1016/j.concog.2019.04.002, and Hanson & Walker (2021), DOI 10.1093/nc/niab014: unfolding/falsifiability objections. Hanson & Walker are cited as a challenge, not as endorsement of ERF's proposed response.
- Casali et al. (2013), DOI 10.1126/scitranslmed.3006294: perturbational complexity, not ERF modulation or proof of a phenomenal bridge.
- Gu & Dao (2023), https://arxiv.org/abs/2312.00752: selective state spaces. The toy model is explicitly not Mamba. Hoel (2026), https://arxiv.org/abs/2512.12802v3: continual-learning argument, distinguished from fixed-weight state updates.
- Kleiner (2020), DOI 10.3390/e22060609: mathematical consciousness modelling; no attribution of ERF's necessity proof. Herzog et al. (2007), DOI 10.1016/j.neunet.2007.09.001: small-network objection.
- Safron (2020), DOI 10.3389/frai.2020.00030, and Williford et al. (2018), DOI 10.3389/fpsyg.2018.02571: neighbouring modelling approaches; priority for perspective-based theories is not claimed.
- Leopold & Logothetis (1999), DOI 10.1016/S1364-6613(99)01332-7: multistable perception as motivation, not proof of a unique slow physical variable.
- VanderWeele (2015), Explanation in Causal Inference, OUP ISBN 9780199325870: interaction methodology background, not attribution of the exact ERF formula. Vershynin (2018), DOI 10.1017/9781108231596: standard metric/packing background; the manuscript states its own elementary proofs and parameter ranges.

Bibliographic metadata and relevant available primary abstracts/texts were checked. Full-text access was not available for every source, and no exhaustive originality certification is claimed. The manuscript retains 20 references and provides direct publication/source links. No long third-party passages or figures are reproduced.

## Editorial and publication scope

Chinese full text, English title and abstract; non-peer-reviewed preprint; substantial ChatGPT/Codex assistance in research, theory, code, criticism and production, with Hongju Liu responsible for publication. v1.1 revises v1.0 under the same Zenodo concept. The first edition's bytes and citation history are retained. New publication checksums and any later preservation evidence are version-specific. Old OTS/Arweave receipts do not cover this revision.
