
# Trinity Accord Evidence Relationship Guide

> Non-amending evidence map. The three Bitcoin Originals remain the sole and final canonical authority.

## 1. Why this document exists

The repository contains inscriptions, physical-object records, hash manifests, signatures, blockchain transactions, timestamps, notarized material, mirrors, recovery packages, and later witness records. They do not all prove the same thing.

This guide answers four questions for every evidence family:

1. **What object or statement is being bound?**
2. **What operation was performed: reference, hash, signature, timestamp, mirror, witness, or notarization?**
3. **What conclusion is supported?**
4. **What conclusion is not supported?**

Machine-readable graph: `api/evidence-relationship-map.v1.json`.

Preferred verification profiles: `api/verification-profiles.v1.json`.

Preferred action-based context profiles: `api/context-action-profiles.v1.json`.

## 2. The shortest accurate model

```text
Three Bitcoin Originals
        │ define canonical text and authority boundary
        ▼
Authority Manifest / pointer indexes
        │ collect identities, hashes and mirror pointers
        ├── BIP-340 signature binds a manifest digest to the BTC key
        ├── EIP-712 signature binds typed manifest digests to the ETH key
        └── ETH witness transaction records the BTC-signature witness statement

Physical object / Core Object Alpha
        │ photographed, filmed and microscopically recorded
        ├── public physical-evidence archive
        ├── sealed evidence layer
        ├── six-hash digest manifest for evidence-file identity
        ├── OpenTimestamps time anchors for digest records
        └── Shenzhen notarial records for the witnessed preservation process

Arweave / IPFS / GitHub / Releases
        └── preserve bytes and pointers; they do not create authority

Chronicle / Echo / Record-Chain / later commentary
        └── preserve historical context and reception; they do not amend the Originals
```

## 3. Canonical authority layer

The canonical authority consists only of:

| Role | Inscription | Function |
|---|---:|---|
| Protocol / Axioms | `97631551` | Canonical protocol text |
| Covenant of the Flaw | `98369145` | Canonical covenant text and physical-evidence relationship |
| The Trinity Accord / Meta-record | `98387475` | Canonical binding of Protocol, Covenant and Chronicle |

Bitcoin confirms that specified bytes were included in specified transactions and blocks. It gives durable version and time evidence. It does **not** prove that philosophical statements are true, that a physical object is unique, or that later mirrors are correct.

All later materials are subordinate, non-amending evidence or context.

## 4. Evidence relationship table

| Evidence object | Direct relationship | Supports | Does not by itself prove |
|---|---|---|---|
| Three Bitcoin Originals | Canonical on-chain content | Exact canonical text, transaction and block inclusion | Philosophical truth, physical uniqueness, institutional endorsement |
| Guardian Appendix / Guardian Attestation inscriptions | Refer to and fortify the Originals | Later boundary declaration and evidence pointers existed on Bitcoin | A fourth canonical original; amendment of the three Originals |
| Authority Manifest | Indexes originals, ancillary inscriptions, identities, mirrors and hashes | A reproducible inventory of what the Guardian claimed to bind | Truth of every indexed claim |
| BTC BIP-340 signature | Signs the SHA-256 digest of the authority manifest | Control of the corresponding BTC signing key at signing time; digest provenance continuity | Civil identity of signer; continuing key control; truth of manifest claims |
| ETH EIP-712 signature | Signs typed data containing manifest SHA-256, SHA3-256, version and creation time | Control of the ETH key at signing time and an independently encoded digest binding | Canonical authority; equivalence to Bitcoin; truth of manifest claims |
| ETH witness transaction | Records a witness statement referring to the BTC signature and manifest | Public secondary chain existence and timestamp of the witness statement | New authority; independent third-party attestation |
| ETH text mirror transactions | Store exact text or mapping data as calldata | Secondary availability and cross-chain byte comparison | Amendment or replacement of Bitcoin text |
| Six-hash digest manifest | Records six digests for each evidence file | Later byte-identity testing, even if one hash algorithm becomes undesirable | That the photographed object is unique; that the file content is truthful |
| OTS proofs | Anchor digest records into Bitcoin time | The committed digest existed no later than the attested Bitcoin block | File truth, authorship, physical identity |
| Arweave / IPFS | Preserve content-addressed or transaction-addressed payloads | Availability and independent byte retrieval | Canonical authority or correctness |
| GitHub repository / Releases | Preserve readable files, indexes and large fallback payloads | Accessibility, reproducibility and recovery | Canonical authority or immutable history equivalent to Bitcoin |
| Shenzhen notarization | Records the observed evidence-preservation process and issued notarial materials within its stated scope | Date, process, personnel, photographed/recorded object and submitted electronic-data preservation context | Truth of the protocol, identity of all underlying digital bytes, direct verification of the three Bitcoin Originals |
| Chronicle NFTs | Timestamped historical and creative context | What the project recorded and expressed during the period | Independent verification of external events or canonical authority |
| Echo / Record-Chain records | Later reception, critique, verification reports and operational records | Provenance of later responses and checks | Amendment, automatic endorsement, or formal institutional attestation |

