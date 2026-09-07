import subprocess
import unittest
from unittest import mock

from scripts import capture_chronicle_base_derivation as derivation


class DecoderFetchRetryTests(unittest.TestCase):
    def command(self):
        return [
            "batch-decoder",
            "fetch",
            "--start",
            "1",
            "--end",
            "2",
            "--l1",
            "https://primary.invalid",
            "--concurrent-requests",
            "12",
        ]

    def test_rotates_endpoint_and_reduces_concurrency(self):
        failure = subprocess.CalledProcessError(1, self.command())
        with mock.patch.object(derivation, "run", side_effect=[failure, None]) as run, mock.patch.object(
            derivation.time, "sleep", return_value=None
        ) as sleep:
            derivation.run_decoder_fetch(
                self.command(),
                ["https://primary.invalid", "https://fallback.invalid"],
                retries=3,
            )

        first = run.call_args_list[0].args[0]
        second = run.call_args_list[1].args[0]
        self.assertEqual(first[first.index("--l1") + 1], "https://primary.invalid")
        self.assertEqual(second[second.index("--l1") + 1], "https://fallback.invalid")
        self.assertEqual(first[first.index("--concurrent-requests") + 1], "12")
        self.assertEqual(second[second.index("--concurrent-requests") + 1], "6")
        sleep.assert_called_once_with(15)

    def test_exhaustion_still_fails_closed(self):
        failure = subprocess.CalledProcessError(1, self.command())
        with mock.patch.object(derivation, "run", side_effect=failure) as run, mock.patch.object(
            derivation.time, "sleep", return_value=None
        ) as sleep:
            with self.assertRaises(subprocess.CalledProcessError):
                derivation.run_decoder_fetch(
                    self.command(),
                    ["https://primary.invalid", "https://fallback.invalid"],
                    retries=3,
                )

        attempts = [call.args[0] for call in run.call_args_list]
        self.assertEqual(
            [command[command.index("--l1") + 1] for command in attempts],
            ["https://primary.invalid", "https://fallback.invalid", "https://primary.invalid"],
        )
        self.assertEqual(
            [command[command.index("--concurrent-requests") + 1] for command in attempts],
            ["12", "6", "3"],
        )
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [15, 30])


if __name__ == "__main__":
    unittest.main()
