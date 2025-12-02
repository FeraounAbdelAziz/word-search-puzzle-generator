from __future__ import annotations


import argparse
import math
import sys
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


from PIL import Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


from .word_search import WordSearchPuzzle, PlacedWord
from .puzzle_bank import PUZZLES


# Import config
sys.path.append(str(Path(__file__).parent.parent))
from config.config_loader import Config

# Load configuration
CONFIG = Config("config/config.json")

# Page settings from config
PAGE_WIDTH = CONFIG.get('page', 'width') * inch
PAGE_HEIGHT = CONFIG.get('page', 'height') * inch
MARGIN = CONFIG.get('page', 'margin') * inch
FONT_DISPLAY = "Biski"
FONT_TEXT = "Biski"


ASSET_LEFT = Path(__file__).with_name(CONFIG.get('images', 'left_image'))
ASSET_RIGHT = Path(__file__).with_name(CONFIG.get('images', 'right_image'))
USER_BISKI_PATH: Path | None = None



def ensure_fonts() -> None:
    """Register Biski font before generating PDF."""
    try:
        pdfmetrics.getFont(FONT_DISPLAY)
    except KeyError:
        register_biski_font()



def register_biski_font() -> None:
    """Register BiskiTrial-Regular.ttf from --biski-path or common locations."""
    candidates: list[Path] = []


    if USER_BISKI_PATH:
        candidates.append(USER_BISKI_PATH)


    # Add common paths (only .ttf, NOT .otf)
    font_name = CONFIG.get('general', 'font_path')
    candidates.extend([
        Path(font_name),
        Path(__file__).parent / font_name,
        Path(__file__).parent.parent / font_name,
    ])


    for candidate in candidates:
        if candidate.exists() and candidate.suffix.lower() == ".ttf":
            pdfmetrics.registerFont(TTFont(FONT_DISPLAY, str(candidate)))
            print(f"[generate_book] Registered Biski font from {candidate}")
            return


    raise FileNotFoundError(
        f"Biski TTF font not found. Tried: {[str(c) for c in candidates]}\n"
        f"Use --biski-path to specify the .ttf file location."
    )



def load_image_reader(asset_path: Path) -> ImageReader | None:
    if asset_path.exists():
        return ImageReader(str(asset_path))
    return None



def draw_page_background(c: canvas.Canvas) -> None:
    bg_color = CONFIG.get('page', 'background_color')
    c.setFillColorRGB(*bg_color)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    
    box_color = CONFIG.get('page', 'box_color')
    c.setFillColorRGB(*box_color)
    border_radius = CONFIG.get('page', 'border_radius')
    c.roundRect(MARGIN * 0.5, MARGIN * 0.5,
                PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN,
                border_radius, fill=1, stroke=0)
    
    border_color = CONFIG.get('page', 'border_color')
    border_width = CONFIG.get('page', 'border_width')
    c.setLineWidth(border_width)
    c.setStrokeColorRGB(*border_color)
    c.roundRect(MARGIN * 0.5, MARGIN * 0.5,
                PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN,
                border_radius, fill=0, stroke=1)



def draw_page_number_box(c: canvas.Canvas, page_num: int) -> None:
    """Draw styled page number box at bottom center with rounded top corners only."""
    if not CONFIG.get('page_number', 'show'):
        return
    
    box_width = CONFIG.get('page_number', 'box_width') * inch
    box_height = CONFIG.get('page_number', 'box_height') * inch
    box_x = (PAGE_WIDTH - box_width) / 2
    box_y = CONFIG.get('page_number', 'position_from_bottom') * inch
    radius = CONFIG.get('page_number', 'border_radius')
    
    box_color = CONFIG.get('page_number', 'box_color')
    c.setFillColorRGB(*box_color)
    
    if CONFIG.get('page_number', 'rounded_top_only'):
        # Draw custom shape with top corners rounded, bottom sharp
        path = c.beginPath()
        path.moveTo(box_x, box_y)
        path.lineTo(box_x + box_width, box_y)
        path.lineTo(box_x + box_width, box_y + box_height - radius)
        path.arcTo(box_x + box_width - radius, box_y + box_height - radius,
                   box_x + box_width, box_y + box_height,
                   startAng=0, extent=90)
        path.lineTo(box_x + radius, box_y + box_height)
        path.arcTo(box_x, box_y + box_height - radius,
                   box_x + radius, box_y + box_height,
                   startAng=90, extent=90)
        path.lineTo(box_x, box_y)
        path.close()
        c.drawPath(path, fill=1, stroke=0)
    else:
        c.roundRect(box_x, box_y, box_width, box_height, radius, fill=1, stroke=0)
    
    # Draw page number
    text_color = CONFIG.get('page_number', 'text_color')
    font_size = CONFIG.get('page_number', 'font_size')
    c.setFont(FONT_DISPLAY, font_size)
    c.setFillColorRGB(*text_color)
    c.drawCentredString(PAGE_WIDTH / 2, box_y + 0.08 * inch, str(page_num))



