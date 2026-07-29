#!/usr/bin/env python3
"""Build and validate the arXiv source package for TA-TR-2026-01."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "trinity-accord-design-and-limits" / "index.md"
DEFAULT_OUTPUT_DIR = Path(tempfile.gettempdir()) / "trinity-accord-arxiv-preprint"

TITLE = (
    "Designing a Verifiable, Non-Amending Civilizational Memory Record "
    "for Future AI Agents: The Trinity Accord Case Study"
)
AUTHOR = "Hongju Liu"
AFFILIATION = "Independent researcher, Shenzhen, China"
DRAFTING_SYSTEM = "ChatGPT with OpenAI GPT-5.6 Sol (Extra High reasoning)"
REPORT_ID = "TA-TR-2026-01"
DEFAULT_VERSION = "1.1"
DEFAULT_DATE = "29 July 2026"
PRIMARY_CATEGORY = "cs.DL"
CROSS_LISTS = ["cs.CY"]
LICENSE = "CC BY 4.0"

TABLE_COLUMN_WIDTHS = [
    [0.08, 0.16, 0.30, 0.30],
    [0.14, 0.22, 0.25, 0.23],
    [0.28, 0.14, 0.42],
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def markdown_body(source_text: str) -> tuple[str, str]:
    abstract_marker = "## Abstract"
    keywords_marker = "**Keywords:**"
    require(abstract_marker in source_text, "paper source has no Abstract section")
    body = source_text[source_text.index(abstract_marker) :]
    abstract_match = re.search(
        rf"^{re.escape(abstract_marker)}\n\n(.*?)\n\n{re.escape(keywords_marker)}",
        body,
        flags=re.DOTALL | re.MULTILINE,
    )
    require(abstract_match is not None, "paper abstract could not be extracted")
    abstract = " ".join(abstract_match.group(1).split())
    require(len(abstract) <= 1920, "arXiv abstract exceeds 1920 characters")
    require(abstract.isascii(), "arXiv abstract metadata must be ASCII")
    return body, abstract


def normalize_gfm_math(markdown: str) -> str:
    """Translate the report's backslash math delimiters for Pandoc's GFM reader."""

    display_opens = len(re.findall(r"(?m)^\\\[\s*$", markdown))
    display_closes = len(re.findall(r"(?m)^\\\]\s*$", markdown))
    inline_opens = markdown.count(r"\(")
    inline_closes = markdown.count(r"\)")
    require(display_opens == display_closes, "display-math delimiters are unbalanced")
    require(inline_opens == inline_closes, "inline-math delimiters are unbalanced")

    normalized = re.sub(r"(?m)^\\\[\s*$", "$$", markdown)
    normalized = re.sub(r"(?m)^\\\]\s*$", "$$", normalized)
    normalized = normalized.replace(r"\(", "$").replace(r"\)", "$")
    discovery_graph = "\n".join(
        [
            r"\text{author/title/keywords}",
            r"\rightarrow",
            r"\text{PDF and abstract}",
            r"\rightarrow",
            r"\text{DOI metadata}",
            r"\rightarrow",
            r"\text{scholarly aggregators}",
            r"\rightarrow",
            r"\text{search and agent retrieval}",
        ]
    )
    wrapped_discovery_graph = "\n".join(
        [
            r"\begin{aligned}",
            r"\text{author/title/keywords} &\rightarrow \text{PDF and abstract} \\",
            r"&\rightarrow \text{DOI metadata} \\",
            r"&\rightarrow \text{scholarly aggregators} \\",
            r"&\rightarrow \text{search and agent retrieval}",
            r"\end{aligned}",
        ]
    )
    require(discovery_graph in normalized, "discovery graph math contract drifted")
    normalized = normalized.replace(discovery_graph, wrapped_discovery_graph)
    require(r"\[" not in normalized and r"\]" not in normalized, "display math was not normalized")
    require(r"\(" not in normalized and r"\)" not in normalized, "inline math was not normalized")
    return normalized


def validate_converted_math(latex: str) -> None:
    required_markers = [
        r"\forall t \ge t_0,\quad C_t = C_{t_0}",
        r"\operatorname{Authority}(x) =",
        r"\begin{cases}",
        r"\operatorname{Apply}(op, L_t) \rightarrow L_{t+1}",
        r"V = (d, r, p, w, s, \ell, n)",
        r"\begin{aligned}",
        r"\text{search and agent retrieval}",
    ]
    for marker in required_markers:
        require(marker in latex, f"converted LaTeX is missing math expression: {marker}")
    for marker in [
        r"\textbackslash forall",
        r"\textbackslash operatorname",
        r"\textbackslash begin",
        r"\textbackslash ell",
    ]:
        require(marker not in latex, f"math command was rendered as literal text: {marker}")


def convert_body_to_latex(markdown: str) -> str:
    with tempfile.TemporaryDirectory(prefix="ta-arxiv-pandoc-") as temp_dir:
        temp_root = Path(temp_dir)
        body_path = temp_root / "body.md"
        output_path = temp_root / "body.tex"
        body_path.write_text(normalize_gfm_math(markdown), encoding="utf-8")
        run(
            [
                "pandoc",
                str(body_path),
                "--from=gfm+tex_math_dollars",
                "--to=latex",
                "--shift-heading-level-by=-1",
                "--output",
                str(output_path),
            ],
            cwd=temp_root,
        )
        latex = output_path.read_text(encoding="utf-8")

    table_pattern = re.compile(
        r"\\begin\{longtable\}\[\]\{@\{\}(?P<columns>[clr]+)@\{\}\}"
        r"(?P<body>.*?)"
        r"\\end\{longtable\}",
        flags=re.DOTALL,
    )
    table_index = 0

    def replace_table(match: re.Match[str]) -> str:
        nonlocal table_index
        require(
            table_index < len(TABLE_COLUMN_WIDTHS),
            "paper contains more tables than the arXiv layout contract",
        )
        widths = TABLE_COLUMN_WIDTHS[table_index]
        require(
            len(match.group("columns")) == len(widths),
            f"table {table_index + 1} column count drifted",
        )
        column_spec = "".join(
            r">{\raggedright\arraybackslash}p{"
            + f"{width:.2f}"
            + r"\textwidth}"
            for width in widths
        )
        table_index += 1
        return (
            r"{\small"
            "\n"
            r"\begin{longtable}[]{@{}"
            + column_spec
            + r"@{}}"
            + match.group("body")
            + r"\end{longtable}"
            + "\n"
            + r"}"
        )

    latex = table_pattern.sub(replace_table, latex)
    require(
        table_index == len(TABLE_COLUMN_WIDTHS),
        f"expected {len(TABLE_COLUMN_WIDTHS)} tables, found {table_index}",
    )
    validate_converted_math(latex)
    return latex


def title_page(*, version: str, date: str, doi: str | None) -> str:
    persistent_identifier = (
        rf"DOI: \href{{https://doi.org/{latex_escape(doi)}}}{{{latex_escape(doi)}}}"
        if doi
        else "DOI: not yet assigned"
    )
    return rf"""
