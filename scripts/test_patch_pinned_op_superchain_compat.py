#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).with_name("patch_pinned_op_superchain_compat.py")
SPEC = importlib.util.spec_from_file_location("op_compat", SCRIPT)
op_compat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(op_compat)


class PinnedOPCompatTests(unittest.TestCase):
    def test_adds_only_expected_registry_metadata_fields(self):
        expected_tags = {"superchain_level", "protocol_versions_addr"}
        actual_tags = set()
        for _, needle, replacement in op_compat.PATCHES.values():
            source = needle + "\tSentinel string\n}\n"
            patched = op_compat.patch_text(source, needle, replacement)
            self.assertIn("\tSentinel", patched)
            for tag in expected_tags:
                if f'toml:"{tag}"' in patched:
                    actual_tags.add(tag)
        self.assertEqual(actual_tags, expected_tags)

    def test_refuses_drift_or_double_patch(self):
        for _, needle, replacement in op_compat.PATCHES.values():
            with self.assertRaises(ValueError):
                op_compat.patch_text("type Config struct {}\n", needle, replacement)
            with self.assertRaises(ValueError):
                op_compat.patch_text(replacement, needle, replacement)


if __name__ == "__main__":
    unittest.main()
