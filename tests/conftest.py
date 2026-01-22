import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `app` imports work in tests.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
