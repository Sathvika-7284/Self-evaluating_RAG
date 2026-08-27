import sys
from pathlib import Path


# Allow "pytest" to be run from the repository root or via an absolute test path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
