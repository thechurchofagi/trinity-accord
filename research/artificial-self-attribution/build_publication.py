#!/usr/bin/env python3
"""Prepare TA-TR-2026-08 v1.1 locally; never reserve, upload, or publish.

Run with $CODEX_PRIMARY_RUNTIME_PYTHON. The orchestrator runs the artifact
operation marker before the first authoring run; this script never runs it.

    build_publication.py check
    build_publication.py build
    # Inspect every rendered qa/<stem>/page-N.png before sealing the package.
    build_publication.py finalize --visual-review-confirmed

Build accepts --languages en/zh for a focused rebuild. It preserves manuscripts
and only replaces publication identity lines in their front matter. No prose,
font size, page budget, or argument is changed to fit pagination.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import build_documents as documents

ROOT = Path(__file__).resolve().parent
REPORT = "TA-TR-2026-08"
VERSION = "1.1"
BASE = "https://www.trinityaccord.org/research/artificial-self-attribution/"
RENDERER = Path("/root/.codex/skills/builtins/documents/render_docx.py")
AUTHOR = "Hongju Liu"
LANGUAGES = ("en", "zh")
DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.I)
DATE_LINE = re.compile(
    r"^(?:Independent research manuscript\b.*|Independent philosophical research preprint\b.*|"
    r"独立研究论文.*|独立哲学研究预印本.*|"
    r"TA-TR-\d{4}-\d+\s*[·|].*|DOI\s*[:：].*)$", re.M
)
CSS = """
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{font-family:Georgia,"Noto Serif CJK SC","Songti SC",serif;max-width:800px;
margin:42px auto;padding:0 22px;line-height:1.72;color:#191919;background:#fff}
h1{font-size:2rem;line-height:1.25}h2{font-size:1.42rem;line-height:1.4;margin-top:1.65em}
h3{font-size:1.13rem;line-height:1.5;margin-top:1.45em}
h1,h2,h3{color:#000}article>header{text-align:center}
.subtitle{font-size:1.22rem;line-height:1.45;margin-top:.4em}.frontmatter{font-size:.94rem}
nav{font:.9rem/1.6 system-ui,sans-serif;border-bottom:1px solid #ddd;padding-bottom:12px}
a{color:#194e77;overflow-wrap:anywhere}p{overflow-wrap:break-word;word-break:normal}
.reference{padding-left:2em;text-indent:-2em;font-size:.94rem}
@media(max-width:600px){body{margin:24px auto;padding:0 18px;font-size:17px}
h1{font-size:1.7rem}.subtitle{font-size:1.12rem}}
@media print{nav{display:none}body{max-width:none;margin:0}a{color:inherit}}
""".strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_deposit(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for field in ("doi", "record_id", "report_number", "version"):
        if field not in data:
            raise ValueError(f"Missing deposit field: {field}")
    if data["report_number"] != REPORT or str(data["version"]) != VERSION:
        raise ValueError("Deposit identity must be TA-TR-2026-08 version 1.1")
    doi = str(data["doi"]).strip()
    if not DOI_RE.fullmatch(doi) or any(x in doi.lower() for x in ("placeholder", "pending", "todo")):
        raise ValueError("A real reserved DOI is required; placeholder values are refused")
    data["doi"] = doi
    data["version"] = VERSION
    data["record_id"] = int(data["record_id"])
    if data["record_id"] <= 0:
        raise ValueError("record_id must be positive")
    if doi.lower().startswith("10.5281/zenodo.") and doi.rsplit(".", 1)[-1] != str(data["record_id"]):
        raise ValueError("Zenodo DOI and record_id disagree")
    data["publication_date"] = date.fromisoformat(data.get("publication_date", "2026-09-19")).isoformat()
    return data


def stem(lang: str) -> str:
    return "artificial-self-attribution" + ("-zh" if lang == "zh" else "") + "-v" + VERSION


def asset_names() -> set[str]:
    return {stem(lang) + ext for lang in LANGUAGES for ext in (".docx", ".pdf", ".md", ".html")} | {
        "citation.bib", "citation.ris", "citation.csl.json", "README-LICENSE.txt",
        "REVIEW-AND-SOURCES.md", "SHA256SUMS.txt",
    }


def manuscript_info(path: Path) -> dict:
    blocks = documents.read_blocks(path)
    if not blocks or blocks[0][0] != 1:
        raise ValueError(f"Missing manuscript title: {path}")
    title = blocks[0][1]
    subtitle = blocks[1][1] if len(blocks) > 1 and blocks[1][0] == 2 else ""
    full_title = title + (": " + subtitle if subtitle else "")
    raw = path.read_text(encoding="utf-8-sig")
    if any(token in raw for token in ("", "TODO", "[INSERT", "PLACEHOLDER")):
        raise ValueError(f"Unfinished manuscript marker: {path}")
    refs = re.findall(r"^\[(\d+)\]\s+(.+)$", raw, re.M)
    if not refs or [int(x[0]) for x in refs] != list(range(1, len(refs) + 1)):
        raise ValueError(f"References must be consecutively numbered: {path}")
    return {"title": full_title, "short_title": title, "subtitle": subtitle,
            "references": refs, "source_sha256": sha(path)}


def publication_markdown(source: str, metadata: dict, lang: str) -> str:
    """Replace only recognized identity lines before the abstract, preserving body bytes."""
    match = re.search(r"^#{2,3}\s+(?:Abstract|摘要)\s*$", source, re.M)
    if not match:
        raise ValueError("Expected an Abstract/摘要 heading to delimit front matter")
    front, body = source[:match.start()], source[match.start():]
    # Existing DOI lines may only refer to this reserved publication record.
    for old_doi in re.findall(r"^DOI\s*[:：]\s*(\S+)\s*$", front, re.M):
        if old_doi.removeprefix("https://doi.org/") != metadata["doi"]:
            raise ValueError("Source front matter contains a different DOI")
    front = DATE_LINE.sub("", front).rstrip()
    d = date.fromisoformat(metadata["publication_date"])
    if lang == "zh":
        identity = f"独立哲学研究预印本 · {REPORT} · 版本 {VERSION} · {d.year} 年 {d.month} 月 {d.day} 日"
    else:
        identity = f"Independent philosophical research preprint · {REPORT} · Version {VERSION} · {d.day} {d.strftime('%B %Y')}"
    return front + "\n\n" + identity + "\n\nDOI: https://doi.org/" + metadata["doi"] + "\n\n" + body


def inline_html(content: str) -> str:
    output, cursor = [], 0
    for match in documents.INLINE_RE.finditer(content):
        output.append(html.escape(content[cursor:match.start()]))
        label, target, raw_url, bold, italic, code = match.groups()
        if target or raw_url:
            suffix = ""
            if raw_url:
                target, suffix = documents.split_url_punctuation(raw_url)
                label = target
            output.append('<a href="' + html.escape(target, quote=True) + '">' + html.escape(label) + "</a>" + html.escape(suffix))
        else:
            tag = "strong" if bold else "em" if italic else "code"
            output.append(f"<{tag}>" + html.escape(bold or italic or code) + f"</{tag}>")
        cursor = match.end()
    output.append(html.escape(content[cursor:]))
    return "".join(output)


def render_html(path: Path, metadata: dict, lang: str, info: dict) -> str:
    name = stem(lang)
    canonical = BASE + ("zh.html" if lang == "zh" else "")
    metas = {
        "citation_title": info["title"], "citation_author": AUTHOR,
        "citation_publication_date": metadata["publication_date"].replace("-", "/"),
        "citation_date": metadata["publication_date"].replace("-", "/"),
        "citation_doi": metadata["doi"], "citation_pdf_url": BASE + name + ".pdf",
        "citation_technical_report_number": REPORT,
        "citation_technical_report_institution": "Independent researcher",
        "citation_language": lang,
    }
    head = "\n".join(f'<meta name="{key}" content="{html.escape(value, quote=True)}">' for key, value in metas.items())
    parts = ["<header>"]
    front, references = True, False
    for index, (level, content) in enumerate(documents.read_blocks(path)):
        text = inline_html(content)
        if index == 0:
            parts.append("<h1>" + text + "</h1>")
        elif index == 1 and level == 2:
            parts.append('<p class="subtitle">' + text + "</p>")
        elif level:
            if front:
                parts.append("</header>")
                front = False
            references = content.strip().casefold() in ("references", "参考文献")
            tag = "h2" if content.strip().casefold() in ("abstract", "摘要") else f"h{min(max(level, 2), 4)}"
            parts.append(f"<{tag}>" + text + f"</{tag}>")
        else:
            cls = ' class="frontmatter"' if front else ' class="reference"' if references else ""
            parts.append("<p" + cls + ">" + text + "</p>")
    if front:
        parts.append("</header>")
    nav = (f'<a href="{BASE}">English</a> · <a href="{BASE}zh.html">中文全文</a> · '
           f'<a href="{BASE}{name}.pdf">PDF</a> · '
           f'<a href="https://zenodo.org/records/{metadata["record_id"]}/files/{name}.docx?download=1">Word</a> · '
           f'<a href="https://doi.org/{html.escape(metadata["doi"], quote=True)}">DOI record</a> · '
           f'<a href="{BASE}publication-record.json">Publication receipt</a>')
    return ('<!doctype html>\n<html lang="' + ("zh-CN" if lang == "zh" else "en") + '">\n<head>\n'
            '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>' + html.escape(info["title"]) + '</title>\n' + head + '\n'
            '<link rel="canonical" href="' + canonical + '">\n<style>' + CSS + '</style>\n</head>\n'
            '<body><nav aria-label="Publication formats">' + nav + '</nav>\n<main><article>\n' +
            '\n'.join(parts) + '\n</article></main></body></html>\n')


def write_citations(output: Path, metadata: dict, title: str) -> None:
    d = date.fromisoformat(metadata["publication_date"])
    note = "Philosophical preprint; not peer reviewed. English and Chinese versions constitute one study."
    bib_title = title.replace("\\", r"\textbackslash{}").replace("{", r"\{").replace("}", r"\}")
    fields = {"author": "Liu, Hongju", "title": bib_title, "institution": "Independent researcher",
              "number": REPORT, "year": str(d.year), "month": d.strftime("%B"),
              "doi": metadata["doi"], "url": "https://doi.org/" + metadata["doi"],
              "version": VERSION, "note": note}
    (output / "citation.bib").write_text("@techreport{liu2026artificialselfattribution,\n" +
        ",\n".join("  " + key + " = {" + value + "}" for key, value in fields.items()) + "\n}\n", encoding="utf-8")
    ris = [("TY", "RPRT"), ("AU", "Liu, Hongju"), ("TI", title), ("PY", str(d.year)),
           ("DA", d.strftime("%Y/%m/%d")), ("PB", "Zenodo"), ("M1", REPORT), ("ET", VERSION),
           ("DO", metadata["doi"]), ("UR", "https://doi.org/" + metadata["doi"]), ("LA", "English; Chinese"),
           ("N1", note), ("ER", "")]
    (output / "citation.ris").write_text("".join(f"{key}  - {value}\n" for key, value in ris), encoding="utf-8")
    write_json(output / "citation.csl.json", {"id": metadata["doi"], "type": "report", "title": title,
        "author": [{"family": "Liu", "given": "Hongju"}], "issued": {"date-parts": [[d.year, d.month, d.day]]},
        "publisher": "Zenodo", "number": REPORT, "version": VERSION, "DOI": metadata["doi"],
        "URL": "https://doi.org/" + metadata["doi"], "genre": "Philosophical preprint", "note": note})


def write_license(output: Path, metadata: dict, title: str) -> None:
    text = f"""{REPORT} | Version {VERSION} | {metadata['publication_date']}
{title}
DOI: {metadata['doi']}

Author of record: Hongju Liu. AI assistance, research limitations and author responsibility are described in the manuscripts and REVIEW-AND-SOURCES.md. This is a philosophical preprint, not a peer-reviewed publication.

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) applies to newly written material to the extent rights are held. Cited third-party works and embedded font software retain their own rights. No third-party full texts or standalone fonts are distributed.

The English paper and complete Chinese translation constitute one study. The cases and numerical illustrations are thought experiments, not newly collected experimental data or measured safety results. This publication does not amend prior DOI records or the Bitcoin Original.

Fourteen publication files: two DOCX, two PDF, two Markdown and two HTML full texts, three citation formats, REVIEW-AND-SOURCES.md, this license note and SHA256SUMS.txt. The checksum list covers the other thirteen files; its own digest is recorded in the external publication manifest and receipt. The PDF files are rendered from the corresponding DOCX files.

A reserved DOI does not establish publication. Publication status and exact-file public readback must be established from the separate publication receipt and public DOI record.
"""
    (output / "README-LICENSE.txt").write_text(text, encoding="utf-8")


def prepare_inputs(root: Path, deposit: Path) -> tuple[dict, dict]:
    metadata = load_deposit(deposit)
    infos = {lang: manuscript_info(root / f"manuscript-{lang}.md") for lang in LANGUAGES}
    if infos["en"]["references"] != infos["zh"]["references"]:
        raise ValueError("English and Chinese reference lists differ")
    if metadata.get("title"):
        normalize_title = lambda value: re.sub(r"[\W_]+", "", value).casefold()
        if normalize_title(metadata["title"]) != normalize_title(infos["en"]["title"]):
            raise ValueError("Deposit title differs substantively from the English title and subtitle")
        # Preserve the citation spelling/capitalization used by the deposit.
        infos["en"]["title"] = metadata["title"]
    else:
        metadata["title"] = infos["en"]["title"]
    return metadata, infos


def check_fonts() -> None:
    for font in (documents.LATIN_FONT, documents.CJK_FONT):
        result = subprocess.run(["fc-match", "--format=%{family}", font], check=True, capture_output=True, text=True)
        if font not in result.stdout.split(","):
            raise RuntimeError(f"Reviewed rendering font is unavailable: {font}; got {result.stdout!r}")


def build(args) -> None:
    metadata, infos = prepare_inputs(args.root, args.deposit)
    if not args.renderer.is_file():
        raise FileNotFoundError(f"DOCX renderer unavailable: {args.renderer}")
    check_fonts()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    unexpected = {p.name for p in output.iterdir()} - asset_names()
    if unexpected:
        raise ValueError(f"Unexpected files in publication directory: {sorted(unexpected)}")
    # A changed package must not retain an apparently current seal.
    for seal in (output / "SHA256SUMS.txt", args.root / "EXPECTED-PUBLICATION.json"):
        if seal.exists():
            seal.unlink()
    report_path = args.root / "format-checks.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    report.update({"state": "BUILDING_NOT_REVIEWED", "report_number": REPORT, "version": VERSION,
                   "doi": metadata["doi"], "languages": report.get("languages", {}),
                   "source_docx_pdf_text_equal": False, "reference_lists_identical": True,
                   "valid_citation_metadata": False, "pdf_text_extractable": False})
    write_json(report_path, report)
    for lang in args.languages:
        source = args.root / f"manuscript-{lang}.md"
        md = publication_markdown(source.read_text(encoding="utf-8-sig"), metadata, lang)
        # Append extensions: with_suffix would truncate the decimal version.
        md_path = output / (stem(lang) + ".md")
        docx_path = output / (stem(lang) + ".docx")
        md_path.write_text(md, encoding="utf-8")
        (output / (stem(lang) + ".html")).write_text(render_html(md_path, metadata, lang, infos[lang]), encoding="utf-8")
        doc_meta = dict(metadata, title=infos[lang]["title"])
        documents.build(md_path, docx_path, lang.upper(), publication=doc_meta)
        render_dir = args.qa_dir / stem(lang)
        if render_dir.exists():
            # Only remove this renderer's stale page files, never unrelated QA.
            for old in render_dir.glob("page-*.png"):
                old.unlink()
        subprocess.run([sys.executable, str(args.renderer), str(docx_path),
                        "--output_dir", str(render_dir), "--emit_pdf"], check=True)
        rendered_pdf = render_dir / (stem(lang) + ".pdf")
        if not rendered_pdf.is_file() or not list(render_dir.glob("page-*.png")):
            raise RuntimeError(f"Missing renderer output for {lang}")
        pdf_path = output / rendered_pdf.name
        shutil.copyfile(rendered_pdf, pdf_path)
        report["languages"][lang] = {"source_sha256": infos[lang]["source_sha256"],
            "published_markdown_sha256": sha(md_path), "docx_sha256": sha(docx_path), "pdf_sha256": sha(pdf_path),
            "references": len(infos[lang]["references"]), "pages": len(list(render_dir.glob("page-*.png"))),
            "render_dir": str(render_dir), "visual_review": "REQUIRED"}
        write_json(report_path, report)
    write_citations(output, metadata, infos["en"]["title"])
    write_license(output, metadata, infos["en"]["title"])
    review = args.root / "REVIEW-AND-SOURCES.md"
    if review.is_file():
        shutil.copyfile(review, output / review.name)
    report["state"] = "RENDERED_VISUAL_AND_CONTENT_REVIEW_REQUIRED"
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def finalize(args) -> None:
    if not args.visual_review_confirmed:
        raise ValueError("Finalize only after every latest page PNG and source/content check has passed; use --visual-review-confirmed")
    metadata, infos = prepare_inputs(args.root, args.deposit)
    review = args.root / "REVIEW-AND-SOURCES.md"
    if not review.is_file():
        raise FileNotFoundError(review)
    report_path = args.root / "format-checks.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for lang in LANGUAGES:
        checks = report.get("languages", {}).get(lang, {})
        if checks.get("source_sha256") != infos[lang]["source_sha256"]:
            raise ValueError(f"Source changed after rendering: {lang}")
        for ext, key in ((".md", "published_markdown_sha256"), (".docx", "docx_sha256"), (".pdf", "pdf_sha256")):
            if sha(args.output / (stem(lang) + ext)) != checks.get(key):
                raise ValueError(f"Rendered publication asset changed: {lang}{ext}")
        expected_md = publication_markdown((args.root / f"manuscript-{lang}.md").read_text(encoding="utf-8-sig"), metadata, lang)
        if (args.output / (stem(lang) + ".md")).read_text(encoding="utf-8") != expected_md:
            raise ValueError(f"Publication Markdown differs from current deposit/source: {lang}")
        expected_html = render_html(args.output / (stem(lang) + ".md"), metadata, lang, infos[lang])
        if (args.output / (stem(lang) + ".html")).read_text(encoding="utf-8") != expected_html:
            raise ValueError(f"Publication HTML differs from current deposit/source: {lang}")
    shutil.copyfile(review, args.output / review.name)
    actual = {p.name for p in args.output.iterdir()}
    expected_without_sums = asset_names() - {"SHA256SUMS.txt"}
    if actual - {"SHA256SUMS.txt"} != expected_without_sums:
        raise ValueError(f"Expected 13 content files before sealing, got {sorted(actual)}")
    if any(not p.is_file() or p.stat().st_size == 0 for p in args.output.iterdir()):
        raise ValueError("Publication directory contains a non-file or empty asset")
    (args.output / "SHA256SUMS.txt").write_text("".join(sha(args.output / name) + "  " + name + "\n"
        for name in sorted(expected_without_sums)), encoding="utf-8")
    assets = [{"name": name, "bytes": (args.output / name).stat().st_size, "sha256": sha(args.output / name)}
              for name in sorted(asset_names())]
    write_json(args.root / "EXPECTED-PUBLICATION.json", {"report_number": REPORT, "record_id": metadata["record_id"],
        "doi": metadata["doi"], "title": infos["en"]["title"], "version": VERSION, "file_count": 14, "files": assets})
    report["state"] = "FINAL_PACKAGE_SEALED_REVIEW_CONFIRMED"
    for checks in report["languages"].values():
        checks["visual_review"] = "CONFIRMED_BY_OPERATOR"
    write_json(report_path, report)
    print("Sealed 14 publication assets; no upload or publication performed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "build", "finalize"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--deposit", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--qa-dir", type=Path)
    parser.add_argument("--renderer", type=Path, default=Path(os.environ.get("DOCX_RENDERER", str(RENDERER))))
    parser.add_argument("--languages", nargs="+", choices=LANGUAGES, default=list(LANGUAGES))
    parser.add_argument("--visual-review-confirmed", action="store_true")
    args = parser.parse_args()
    args.root = args.root.resolve()
    args.deposit = (args.deposit or args.root / "deposit.json").resolve()
    args.output = (args.output or args.root / "published").resolve()
    args.qa_dir = (args.qa_dir or args.root / "qa").resolve()
    if args.command == "check":
        metadata, infos = prepare_inputs(args.root, args.deposit)
        check_fonts()
        print(json.dumps({"state": "INPUTS_VALID_NO_FILES_WRITTEN", "metadata": metadata,
            "titles": {lang: info["title"] for lang, info in infos.items()},
            "publication_file_count": len(asset_names()), "renderer": str(args.renderer)}, ensure_ascii=False, indent=2))
    elif args.command == "build":
        build(args)
    else:
        finalize(args)


if __name__ == "__main__":
    main()