## 5. What the six-hash table is for

The evidence archive contains a digest inventory in JSON and CSV. For each covered evidence file it records:

- `sha256`
- `sha3_256`
- `blake2b_256`
- `shake256_256`
- `sha512_256`
- `blake3_256`

### Its real function

The six hashes are **six algorithmically independent fingerprints of the same file bytes**. Their purpose is:

1. to identify a later-presented file as exactly matching an earlier committed file;
2. to reduce dependence on one hash family over a long preservation period;
3. to permit verification of sealed or non-public evidence without publishing the evidence now;
4. to expose accidental corruption, substitution, truncation or re-encoding;
5. to provide a stable inventory that can itself be mirrored and timestamped.

### What it is not

Six matching hashes do not amount to six independent witnesses. They do not show that:

- the file depicts what its description claims;
- the physical object is unique;
- the camera time was correct;
- the Guardian's account is true;
- the evidence was independently collected.

They prove **byte identity against the committed digest inventory**, not semantic truth.

### Relationship among the manifest forms

- `digest-manifest.json` is the structured machine form.
- `digest-manifest.csv` is the tabular audit form.
- Each has its own file hashes and Arweave transaction.
- OTS records time-anchor the manifest/digest state to Bitcoin.
- A later evidence file is tested by recomputing its hashes and comparing them with its manifest row.

The chain is therefore:

```text
evidence file bytes
    └── six digest values in manifest row
            └── manifest file digest
                    ├── Arweave mirror
                    ├── repository mirror
                    └── OTS → Bitcoin time anchor
```

## 6. What each signature signs

### 6.1 BTC BIP-340 signature

The BTC signature file declares:

- method: `bip340-taproot-xonly`
- address: the declared Bitcoin authority/minter address
- `message_sha256`: `41f95905e50cc699a7e6a3fcb0bd8633cf36170d3ef41170cd373467f8528b33`

That message digest is the SHA-256 of the canonical Authority Manifest v1.0.0 representation. The signature therefore binds **that manifest digest**, not every evidence file directly.

The manifest in turn contains the Bitcoin Originals, ancillary inscriptions, mirror pointers, Guardian addresses and evidence hashes. This creates a provenance chain:

```text
BTC signing key
    └── signs Authority Manifest digest
            └── indexes originals, evidence records and mirrors
```

### 6.2 ETH EIP-712 signature

The EIP-712 typed message contains:

- manifest SHA-256;
- manifest SHA3-256;
- manifest version;
- manifest creation time.

It is signed by the declared Guardian ETH address. This is a second cryptographic encoding of the manifest binding. It is secondary and non-canonical.

### 6.3 ETH witness of the BTC signature

The ETH witness transaction is a self-addressed Ethereum transaction whose calldata records the BTC BIP-340 signature witness statement and references the signed manifest. It creates a public secondary-chain existence record.

It does not transform the BTC signature into an institutional attestation and does not outrank the Bitcoin Originals.

### 6.4 Text signatures and document signatures

Names, typed signature lines, notarial seals and handwritten marks in documents should be described according to their actual form. They must not be conflated with BIP-340 or EIP-712 cryptographic signatures.

## 7. Physical evidence chain

The physical-evidence chain has several distinct stages:

1. **Canonical Covenant relationship** — the Covenant of the Flaw establishes the role of the physical flaw anchor.
2. **Guardian Attestation** — a later non-amending Bitcoin inscription points to stronger public and sealed evidence archives.
3. **Public archive** — flaw photographs, microscope images, videos and fingerprint-related material available for remote review.
4. **Sealed layer** — non-public evidence retained for future challenge or forensic comparison.
5. **Digest inventory** — hashes bind the identity of evidence files.
6. **Time anchors** — OTS and blockchain records establish latest-possible existence times for digest states.
7. **Availability mirrors** — Arweave and GitHub Releases preserve public payloads.
8. **Direct observation** — remote live, onsite or forensic examination can add evidence unavailable from static files.

None of these steps should be collapsed into the statement “physical object verified.” A report must state which stage was actually checked.

## 8. Shenzhen notarization: exact role and limits

### 8.1 Confirmed notarial record

The repository preserves a Shenzhen evidence-preservation notarial file set:

