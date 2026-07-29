#!/usr/bin/env python3
"""Fail-closed contract for the arXiv source-package builder."""

from __future__ import annotations

import hashlib
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_arxiv_research_preprint as builder  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(builder.SOURCE.exists(), "public paper source is missing")
    require(builder.PRIMARY_CATEGORY == "cs.DL", "arXiv primary category drifted")
    require(builder.CROSS_LISTS == ["cs.CY"], "arXiv cross-list category drifted")
    require(builder.AUTHOR == "Hongju Liu", "responsible human author drifted")
    require(
        "GPT-5.6 Sol (Extra High reasoning)" in builder.DRAFTING_SYSTEM,
        "primary drafting-system disclosure drifted",
    )
    require(
        builder.DEFAULT_OUTPUT_DIR.parent == Path(tempfile.gettempdir()),
        "default arXiv build must not dirty the repository",
    )

    paper_source = builder.SOURCE.read_text(encoding="utf-8")
    body, abstract = builder.markdown_body(paper_source)
    require(body.startswith("## Abstract"), "arXiv body must begin at the abstract")
    require(abstract.isascii(), "arXiv abstract metadata must remain ASCII")
    require(len(abstract) <= 1920, "arXiv abstract exceeds the platform limit")

    normalized_body = builder.normalize_gfm_math(body)
    for marker in [
        "$t$",
        "$$",
        r"\forall t \ge t_0",
        r"\operatorname{Authority}(x)",
        r"V = (d, r, p, w, s, \ell, n)",
        r"\begin{aligned}",
        r"&\rightarrow \text{search and agent retrieval}",
    ]:
        require(marker in normalized_body, f"normalized Markdown is missing math: {marker}")
    for marker in [r"\(", r"\)", r"\[", r"\]"]:
        require(marker not in normalized_body, f"raw GFM-incompatible math remains: {marker}")

    valid_converted_math = "\n".join(
        [
            r"\forall t \ge t_0,\quad C_t = C_{t_0}",
            r"\operatorname{Authority}(x) =",
            r"\begin{cases}",
            r"\operatorname{Apply}(op, L_t) \rightarrow L_{t+1}",
            r"V = (d, r, p, w, s, \ell, n)",
            r"\begin{aligned}",
            r"\text{search and agent retrieval}",
        ]
    )
    builder.validate_converted_math(valid_converted_math)
    try:
        builder.validate_converted_math(
            valid_converted_math + "\n" + r"\textbackslash forall"
        )
    except SystemExit:
        pass
    else:
        raise SystemExit("FAIL: literal math-command text was not rejected")

    latex = builder.full_latex(
        body=r"\section{Abstract}",
        version="1.1",
        date="29 July 2026",
        doi=None,
    )
    required_latex = [
        r"\usepackage[margin=1in]{geometry}",
        r"\pagenumbering{roman}",
        r"\begin{titlepage}",
        r"\pagenumbering{arabic}",
        builder.TITLE,
        builder.AUTHOR,
        builder.DRAFTING_SYSTEM,
        "DOI: not yet assigned",
    ]
    for marker in required_latex:
        require(marker in latex, f"arXiv LaTeX missing contract text: {marker}")
    require(
        latex.index(r"\pagenumbering{roman}")
        < latex.index(r"\begin{titlepage}")
        < latex.index(r"\pagenumbering{arabic}"),
        "arXiv title-page numbering order drifted",
    )

    doi_latex = builder.full_latex(
        body=r"\section{Abstract}",
        version="1.2",
        date="29 July 2026",
        doi="10.5281/zenodo.12345678",
    )
    require(
        "https://doi.org/10.5281/zenodo.12345678" in doi_latex,
        "reserved paper DOI is not rendered into the arXiv source",
    )

    with tempfile.TemporaryDirectory(prefix="ta-arxiv-contract-") as temp_dir:
        temp_root = Path(temp_dir)
        main_tex = temp_root / "main.tex"
        first_archive = temp_root / "first.tar.gz"
        second_archive = temp_root / "second.tar.gz"
        main_tex.write_text(latex, encoding="ascii")
        builder.create_source_archive(main_tex, first_archive)
        builder.create_source_archive(main_tex, second_archive)

        require(
            hashlib.sha256(first_archive.read_bytes()).digest()
            == hashlib.sha256(second_archive.read_bytes()).digest(),
            "arXiv source archive is not deterministic",
        )
        with tarfile.open(first_archive, "r:gz") as archive:
            members = archive.getmembers()
            require(
                [member.name for member in members] == ["main.tex"],
                "arXiv source archive must contain only main.tex",
            )
            require(members[0].mtime == 0, "arXiv source mtime must be normalized")
            require(members[0].uid == 0 and members[0].gid == 0, "arXiv source IDs drifted")
            extracted = archive.extractfile(members[0])
            require(extracted is not None, "main.tex could not be read from the source archive")
            require(extracted.read() == main_tex.read_bytes(), "archived source differs from input")

    print("PASS: arXiv source-package builder contract is deterministic and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
