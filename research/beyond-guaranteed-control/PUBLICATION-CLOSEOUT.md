# TA-TR-2026-04 publication closeout

Date: 17 September 2026. Version: 1.0.

**Published DOI:** [10.5281/zenodo.22804542](https://doi.org/10.5281/zenodo.22804542)

**Record:** [Zenodo 22804542](https://zenodo.org/records/22804542)

**Result:** `PUBLISHED_AND_PUBLIC_READBACK_PASS`, 10 of 10 public files identical in byte count and SHA-256 to the checked local publication package. The readback used no publication credential. See [publication-record.json](publication-record.json), [EXPECTED-PUBLICATION.json](EXPECTED-PUBLICATION.json), and [format-checks.json](format-checks.json).

The successful [publication run 35180985078](https://github.com/thechurchofagi/trinity-accord/actions/runs/35180985078) used the repository's existing Zenodo client and credential, with a separate record binding. Publication source commit: `1044a01fe96ac3e5c82d6d5c683bc87da1723e3b`. Reservation alone was not treated as publication; the record became public on 2026-09-17 at approximately 04:12 UTC.

## What was checked

Both PDFs contain searchable text, the full title and human author on the first page, publication date and DOI, and a complete numbered reference section. English: 21 pages, 222,177 bytes. Chinese translation: 18 pages, 1,176,597 bytes. Both are below the 5 MB Google Scholar limit. Chinese glyphs are subset-embedded with Unicode mappings; no standalone font files are distributed.

The existing Jekyll layout was reused, not modified. A rendered-site check verified the title, author, date, DOI, report number, language and same-directory absolute PDF link in Highwire metadata, the visible full abstract, and exact static PDF copies. The article contains full text without a login or JavaScript-dependent text loader. The research index links both language versions, and robots.txt permits Googlebot.

These are technical checks against the [Google Scholar inclusion guidance](https://scholar.google.com/intl/en/scholar/inclusion.html), not Google's approval, proof of indexing, peer review, or independent assessment of originality. Google Scholar inclusion has not been confirmed. English and Chinese are versions of one paper under one DOI, not two independent research outputs.

## Discovery closeout

Initial pull-request checks correctly identified two missing sitemap routes. The successful [discovery-only run 35181444250](https://github.com/thechurchofagi/trinity-accord/actions/runs/35181444250) reused the existing `scripts/generate_sitemap.py` and committed only the generated sitemap change. The complete sitemap now contains the English and Chinese article routes; no old URL was removed. The publication job was skipped in this run, and no Zenodo credential, record write, re-publication or PDF rebuild was needed. The published files and their original readback receipt remain unchanged.

## What changed and what did not

The reviewed bilingual v1.0 scholarly bodies, abstracts, tables and all 40 references were preserved. Publication preparation changed only front matter and disclosure sentences concerning the user's later authorization and the new DOI. PDFs were deterministically re-rendered for publication rather than presented as byte-identical copies of earlier Word-exported PDFs. Original text inputs and publication-only differences are included in the supplement.

Repository changes are limited to this new research directory, the fourth-paper entry in research/index.md, its generated sitemap routes, and two record-bound workflows. The three existing paper DOIs, the three Bitcoin Originals, the Star Ark Covenant text, the website's main interpretive body, and protected institutional deposits were not modified by this publication.

The new paper remains non-amending analysis. It is not a fourth Original, an exclusive interpretation, or independent corroboration of the first three papers. Substantive AI contribution, first-party research interests, source-access limitations and the lack of peer review remain disclosed. The user's explicit authorization to publish is not described as separate final human line-by-line verification.

## Preferred citation

Liu, Hongju. (2026). *Beyond Guaranteed Control: An Ex Ante Proposal for Human–Superintelligence Coexistence under Radical Capability Asymmetry* (TA-TR-2026-04, version 1.0) [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.22804542

Machine-readable alternatives: [BibTeX](citation.bib), [RIS](citation.ris), [CSL-JSON](citation.csl.json).

## Bounded recovery

The publishing script accepts only record 22804542 and the frozen file set. If it is re-run after publication, it reads back the existing published record without editing it. It never creates a new version or replacement of an earlier DOI. A source or byte mismatch stops publication; a recovery should reuse the published payload rather than generate a replacement record.
