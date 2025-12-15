import os
import json
from pathlib import Path
import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "optimization/outputs/releases/v1.4.0"
FIG_DIR = OUT_DIR / "figures"


def run_notebook(nb_path: Path):
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(nb, timeout=300, kernel_name="python3", allow_errors=False)
    client.execute()


def test_release_demo_runs_and_outputs():
    nb_path = ROOT / "notebooks" / "v1.4.0_release_demo.ipynb"
    assert nb_path.exists()
    run_notebook(nb_path)
    assert (OUT_DIR / "demo_summary.json").exists()


def test_performance_compare_runs_and_outputs():
    nb_path = ROOT / "notebooks" / "v1.4.0_performance_compare.ipynb"
    assert nb_path.exists()
    run_notebook(nb_path)
    assert (OUT_DIR / "metrics.json").exists()
    assert FIG_DIR.exists()
