"""
User preferences management
Save and load user-specific settings
"""

import streamlit as st
import json
from pathlib import Path

class UserPreferences:
    def __init__(self, user_email):
        self.user_email = user_email
        self.prefs_dir = Path("user_data/preferences")
        self.prefs_dir.mkdir(parents=True, exist_ok=True)
        self.prefs_file = self.prefs_dir / f"{user_email.replace('@', '_at_').replace('.', '_')}.json"
    
    def get_default_preferences(self):
        """Get default preferences - extracted from generate_book.py hardcoded values"""
        return {
            "colors": {
                "bg_color": "#D9F0F8",           # 0.85, 0.94, 0.97
                "border_color": "#5A9CBD",       # 0.35, 0.61, 0.74
                "page_num_color": "#3489B3",     # 0.2, 0.55, 0.7
                "page_num_text_color": "#FFFFFF",
                "title_color": "#3489B3",        # 0.2, 0.55, 0.7
                "letter_color": "#1F3B4D",       # 0.12, 0.23, 0.30
                "wb_bg_color": "#F0F8FB",        # 0.94, 0.97, 0.98
                "wb_border_color": "#5A9CBD",    # 0.35, 0.61, 0.74
                "grid_line_color": "#BDD9F0",    # 0.74, 0.87, 0.94
                "highlight_color": "#7BBDE9",    # 0.48, 0.74, 0.91
            },
            "settings": {
                # From generate_book.py hardcoded values
                "puzzle_count": 6,
                "grid_size": 25,
                "seed": 42,
                "min_words": 8,
                "page_width": 8.5,
                "page_height": 11.0,
                "margin": 0.5,
                "border_width": 2,
                "border_radius": 20,
                "title_size": 28,
                "title_position": 1.1,
                "title_bold": True,
                "title_bold_offset": 0.5,
                "wb_columns": 4,
                "wb_rows": 10,
                "wb_font_size": 13,
                "wb_min_font": 8,
                "wb_sort": True,
                "wb_position": 1.8,
                "wb_height": 8.2,
                "wb_margin_left": 0.3,
                "wb_margin_right": 0.3,
                "wb_border_width": 2,
                "wb_border_radius": 12,
                "wb_vertical_align": "center",
                "grid_line_width": 1,
                "letter_font_factor": 0.55,
                "letter_v_offset": 0.2,
                "grid_position": 2.0,
                "show_solutions": True,
                "highlight_thickness": 0.7,
                "end_padding": 0.45,
                "show_page_nums": True,
                "page_num_position": 0.25,
                "page_num_width": 1.2,
                "page_num_height": 0.35,
                "page_num_font_size": 18,
                "rounded_top_only": True,
                "show_images": True,
                "alternate_images": True,
                "image_height": 1.1,
                "image_x_offset": 0.2,
                "image_y_offset": 0.2,
            },
            "saved_books": [],
            "history": []
        }
    
    def load(self):
        """Load user preferences"""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_preferences()
        return self.get_default_preferences()
    
    def save(self, preferences):
        """Save user preferences"""
        with open(self.prefs_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def save_current_colors(self):
        """Save current session colors to user preferences"""
        prefs = self.load()
        prefs['colors'] = {
            'bg_color': st.session_state.get('bg_color', '#D9F0F8'),
            'border_color': st.session_state.get('border_color', '#5A9CBD'),
            'page_num_color': st.session_state.get('page_num_color', '#3489B3'),
            'page_num_text_color': st.session_state.get('page_num_text_color', '#FFFFFF'),
            'title_color': st.session_state.get('title_color', '#3489B3'),
            'letter_color': st.session_state.get('letter_color', '#1F3B4D'),
            'wb_bg_color': st.session_state.get('wb_bg_color', '#F0F8FB'),
            'wb_border_color': st.session_state.get('wb_border_color', '#5A9CBD'),
            'grid_line_color': st.session_state.get('grid_line_color', '#BDD9F0'),
            'highlight_color': st.session_state.get('highlight_color', '#7BBDE9'),
        }
        self.save(prefs)
    
    def load_colors_to_session(self):
        """Load user's saved colors into session state"""
        prefs = self.load()
        colors = prefs.get('colors', {})
        
        for key, value in colors.items():
            st.session_state[key] = value
    
    def save_book(self, book_name, config_snapshot):
        """Save a book configuration"""
        prefs = self.load()
        
        existing = next((b for b in prefs['saved_books'] if b['name'] == book_name), None)
        
        if existing:
            existing['config'] = config_snapshot
            existing['updated_at'] = str(st.session_state.get('timestamp', 'unknown'))
        else:
            prefs['saved_books'].append({
                'name': book_name,
                'config': config_snapshot,
                'created_at': str(st.session_state.get('timestamp', 'unknown'))
            })
        
        self.save(prefs)
    
    def get_saved_books(self):
        """Get all saved books"""
        prefs = self.load()
        return prefs.get('saved_books', [])
    
    def delete_book(self, book_name):
        """Delete a saved book"""
        prefs = self.load()
        prefs['saved_books'] = [b for b in prefs['saved_books'] if b['name'] != book_name]
        self.save(prefs)
    
    def load_book(self, book_name):
        """Load a saved book configuration"""
        books = self.get_saved_books()
        book = next((b for b in books if b['name'] == book_name), None)
        return book['config'] if book else None
    
    def save_history_state(self, config_snapshot):
        """Save current state to history for undo/redo"""
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'history_index' not in st.session_state:
            st.session_state.history_index = -1
        
        # Remove any future history if we're not at the end
        if st.session_state.history_index < len(st.session_state.history) - 1:
            st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]
        
        # Add new state
        st.session_state.history.append(config_snapshot.copy())
        st.session_state.history_index += 1
        
        # Limit history to 50 states
        if len(st.session_state.history) > 50:
            st.session_state.history.pop(0)
            st.session_state.history_index -= 1
    
    def undo(self):
        """Undo to previous state"""
        if 'history' not in st.session_state or st.session_state.history_index <= 0:
            return None
        
        st.session_state.history_index -= 1
        return st.session_state.history[st.session_state.history_index]
    
    def redo(self):
        """Redo to next state"""
        if 'history' not in st.session_state or st.session_state.history_index >= len(st.session_state.history) - 1:
            return None
        
        st.session_state.history_index += 1
        return st.session_state.history[st.session_state.history_index]
    
    def can_undo(self):
        """Check if undo is available"""
        return 'history' in st.session_state and st.session_state.history_index > 0
    
    def can_redo(self):
        """Check if redo is available"""
        return 'history' in st.session_state and st.session_state.history_index < len(st.session_state.history) - 1
