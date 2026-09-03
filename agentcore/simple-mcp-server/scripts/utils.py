"""Shared helpers for the scripts in this directory."""
from __future__ import annotations

import sys
from pathlib import Path

# tmp/ lives at the repo root, one level up from this scripts/ directory.
TMP_DIR = Path(__file__).resolve().parent.parent / "tmp"


def read_value(filename: str) -> str:
    """Read and strip a single value from a file in the ./tmp directory."""
    path = TMP_DIR / filename
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        sys.exit(f"error: missing required file {path}")
