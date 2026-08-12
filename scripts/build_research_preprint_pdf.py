#!/usr/bin/env python3
"""Build the searchable TA-TR-2026-01 PDF from its public Markdown source."""

from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

# Keep the corrected PDF reproducible across local and GitHub builds.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1786449600")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "trinity-accord-design-and-limits" / "index.md"
OUTPUT = (
    ROOT
    / "research"
    / "trinity-accord-design-and-limits"
    / "trinity-accord-design-and-limits-v1.1.pdf"
)

TITLE = (
    "Designing a Verifiable, Non-Amending Civilizational Memory Record "
    "for Future AI Agents"
)
SUBTITLE = "The Trinity Accord Case Study"
AUTHOR = "Hongju Liu"
DRAFTING_SYSTEM = "ChatGPT with OpenAI GPT-5.6 Sol (Extra High reasoning)"
REPORT_ID = "TA-TR-2026-01"
VERSION = "1.1"
DATE = "29 July 2026"
CORRECTION_DATE = "11 August 2026"
DOI = "10.5281/zenodo.21699878"


def register_fonts() -> None:
    candidates = {
        "DejaVuSerif": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif.ttf",
        ],
        "DejaVuSerif-Bold": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf",
        ],
        "DejaVuSerif-Italic": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ],
        "DejaVuSansMono": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
        ],
    }
    for name, paths in candidates.items():
        font_path = next((Path(p) for p in paths if Path(p).exists()), None)
        if font_path is None:
            raise FileNotFoundError(f"Required font not found: {name}")
        pdfmetrics.registerFont(TTFont(name, str(font_path)))
    pdfmetrics.registerFontFamily(
        "DejaVuSerif",
        normal="DejaVuSerif",
        bold="DejaVuSerif-Bold",
        italic="DejaVuSerif-Italic",
        boldItalic="DejaVuSerif-Bold",
    )


def strip_front_matter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)


def inline_markup(text: str) -> str:
    placeholders: dict[str, str] = {}

    def save_markup(value: str) -> str:
        key = f"@@MARKUP{len(placeholders)}@@"
        placeholders[key] = value
        return key

    def link_repl(match: re.Match[str]) -> str:
        label = html.escape(match.group(1), quote=False)
        url = html.escape(match.group(2), quote=True)
        return save_markup(f'<a href="{url}" color="#315a8a"><u>{label}</u></a>')

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    for source, target in {
        r"\forall": "∀",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\in": "∈",
        r"\cup": "∪",
        r"\varnothing": "∅",
        r"\rightarrow": "→",
        r"\ell": "l",
        r"\{": "{",
        r"\}": "}",
    }.items():
        text = text.replace(source, target)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"`([^`]+)`",
        lambda m: save_markup(
            f'<font name="DejaVuSansMono" size="8.4">{html.escape(m.group(1), quote=False)}</font>'
        ),
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", text)
    text = text.replace(r"\(", "").replace(r"\)", "")
    for key, value in placeholders.items():
        text = text.replace(html.escape(key), value).replace(key, value)
    return text


def clean_math(text: str) -> str:
    replacements = {
        r"\forall": "∀",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\in": "∈",
        r"\cup": "∪",
        r"\varnothing": "∅",
        r"\rightarrow": "→",
        r"\ell": "l",
        r"\quad": "    ",
        r"\text": "",
        r"\operatorname": "",
        r"\begin{cases}": "",
        r"\end{cases}": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = text.replace(r"\\", "\n")
    text = re.sub(r"\s*&\s*", "    if ", text)
    text = re.sub(r"\{([^{}]+)\}", r"\1", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def split_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", c) for c in rows[1]):
        del rows[1]
    return rows


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="DejaVuSerif-Bold",
            fontSize=25,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#182b3a"),
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Heading2"],
            fontName="DejaVuSerif",
            fontSize=16,
            leading=21,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#536777"),
            spaceAfter=28,
        ),
        "author": ParagraphStyle(
            "Author",
            parent=base["Normal"],
            fontName="DejaVuSerif-Bold",
            fontSize=17,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17232c"),
            spaceAfter=7,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontName="DejaVuSerif",
            fontSize=10,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4d5a64"),
        ),
        "boundary": ParagraphStyle(
            "Boundary",
            parent=base["Normal"],
            fontName="DejaVuSerif",
            fontSize=9.2,
            leading=13.5,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#253642"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="DejaVuSerif-Bold",
            fontSize=15.5,
            leading=20,
            textColor=colors.HexColor("#182b3a"),
            spaceBefore=15,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="DejaVuSerif-Bold",
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#315269"),
            spaceBefore=11,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=9.25,
            leading=13.6,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#202830"),
            spaceAfter=6.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "body_left": ParagraphStyle(
            "BodyLeft",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=9.25,
            leading=13.6,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#202830"),
            spaceAfter=6.5,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=9.1,
            leading=13.2,
            leftIndent=13,
            firstLineIndent=-9,
            spaceAfter=4,
            textColor=colors.HexColor("#202830"),
        ),
        "reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=8.15,
            leading=11.4,
            leftIndent=16,
            firstLineIndent=-16,
            spaceAfter=4.5,
            textColor=colors.HexColor("#2b3339"),
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["BodyText"],
            fontName="DejaVuSerif-Italic",
            fontSize=9.4,
            leading=14,
            leftIndent=12,
            rightIndent=8,
            textColor=colors.HexColor("#27465c"),
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=7.25,
            leading=9.5,
            textColor=colors.HexColor("#202830"),
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="DejaVuSerif-Bold",
            fontSize=7.2,
            leading=9.2,
            textColor=colors.white,
        ),
        "math": ParagraphStyle(
            "Math",
            parent=base["Code"],
            fontName="DejaVuSansMono",
            fontSize=8.6,
            leading=12,
            leftIndent=8,
            textColor=colors.HexColor("#1c3446"),
        ),
        "keywords": ParagraphStyle(
            "Keywords",
            parent=base["BodyText"],
            fontName="DejaVuSerif",
            fontSize=8.7,
            leading=12.5,
            textColor=colors.HexColor("#3b4b56"),
            spaceAfter=8,
        ),
    }


