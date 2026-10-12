# A5H validation

- `python3 check_coarse_o_contrast.py`: PASS; six compatible response models remain, including two invariant-target and four direct-`X` decision models. H-sensitive sign-free restriction leaves two target poles; positive orientation leaves one; an independent fixed-oriented target channel still leaves direct-`X` versus `H` decision ambiguity.
- `python3 audit_map.py <root> <restored map>`: PASS; effective 913 nodes, 424 rules and 261 context links; no unresolved deductive references, cycles or bad `all_of` fields.
- All new and changed JSON parses successfully.
- Formal promotion: none; `MAP_EXTENSION.json` records disabled 0/0/0.
- Source boundary: Miyazaki et al. supply held-stick external localization but only pointer report; Blankenburg et al. supply same-site sequence contrast and somatotopic neural localization on skin, not a held tool. The rows are not pooled into one actual installation.
- Scope boundary: `FIX_COARSE_O_A5F` is not `FIX_COMPLETE_K`.
