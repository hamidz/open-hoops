# Root-level conftest.py
#
# Ensures that each service's package root is on sys.path so that tests can be
# run from the repository root (e.g. `pytest services/`) in addition to the
# per-service invocations used by the Makefile.
#
# Each service's own pyproject.toml already sets `pythonpath = ["."]` for
# per-directory invocations; this file covers the combined/root case.

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_SERVICE_ROOTS = [
    _REPO_ROOT / "apps" / "api",
    _REPO_ROOT / "services" / "cv_worker",
    _REPO_ROOT / "services" / "analytics_worker",
    _REPO_ROOT / "services" / "llm_service",
]

for _root in _SERVICE_ROOTS:
    _root_str = str(_root)
    if _root_str not in sys.path:
        sys.path.insert(0, _root_str)