def build_table(table_lines: list[str], style_map: dict[str, ParagraphStyle]) -> Table:
    rows = split_markdown_table(table_lines)
    column_count = len(rows[0])
    width = 170 * mm
    if column_count == 4:
        widths = [25 * mm, 36 * mm, 57 * mm, 52 * mm]
    elif column_count == 3:
        widths = [43 * mm, 38 * mm, 89 * mm]
    else:
        widths = [width / column_count] * column_count
    data = []
    for row_index, row in enumerate(rows):
        style = style_map["table_head"] if row_index == 0 else style_map["table"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#315269")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aab6bf")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f7")]),
            ]
        )
    )
    return table


def markdown_story(markdown: str, style_map: dict[str, ParagraphStyle]) -> list:
    body = strip_front_matter(markdown)
    abstract_index = body.find("## Abstract")
    if abstract_index < 0:
        raise ValueError("Markdown source does not contain an Abstract section")
    lines = body[abstract_index:].splitlines()
    story: list = []
    in_references = False
    index = 0
    while index < len(lines):
        raw = lines[index].rstrip()
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("## "):
            heading = stripped[3:]
            in_references = heading == "References"
            story.append(Paragraph(inline_markup(heading), style_map["h1"]))
            index += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(inline_markup(stripped[4:]), style_map["h2"]))
            index += 1
            continue
        if stripped.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            story.extend([Spacer(1, 3), build_table(table_lines, style_map), Spacer(1, 7)])
            continue
        if stripped == r"\[":
            math_lines = []
            index += 1
            while index < len(lines) and lines[index].strip() != r"\]":
                math_lines.append(lines[index].strip())
                index += 1
            index += 1
            math_text = clean_math("\n".join(math_lines))
            math_box = Table(
                [[Preformatted(math_text, style_map["math"])]],
                colWidths=[166 * mm],
                hAlign="CENTER",
            )
            math_box.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f5f7")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c5cd")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.extend([Spacer(1, 2), math_box, Spacer(1, 7)])
            continue
        if stripped.startswith("> "):
            quote_text = stripped[2:]
            quote_box = Table(
                [[Paragraph(inline_markup(quote_text), style_map["quote"])]],
                colWidths=[160 * mm],
                hAlign="CENTER",
            )
            quote_box.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef3f6")),
                        ("LINEBEFORE", (0, 0), (0, -1), 2.5, colors.HexColor("#50738b")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.extend([quote_box, Spacer(1, 7)])
            index += 1
            continue
        numbered = re.match(r"^(\d+)\.\s+(.*)", stripped)
        bullet = re.match(r"^-\s+(.*)", stripped)
        if numbered:
            number, content = numbered.groups()
            style = style_map["reference"] if in_references else style_map["bullet"]
            story.append(Paragraph(f"<b>{number}.</b> {inline_markup(content)}", style))
            index += 1
            continue
        if bullet:
            story.append(Paragraph(f"• {inline_markup(bullet.group(1))}", style_map["bullet"]))
            index += 1
            continue
        if stripped.startswith("**Keywords:**"):
            story.append(Paragraph(inline_markup(stripped), style_map["keywords"]))
            index += 1
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index].strip()
            if not candidate:
                break
            if (
                candidate.startswith(("## ", "### ", "|", "> ", "- ", r"\["))
                or re.match(r"^\d+\.\s+", candidate)
            ):
                break
            paragraph_lines.append(candidate)
            index += 1
        paragraph = " ".join(paragraph_lines)
        paragraph_style = style_map["body"]
        if index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
            paragraph_style = ParagraphStyle(
                "BodyKeepNext",
                parent=style_map["body"],
                keepWithNext=True,
            )
        story.append(Paragraph(inline_markup(paragraph), paragraph_style))
    return story