def draw_word_bank_page(
    c: canvas.Canvas,
    theme: str,
    words: Sequence[str],
    page_num: int,
) -> None:
    """Left page: theme + PNGs + 40-word box."""
    draw_page_background(c)


    # ALTERNATE images based on page number (ONLY ON WORD BANK PAGES)
    if CONFIG.get('images', 'show'):
        if CONFIG.get('images', 'alternate'):
            if page_num % 2 == 1:
                left_asset = ASSET_LEFT
                right_asset = ASSET_RIGHT
            else:
                left_asset = ASSET_RIGHT
                right_asset = ASSET_LEFT
        else:
            left_asset = ASSET_LEFT
            right_asset = ASSET_RIGHT


        # LEFT SIDE IMAGE
        left_img = load_image_reader(left_asset)
        if left_img:
            img = Image.open(left_asset)
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height
            
            max_height = CONFIG.get('images', 'max_height') * inch
            img_height = max_height
            img_width = img_height * aspect_ratio
            
            x_offset = CONFIG.get('images', 'position_x_offset') * inch
            y_offset = CONFIG.get('images', 'position_y_offset') * inch
            left_x = MARGIN * 0.5 + x_offset
            left_y = PAGE_HEIGHT - MARGIN * 0.5 - img_height - y_offset
            c.drawImage(left_img, left_x, left_y,
                        width=img_width, height=img_height, mask="auto", 
                        preserveAspectRatio=CONFIG.get('images', 'preserve_aspect_ratio'))


        # RIGHT SIDE IMAGE
        right_img = load_image_reader(right_asset)
        if right_img:
            img = Image.open(right_asset)
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height
            
            max_height = CONFIG.get('images', 'max_height') * inch
            img_height = max_height
            img_width = img_height * aspect_ratio
            
            x_offset = CONFIG.get('images', 'position_x_offset') * inch
            y_offset = CONFIG.get('images', 'position_y_offset') * inch
            right_x = PAGE_WIDTH - MARGIN * 0.5 - img_width - x_offset
            right_y = PAGE_HEIGHT - MARGIN * 0.5 - img_height - y_offset
            c.drawImage(right_img, right_x, right_y,
                        width=img_width, height=img_height, mask="auto",
                        preserveAspectRatio=CONFIG.get('images', 'preserve_aspect_ratio'))


    # Theme header
    title_config = CONFIG.get('title')
    c.setFont(FONT_DISPLAY, title_config['font_size'])
    title_color = title_config['color']
    c.setFillColorRGB(*title_color)
    
    title = theme.upper()
    center_x = PAGE_WIDTH / 2
    title_y = PAGE_HEIGHT - title_config['position_from_top'] * inch
    
    # Bold effect
    if title_config['bold_effect']:
        offset = title_config['bold_offset']
        for off in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
            c.drawCentredString(center_x + off[0], title_y + off[1], title)
    
    c.drawCentredString(center_x, title_y, title)


    # Word box
    wb_config = CONFIG.get('word_box')
    box_top = PAGE_HEIGHT - wb_config['position_from_top'] * inch
    box_left = MARGIN + wb_config['margin_left'] * inch
    box_right = PAGE_WIDTH - MARGIN - wb_config['margin_right'] * inch
    box_width = box_right - box_left
    box_height = wb_config['height'] * inch
    box_bottom = box_top - box_height


    c.setLineWidth(wb_config['border_width'])
    border_color = wb_config['border_color']
    c.setStrokeColorRGB(*border_color)
    bg_color = wb_config['background_color']
    c.setFillColorRGB(*bg_color)
    c.roundRect(box_left, box_bottom, box_width, box_height, 
                wb_config['border_radius'], fill=1, stroke=1)


    # Words - sorted by length, 4 columns, vertically centered
    cleaned = [w.upper() for w in words]
    if wb_config['sort_by_length']:
        cleaned.sort(key=len)
    
    if cleaned:
        columns = wb_config['columns']
        rows_per_column = wb_config['rows_per_column']
        col_width = box_width / columns
        
        # Calculate total rows needed
        total_rows = (len(cleaned) + columns - 1) // columns

        usable_height = box_height - 0.5 * inch
        row_spacing = usable_height / rows_per_column

        # Better vertical centering
        if wb_config['vertical_align'] == 'center':
            vertical_offset = (box_height - (total_rows * row_spacing)) / 2
        elif wb_config['vertical_align'] == 'top':
            vertical_offset = 0
        else:  # bottom
            vertical_offset = box_height - (total_rows * row_spacing)
        
        base_font_size = wb_config['base_font_size']
        min_font_size = wb_config['min_font_size']
        max_width = col_width - 0.2 * inch
        
        c.setFillColor(colors.black)

        for idx, word in enumerate(cleaned):
            col = idx // rows_per_column
            row = idx % rows_per_column
            
            if col >= columns:
                break
            
            x = box_left + col * col_width + col_width / 2
            y = box_top - vertical_offset - 0.25 * inch - row * row_spacing
            
            # Check if word fits at base size
            text_width = c.stringWidth(word, FONT_TEXT, base_font_size)
            
            if text_width > max_width:
                # Shrink long words
                font_scale = max_width / text_width
                actual_size = max(base_font_size * font_scale * 0.95, min_font_size)
            else:
                # Keep base size for short words
                actual_size = base_font_size
            
            c.setFont(FONT_TEXT, actual_size)
            c.drawCentredString(x, y, word)


    draw_page_number_box(c, page_num)



def draw_puzzle_page(
    c: canvas.Canvas,
    theme: str,
    rows: Sequence[str],
    page_num: int,
) -> None:
    """Right page: puzzle grid - NO IMAGES."""
    draw_page_background(c)


    # Theme header - SAME AS WORD BANK PAGE
    title_config = CONFIG.get('title')
    c.setFont(FONT_DISPLAY, title_config['font_size'])
    title_color = title_config['color']
    c.setFillColorRGB(*title_color)
    
    title = theme.upper()
    center_x = PAGE_WIDTH / 2
    title_y = PAGE_HEIGHT - title_config['position_from_top'] * inch
    
    # Bold effect
    if title_config['bold_effect']:
        offset = title_config['bold_offset']
        for off in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
            c.drawCentredString(center_x + off[0], title_y + off[1], title)
    
    c.drawCentredString(center_x, title_y, title)


    # Puzzle grid
    pg_config = CONFIG.get('puzzle_grid')
    grid_size = len(rows)
    usable_width = PAGE_WIDTH - 2 * MARGIN
    usable_height = PAGE_HEIGHT - pg_config['position_from_top'] * inch - MARGIN
    cell_size = min(usable_width / grid_size, usable_height / grid_size)
    origin_x = (PAGE_WIDTH - cell_size * grid_size) / 2
    origin_y = PAGE_HEIGHT - pg_config['position_from_top'] * inch - cell_size * grid_size


    grid_color = pg_config['grid_line_color']
    c.setLineWidth(pg_config['grid_line_width'])
    c.setStrokeColorRGB(*grid_color)
    for i in range(grid_size + 1):
        c.line(origin_x, origin_y + i * cell_size,
               origin_x + grid_size * cell_size, origin_y + i * cell_size)
        c.line(origin_x + i * cell_size, origin_y,
               origin_x + i * cell_size, origin_y + grid_size * cell_size)


    letter_color = pg_config['letter_color']
    letter_size = cell_size * pg_config['letter_font_size_factor']
    letter_offset = pg_config['letter_vertical_offset']
    c.setFont(FONT_DISPLAY, letter_size)
    c.setFillColorRGB(*letter_color)
    for row_idx, row in enumerate(rows):
        for col_idx, letter in enumerate(row):
            cx = origin_x + col_idx * cell_size + cell_size / 2
            cy = origin_y + (grid_size - row_idx - 1) * cell_size + cell_size / 2
            c.drawCentredString(cx, cy - (cell_size * letter_offset), letter)


    draw_page_number_box(c, page_num)



def draw_solution_overlay(
    c: canvas.Canvas,
    placements: Sequence[PlacedWord],
    grid_size: int,
    origin_x: float,
    origin_y: float,
    cell_size: float,
) -> None:
    sol_config = CONFIG.get('solution')
    highlight_color = sol_config['highlight_color']
    bubble_color = colors.Color(highlight_color[0], highlight_color[1], highlight_color[2])
    thickness = cell_size * sol_config['thickness_factor']
    end_padding = cell_size * sol_config['end_padding_factor']


    for placed in placements:
        if not placed.path:
            continue
        start = placed.path[0]
        end = placed.path[-1]
        start_x = origin_x + start[0] * cell_size + cell_size / 2
        start_y = origin_y + (grid_size - start[1] - 1) * cell_size + cell_size / 2
        end_x = origin_x + end[0] * cell_size + cell_size / 2
        end_y = origin_y + (grid_size - end[1] - 1) * cell_size + cell_size / 2


        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy)


        if length == 0:
            c.setFillColor(bubble_color)
            c.circle(start_x, start_y, thickness / 2, stroke=0, fill=1)
            continue


        pad_x = (dx / length) * end_padding
        pad_y = (dy / length) * end_padding
        adj_start_x = start_x - pad_x
        adj_start_y = start_y - pad_y
        adj_end_x = end_x + pad_x
        adj_end_y = end_y + pad_y


        draw_capsule(c, adj_start_x, adj_start_y, adj_end_x, adj_end_y, thickness, bubble_color)



def draw_capsule(
    c: canvas.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    thickness: float,
    color,
) -> None:
    radius = thickness / 2
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        c.setFillColor(color)
        c.circle(x1, y1, radius, stroke=0, fill=1)
        return
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    c.saveState()
    c.translate(mid_x, mid_y)
    c.rotate(angle)
    c.setFillColor(color)
    c.roundRect(-length / 2, -radius, length, thickness, radius, stroke=0, fill=1)
    c.restoreState()



def draw_solution_page_full(
    c: canvas.Canvas,
    puzzle_page_num: int,
    puzzle: WordSearchPuzzle,
    page_num: int,
) -> None:
    """Solution page - NO IMAGES."""
    draw_page_background(c)


    # Title
    title_config = CONFIG.get('title')
    c.setFont(FONT_DISPLAY, title_config['font_size'])
    title_color = title_config['color']
    c.setFillColorRGB(*title_color)
    
    title = f"SOLUTION {puzzle_page_num}"
    center_x = PAGE_WIDTH / 2
    title_y = PAGE_HEIGHT - title_config['position_from_top'] * inch
    
    # Bold effect
    if title_config['bold_effect']:
        offset = title_config['bold_offset']
        for off in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
            c.drawCentredString(center_x + off[0], title_y + off[1], title)
    
    c.drawCentredString(center_x, title_y, title)


    # Grid
    pg_config = CONFIG.get('puzzle_grid')
    rows = puzzle.as_rows()
    grid_size = len(rows)
    usable_width = PAGE_WIDTH - 2 * MARGIN
    usable_height = PAGE_HEIGHT - pg_config['position_from_top'] * inch - MARGIN
    cell_size = min(usable_width / grid_size, usable_height / grid_size)
    origin_x = (PAGE_WIDTH - cell_size * grid_size) / 2
    origin_y = PAGE_HEIGHT - pg_config['position_from_top'] * inch - cell_size * grid_size


    draw_solution_overlay(c, puzzle.placements, grid_size, origin_x, origin_y, cell_size)


    grid_color = pg_config['grid_line_color']
    c.setLineWidth(pg_config['grid_line_width'])
    c.setStrokeColorRGB(*grid_color)
    for i in range(grid_size + 1):
        c.line(origin_x, origin_y + i * cell_size,
               origin_x + grid_size * cell_size, origin_y + i * cell_size)
        c.line(origin_x + i * cell_size, origin_y,
               origin_x + i * cell_size, origin_y + grid_size * cell_size)


    letter_color = pg_config['letter_color']
    letter_size = cell_size * pg_config['letter_font_size_factor']
    letter_offset = pg_config['letter_vertical_offset']
    c.setFont(FONT_DISPLAY, letter_size)
    c.setFillColorRGB(*letter_color)
    for row_idx, row in enumerate(rows):
        for col_idx, letter in enumerate(row):
            cx = origin_x + col_idx * cell_size + cell_size / 2
            cy = origin_y + (grid_size - row_idx - 1) * cell_size + cell_size / 2
            c.drawCentredString(cx, cy - (cell_size * letter_offset), letter)


    draw_page_number_box(c, page_num)



def debug_puzzles() -> None:
    """Print quick info about PUZZLES so you can see why 0 are used."""
    print(f"[generate_book] PUZZLES themes: {len(PUZZLES)}")
    if not PUZZLES:
        print("  ⚠ PUZZLES is empty. Check puzzle_bank.py / JSON path.")
        return
    for entry in PUZZLES[:3]:
        theme = entry.get("theme", "???")
        words = entry.get("words", [])
        print(f"  Theme: {theme} ({len(words)} words) sample: {words[:5]}")



def build_puzzles(count: int, size: int, seed: int) -> List[Tuple[dict, WordSearchPuzzle]]:
    puzzles: List[Tuple[dict, WordSearchPuzzle]] = []
    src_idx = 0
    safety = 0
    max_safety = max(len(PUZZLES) * 10, 1)
    min_words = CONFIG.get('puzzle_generation', 'min_words_per_puzzle')
    
    while len(puzzles) < count and safety < max_safety:
        data = PUZZLES[src_idx % len(PUZZLES)]
        usable_words = [w for w in data["words"] if len(w.replace(" ", "")) <= size]
        src_idx += 1
        safety += 1
        if len(usable_words) < min_words:
            continue
        puzzle = WordSearchPuzzle(size=size, words=usable_words, seed=seed + src_idx)
        try:
            puzzle.generate()
        except RuntimeError:
            continue
        puzzles.append(({"theme": data["theme"], "words": usable_words}, puzzle))
    return puzzles



def generate_pdf(
    output: Path,
    count: int,
    size: int,
    seed: int,
    biski_path: Path | None = None,
    compact_solutions: bool = False,
) -> None:
    global USER_BISKI_PATH
    USER_BISKI_PATH = biski_path
    ensure_fonts()


    c = canvas.Canvas(str(output), pagesize=(PAGE_WIDTH, PAGE_HEIGHT), pageCompression=0)
    c.setPageCompression(0)


    debug_puzzles()
    puzzles = build_puzzles(count, size, seed)
    num_puzzles = len(puzzles)


    solution_pages = num_puzzles if CONFIG.get('solution', 'show_solutions') else 0


    total_pages = (num_puzzles * 2) + solution_pages
    print(f"Generating {num_puzzles} puzzles ({total_pages} pages)...")


    page_num = 1


    for idx, (data, puzzle) in enumerate(puzzles, start=1):
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{num_puzzles} puzzles...")


        draw_word_bank_page(c, data["theme"], data["words"], page_num)
        c.showPage()
        page_num += 1


        draw_puzzle_page(c, data["theme"], puzzle.as_rows(), page_num)
        c.showPage()
        page_num += 1


    if CONFIG.get('solution', 'show_solutions'):
        for idx, (data, puzzle) in enumerate(puzzles, start=1):
            if idx % 5 == 0:
                print(f"  Solution pages: {idx}/{num_puzzles}...")
            puzzle_page = idx
            draw_solution_page_full(c, puzzle_page, puzzle, page_num)
            c.showPage()
            page_num += 1


    c.save()
    print(f"[INFO] Generating {num_puzzles} puzzles ({total_pages} pages)...")
    USER_BISKI_PATH = None



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Winter Word Search Book Generator")
    
    # Get defaults from config
    default_output = CONFIG.get('general', 'output_file')
    default_count = CONFIG.get('puzzle_generation', 'count')
    default_size = CONFIG.get('puzzle_generation', 'grid_size')
    default_seed = CONFIG.get('puzzle_generation', 'seed')
    
    parser.add_argument("--output", type=Path, default=Path(default_output), help="PDF path")
    parser.add_argument("--count", type=int, default=default_count, help="Number of puzzles")
    parser.add_argument("--size", type=int, default=default_size, help="Grid size (NxN)")
    parser.add_argument("--seed", type=int, default=default_seed, help="Random seed")
    parser.add_argument("--biski-path", type=Path, help="Biski TTF font path (optional)")
    parser.add_argument("--compact-solutions", action="store_true", help="(Ignored - always 1 per page)")
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    generate_pdf(args.output, args.count, args.size, args.seed, args.biski_path, args.compact_solutions)



if __name__ == "__main__":
    main()
