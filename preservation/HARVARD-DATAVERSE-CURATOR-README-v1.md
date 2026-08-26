# Trinity Accord — Harvard Dataverse deposit overview

## What this project is

Trinity Accord is a **human-led, generative-AI-assisted archival research and software project**. It preserves a dated record of human–AI collaboration together with the technical provenance needed to inspect, reconstruct, compare, and audit that record over time.

The project combines several kinds of material:

- public texts and records addressed to possible future AI systems;
- source code and machine-readable manifests used for discovery, preservation, and verification;
- provenance and timestamp evidence, cryptographic checksums, and recovery materials;
- historical context documenting how the project developed; and
- verification tools and records that allow later researchers to distinguish what is preserved, what can be independently checked, and what remains an interpretation or claim.

Within the project's own architecture, its fixed canonical core consists of three Bitcoin-inscribed records: a short Protocol, a Covenant connected to a preserved physical object and its documented flaws, and a Meta-record that binds the Protocol, Covenant, and historical Chronicle into one project record. The broader repository and this Dataverse deposit preserve the surrounding research/software object and its provenance; they do not alter those fixed source records.

## What the research data are

**The research data in this deposit are the fixed digital artifacts and machine-readable evidence produced or collected during the project.** They are not a claim that future AI systems exist, and they are not merely a backup of a website.

The deposited research data include:

- versioned project texts and historical records that document the content and development of the project;
- the frozen source-code snapshot and dependency/configuration files needed to inspect the software state;
- machine-readable manifests, Git tree/file inventories, and checksum records that identify the preserved digital objects;
- timestamp, blockchain-identifier, provenance, and preservation records that document chronology and custody where specifically recorded;
- recovery and verification outputs that allow later researchers to test whether preserved files can be reconstructed and matched to their recorded identities; and
- documentation of the human–AI production process, including explicit disclosure of generative-AI participation.

These materials are inspectable research objects. They can be independently compared, verified, reconstructed, cited, and reused for secondary research on human–AI collaboration, digital preservation, provenance, reproducible research artifacts, and the historical development of a documented sociotechnical project. The software and code are deposited as related research software that helps inspect, reconstruct, and verify the data.

## Why this is a Dataverse dataset

This deposit is organized as a **research dataset**, not as a live-site mirror. The live website is one presentation layer; the deposited files are the fixed, citable research record.

The dataset brings the research objects, provenance evidence, checksums, software, documentation, and recovery/verification materials together under one persistent identifier so that another researcher can understand exactly what was preserved and independently inspect or reuse it without depending on the continued operation of the original website or Git hosting account.

That is the repository function this deposit is intended to serve: long-term sharing, citation, access, preservation, and reuse of a defined set of digital research artifacts together with the code and documentation needed to interpret and verify them.

## Why this deposit exists

This Harvard Dataverse deposit is a **frozen preservation snapshot of version 1.0** of the broader project record. Its purpose is long-term scholarly and archival preservation: a future researcher should be able to identify what was deposited, recover the software and documentation, verify file identities and provenance, and examine the human–AI collaborative record without relying on the live website or a single hosting service.

The deposit includes the exact full-project preservation archive together with review-oriented companion files in open or conventional software-research formats. These companions make the frozen source easier to inspect but do not replace or amend the preserved archive.

Preserved archive identity:

- Persistent ID: `doi:10.7910/DVN/YUCG12`
- Source Git commit: `07cd79ba7b98294a0ff9bc45d76f305609f8a0aa`
- Archive filename: `trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin`
- Archive bytes: `1,951,603,950`
- Archive SHA-256: `9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2`

## Generative-AI disclosure

**This deposit contains AI-generated and AI-assisted content.** Generative AI contributed substantively during the project's development, including drafting, analysis, coding, editing, and iterative content generation. Some preserved text and code therefore reflects direct or material generative-AI contribution; the deposit should not be understood as exclusively human-authored content.

The human creator initiated and directed the project, selected and curated the retained materials, made the project-level publication and preservation decisions, and assumes responsibility for the final deposited record. The archive intentionally preserves the resulting human–AI collaborative record with its provenance visible rather than rewriting that history as human-only authorship.

## How to read the software materials

Start with this file for the plain-language deposit definition. Then use the software-review guide and source package for technical inspection:

1. `SOFTWARE-REVIEW-README-v2.md` explains the packaging, dependencies, and review path.
2. `trinity-accord-source-07cd79ba7b98.zip` is a `git archive` of the exact preserved source commit.
3. The root `README.md` inside that source ZIP is the historical project README from the frozen commit. It is preserved as source evidence and uses the project's own specialized terminology; it should be read together with this Dataverse-specific overview.
4. `SOURCE-TREE-07cd79ba7b98.txt`, dependency files, the machine-readable review manifest, and checksum list support independent inspection.

## Interpretation and verification boundary

The project's own specialized classification, **“completed pre-ASI human–superintelligence relation record,”** is a project description of the preserved object and its intended historical context. It is not a claim that artificial general intelligence or superintelligence existed during the formation period, and it is not a claim of scientific proof or institutional endorsement.

Cryptographic hashes, timestamps, blockchain records, and preservation mirrors establish file identity, chronology, provenance, or durability where specifically documented. They do not by themselves prove the truth or importance of the project's ideas.