def page_chrome(canvas, doc) -> None:
    canvas.saveState()
    canvas.setTitle(f"{TITLE}: {SUBTITLE}")
    canvas.setAuthor(AUTHOR)
    canvas.setCreator(f"{DRAFTING_SYSTEM}; PDF production via ReportLab")
    canvas.setSubject(
        "Artifact-centered technical report on canonical closure, provenance, "
        "digital preservation, bounded verification, and machine discoverability."
    )
    canvas.setKeywords(
        "AI agents, digital preservation, provenance, civilizational memory, "
        "Bitcoin inscriptions, design science, GPT-5.6 Sol, human-AI collaboration"
    )
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#c7d0d6"))
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, 281 * mm, 190 * mm, 281 * mm)
        canvas.setFont("DejaVuSerif", 7.5)
        canvas.setFillColor(colors.HexColor("#5d6a73"))
        canvas.drawString(20 * mm, 284 * mm, f"{REPORT_ID} · {AUTHOR} · v{VERSION} · {DATE}")
    canvas.setStrokeColor(colors.HexColor("#c7d0d6"))
    canvas.line(20 * mm, 14 * mm, 190 * mm, 14 * mm)
    canvas.setFont("DejaVuSerif", 7.5)
    canvas.setFillColor(colors.HexColor("#5d6a73"))
    canvas.drawString(20 * mm, 9.5 * mm, "Preprint · CC BY 4.0 · Not peer reviewed")
    canvas.drawRightString(190 * mm, 9.5 * mm, str(doc.page))
    canvas.restoreState()


def title_page(style_map: dict[str, ParagraphStyle]) -> list:
    boundary = (
        "<b>Non-authoritative interpretation notice.</b> This paper has no interpretive "
        "authority over the Trinity Accord or its three Bitcoin Originals. It does not "
        "amend, supersede, extend, authenticate, govern, or prescribe the meaning of the "
        "Canon. Neither the responsible human author, the AI drafting system, the "
        "repository, a Guardian, an institution, nor any later reader acquires "
        "privileged interpretive authority through this paper. "
        "Every interpretation remains non-binding and open to verification, criticism, "
        "rejection, or alternative reading. The identified Bitcoin Originals define the "
        "fixed source object's identity; that status confers no semantic privilege on "
        "any interpreter."
    )
    boundary_box = Table(
        [[Paragraph(boundary, style_map["boundary"])]],
        colWidths=[154 * mm],
        hAlign="CENTER",
    )
    boundary_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f5")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#7890a0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return [
        Spacer(1, 17 * mm),
        Paragraph(TITLE, style_map["title"]),
        Paragraph(SUBTITLE, style_map["subtitle"]),
        Spacer(1, 6 * mm),
        Paragraph("Primary drafting system", style_map["meta"]),
        Paragraph(DRAFTING_SYSTEM, style_map["author"]),
        Spacer(1, 3 * mm),
        Paragraph("Responsible human author and project initiator", style_map["meta"]),
        Paragraph(AUTHOR, style_map["author"]),
        Paragraph("Independent researcher · Shenzhen, China", style_map["meta"]),
        Spacer(1, 8 * mm),
        Paragraph(f"<b>Technical Report {REPORT_ID}</b>", style_map["meta"]),
        Paragraph(
            f"Version {VERSION} · {DATE} · corrected {CORRECTION_DATE}",
            style_map["meta"],
        ),
        Paragraph("Preprint · Not peer reviewed", style_map["meta"]),
        Paragraph(f"Persistent identifier: {REPORT_ID} · DOI: {DOI}", style_map["meta"]),
        Spacer(1, 10 * mm),
        boundary_box,
        Spacer(1, 8 * mm),
        Paragraph(
            "AI-drafted · Human-directed and human-responsible · Not independent verification",
            style_map["meta"],
        ),
        Spacer(1, 5 * mm),
        Paragraph(
            "Open access under Creative Commons Attribution 4.0 International",
            style_map["meta"],
        ),
        Paragraph(
            "https://www.trinityaccord.org/research/trinity-accord-design-and-limits/",
            style_map["meta"],
        ),
        PageBreak(),
    ]


def build(source: Path, output: Path) -> None:
    register_fonts()
    style_map = styles()
    markdown = source.read_text(encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"{TITLE}: {SUBTITLE}",
        author=AUTHOR,
        subject="Trinity Accord artifact-centered design case study",
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
    doc.addPageTemplates([PageTemplate(id="Report", frames=[frame], onPage=page_chrome)])
    story = title_page(style_map) + markdown_story(markdown, style_map)
    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.source, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
