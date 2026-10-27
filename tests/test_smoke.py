import importlib.util
from pathlib import Path


def test_probe_script_parses():
    path = Path(__file__).resolve().parents[1] / "scripts" / "probe_phase0.py"
    spec = importlib.util.spec_from_file_location("probe_phase0", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.main)
