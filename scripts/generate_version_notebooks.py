import shutil
from pathlib import Path
import json


def generate(version: str):
    root = Path(__file__).resolve().parents[1]
    nb_dir = root / "notebooks"
    nb_dir.mkdir(exist_ok=True)

    mapping = {
        "template_release_demo.ipynb": f"{version}_release_demo.ipynb",
        "template_performance_compare.ipynb": f"{version}_performance_compare.ipynb",
    }

    for src_name, dst_name in mapping.items():
        src = nb_dir / src_name
        dst = nb_dir / dst_name
        shutil.copyfile(src, dst)
        print(f"Created {dst}")


if __name__ == "__main__":
    generate("vX.Y.Z")