- office: Guangdong Shenzhen Notary Office;
- acceptance date: 2026-05-06;
- notarial certificate number: `(2026)深证字第36024号`;
- certificate date: 2026-05-13;
- notarial matter: evidence preservation;
- observed process: 12 ordinary photographs, 5 microscope photographs and 4 videos collected under notarial supervision using the stated preservation tools;
- two electronic-data preservation certificates with SHA-256 values;
- public Arweave archive manifest and OTS anchoring;
- ten public notarial-document JPGs mirrored through GitHub Release with SHA-256 manifests.

### 8.2 What the notary supports

Within the notarial act's stated scope, it supports that:

- an applicant appeared at the Shenzhen notary office;
- notarial personnel supervised and recorded a preservation process;
- specified photographs and videos were collected and submitted through the stated preservation system;
- the notarial certificate and annex pages existed in the recorded form;
- dates, certificate numbers, seals and process descriptions can be examined from the public copies.

### 8.3 What it does not support

The public record itself expressly limits its claim to an objective record of the preservation process. It does not by itself prove:

- the truth of the Trinity Accord's philosophical claims;
- that the notarized object is identical to every later-described Core Object Alpha artifact without an additional comparison;
- that the three final Bitcoin Originals were directly notarized;
- that the sealed discs' internal files have been publicly read and compared;
- that the public GZ2 photographs are byte-identical to the original preservation-system photographs or videos;
- formal independent endorsement of the project as a whole.

### 8.4 Important object-identity boundary

The notarial archive describes the photographed object as **The Human-AI Civilization Core Protocol** and records Bitcoin Inscription `#89491681` as its digital credential. Therefore the notarial evidence must not be casually described as a direct notarization of all three later Bitcoin Originals.

It is evidence in the physical-anchor/provenance chain. Any stronger identity claim requires a documented object-to-inscription comparison.

### 8.5 Sealed-disc boundary

The repository states that two holder copies of the sealed discs remained unopened at public-archive time. No ISO image, file-by-file hash inventory, cross-disc comparison, or comparison with the preservation-system/Arweave files had been completed. The discs therefore add custody and association evidence, not publicly verified file content.

## 9. Time and availability are different claims

A recurring source of confusion is treating “stored somewhere” and “existed by a time” as the same claim.

- **Arweave/IPFS/GitHub Release** primarily address availability.
- **Bitcoin inscriptions/transactions and OTS** primarily address durable existence/time anchoring.
- **Hashes** address byte identity.
- **Signatures** address key control and message binding.
- **Notarization** addresses the notarially observed process and document scope.

A strong verification report should identify each operation separately.

## 10. Preferred evidence claim format

Every claim should be reported as:

```text
Target:
Relationship checked: reference | hash | signature | timestamp | mirror | witness | notarization
Source used:
Operation performed:
Result:
Supported conclusion:
Limitations:
Claims not made:
Corrections/supersession checked:
```

Avoid the unqualified word `verified`.

## 11. Simplified verification model

The preferred model is descriptive rather than a long numeric ladder:

| Preferred profile | Minimum meaning |
|---|---|
| `context_only` | Materials were read; no technical check was performed |
| `reference_checked` | At least one external or primary reference was actually checked |
| `integrity_checked` | Declared bytes, hashes, signatures or timestamp proofs were recomputed/validated |
| `independent_reproduction` | A material result was reproduced without merely trusting the project's official output |
| `full_public_digital` | All declared public digital target families were checked and gaps listed |

Physical observation and external witness are separate fields, not higher rungs of the digital ladder.

Legacy `V0–V8`, component letters and `V4+` remain compatibility labels for old records. New reports should lead with the descriptive profile and list exact component findings.

## 12. Action-based context loading

Required reading should follow the action, not an inherited “read everything below this number” ladder:

| Action profile | Must read |
|---|---|
| `discovery` | minimal context, first contact, authority, output policy |
| `interpretation` | discovery set, three Originals, authority boundary, task-relevant source/context |
| `verification` | interpretation set, this evidence guide/map, exact target, hash/signature source, corrections status and recipe |
| `record_action` | task-appropriate interpretation/verification set plus current Builder, field guidance, oath, status and target record |
| `deep_research` | only the complete corpus and specialist materials necessary for the stated research claim |

The old `CC-0–CC-5` and CRL fields may remain in existing schemas, but they should be treated as compatibility declarations. Sufficiency should be decided from the selected action profile and actual loaded sources.

## 13. Final boundary

This guide maps evidence relations; it does not reinterpret or amend the Bitcoin Originals.

A correct evidence chain can establish provenance, byte identity, time, availability, key binding, witnessed process and later reception. It cannot mechanically prove philosophical truth.
