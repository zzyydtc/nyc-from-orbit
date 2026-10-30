import importlib.util
from pathlib import Path

import numpy as np


def load_script(name):
    path = Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deviance_is_zero_for_perfect_prediction_and_positive_otherwise():
    m8 = load_script("08_incremental_value")
    y = np.array([0, 1, 5, 20])
    assert np.allclose(m8.deviance(y, y.astype(float).clip(min=1e-9)), 0.0, atol=1e-6)
    assert (m8.deviance(y, np.array([2.0, 2.0, 2.0, 2.0])) > 0).all()


def test_deviance_handles_zero_counts():
    m8 = load_script("08_incremental_value")
    d = m8.deviance(np.array([0, 0]), np.array([0.5, 3.0]))
    assert np.allclose(d, [1.0, 6.0])
