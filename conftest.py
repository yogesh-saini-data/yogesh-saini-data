"""
conftest.py — Pytest and IDE configuration for module path resolution.

Adds the 'scripts' directory to sys.path so test files can import modules
directly (e.g. `import github_api`) without static linter warnings.
"""

import sys
from pathlib import Path

# Add project root and scripts directory to sys.path
root_dir = Path(__file__).resolve().parent
scripts_dir = root_dir / "scripts"

if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
