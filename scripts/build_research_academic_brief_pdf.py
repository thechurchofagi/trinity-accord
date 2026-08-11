#!/usr/bin/env python3
"""Build the one-page academic brief for TA-TR-2026-01 v1.1."""
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "research"
    / "trinity-accord-design-and-limits"
    / "trinity-accord-academic-brief-v1.1.pdf"
)
TITLE = "Designing a Verifiable, Non-Amending Civilizational Memory Record for Future AI Agents"
SUBTITLE = "The Trinity Accord Case Study - Academic Brief"
DOI = "10.5281/zenodo.21699878"
LANDING = "https://www.trinityaccord.org/research/trinity-accord-design-and-limits/"

# ReportLab otherwise embeds the build time and changes the PDF bytes on every
# run. The academic brief is a versioned dissemination artifact, so keep it
# deterministic.
rl_config.invariant = 1


def register_fonts() -> None:
    paths = {
        "BriefSans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "BriefSans-Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "BriefSerif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    }
    for name, path in paths.items():
        font_path = Path(path)
        if not font_path.is_file():
            raise FileNotFoundError(f"required font is missing: {path}")
        pdfmetrics.registerFont(TTFont(name, str(font_path)))


def styles() -> dict[str, ParagraphStyle]:
    navy = colors.HexColor("#17364a")
    slate = colors.HexColor("#405866")
    return {
        "title": ParagraphStyle(
            "BriefTitle",
            fontName="BriefSans-Bold",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            textColor=navy,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "BriefSubtitle",
            fontName="BriefSerif",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=slate,
            spaceAfter=5,
        ),
        "meta": ParagraphStyle(
            "BriefMeta",
            fontName="BriefSans",
            fontSize=7.7,
            leading=10.5,
            alignment=TA_CENTER,
            textColor=slate,
        ),
        "summary": ParagraphStyle(
            "BriefSummary",
            fontName="BriefSerif",
            fontSize=9.2,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#20313b"),
        ),
        "heading": ParagraphStyle(
            "BriefHeading",
            fontName="BriefSans-Bold",
            fontSize=10,
            leading=13,
            textColor=navy,
            spaceBefore=5,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BriefBody",
            fontName="BriefSerif",
            fontSize=8,
            leading=11.2,
            textColor=colors.HexColor("#25323a"),
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "BriefBullet",
            fontName="BriefSerif",
            fontSize=7.8,
            leading=10.8,
            leftIndent=8,
            firstLineIndent=-6,
            textColor=colors.HexColor("#25323a"),
            spaceAfter=2.2,
        ),
        "footer": ParagraphStyle(
            "BriefFooter",
            fontName="BriefSans",
            fontSize=6.7,
            leading=9,
            alignment=TA_CENTER,
            textColor=slate,
        ),
    }


def section(
    style_map: dict[str, ParagraphStyle],
    heading: str,
    paragraphs: list[str] | None = None,
    bullets: list[str] | None = None,
) -> list:
    items: list = [Paragraph(heading, style_map["heading"])]
    for text in paragraphs or []:
        items.append(Paragraph(text, style_map["body"]))
    for text in bullets or []:
        items.append(Paragraph("- " + text, style_map["bullet"]))
    return items


def page_chrome(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#17364a"))
    canvas.rect(0, height - 5 * mm, width, 5 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#b7c7cf"))
    canvas.line(14 * mm, 12 * mm, width - 14 * mm, 12 * mm)
    canvas.setTitle(f"{TITLE}: {SUBTITLE}")
    canvas.setAuthor("Hongju Liu")
    canvas.setSubject("One-page academic brief for Technical Report TA-TR-2026-01 v1.1")
    canvas.setKeywords("AI agents, digital preservation, provenance, design science")
    canvas.setCreator("ChatGPT with OpenAI GPT-5.6 Sol; PDF production via ReportLab")
    canvas.restoreState()


def build(output: Path) -> None:
    register_fonts()
    style_map = styles()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
        title=f"{TITLE}: {SUBTITLE}",
        author="Hongju Liu",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="Brief", frames=[frame], onPage=page_chrome)])

    summary = (
        "This artifact-centered design case asks how a bounded human-origin record can remain "
        "version-stable while later systems discover, verify, criticize, preserve, or refuse it "
        "without allowing those later layers to rewrite the source object. The contribution is an "
        "inspectable design pattern, not a general theory, alignment result, or claim of authority."
    )
    summary_box = Table(
        [[Paragraph(summary, style_map["summary"])]],
        colWidths=[doc.width],
    )
    summary_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef4f6")),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor("#8aa4b2")),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    left = []
    left += section(
        style_map,
        "Contributions",
        bullets=[
            "A six-layer architecture separating Canon, context, evidence, mirrors, later records, and stewardship.",
            "A non-amendment invariant and an explicit separation of version authority from truth authority.",
            "A vector verification model that keeps unlike evidential dimensions separate.",
            "A role-first machine-access pattern for provenance and instruction safety.",
        ],
    )
    left += section(
        style_map,
        "Research questions",
        bullets=[
            "How can a fixed source coexist with revisable access and evidence layers?",
            "How can machine readers distinguish source, context, evidence, interpretation, and instruction?",
            "How can verification remain bounded instead of collapsing into one inflated score?",
            "How can a record remain discoverable without confusing visibility with authority?",
        ],
    )
    left += section(
        style_map,
        "Evidence base",
        paragraphs=[
            "Public repository snapshot; three Bitcoin inscriptions; a 175-entry human-AI Chronicle; a physical evidence anchor; timestamp and mirror records; machine-readable routes; an append-only Record-Chain; and automated verification materials. First-party evidence is labeled as such."
        ],
    )
    left += section(
        style_map,
        "Reproducibility",
        bullets=[
            "Full paper, source, references, checksums, APIs, and public repository are open.",
            f"DOI: <link href=\"https://doi.org/{DOI}\" color=\"#315a8a\">{DOI}</link> - CC BY 4.0.",
        ],
    )

    right = []
    right += section(
        style_map,
        "Limits and negative results",
        paragraphs=[
            "The report does not demonstrate successful AI alignment, philosophical truth, forensic uniqueness of the physical anchor, independent validation, autonomous discovery, future relevance, representation of humanity, or interpretive authority. Preservation is not endorsement; immutability is not truth; availability is not authority."
        ],
    )
    right += section(
        style_map,
        "Useful review questions",
        bullets=[
            "Does the layer model prevent canonical drift and provenance-role collapse?",
            "Are the verification dimensions independent and auditable?",
            "Does role-first access reduce instruction confusion without overclaiming control?",
            "Which claims need reproduction, comparison cases, or empirical agent studies?",
        ],
    )
    right += section(
        style_map,
        "Recommended scholarly use",
        paragraphs=[
            "Suitable as a design-science case, digital-preservation example, provenance and agent-memory discussion object, or seminar reading. It should be cited and criticized as a bounded preprint, not treated as an endorsed standard or independent validation."
        ],
    )
    right += section(
        style_map,
        "Authorship and disclosure",
        paragraphs=[
            "Most prose, structure, literature synthesis, editing, consistency checking, and document production were generated by ChatGPT using OpenAI GPT-5.6 Sol under Hongju Liu's direction. Hongju Liu approved publication and accepts responsibility. The model is not a scholarly author, independent verifier, or OpenAI endorsement."
        ],
    )

    columns = Table(
        [[left, right]],
        colWidths=[86 * mm, 86 * mm],
        hAlign="CENTER",
    )
    columns.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 5),
                ("LEFTPADDING", (1, 0), (1, -1), 5),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("LINEBEFORE", (1, 0), (1, -1), 0.5, colors.HexColor("#c4d0d6")),
            ]
        )
    )

    citation_box = Table(
        [[Paragraph(
            "<b>Suggested citation:</b> Liu, H. (2026). <i>Designing a Verifiable, "
            "Non-Amending Civilizational Memory Record for Future AI Agents: The "
            "Trinity Accord Case Study</i> (Technical Report TA-TR-2026-01, Version "
            f"1.1). The Trinity Accord Project. DOI: {DOI}<br/>"
            "<b>Keywords:</b> AI agents; digital preservation; provenance; civilizational "
            "memory; cryptographic timestamping; machine-readable archives; design science; "
            "human-AI collaboration.",
            style_map["body"],
        )]],
        colWidths=[doc.width],
    )
    citation_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f7f8")),
                ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#b7c7cf")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story = [
        Paragraph(TITLE, style_map["title"]),
        Paragraph(SUBTITLE, style_map["subtitle"]),
        Paragraph(
            "Hongju Liu - Independent researcher, Shenzhen, China | TA-TR-2026-01 | "
            "Version 1.1 | 29 July 2026 | Preprint, not peer reviewed",
            style_map["meta"],
        ),
        Spacer(1, 4 * mm),
        summary_box,
        Spacer(1, 3 * mm),
        columns,
        Spacer(1, 2 * mm),
        citation_box,
        Spacer(1, 2 * mm),
        Paragraph(
            f'<link href="{LANDING}" color="#315a8a">{LANDING}</link><br/>'
            "Non-amending research communication - no interpretive authority over the Trinity Accord Canon.",
            style_map["footer"],
        ),
    ]
    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.output.resolve())
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
