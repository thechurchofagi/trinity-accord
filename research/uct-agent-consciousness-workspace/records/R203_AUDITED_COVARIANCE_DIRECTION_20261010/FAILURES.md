# Failures, corrections and limits

- A local R203 checkpoint already existed, with partial covariance code and a restored review ledger. It was resumed after inspecting its parent R202 remote head; it was not counted as a new completed result or an execution in this turn.
- The first attempt to create r203repo as a worktree failed because it already existed. No files were overwritten by that failed command.
- The remote R202 review-supervision file failed UTF-8 retrieval. The partial R203 checkpoint already restored the full readable ledger, including R202 responses. The restoration is preserved; no OPEN item is closed.
- R202's “within endpoint class” residual test is invalid for checking conditioning on H. It is explicitly superseded by the external-residual-budget requirement.
- Intermediate witness-table transcription did not preserve marginals; tables were constructed from q_h, endpoint means and joint t_h, corrected, and verified before the final note. Marginal algebra alone is insufficient for a feasible joint witness.
- Full semantic adoption across all 1,608 objects is not claimed: mechanical coverage and inherited-compatibility records are distinct from new semantic proof. Candidate stays disabled.
- No real adult data, independent H-positive endpoint, residual budget, actual human use stratum or nonreport transport was obtained.
- PMC openings hit a checking-browser wall; the Keddie publisher text was obtained instead. Hui/Walter and Hoeffding source coverage remains abstract/metadata-limited.
- Prior R202 master v66 was freshly downloaded this turn and matched the local exact bytes, SHA256 50e52672de328802ad75f61d671949dd4c46488ce5e1b73966843aa438897241. This repairs master-readback debt only; the R202 ZIP debt is not silently declared cleared.

- First extended-checker output reused the name negative for both probability tables and a finite-sample scenario. The table export contained string keys despite valid in-memory table checks. Renamed negative_tables and reran; final export contains the exact rational cells.

- First structural audit assumed every baseline context used from/to. TH20261009 retains source/target and declared external-source records; normalizer now accepts both schemas and distinguishes external source anchors from node references. Failed run preserved.

- Review-ledger recovery evidence: starting remote head `c9dd1659b1849863a7c68f18966e5253e4c6b19e` contained a 60,060-byte non-UTF-8 ledger with SHA256 `f4b7ec27993ea66b2182f3b486f4a043a0e178b01baf60782b2cce1a69546ee7`. A file-by-file comparison of the complete research tree against the intended verified R202 local tree found no other mismatch. The restored pre-R203 UTF-8 ledger was 88,613 bytes with SHA256 `828a90d84d01bda2374da4eb9b33164bf61e41f7e08cdb293ea2243f61b16d1a`; the final ledger differs only by the appended R203 response. The precise earlier upload failure mechanism remains unknown.

- Second audit found four typed nondeductive source/module references and mistakenly treated them as node IDs. Ref-type normalization was corrected without changing the frozen graph; references labelled node still require node resolution.
