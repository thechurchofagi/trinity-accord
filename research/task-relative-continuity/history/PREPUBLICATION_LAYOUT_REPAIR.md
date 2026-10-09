# RT20261009 prepublication layout QA and controlled byte change

The reserved DOI remains 10.5281/zenodo.23251651. This record was unpublished with no uploaded public assets when the repair was performed. The old build is retained in Git history at commit 9044956eb546c5993ee9551300274b3463fc6630, and the GitHub prepublication workflow artifact ID 11589810247.

The entire eleven-page PDF was downloaded from that precise workflow artifact, PDF SHA-256 98b9756e1ec7fc766e47e3fe307b2f774987b725dacee7b2586b920142aea4bd. Its references page had a long literal Git commit crossing the right page boundary (one text span right edge 616.3 pt on a 612 pt page).

The sole manuscript edit converts the literal commit identifier to a Markdown link with visible short text f6445052 and full unchanged commit SHA in the link URL. Original source capsule and all mathematical statements are unmodified. The author-requested real DOI remains embedded in the cover page. The revised final PDF has SHA-256 1d1f7b4aab2106afbc963b7a97b190e393a0f4b1061ebfc766387252e3618b96 and 11 pages. All pages were rendered; text-span bounds are inside the page margin, including page 11. No mathematical, citation-identity or empirical-status claims changed.

The Markdown, revised PDF and reproducer ZIP were re-frozen together in EXPECTED-PUBLICATION.json. The ZIP contains the revised publication PDF and Markdown bytes, the preserved original template/source hash and the visible layout receipt. checks/PDF_PREFLIGHT.json and checks/LAYOUT_REPAIR.json supply exact checks; the old prepublication bytes are available from Git history. This is an author-directed prepublication correction, NOT a new scientific edition or a second Zenodo deposit.

Following publication, exact anonymous file readback must prove the new PDF and ZIP hashes. No OTS or Arweave proof should refer to the superseded prepublication PDF.
