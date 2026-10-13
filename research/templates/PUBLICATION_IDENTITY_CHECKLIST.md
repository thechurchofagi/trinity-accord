# Publication identity checklist

Policy: [PUB-AUTHOR-IDENTITY-20261013](../PUBLICATION_AUTHOR_IDENTITY.md), v1.0.0.
Fill this for each new publication edition; record observed results rather than pre-checking the boxes.

- [ ] Read `research/AUTHOR_IDENTITY.json`; use Hongju Liu / Liu, Hongju consistently.
- [ ] First/title page visibly associates Hongju Liu with `Independent researcher, Shenzhen, China` and `liuhongju3@163.com`.
- [ ] Extracted text from that page contains the exact author email; it is not an image-only or hidden-metadata contact.
- [ ] Source, final PDF, deposit creator and citation files agree on name and affiliation.
- [ ] Public deposit description/contact area explicitly shows the same author and email; only supported API fields are used.
- [ ] ORCID is verified and consistently reused, or explicitly `PENDING_VERIFICATION` with no invented identifier.
- [ ] After DOI injection, repeat the author checks and rebuild final hashes/manifests before publishing.
- [ ] Anonymous published PDF readback matches the frozen bytes and retains the readable author contact.
- [ ] Anonymous landing-page readback shows the public contact, or records an access/readback limitation for correction.
- [ ] Preserve earlier editions and apply DOI -> OTS -> verified Bitcoin attestation -> guarded Arweave/readback in order.
- [ ] When indexed, check the relevant author assignment against `https://openalex.org/A5150552024`; if not yet indexed, record `PENDING_INDEXING`.

Record: work/title/version; DOI; policy version; checked_at; source and PDF SHA-256; rendered first-page review; extracted-text result; deposit name/affiliation/contact result; ORCID verification source or pending status; public readback evidence; OpenAlex work ID and checked author assignment or pending status.

Missing/mismatched author contact prevents a new release. An unavailable or unverified ORCID must not be fabricated. Do not mark indexing or profile correction complete until the corresponding public result has actually been checked. This checklist is completed during normal publication preparation; it does not require a new CI workflow.