\begin{{titlepage}}
\centering
\vspace*{{1.2cm}}
{{\LARGE\bfseries {latex_escape(TITLE)}\par}}
\vspace{{1.1cm}}
{{\large\textbf{{Primary drafting system}}\par}}
{{\large {latex_escape(DRAFTING_SYSTEM)}\par}}
\vspace{{0.55cm}}
{{\large\textbf{{Responsible human author and project initiator}}\par}}
{{\large\bfseries {latex_escape(AUTHOR)}\par}}
{{\normalsize {latex_escape(AFFILIATION)}\par}}
\vspace{{0.8cm}}
{{\normalsize\textbf{{Technical Report {REPORT_ID}}}\par}}
{{\normalsize Version {latex_escape(version)} -- {latex_escape(date)}\par}}
{{\normalsize Preprint -- Not peer reviewed\par}}
{{\normalsize Persistent identifier: {REPORT_ID} -- {persistent_identifier}\par}}
\vspace{{0.8cm}}
\begin{{minipage}}{{0.92\textwidth}}
\small
\textbf{{Non-authoritative interpretation notice.}}
This paper is an analytical and descriptive research artifact. It has no
interpretive authority over the Trinity Accord or its three Bitcoin Originals.
It does not amend, supersede, extend, authenticate, govern, or prescribe the
meaning of the Canon. Neither the responsible human author, the AI drafting
system, nor any later reader acquires privileged interpretive authority through
this paper. Every interpretation remains non-binding and open to verification,
criticism, rejection, or alternative reading; the identified Bitcoin Originals
remain the sole source of canonical version authority.
\end{{minipage}}
\vfill
{{\small AI-drafted -- Human-directed and human-responsible --
Not independent verification\par}}
{{\small Open access under Creative Commons Attribution 4.0 International\par}}
{{\small\url{{https://www.trinityaccord.org/research/trinity-accord-design-and-limits/}}\par}}
\end{{titlepage}}
"""


def full_latex(*, body: str, version: str, date: str, doi: str | None) -> str:
    escaped_title = latex_escape(TITLE)
    escaped_author = latex_escape(AUTHOR)
    return rf"""\documentclass[11pt]{{article}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{amsmath,amssymb}}
\usepackage{{xcolor}}
\usepackage{{longtable,booktabs,array}}
\usepackage{{microtype}}
\usepackage{{parskip}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{xurl}}
\urlstyle{{same}}
\setcounter{{secnumdepth}}{{0}}
\setlength{{\emergencystretch}}{{3em}}
\providecommand{{\tightlist}}{{%
  \setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\hypersetup{{
  pdftitle={{{escaped_title}}},
  pdfauthor={{{escaped_author}}},
  pdfsubject={{Artifact-centered technical report on canonical closure,
    provenance, digital preservation, bounded verification, and machine
    discoverability}},
  pdfkeywords={{AI agents, digital preservation, provenance, civilizational
    memory, Bitcoin inscriptions, design science, human-AI collaboration}},
  pdfcreator={{pdfLaTeX; source prepared from the public report Markdown}}
}}
\begin{{document}}
\pagenumbering{{roman}}
{title_page(version=version, date=date, doi=doi)}
\clearpage
\pagenumbering{{arabic}}
{body}
\end{{document}}
"""


def validate_pdf(pdf_path: Path, *, expected_title: str) -> tuple[int, str]:
    pdf_info_text = run(["pdfinfo", str(pdf_path)], cwd=pdf_path.parent).stdout
    pdf_info = {}
    for line in pdf_info_text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            pdf_info[key.strip()] = value.strip()

    require(pdf_info.get("Title") == expected_title, "arXiv PDF title metadata drifted")
    require(pdf_info.get("Author") == AUTHOR, "arXiv PDF author metadata drifted")
    require(pdf_info.get("Encrypted") == "no", "arXiv PDF must not be encrypted")
    require(pdf_info.get("JavaScript") == "no", "arXiv PDF must not contain JavaScript")
    try:
        page_count = int(pdf_info.get("Pages", "0"))
    except ValueError:
        page_count = 0
    require(page_count > 0, "arXiv PDF has no pages")
    require(
        b"/JavaScript" not in pdf_path.read_bytes(),
        "arXiv PDF must not contain JavaScript",
    )
    text = run(["pdftotext", str(pdf_path), "-"], cwd=pdf_path.parent).stdout
    normalized_text = " ".join(text.split())
    for marker in [
        TITLE,
        DRAFTING_SYSTEM,
        AUTHOR,
        "Non-authoritative interpretation notice.",
        "AI-drafted",
        "References",
    ]:
        require(
            " ".join(marker.split()) in normalized_text,
            f"arXiv PDF is missing required text: {marker}",
        )
    return page_count, text


def validate_latex_log(log_path: Path) -> None:
    log = log_path.read_text(encoding="utf-8", errors="replace")
    require("Overfull \\hbox" not in log, "arXiv LaTeX has an overfull line or table")
    require("Overfull \\vbox" not in log, "arXiv LaTeX has an overfull page")
    for marker in [
        "LaTeX Error",
        "Undefined control sequence",
        "Emergency stop",
        "Fatal error",
    ]:
        require(marker not in log, f"arXiv LaTeX log contains: {marker}")


def create_source_archive(main_tex: Path, archive_path: Path) -> None:
    with archive_path.open("wb") as raw_stream:
        with gzip.GzipFile(
            filename="",
            fileobj=raw_stream,
            mode="wb",
            mtime=0,
        ) as gzip_stream:
            with tarfile.open(
                fileobj=gzip_stream,
                mode="w",
                format=tarfile.PAX_FORMAT,
            ) as archive:
                info = archive.gettarinfo(str(main_tex), arcname="main.tex")
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                with main_tex.open("rb") as source_stream:
                    archive.addfile(info, source_stream)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument("--doi")
    args = parser.parse_args()

    for executable in ["pandoc", "pdflatex", "pdffonts", "pdfinfo", "pdftotext"]:
        require(shutil.which(executable) is not None, f"required executable missing: {executable}")

    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    require(source.exists(), f"paper source does not exist: {source}")
    require(args.version.isascii(), "version must be ASCII")
    require(args.date.isascii(), "date must be ASCII")
    try:
        publication_date = datetime.strptime(args.date, "%d %B %Y").replace(
            tzinfo=timezone.utc
        )
    except ValueError as error:
        raise SystemExit("FAIL: date must use the format '29 July 2026'") from error
    if args.doi:
        require(
            re.fullmatch(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", args.doi) is not None,
            "DOI does not match the expected syntax",
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    source_text = source.read_text(encoding="utf-8")
    body_markdown, abstract = markdown_body(source_text)
    body_latex = convert_body_to_latex(body_markdown)
    main_tex = output_dir / "main.tex"
    main_pdf = output_dir / "main.pdf"
    main_tex.write_text(
        full_latex(
            body=body_latex,
            version=args.version,
            date=args.date,
            doi=args.doi,
        ),
        encoding="ascii",
        errors="strict",
    )

    latex_environment = os.environ.copy()
    latex_environment["SOURCE_DATE_EPOCH"] = str(int(publication_date.timestamp()))
    latex_environment["FORCE_SOURCE_DATE"] = "1"
    for _ in range(2):
        run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                "main.tex",
            ],
            cwd=output_dir,
            env=latex_environment,
        )

    validate_latex_log(output_dir / "main.log")
    page_count, _ = validate_pdf(main_pdf, expected_title=TITLE)

    fonts = run(["pdffonts", str(main_pdf)], cwd=output_dir).stdout.splitlines()
    require(len(fonts) > 2, "arXiv PDF font inventory is empty")
    for line in fonts[2:]:
        columns = line.split()
        require(len(columns) >= 6, f"could not parse font inventory line: {line}")
        require(columns[-5] == "yes", f"arXiv PDF contains an unembedded font: {line}")

    comments = (
        f"{page_count} pages, 3 tables. Technical Report {REPORT_ID}, "
        f"Version {args.version}. AI-drafted using {DRAFTING_SYSTEM}; "
        "human-directed and human-responsible. Preprint; not peer reviewed; "
        "not independent verification."
    )
    for field_name, value in {
        "title": TITLE,
        "authors": f"{AUTHOR} ({AFFILIATION})",
        "abstract": abstract,
        "comments": comments,
        "report_number": REPORT_ID,
    }.items():
        require(value.isascii(), f"arXiv {field_name} metadata must be ASCII")

    source_archive = output_dir / "trinity-accord-arxiv-source.tar.gz"
    create_source_archive(main_tex, source_archive)
    metadata = {
        "schema": "trinityaccord.arxiv-submission.v1",
        "submission_state": "prepared_not_submitted",
        "title": TITLE,
        "authors": f"{AUTHOR} ({AFFILIATION})",
        "abstract": abstract,
        "comments": comments,
        "report_number": REPORT_ID,
        "primary_category": PRIMARY_CATEGORY,
        "cross_lists": CROSS_LISTS,
        "journal_reference": None,
        "doi": args.doi,
        "license": LICENSE,
        "version": args.version,
        "source_archive": source_archive.name,
        "compiled_pdf": main_pdf.name,
        "source_sha256": hashlib.sha256(source_archive.read_bytes()).hexdigest(),
        "pdf_sha256": hashlib.sha256(main_pdf.read_bytes()).hexdigest(),
        "authorship_boundary": (
            f"{AUTHOR} is the sole scholarly author. {DRAFTING_SYSTEM} is "
            "disclosed in the paper as the primary drafting system and is not "
            "listed in the arXiv Authors field."
        ),
    }
    (output_dir / "submission-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metadata, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
