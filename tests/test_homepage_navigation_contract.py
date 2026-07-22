import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
HOMEPAGE = (ROOT / "index.md").read_text(encoding="utf-8")


def _markup_for_class(source: str, class_name: str) -> str:
    match = re.search(
        rf'<(?:div|nav) class="{re.escape(class_name)}">(?P<markup>.*?)</(?:div|nav)>',
        source,
        flags=re.DOTALL,
    )
    assert match, f"{class_name} block is missing"
    return match.group("markup")


def _links(markup: str) -> list[tuple[str, str]]:
    return re.findall(r'<a href="([^"]+)">([^<]+)</a>', markup)


def test_primary_navigation_is_the_same_six_item_contract_on_every_page() -> None:
    primary = _markup_for_class(LAYOUT, "nav-links")
    assert "{%" not in primary, "primary navigation must not branch by page"
    assert _links(primary) == [
        ("/#home-in-one-minute", "Structure"),
        ("/#philosophical-core", "Propositions"),
        ("/#chronicle-witness", "Chronicle"),
        ("/#research-entry", "Paths"),
        ("/verify/", "Verify"),
        ("/agent-first-contact/", "First Contact"),
    ]


def test_supplemental_evidence_routes_remain_discoverable() -> None:
    footer = _markup_for_class(LAYOUT, "footer-links")
    assert ("/inscriptions/", "Inscriptions") in _links(footer)
    assert ("/physical-anchor/", "Physical Anchor") in _links(footer)

    assert 'href="/physical-anchor/"' in HOMEPAGE
    assert 'href="/authority-address-inscriptions/"' in HOMEPAGE
    assert "Inspect the complete 3 + 5 index" in HOMEPAGE


def test_homepage_javascript_does_not_rewrite_primary_navigation() -> None:
    assert "document.querySelector('.nav-links')" not in HOMEPAGE
    assert "navigation.querySelectorAll('a')" not in HOMEPAGE
