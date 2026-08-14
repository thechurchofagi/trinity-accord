# Address-wide Bitcoin inscription mirror

Authority address: `bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`.

The current set is discovered at runtime; no inscription count is hard-coded. Objects are cumulative, so previously observed inscriptions remain preserved if they later leave the address.

For every inscription, the archive preserves the inscription body returned by `/content/<ID>` and the independent tag-5 CBOR metadata returned by `/r/metadata/<ID>` when present. HTTP 404 from that optional metadata endpoint is recorded as absence, not as a synchronization failure. A human-readable decoded metadata JSON is only a derivative; the exact CBOR bytes and SHA-256 remain the preserved verification source.

This is an archival/discovery mirror only. The three Bitcoin Originals remain the canonical body.
