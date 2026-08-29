from scripts import publish_second_star_moon_to_zenodo as zenodo


def test_normalize_md5_accepts_bare_and_prefixed_forms():
    digest = "1c668439ef8fcf403331029ae3422ca3"
    assert zenodo.normalize_md5(digest) == digest
    assert zenodo.normalize_md5(f"md5:{digest}") == digest
    assert zenodo.normalize_md5(f"MD5:{digest.upper()}") == digest


def test_verify_remote_rows_accepts_bare_zenodo_md5():
    digest = "1c668439ef8fcf403331029ae3422ca3"
    inventory = {"ARCHIVE-README.md": {"bytes": 2280, "md5": digest}}
    rows = [
        {
            "filename": "ARCHIVE-README.md",
            "filesize": 2280,
            "checksum": digest,
        }
    ]

    verified = zenodo.verify_remote_rows(rows, inventory)

    assert verified["ARCHIVE-README.md"]["checksum"] == digest


def test_verify_remote_rows_accepts_prefixed_zenodo_md5():
    digest = "1c668439ef8fcf403331029ae3422ca3"
    inventory = {"ARCHIVE-README.md": {"bytes": 2280, "md5": digest}}
    rows = [
        {
            "filename": "ARCHIVE-README.md",
            "filesize": 2280,
            "checksum": f"md5:{digest}",
        }
    ]

    verified = zenodo.verify_remote_rows(rows, inventory)

    assert verified["ARCHIVE-README.md"]["checksum"] == f"md5:{digest}"
