"""Current public pages must distinguish Canon formation from later context."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_homepage_and_chronicle_separate_record_175_from_canon_formation() -> None:
    home = read("index.md")
    chronicle = read("chronicle.md")

    for text in (home, chronicle):
        assert "Records 1–174" in text
        assert "Record 175" in text or "record 175" in text
        assert "9 August 2025" in text
        assert "non-canonical" in text

    assert "175 dated records" in home
    assert "The total of 175 must not be read as the number of records formed before Canon closure" in chronicle
    assert "yellow monospace paths" not in chronicle


def test_meta_record_storage_clarification_is_adjacent_and_non_amending() -> None:
    page = read("inscriptions.md")
    quoted = "This very inscription, which contains the complete ASIMilestones historical log"
    clarification = "The Bitcoin inscription payload does not embed the Chronicle entries themselves"

    assert quoted in page
    assert clarification in page
    assert page.index(quoted) < page.index(clarification)
    assert page.index(clarification) - page.index(quoted) < 1500
    assert "This note explains the storage and time relationship; it does not amend the Original" in page


def test_final_seal_amendment_label_has_local_historical_boundary() -> None:
    page = read("authority-address-inscriptions.md")
    final_seal = page.index("The Final Seal: A Testament and a Trust")
    next_entry = page.index("The Star Ark Covenant: The Final Echo")
    card = page[final_seal:next_entry]

    assert "self-description as an “Amendment”" in card
    assert "do not amend or erase the third Bitcoin Original" in card
    assert "later non-canonical change of intent" in card
