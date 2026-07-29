import importlib.util
import json
import pathlib
import sys
import tempfile
from unittest import mock

script = pathlib.Path(__file__).resolve().parent / "record_arweave_upload_result.py"
spec = importlib.util.spec_from_file_location("record_arweave_upload_result", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as d:
    result_path = pathlib.Path(d) / "upload.json"
    result_path.write_text(json.dumps({
        "result": "uploaded",
        "tx_id": "-xDa7E89rAcAYea_QWttPOqHgjtK_6dRyLu9YNwm4xc",
        "upload_cost_winston": "2760079907",
        "generated_at": "2026-07-29T04:51:56.224Z",
    }), encoding="utf-8")
    commands = []
    with mock.patch.object(module, "run", side_effect=lambda cmd: commands.append(cmd)), \
         mock.patch.object(sys, "argv", [
             str(script), "--upload-result-json", str(result_path),
             "--kind", "native_ots_bundle_archive", "--skip-balance"
         ]):
        assert module.main() == 0

    assert commands
    assert "--tx-id=-xDa7E89rAcAYea_QWttPOqHgjtK_6dRyLu9YNwm4xc" in commands[0]
    assert "--tx-id" not in commands[0]
print("PASS: leading-dash Arweave tx id is passed safely to argparse")
