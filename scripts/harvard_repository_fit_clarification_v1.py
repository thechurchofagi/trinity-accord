#!/usr/bin/env python3
"""Strengthen the existing Harvard Dataverse v1.0 draft for research-data scope.

This wrapper reuses the fail-closed curator clarification state machine while
making two narrowly scoped improvements requested by curator feedback:
1. define exactly which deposited digital artifacts constitute the research data;
2. explain why the deposit is organized as a citable research dataset rather
   than as a website backup.

If the Dataverse-specific README already exists with older content, it is
replaced in the same unreleased initial draft using Dataverse's file-replace API.
The fixed preservation archive is never replaced. No v1.1 or post-publication
mutation is authorized.
"""
from __future__ import annotations

import json

import harvard_curator_clarification_v1 as base


DESCRIPTION = (
    "Trinity Accord is a human-led, generative-AI-assisted archival research and software project. "
    "It preserves a dated record of human-AI collaboration together with the technical provenance "
    "needed to inspect, reconstruct, compare, and audit that record over time. The project includes "
    "public texts and historical records, source code, machine-readable manifests, provenance and "
    "timestamp evidence, cryptographic checksums, recovery materials, and verification tools.\n\n"
    "The research data in this deposit are the fixed digital artifacts and machine-readable evidence "
    "produced or collected during the project: versioned texts and records; the frozen source-code "
    "snapshot and dependency/configuration files; manifests and Git tree/file inventories; checksums; "
    "timestamp, blockchain-identifier, provenance, and preservation records; recovery and verification "
    "outputs; and documentation of the human-AI production process. These are inspectable research "
    "objects that can be independently compared, verified, reconstructed, cited, and reused for "
    "secondary research on human-AI collaboration, digital preservation, provenance, reproducible "
    "research artifacts, and the historical development of a documented sociotechnical project. "
    "Related software and code are included to help inspect, reconstruct, and verify those data.\n\n"
    "This deposit is organized as a research dataset rather than as a live-site backup. The live "
    "website is one presentation layer; the deposited files are the fixed, citable research record. "
    "The Harvard Dataverse deposit brings the research objects, provenance evidence, checksums, "
    "software, documentation, and recovery/verification materials together under one persistent "
    "identifier for long-term sharing, citation, access, preservation, and reuse.\n\n"
    "This deposit contains AI-generated and AI-assisted content. Generative AI contributed "
    "substantively during development, including drafting, analysis, coding, editing, and iterative "
    "content generation. The human creator initiated and directed the project, selected and curated "
    "the retained materials, made the project-level publication and preservation decisions, and "
    "assumes responsibility for the final deposited record. The archive intentionally preserves the "
    "resulting human-AI collaborative record with its provenance visible rather than presenting all "
    "deposited language or code as exclusively human-authored.\n\n"
    "This Harvard Dataverse v1.0 deposit is a frozen preservation snapshot. Within the project's own "
    "architecture, its fixed canonical core consists of three Bitcoin-inscribed records; the broader "
    "repository and this dataset preserve the surrounding research/software object and its provenance. "
    "The project's specialized phrase 'completed pre-ASI human-superintelligence relation record' is "
    "a project description, not a claim that AGI or superintelligence existed during the formation "
    "period, nor a claim of scientific proof or institutional endorsement."
)

ORIGINAL_ENSURE_README = base.ensure_readme


def ensure_repository_fit_readme(client, token):
    """Verify, add, or safely replace only the Dataverse-specific README."""
    version = base.latest(base.get_dataset(client, token))
    matches = [x for x in base.files(version) if base.file_tuple(x)[1] == base.README_UPLOAD_NAME]
    if len(matches) > 1:
        raise base.ClarificationError("multiple curator README files exist")
    if not matches:
        return ORIGINAL_ENSURE_README(client, token)

    current_id, current_name, _ = base.file_tuple(matches[0])
    if current_name != base.README_UPLOAD_NAME:
        raise base.ClarificationError("unexpected curator README filename")

    try:
        verified_id = base.verify_readme_item(matches[0])
    except base.ClarificationError:
        metadata = json.dumps({
            "description": (
                "START HERE: plain-language definition of the deposited research data, "
                "repository purpose, and explicit generative-AI disclosure requested during curator review."
            ),
            "categories": ["Documentation"],
            "restrict": "false",
            "tabIngest": "false",
            "forceReplace": False,
        })
        with base.README_PATH.open("rb") as fh:
            response = base.require(
                client.post(
                    f"{base.SERVER}/api/files/{current_id}/replace",
                    headers=base.headers(token),
                    files={"file": (base.README_UPLOAD_NAME, fh, "text/markdown")},
                    data={"jsonData": metadata},
                    timeout=600,
                ),
                {200, 201},
                "curator README replace",
            )
        base.log(
            "CURATOR_README_REPLACE PASS "
            f"HTTP={response.status_code} old_id={current_id} sha256={base.digest_file(base.README_PATH)}"
        )
        live = base.latest(base.get_dataset(client, token))
        live_matches = [x for x in base.files(live) if base.file_tuple(x)[1] == base.README_UPLOAD_NAME]
        if len(live_matches) != 1:
            raise base.ClarificationError("curator README not uniquely present after replacement")
        new_id = base.verify_readme_item(live_matches[0])
        return new_id, "replaced"

    base.log(
        f"CURATOR_README VERIFIED existing id={verified_id} sha256={base.digest_file(base.README_PATH)}"
    )
    return verified_id, "verified_existing"


def main() -> int:
    base.DESCRIPTION = DESCRIPTION
    base.USER_AGENT = "trinity-accord-harvard-research-data-scope/1.0"
    base.ensure_readme = ensure_repository_fit_readme
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
