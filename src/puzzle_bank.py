from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Import config to read puzzle_data setting
sys.path.append(str(Path(__file__).parent.parent))
from config.config_loader import Config

# Base directory where this file lives
BASE_DIR = Path(__file__).resolve().parent

# Load config to get puzzle_data file
config = Config("config/config.json")
configured_puzzle_file = config.get('general', 'puzzle_data')

# Candidate JSON files (check config first, then fallbacks)
_CANDIDATE_FILES = [
    BASE_DIR.parent / configured_puzzle_file,  # FROM CONFIG (e.g., puzzle_bank_custom.json)
    BASE_DIR / configured_puzzle_file,         # Try in src/ folder too
    BASE_DIR / "puzzle_bank_clean.json",       # Fallback 1
    BASE_DIR / "puzzle_bank_data.json",        # Fallback 2
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
