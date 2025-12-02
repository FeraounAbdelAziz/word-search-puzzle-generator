import json
from pathlib import Path
from collections import defaultdict
from src.replacements import REPLACEMENTS as MANUAL_REPLACEMENTS

BASE_DIR = Path(__file__).resolve().parent

# adjust INPUT name/path if needed
INPUT = BASE_DIR / "puzzle_bank_data.json"
OUTPUT = BASE_DIR / "puzzle_bank_clean.json"


def build_word_theme_index(data):
    """Map each word -> list of themes it appears in."""
    word_to_themes = defaultdict(list)
    for block in data:
        theme = block["theme"]
        for w in block["words"]:
            word_to_themes[w].append(theme)
    return word_to_themes


def slugify_theme(theme: str) -> str:
    """
    Make a short, letter-only suffix from the theme name.
    'Alpine Skiing' -> 'skiing'
    'Winter Mountaineering' -> 'mountaineering'
    """
    letters = [ch for ch in theme if ch.isalpha()]
    slug = "".join(letters)
    # use the last 12 letters to keep it reasonably short
    return (slug[-12:] or slug).lower()


def build_auto_replacements(data):
    """
    For every word that appears in multiple themes, create replacements
    for all *but the first* theme.

    Example: 'alpine' in 3 themes ->
      first theme keeps 'alpine'
      others get 'alpinemountaineering', 'alpineclimbing', etc.
    """
    word_to_themes = build_word_theme_index(data)
    auto = {}
    # collect all existing words to avoid collisions
    all_words = set()
    for block in data:
        all_words.update(block["words"])

    for word, themes in word_to_themes.items():
        if len(themes) <= 1:
            continue

        owner = themes[0]  # first theme keeps original
        theme_map = {}
        for theme in themes[1:]:
            base_slug = slugify_theme(theme)
            candidate = f"{word}{base_slug}"  # e.g. 'alpine' + 'mountaineering'
            # ensure uniqueness
            while candidate in all_words:
                candidate += "x"
            all_words.add(candidate)
            theme_map[theme] = candidate

        auto[word.upper()] = theme_map

    return auto


def merge_replacements(auto, manual):
    """
    Merge auto-generated and manual replacements.
    Manual (your REPLACEMENTS.py) always wins if both exist.
    """
    merged = auto.copy()
    for word, theme_map in manual.items():
        if word not in merged:
            merged[word] = {}
        merged[word].update(theme_map)
    return merged


def transform(data, replacements):
    """Apply replacements to the JSON data."""
    for block in data:
        theme = block["theme"]
        new_words = []
        for w in block["words"]:
            key = w.upper()
            if key in replacements and theme in replacements[key]:
                new_words.append(replacements[key][theme])
            else:
                new_words.append(w)
        block["words"] = new_words
    return data


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))

    # 1) Build automatic replacements for ALL duplicates (e.g. ALPINE x3)
    auto_repl = build_auto_replacements(data)

    # 2) Merge with your hand-made REPLACEMENTS (powdersnow, powstash, etc.)
    all_repl = merge_replacements(auto_repl, MANUAL_REPLACEMENTS)

    # 3) Apply everything
    cleaned = transform(data, all_repl)

    # Optional: inspect a few specific words like 'alpine'
    # print(json.dumps(all_repl.get("ALPINE", {}), indent=2))

    OUTPUT.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote cleaned JSON to {OUTPUT}")


if __name__ == "__main__":
    main()
