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
        """Get default preferences"""
        return {
            "colors": {
                "bg_color": "#D9F0F8",
                "border_color": "#5A9CBD",
                "page_num_color": "#3489B3",
                "page_num_text_color": "#FFFFFF",
                "title_color": "#3489B3",
                "letter_color": "#1F3B4D",
                "wb_bg_color": "#F0F8FB",
                "wb_border_color": "#5A9CBD",
                "grid_line_color": "#BDD9F0",
                "highlight_color": "#7BBDE9",
            },
            "saved_books": []
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
        
        # Check if book already exists
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
