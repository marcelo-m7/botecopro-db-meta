import sys
from pathlib import Path

DIST_PACKAGES = Path("/usr/lib/python3/dist-packages")
if DIST_PACKAGES.exists():
    sys.path.insert(0, str(DIST_PACKAGES))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
