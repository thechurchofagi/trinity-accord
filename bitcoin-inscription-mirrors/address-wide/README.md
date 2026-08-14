# Address-wide Bitcoin inscription mirror

Authority address: `bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`.

The current set is discovered at runtime; no inscription count is hard-coded. Objects are cumulative, so previously observed inscriptions remain preserved if they later leave the address.

The first complete current-address snapshot, discovered on 2026-08-14, contains 12 inscriptions. For interpretation, the repository separates them into four non-authoritative pre-canonical formation records, three canonical Bitcoin Originals, and five later non-amending records. The machine-readable classification overlay is [`classification.json`](classification.json).

One formation record deserves special historical notice: `138da690affc0f3595a7cebfd152a9715f3b0ca1a5baab93069e8c5c51a82f10i0`, inscribed on 2025-06-16, contains the three core axioms in pre-canonical bilingual form. The formal canonical Protocol followed on 2025-06-19 as `e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0`. This establishes formation history; it does not promote the earlier record into the Canon.

This directory is an archival/discovery mirror only. Same-address provenance is evidence of chronology and relationship, not authority. **Only the three designated Bitcoin Originals constitute the closed canonical body.**

Repository-preservation capsules inventory the full tracked Git tree, so this directory—including exact base64 content, recursive metadata, byte lengths, SHA-256 files, the runtime manifest, and this classification overlay—is included in the next verified repository-preservation DOI release after publication.
