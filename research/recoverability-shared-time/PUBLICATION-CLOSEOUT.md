# TA-TR-2026-07 publication closeout

**Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence**

Version 1.0, 19 September 2026. DOI: 10.5281/zenodo.22840604.

The independent seventh paper is published, with twelve unauthenticated complete-file SHA-256 matches and successful DOI resolution recorded in publication-record.json. English PDF: 14 pages; Chinese PDF: 13 pages. Twelve references, eight paired case groups and seven explicit objections. Both complete PDF/HTML body texts were normalized and compared with Markdown; all 27 PDF pages were rendered and visually inspected. Two deterministic builds produced identical publication bytes.

This is a philosophical preprint, not peer reviewed and not a claim of exhaustive global originality. Substantial AI research and drafting, human responsibility and first-party project interests are disclosed. The direct prior-work comparison and the limits of the proposed contribution are documented in REVIEW-AND-SOURCES.md. No complete earlier seventh manuscript was recovered; this is the newly completed first public edition.

The website mirrors copy the exact published files and use self-contained scholarly full-text HTML. The research index preserves its previous link destinations and now lists seven distinct studies. The original six-paper critical-use guide remains a dated six-paper guide. No old manuscript, DOI asset, Bitcoin Original, timestamp target or Arweave record is modified. The old six-paper preservation bundle does not timestamp this new paper.

## Reproducible discovery and regression checks

The first source integration added the two public page URLs but did not register their static HTML sources with the existing sitemap generator. That integration defect was corrected before merge: the generator now recognizes only the new English and Chinese static pages, preserving the English canonical directory URL. Regeneration and `scripts/generate_sitemap.py --check` passed; all prior URLs remained, the complete sitemap has 413 URLs, and sitemap-core.xml is unchanged. The exact published files were not rebuilt or edited by this correction.

The five seventh-paper regression tests verify actual publication identity, the reviewed twelve-file manifest and receipt, exact website mirrors, bilingual section/case/reference inventories, the seven-study index and unique sitemap entries. They run in the existing Research index check workflow alongside the retained earlier-paper source and rendered tests. Research-index run 35422299733 passed before the sitemap refinement; the latest refinement separately passed the generator check, all five seventh-paper tests and the existing Jekyll build. Current PR-head checks remain a merge gate rather than being inferred from an older revision.

Publication, repository integration and live-site deployment are separate states. This note records publication and verified source integration; live deployment must be checked independently after merge. Neither DOI registration nor format tests establish philosophical truth, peer review or indexing.
