# R202 failures and retained negative results

1. Fresh materialization of fixed Library master v64 returned HTTP 403 twice after a successful current-version check. The previously byte-verified local v64 copy was used only after confirming that the Library still reported v64 and the same file ID. This transient download failure is retained; final replacement/materialization must be retried.
2. The first map audit referenced disabled R201 candidate node `R201:CLASS_CONDITIONAL_DRIFT_BOUNDS`, absent from the authoritative v1.1.2 base. The context was corrected to authoritative `R157:COORDINATE_TRANSPORT`; the audit was rerun and all 20 checks passed.
3. No actual endpoint, audit cohort, class-conditional transport bound or admitted target token was obtained. This is a substantive empirical limit, not a successful validation.
4. The first batch-upload request used an unsupported optional artifact classification and was rejected before any write. The classification was removed and both incremental files then received successful write acknowledgements.
5. Fixed-master replacement to version 65 succeeded, but fresh postwrite materialization again returned HTTP 403. The write acknowledgement, returned version and size are retained; remote byte-for-byte readback remains pending and is not reported as PASS.
