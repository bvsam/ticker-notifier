import shutil
from pathlib import Path

# Source and target layer paths
LAYER1_PATH = Path("layers") / "layer1" / "python"
LAYER2_PATH = Path("layers") / "layer2" / "python"

# Packages to move
TARGET_PACKAGES = ["numpy", "pandas"]


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def move_package(pkg: str):
    moved = []
    for item in LAYER1_PATH.iterdir():
        if item.name.startswith(pkg):
            dst = LAYER2_PATH / item.name
            print(f"Moving {item} -> {dst}")
            shutil.move(str(item), str(dst))
            moved.append(item.name)
    if not moved:
        print(f"WARNING: {pkg} not found in {LAYER1_PATH}")


def main():
    ensure_dir(LAYER2_PATH)
    for pkg in TARGET_PACKAGES:
        move_package(pkg)


if __name__ == "__main__":
    main()
