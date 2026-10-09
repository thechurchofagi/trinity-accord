# RT-TH: DOI-embedded publication workflow

Research ID: RT20261009; manuscript: RT-TH-PAPER-v1.0.0; creator: Hongju Liu.

The frozen reviewed source is source-main.md (SHA256 52f879101be072efd0651a512b03bac27e3dbf5a80facf55aa726b7515f88ed4).
The original 108,986-byte reproducibility ZIP is RT_TH_Reproducibility_v1.0.0.zip (SHA256 83c0050bfdddff7ac94cf716db107e6f63ef09d9d6b04cd74ead0be4adcb860b).

Publication is intentionally DOI-first and must run through .github/workflows/publish-rt-th-v100.yml, not a manual PDF upload. The publisher saves a create-once intent, obtains a real Zenodo draft DOI, inserts the DOI into the final Markdown and PDF, validates searchable PDF and exact nine-file manifest, saves publish-once intent, publishes once, and anonymously checks every published byte.

The DOI published version is frozen separately in published/. Check publication-record.json, not the workflow green label, before saying publication completed. No OTS stamp or Arweave upload may refer to the preliminary 111,737-byte PDF. Once published, OTS target must refer to the DOI-embedded PDF bytes from publication-record.json. Preserve all pending OTS proofs; only Bitcoin-verified proof unlocks guarded Arweave spend. No journal acceptance or empirical consciousness verification implied.
