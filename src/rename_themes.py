from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


DATA_PATH = Path(__file__).with_name("puzzle_bank_data.json")
BACKUP_PATH = Path(__file__).with_name("puzzle_bank_data.backup.json")


def normalize_theme(theme: str) -> str:
    """
    Strip trailing numeric suffixes like 'Winter Weather 03' -> 'Winter Weather'.
    Also collapse excess whitespace.
    """
    # Remove trailing sequences of whitespace + digits
    stripped = re.sub(r"\s+\d+\s*$", "", theme)
    # Normalise internal whitespace
    stripped = " ".join(stripped.split())
    return stripped


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing data file: {DATA_PATH}")

    data: List[Dict] = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    # Backup original once, if not already there.
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    seen: Dict[str, int] = {}
    for entry in data:
        old_theme = entry.get("theme", "")
        base = normalize_theme(old_theme)

        # If we've used this theme label before, add a small letter suffix (no numbers).
        count = seen.get(base, 0)
        seen[base] = count + 1
        if count == 0:
            new_theme = base
        else:
            # e.g. "Winter Weather (B)", "Winter Weather (C)", etc.
            suffix = chr(ord("A") + count)
            new_theme = f"{base} ({suffix})"

        entry["theme"] = new_theme

    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Updated {len(data)} themes in {DATA_PATH}")
    print(f"Original copy saved to {BACKUP_PATH}")


if __name__ == "__main__":
    main()


