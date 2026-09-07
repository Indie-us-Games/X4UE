"""Build a Blender-installable X4UE add-on archive."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ADDON_ROOT = REPOSITORY_ROOT / "x4ue"


def build_archive(output: Path) -> None:
    if not ADDON_ROOT.is_dir() or not (ADDON_ROOT / "__init__.py").is_file():
        raise RuntimeError(f"Blender add-on package not found: {ADDON_ROOT}")

    output = output if output.is_absolute() else REPOSITORY_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(ADDON_ROOT.rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            archive_name = Path("x4ue") / source.relative_to(ADDON_ROOT)
            archive.write(source, archive_name.as_posix())

    print(output.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="dist/X4UE-Blender.zip",
        help="output archive path, relative to the repository root",
    )
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None
    args = parser.parse_args(script_args)
    build_archive(Path(args.output))


if __name__ == "__main__":
    main()
