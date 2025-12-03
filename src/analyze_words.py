from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import List

# REMOVE this:
# from .puzzle_bank import PUZZLES

# NEW: load puzzles from puzzle_bank_clean.json next to this file
BASE_DIR = Path(__file__).resolve().parent
PUZZLES: List[dict] = json.loads(
     (BASE_DIR.parent / "8-10_clean.json").read_text(encoding="utf-8")
    # (BASE_DIR / "8-10_clean.json").read_text(encoding="utf-8")
)


def normalize(word: str) -> str:
    """Upper-case and strip spaces so duplicates are caught reliably."""
    return word.strip().upper()


def build_cleaned_puzzles() -> List[dict]:
    """Return a copy of PUZZLES with duplicate words removed globally."""
    seen: set[str] = set()
    cleaned = []
    for entry in PUZZLES:
        unique_words = []
        for word in entry["words"]:
            key = normalize(word)
            if key in seen:
                continue
            seen.add(key)
            unique_words.append(word)
        cleaned.append({"theme": entry["theme"], "words": unique_words})
    return cleaned


def analyze() -> dict:
    """Return statistics and duplicate list."""
    word_counter: Counter[str] = Counter()
    for entry in PUZZLES:
        word_counter.update(normalize(word) for word in entry["words"])

    duplicates = sorted(
        [(word, count) for word, count in word_counter.items() if count > 1],
        key=lambda item: (-item[1], item[0]),
    )
    return {
        "theme_count": len(PUZZLES),
        "total_words": sum(len(entry["words"]) for entry in PUZZLES),
        "unique_words": len(word_counter),
        "duplicates": duplicates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze puzzle bank entries, list duplicates, and optionally write a cleaned copy."
    )
    parser.add_argument(
        "--write-clean",
        type=Path,
        help="Optional path to write a deduplicated JSON copy of PUZZLES.",
    )
    args = parser.parse_args()

    stats = analyze()
    print(f"Total themes: {stats['theme_count']}")
    print(f"Total words (with duplicates): {stats['total_words']}")
    print(f"Unique words: {stats['unique_words']}")
    print(f"Duplicate words ({len(stats['duplicates'])} entries):")
    for word, count in stats["duplicates"]:
        print(f"  {word} ×{count}")

    if args.write_clean:
        cleaned = build_cleaned_puzzles()
        args.write_clean.write_text(json.dumps(cleaned, indent=2))
        print(f"\nClean copy written to {args.write_clean}")


if __name__ == "__main__":
    main()
