# Winter Word Search Factory

Generate polished, print-ready winter word-search books packed with unique vocabulary, seasonal hobbies, cozy cabin life, and more. The tooling here builds a deduplicated puzzle bank with thousands of curated words, renders 6"×9" PDFs with custom art/fonts, and keeps everything reproducible.

## Highlights
- **Massive themed bank:** 542 puzzle themes, 8,015 total placements, 5,166 unique winter-friendly words (gear, food, science, wellness, crafts, sports, fauna, flora, etc.).
- **Print-ready layout:** ReportLab-powered renderer with backgrounds, header art, Biski display font, puzzle & solution spreads, and rounded numbered page tabs.
- **Deterministic builds:** Seeds ensure puzzles can be regenerated identically; data is JSON-driven so you can tweak vocab without touching code.
- **Quality gate:** `src/analyze_words.py` surfaces duplicates, totals, and can emit a deduped JSON snapshot whenever you refresh the source list.

## Prerequisites
- Python 3.11+ (3.12 works too).
- Windows font install for **Biski** (Biski.ttf / BiskiTrial-Regular.otf) or drop the file next to `src/generate_book.py` and use `--biski-path`.
- System deps: `pip install -r requirements.txt` (ReportLab + Pillow).
- Asset: `src/WINTER.png` (already included) for the banner graphic.

```powershell
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Data Workflow
1. **Curated baseline:** `puzzle_bank_clean.json` holds the raw winter vocab grouped by theme (duplicates allowed here for convenience).
2. **Generate production bank:**  
   ```powershell
   python -m src.build_winter_bank
   ```  
   This writes `src/puzzle_bank_data.json` (542 themes / 8,015 entries) and is what the renderer consumes.
3. **Check counts & duplicates (one-liner):**  
   ```powershell
   python -m src.analyze_words
   ```  
   This prints total themes, total words, unique words, and every duplicate entry.  
   Add `--write-clean puzzle_bank_deduped.json` if you also want a deduped snapshot written to disk.

If you edit the curated sets inside `src/build_winter_bank.py` (e.g., add more hobbies, food, or custom compound rules), rerun the module to refresh `puzzle_bank_data.json`.

## Generating the PDF
```powershell
python -m src.generate_book `
  --output winter_puzzles_192.pdf `
  --count 96 `
  --size 14 `
  --seed 42 `
  --biski-path "C:\Fonts\Biski.ttf"
```

- `--count`: puzzle count (each puzzle gets a solution page, so 96 ⇒ 192 pages).
- `--size`: grid size (e.g., 14x14).
- `--seed`: reproducible randomness for word placement.
- `--biski-path`: optional override if the font isn’t installed globally.

Output is a 300‑dpi-ready PDF with alternating puzzle/solution spreads, word banks, highlight overlays, and rounded page-number capsules anchored to the border.

## Customization
- **Layout tweaks:** adjust constants near the top of `src/generate_book.py` (`PAGE_WIDTH`, `PAGE_HEIGHT`, padding, colors).
- **Themes/words:** curate sets in `src/build_winter_bank.py`; the helper functions (`build_compounds`, curated category sets) make it easy to seed more vocab or merge additional niches.
- **Fonts/branding:** drop new assets alongside `WINTER.png`, update headers, or swap `FONT_DISPLAY`/`FONT_TEXT`.

## Repository Map
```
src/
  analyze_words.py      # Duplicate detector & stats helper
  build_winter_bank.py  # Curated + synthetic bank generator
  generate_book.py      # ReportLab renderer for puzzles/solutions
  puzzle_bank.py        # Thin loader that reads puzzle_bank_data.json
  puzzle_bank_data.json # Generated production bank (git-tracked)
  WINTER.png            # Banner artwork
  word_search.py        # Word-placement engine
```

## Tips
- Commit the regenerated `puzzle_bank_data.json` whenever you change the builder inputs so collaborators get identical PDFs.
- Keep `--seed` values logged for each book/edition; that makes incremental edits painless.
- If ReportLab throws a Biski font error, verify the font path and that the file isn’t an OTF collection (use the single-face TTF/OTF included with the asset pack).

Happy publishing! Let me know if you want automation scripts for KDP metadata or bleed versions.

