from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

# Base directory where this file lives
BASE_DIR = Path(__file__).resolve().parent

# Candidate JSON files (first one that exists will be used)
_CANDIDATE_FILES = [
    BASE_DIR / "puzzle_bank_clean.json",  # cleaned list you generated
    BASE_DIR / "puzzle_bank_data.json",   # original / backup
]

PUZZLES: List[Dict[str, Any]] = []

for path in _CANDIDATE_FILES:
    if path.exists():
        PUZZLES = json.loads(path.read_text(encoding="utf-8"))
        print(f"[puzzle_bank] Loaded {len(PUZZLES)} themes from {path.name}")
        break

if not PUZZLES:
    raise FileNotFoundError(
        "No puzzle bank JSON found. Expected one of: "
        + ", ".join(str(p) for p in _CANDIDATE_FILES)
    )
    
