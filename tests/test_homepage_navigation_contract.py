import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
HOMEPAGE = (ROOT / "index.md").read_text(encoding="utf-8")


def _navigation_branches() -> tuple[str, str]:
    nav_match = re.search(
        r'<div class="nav-links">(?P<nav>.*?)</div>',
        LAYOUT,
        flags=re.DOTALL,
    )
    assert nav_match, "primary navigation block is missing"

    branch_match = re.fullmatch(
        r'\s*{% if page\.url == "/" %}(?P<home>.*?){% else %}'
        r'(?P<inner>.*?){% endif %}\s*',
        nav_match.group("nav"),
        flags=re.DOTALL,
    )
    assert branch_match, "primary navigation must render explicit home and inner-page branches"
    return branch_match.group("home"), branch_match.group("inner")


def _links(markup: str) -> list[tuple[str, str]]:
    return re.findall(r'<a href="([^"]+)">([^<]+)</a>', markup)


def test_homepage_initial_html_contains_the_final_six_item_navigation() -> None:
    home, _ = _navigation_branches()
    assert _links(home) == [
        ("/#home-in-one-minute", "Structure"),
        ("/#philosophical-core", "Propositions"),
        ("/#chronicle-witness", "Chronicle"),
        ("/#research-entry", "Paths"),
        ("/verify/", "Verify"),
        ("/agent-first-contact/", "First Contact"),
    ]


def test_inner_pages_retain_the_complete_eight_item_navigation() -> None:
    _, inner = _navigation_branches()
    assert _links(inner) == [
        ("/#home-in-one-minute", "Overview"),
        ("/#philosophical-core", "Propositions"),
        ("/#chronicle-witness", "Chronicle"),
        ("/#later-inscriptions", "3 + 5"),
        ("/physical-anchor/", "Physical Anchor"),
        ("/#research-entry", "Research"),
        ("/verify/", "Verify"),
        ("/agent-first-contact/", "First Contact"),
    ]


def test_homepage_javascript_does_not_rewrite_primary_navigation() -> None:
    assert "document.querySelector('.nav-links')" not in HOMEPAGE
    assert "navigation.querySelectorAll('a')" not in HOMEPAGE
