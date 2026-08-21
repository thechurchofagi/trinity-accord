from __future__ import annotations

import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_deployment_freshness as deployment  # noqa: E402


def _valid_article(**overrides: object) -> dict[str, object]:
    article: dict[str, object] = {
        "@type": "ScholarlyArticle",
        "name": deployment.SCHOLARLY_TITLE,
        "headline": deployment.SCHOLARLY_TITLE,
        "datePublished": "2026-07-29",
        "version": "1.1",
        "identifier": [
            {
                "@type": "PropertyValue",
                "propertyID": "Technical report number",
                "value": deployment.SCHOLARLY_REPORT_NUMBER,
            },
            {
                "@type": "PropertyValue",
                "propertyID": "DOI",
                "value": deployment.SCHOLARLY_DOI,
                "url": deployment.SCHOLARLY_DOI_URL,
            },
        ],
        "url": deployment.SCHOLARLY_HTML_URL,
        "sameAs": [deployment.SCHOLARLY_DOI_URL, deployment.SCHOLARLY_ZENODO_URL],
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "encoding": {
            "@type": "MediaObject",
            "contentUrl": deployment.SCHOLARLY_PDF_URL,
            "encodingFormat": "application/pdf",
        },
    }
    article.update(overrides)
    return article


def _landing(document: object) -> str:
    meta = "".join(
        f'<meta name="{html.escape(name, quote=True)}" '
        f'content="{html.escape(value, quote=True)}">'
        for name, value in deployment.SCHOLARLY_META_EXPECTED.items()
    )
    json_ld = json.dumps(document)
    return (
        "<!doctype html><html><head>"
        + meta
        + f'<script type="application/ld+json">{json_ld}</script>'
        + "</head><body></body></html>"
    )


def test_non_head_start_tag_implicitly_ends_head_without_body_tag() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<meta name="citation_title" content="before-main">'
        "<main>"
        '<meta name="citation_author" content="after-main">'
        "</main></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["before-main"]
    assert "citation_author" not in parser.meta
    assert parser._body_started is True
    assert parser._in_head is False


def test_non_whitespace_character_token_implicitly_ends_head() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>body-effective text"
        '<meta name="citation_title" content="after-text">'
        "</html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser._body_started is True
    assert parser._in_head is False


def test_duplicate_meta_attributes_use_first_values_and_fail_closed() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<meta name="citation_title" name="citation_author" '
        'content="first-content" content="second-content">'
        "</head><body></body></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["first-content"]
    assert "citation_author" not in parser.meta
    assert parser.errors == [
        "scholarly meta contains duplicate attribute(s): content, name"
    ]


def test_duplicate_script_type_keeps_first_jsonld_value_and_fails_closed() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<script type="application/ld+json" type="text/plain">'
        '{"@context":"https://schema.org"}'
        "</script></head><body></body></html>"
    )
    parser.close()

    assert len(parser.json_ld_blocks) == 1
    assert parser.errors == [
        "scholarly JSON-LD script contains duplicate type attribute"
    ]


def test_duplicate_script_type_does_not_promote_ignored_second_jsonld_value() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<script type="text/plain" type="application/ld+json">'
        '{"@context":"https://schema.org"}'
        "</script></head><body></body></html>"
    )
    parser.close()

    assert parser.json_ld_blocks == []
    assert parser.errors == [
        "scholarly JSON-LD script contains duplicate type attribute"
    ]


def test_template_contents_are_inert_for_scholarly_metadata() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        "<template>"
        '<meta name="citation_title" content="template-title">'
        '<script type="application/ld+json">{not-json}</script>'
        "</template>"
        '<meta name="citation_title" content="real-title">'
        '<script type="application/ld+json">{"real":true}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["real-title"]
    assert parser.json_ld_blocks == ['{"real":true}']
    assert parser.errors == []


def test_self_closing_template_slash_does_not_end_html_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head><template/>"
        '<meta name="citation_title" content="still-template">'
        '<script type="application/ld+json">{"still":"template"}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser.json_ld_blocks == []
    assert parser._template_depth == 1


def test_scholarly_article_inherits_root_schema_org_context() -> None:
    page = _landing(
        {"@context": "https://schema.org", "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert errors == []


def test_scholarly_article_without_schema_org_context_is_rejected() -> None:
    page = _landing({"@graph": [_valid_article()]})
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_scholarly_article_with_non_schema_context_is_rejected() -> None:
    page = _landing(
        {"@context": "https://example.invalid/schema", "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_child_context_can_reset_inherited_schema_org_context() -> None:
    article = _valid_article(**{"@context": None})
    page = _landing({"@context": "https://schema.org", "@graph": [article]})
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_explicit_scholarly_article_term_override_is_honored() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "ScholarlyArticle": "https://example.invalid/Fake",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_explicit_schema_org_scholarly_article_term_is_accepted() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://example.invalid/vocab/",
                "ScholarlyArticle": "https://schema.org/ScholarlyArticle",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert errors == []


def test_propagate_false_does_not_apply_context_to_graph_descendants() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "@propagate": False,
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )

def test_noscript_raw_text_does_not_close_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head><template><noscript></template></noscript>"
        '<meta name="citation_title" content="still-template">'
        '<script type="application/ld+json">{"still":"template"}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser.json_ld_blocks == []
    assert parser._template_depth == 1


def test_schema_org_vocab_requires_trailing_slash() -> None:
    page = _landing(
        {"@context": {"@vocab": "https://schema.org"}, "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_property_scoped_context_override_is_applied_before_child_nodes() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "items": {
                    "@id": "https://example.invalid/items",
                    "@context": {
                        "ScholarlyArticle": "https://example.invalid/Fake"
                    },
                },
            },
            "items": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )
