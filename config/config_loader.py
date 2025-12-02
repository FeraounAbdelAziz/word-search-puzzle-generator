import json
from pathlib import Path
from typing import Any, Dict


class Config:
    """Load and access configuration from config.json"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self.data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config file or create default if missing."""
        if not self.config_path.exists():
            print(f"⚠️ Config file not found: {self.config_path}")
            print("   Using default settings...")
            return self._default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "page": {
                "width": 8.5,
                "height": 11.0,
                "margin": 0.5,
                "background_color": [0.85, 0.94, 0.97],
                "box_color": [1.0, 1.0, 1.0],
                "border_color": [0.35, 0.61, 0.74],
                "border_width": 2,
                "border_radius": 20
            },
            "title": {
                "font_size": 28,
                "color": [0.2, 0.55, 0.7],
                "position_from_top": 1.1,
                "bold_effect": True,
                "bold_offset": 0.5
            },
            "word_box": {
                "position_from_top": 2.0,
                "height": 8.0,
                "margin_left": 0.3,
                "margin_right": 0.3,
                "background_color": [0.94, 0.97, 0.98],
                "border_color": [0.35, 0.61, 0.74],
                "border_width": 2,
                "border_radius": 12,
                "columns": 4,
                "rows_per_column": 10,
                "base_font_size": 13,
                "min_font_size": 8,
                "sort_by_length": True,
                "vertical_align": "center"
            },
            "puzzle_grid": {
                "position_from_top": 2.0,
                "grid_line_color": [0.74, 0.87, 0.94],
                "grid_line_width": 1,
                "letter_font_size_factor": 0.55,
                "letter_color": [0.12, 0.23, 0.30],
                "letter_vertical_offset": 0.2
            },
            "solution": {
                "highlight_color": [0.48, 0.74, 0.91],
                "thickness_factor": 0.7,
                "end_padding_factor": 0.45,
                "show_solutions": True
            },
            "page_number": {
                "show": True,
                "position_from_bottom": 0.2,
                "box_width": 1.2,
                "box_height": 0.35,
                "box_color": [0.2, 0.55, 0.7],
                "text_color": [1.0, 1.0, 1.0],
                "font_size": 18,
                "rounded_top_only": True,
                "border_radius": 10
            },
            "images": {
                "show": True,
                "pages": "word_bank_only",
                "alternate": True,
                "max_height": 1.1,
                "position_x_offset": 0.2,
                "position_y_offset": 0.2,
                "preserve_aspect_ratio": True,
                "left_image": "left.png",
                "right_image": "right.png"
            },
            "puzzle_generation": {
                "count": 6,
                "grid_size": 25,
                "seed": 42,
                "min_words_per_puzzle": 8,
                "max_word_length": 25
            },
            "general": {
                "font_path": "BiskiTrial-Regular.ttf",
                "output_file": "winter_word_search.pdf",
                "puzzle_data": "puzzle_bank_no_duplicates.json"
            }
        }
    
    def get(self, *keys):
        """Get nested config value. Example: config.get('page', 'width')"""
        value = self.data
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value
    
    def save(self):
        """Save current config back to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ Config saved to {self.config_path}")
