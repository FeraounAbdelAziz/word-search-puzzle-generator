import streamlit as st
import json
import sys
from pathlib import Path
import base64
import time
from config.config_loader import Config
from auth import Auth, show_auth_page
from user_preferences import UserPreferences

# CRITICAL FIX: Import PDF generation directly instead of subprocess
from src.generate_book import generate_pdf

# Ensure folders exist
Path("images").mkdir(exist_ok=True)
Path("fonts").mkdir(exist_ok=True)
Path("user_data/preferences").mkdir(parents=True, exist_ok=True)

# Page config
st.set_page_config(page_title="Word Search PDF Generator", layout="wide", page_icon="🔍")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Check if user is logged in
auth = Auth()
if not auth.is_logged_in():
    show_auth_page()
    st.stop()

# User is logged in - show main app
user = auth.get_current_user()
user_prefs = UserPreferences(user['email'])

# Custom CSS
st.markdown(f"""
<style>
    .main-header {{
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background: #3d256c;
        border-radius: 12px 12px 0 0;
        padding-left: 0.2em;
        flex-wrap: nowrap;
        overflow-x: auto;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px;
        padding: 6px 10px;
        background-color: #4d318b !important;
        color: #fff !important;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-family: 'Inter', -apple-system, sans-serif;
        transition: background 0.2s;
        opacity: 0.92;
        font-size: 0.8rem;
        white-space: nowrap;
        min-width: fit-content;
        flex-shrink: 0;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #fff !important;
        color: #5a3297 !important;
        box-shadow: 0 -3px 18px #764ba239;
        font-weight: bold;
        opacity: 1;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }}

    /* User info box styling */
    .user-info-box {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        display: inline-block;
        margin-bottom: 10px;
    }}

    /* Logout button styling to match */
    .stButton button[key="navbar_logout"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        transition: all 0.2s !important;
        height: auto !important;
    }}
    .stButton button[key="navbar_logout"]:hover {{
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-1px) !important;
    }}
</style>
""", unsafe_allow_html=True)

# AUTO-LOAD LAST SESSION
if 'session_loaded' not in st.session_state:
    last_session = user_prefs.load_last_session()
    if last_session:
        st.session_state.update(last_session)
        st.toast("Restored your last session!", icon="🔄")
    else:
        user_prefs.load_colors_to_session()
    st.session_state.session_loaded = True

# Load config
config = Config("config/config.json")

# NAVBAR - User info + Logout button
navbar_col1, navbar_col2, navbar_col3 = st.columns([2, 1, 10])

with navbar_col1:
    st.markdown(f'<div class="user-info-box">👤 {user["name"]} | {user["email"]}</div>', unsafe_allow_html=True)

with navbar_col2:
    if st.button("🚪 Logout", key="navbar_logout", type="secondary"):
        auth.logout()
        st.rerun()

with navbar_col3:
    st.empty()

st.markdown("---")

# Initialize session state
if 'last_config' not in st.session_state:
    st.session_state.last_config = None
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None

# DEFAULT VALUES
DEFAULT_COLORS = {
    'bg_color': "#D9F0F8",
    'border_color': "#5A9CBD",
    'page_num_color': "#3489B3",
    'page_num_text_color': "#FFFFFF",
    'title_color': "#3489B3",
    'letter_color': "#1F3B4D",
    'wb_bg_color': "#F0F8FB",
    'wb_border_color': "#5A9CBD",
    'grid_line_color': "#BDD9F0",
    'highlight_color': "#7BBDE9",
}

# Initialize colors in session state
for key, value in DEFAULT_COLORS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Main layout: Left for tabs, Right for preview
left, right = st.columns([2, 3], gap="large")

with left:
    # EVEN SHORTER TAB NAMES - all fit on one line
    tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⚡ Quick",
        "📄 Page", 
        "📝 Text", 
        "📦 Box", 
        "🔲 Grid",
        "🎨 Color",
        "🖼️ Extra"
    ])

    # TAB 0: Quick Controls
    with tab0:
        st.header("⚡ Quick Controls")

        live_mode = st.toggle("🔴 LIVE PREVIEW", value=True, help="Auto-generate on every change", key="live_mode_ctrl")

        st.markdown("---")

        st.subheader("📂 Puzzle Data")

        # Track the last uploaded file name to detect changes
        if 'last_uploaded_file_name' not in st.session_state:
            st.session_state.last_uploaded_file_name = None

        uploaded_file = st.file_uploader("Upload Puzzle JSON", type=['json'], help="Upload your custom puzzle themes", key="puzzle_upload")

        # Process file if it's new or changed
        if uploaded_file is not None:
            current_file_name = uploaded_file.name

            # Only process if file name changed (new upload)
            if current_file_name != st.session_state.last_uploaded_file_name:
                try:
                    puzzle_data = json.load(uploaded_file)

                    # Validate format
                    if not isinstance(puzzle_data, list) or not all('theme' in p and 'words' in p for p in puzzle_data):
                        st.error("❌ Invalid format! Expected: [{'theme':'...', 'words':['...']}]")
                    else:
                        # Save to file
                        temp_json_path = Path("puzzle_bank_custom.json")
                        with open(temp_json_path, 'w', encoding='utf-8') as f:
                            json.dump(puzzle_data, f, indent=2, ensure_ascii=False)

                        # Update config
                        config.data['general']['puzzle_data'] = 'puzzle_bank_custom.json'
                        config.save()

                        # Mark as changed and update file name
                        st.session_state.last_config = None
                        st.session_state.pdf_bytes = None
                        st.session_state.last_uploaded_file_name = current_file_name

                        st.success(f"✅ Loaded {len(puzzle_data)} themes from '{current_file_name}'!")

                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            # Reset when no file
            st.session_state.last_uploaded_file_name = None

        # Show current puzzle source
        current_puzzle_file = config.get('general', 'puzzle_data')
        if current_puzzle_file == 'puzzle_bank_custom.json' and Path('puzzle_bank_custom.json').exists():
            with open('puzzle_bank_custom.json', 'r', encoding='utf-8') as f:
                custom_data = json.load(f)
            st.info(f"📚 Using custom puzzles: **{len(custom_data)} themes**")
        else:
            st.info(f"📚 Using default: **{current_puzzle_file}**")

        st.markdown("---")

        st.subheader("📊 Generation")
        puzzle_count = st.slider("Puzzles", 1, 50, min(config.get('puzzle_generation', 'count'), 10), key="puzzle_count_ctrl")
        grid_size = st.slider("Grid Size", 15, 30, config.get('puzzle_generation', 'grid_size'), key="grid_size_ctrl")
        seed = st.number_input("Seed", 0, 10000, config.get('puzzle_generation', 'seed'), key="seed_ctrl")

        st.markdown("---")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🔄 Regenerate", use_container_width=True, key="force_regen_btn", type="primary"):
                st.session_state.last_config = None
                st.rerun()

        with col_b:
            if st.button("♻️ Reset All", use_container_width=True, key="reset_btn", type="secondary"):
                for key, value in DEFAULT_COLORS.items():
                    st.session_state[key] = value
                st.session_state.last_config = None
                st.toast("✅ Reset to defaults!", icon="♻️")
                st.rerun()

        if st.session_state.pdf_bytes:
            st.download_button(
                label="📥 Download PDF",
                data=st.session_state.pdf_bytes,
                file_name=config.get('general', 'output_file'),
                mime="application/pdf",
                use_container_width=True,
                key="download_btn"
            )

        st.markdown("---")

        st.subheader("📚 My Saved Books")

        book_name = st.text_input("Book Name", placeholder="My Awesome Book", key="book_name_input")

        col_save, col_colors = st.columns(2)

        with col_save:
            if st.button("💾 Save Book", use_container_width=True, key="save_book_btn"):
                if book_name:
                    try:
                        user_prefs.save_book(book_name, st.session_state.get('current_config_snapshot', {}))
                        user_prefs.save_current_colors()
                        st.success(f"✅ Saved '{book_name}'!")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.warning("Generate a PDF first before saving")
                else:
                    st.warning("Please enter a book name")

        with col_colors:
            if st.button("💾 Save Colors", use_container_width=True, key="save_colors_btn"):
                user_prefs.save_current_colors()
                st.success("✅ Colors saved!")
                time.sleep(0.5)

        saved_books = user_prefs.get_saved_books()

        if saved_books:
            st.markdown("##### Your Saved Books:")
            for book in saved_books:
                col_book, col_actions = st.columns([3, 2])

                with col_book:
                    st.write(f"📖 **{book['name']}**")

                with col_actions:
                    col_load_btn, col_del_btn = st.columns(2)

                    with col_load_btn:
                        if st.button("📂", key=f"load_{book['name']}", help="Load book", use_container_width=True):
                            loaded_config = user_prefs.load_book(book['name'])
                            if loaded_config:
                                st.session_state.update(loaded_config)
                                st.session_state.last_config = None
                                st.success(f"✅ Loaded '{book['name']}'!")
                                time.sleep(0.5)
                                st.rerun()

                    with col_del_btn:
                        if st.button("🗑️", key=f"del_{book['name']}", help="Delete book", use_container_width=True):
                            user_prefs.delete_book(book['name'])
                            st.toast(f"🗑️ Deleted '{book['name']}'", icon="🗑️")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info("No saved books yet. Create and save your first book!")

    # TAB 1: Page Design
    with tab1:
        st.subheader("📄 Page Layout")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Page Settings")
            page_width = st.slider("Width (inches)", 7.0, 11.0, config.get('page', 'width'), 0.5)
            page_height = st.slider("Height (inches)", 9.0, 14.0, config.get('page', 'height'), 0.5)
            margin = st.slider("Margin (inches)", 0.25, 1.0, config.get('page', 'margin'), 0.05)

        with col2:
            st.markdown("##### Border")
            border_width = st.slider("Border Width", 1, 10, config.get('page', 'border_width'))
            border_radius = st.slider("Border Radius", 0, 50, config.get('page', 'border_radius'))

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("##### Page Numbers")
            show_page_nums = st.checkbox("Show Page Numbers", config.get('page_number', 'show'))
            page_num_position = st.slider("Position from Bottom", 0.1, 1.0, 
                                           config.get('page_number', 'position_from_bottom'), 0.05)
            rounded_top_only = st.checkbox("Rounded Top Only", config.get('page_number', 'rounded_top_only'))

        with col4:
            st.markdown("##### Page Number Size")
            page_num_width = st.slider("Box Width", 0.8, 2.0, 
                                         config.get('page_number', 'box_width'), 0.1)
            page_num_height = st.slider("Box Height", 0.2, 0.6, 
                                          config.get('page_number', 'box_height'), 0.05)
            page_num_font_size = st.slider("Font Size", 12, 28, config.get('page_number', 'font_size'))

    # TAB 2: Typography
    with tab2:
        st.subheader("📝 Typography")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Title")
            title_size = st.slider("Font Size", 16, 50, config.get('title', 'font_size'))
            title_position = st.slider("Position from Top", 0.5, 3.0, 
                                         config.get('title', 'position_from_top'), 0.1)
            title_bold = st.checkbox("Bold Effect", config.get('title', 'bold_effect'))
            title_bold_offset = st.slider("Bold Thickness", 0.0, 2.0, 
                                            config.get('title', 'bold_offset'), 0.1)

        with col2:
            st.markdown("##### Solution Title")
            solution_title_size = st.slider("Size", 16, 50, 24)
            solution_title_prefix = st.text_input("Prefix", "SOLUTION")

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("##### Letters")
            letter_font_factor = st.slider("Size Factor", 0.3, 0.8, 
                                            config.get('puzzle_grid', 'letter_font_size_factor'), 0.05,
                                            help="Multiplier for cell size")
            letter_v_offset = st.slider("Vertical Offset", 0.0, 0.5, 
                                          config.get('puzzle_grid', 'letter_vertical_offset'), 0.05)

        with col4:
            st.markdown("##### Font File")
            st.info("📝 Current: Biski")
            uploaded_font = st.file_uploader("Upload (.ttf, .otf)", type=["ttf", "otf"], key="font_upload")
            if uploaded_font is not None:
                font_bytes = uploaded_font.read()
                font_save_path = f"fonts/{uploaded_font.name}"
                with open(font_save_path, "wb") as f:
                    f.write(font_bytes)
                font_path = font_save_path
                st.success(f"✅ {uploaded_font.name}")
            else:
                font_path = config.get('general', 'font_path')

    # TAB 3: Word Box
    with tab3:
        st.subheader("📦 Word Box")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Layout")
            wb_columns = st.slider("Columns", 2, 8, config.get('word_box', 'columns'))
            wb_rows = st.slider("Rows per Column", 5, 20, config.get('word_box', 'rows_per_column'))
            wb_position = st.slider("Position from Top", 1.0, 4.0, 
                                     config.get('word_box', 'position_from_top'), 0.1)
            wb_height = st.slider("Height", 4.0, 10.0, 
                                  config.get('word_box', 'height'), 0.1)

        with col2:
            st.markdown("##### Spacing")
            wb_margin_left = st.slider("Left Margin", 0.0, 1.0, 
                                         config.get('word_box', 'margin_left'), 0.05)
            wb_margin_right = st.slider("Right Margin", 0.0, 1.0, 
                                          config.get('word_box', 'margin_right'), 0.05)
            wb_border_width = st.slider("Border Width", 1, 5, config.get('word_box', 'border_width'))
            wb_border_radius = st.slider("Border Radius", 0, 30, config.get('word_box', 'border_radius'))

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("##### Text")
            wb_font_size = st.slider("Base Font Size", 8, 24, config.get('word_box', 'base_font_size'))
            wb_min_font = st.slider("Min Font Size", 6, 16, config.get('word_box', 'min_font_size'))

        with col4:
            st.markdown("##### Options")
            wb_sort = st.checkbox("Sort by Length", config.get('word_box', 'sort_by_length'))
            wb_vertical_align = st.selectbox("Vertical Alignment", 
                                              ["center", "top", "bottom"],
                                              index=0 if config.get('word_box', 'vertical_align') == 'center' else 1)
            min_words = st.slider("Min Words", 5, 30, 
                                  config.get('puzzle_generation', 'min_words_per_puzzle'))

    # TAB 4: Puzzle Grid
    with tab4:
        st.subheader("🔲 Puzzle Grid")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Layout")
            grid_position = st.slider("Position from Top", 0.5, 4.0, 
                                       config.get('puzzle_grid', 'position_from_top'), 0.1)
            grid_line_width = st.slider("Line Width", 1, 5, 
                                         config.get('puzzle_grid', 'grid_line_width'))

        with col2:
            st.markdown("##### Cell Settings")
            st.info(f"Grid: {grid_size}×{grid_size}")
            st.info("Cell size: Auto")

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("##### Solution")
            show_solutions = st.checkbox("Include Solutions", config.get('solution', 'show_solutions'))
            highlight_thickness = st.slider("Thickness", 0.3, 1.5, 
                                            config.get('solution', 'thickness_factor'), 0.05)

        with col4:
            st.markdown("##### Padding")
            end_padding = st.slider("End Padding", 0.0, 1.0, 
                                    config.get('solution', 'end_padding_factor'), 0.05)

    # TAB 5: Colors
    with tab5:
        st.subheader("🎨 Color Palette")

        # Preset buttons FIRST
        st.markdown("##### 🎨 Quick Presets")
        col_presets = st.columns(5)

        with col_presets[0]:
            if st.button("🔵 Blue", use_container_width=True, key="blue_preset"):
                st.session_state.bg_color = "#D9F0F8"
                st.session_state.border_color = "#5A9CBD"
                st.session_state.page_num_color = "#3489B3"
                st.session_state.page_num_text_color = "#FFFFFF"
                st.session_state.title_color = "#3489B3"
                st.session_state.letter_color = "#1F3B4D"
                st.session_state.wb_bg_color = "#F0F8FB"
                st.session_state.wb_border_color = "#5A9CBD"
                st.session_state.grid_line_color = "#BDD9F0"
                st.session_state.highlight_color = "#7BBDE9"
                st.session_state.last_config = None
                st.rerun()

        with col_presets[1]:
            if st.button("🟢 Green", use_container_width=True, key="green_preset"):
                st.session_state.bg_color = "#E8F5E9"
                st.session_state.border_color = "#66BB6A"
                st.session_state.page_num_color = "#43A047"
                st.session_state.page_num_text_color = "#FFFFFF"
                st.session_state.title_color = "#2E7D32"
                st.session_state.letter_color = "#1B5E20"
                st.session_state.wb_bg_color = "#F1F8E9"
                st.session_state.wb_border_color = "#66BB6A"
                st.session_state.grid_line_color = "#A5D6A7"
                st.session_state.highlight_color = "#81C784"
                st.session_state.last_config = None
                st.rerun()

        with col_presets[2]:
            if st.button("🟣 Purple", use_container_width=True, key="purple_preset"):
                st.session_state.bg_color = "#F3E5F5"
                st.session_state.border_color = "#AB47BC"
                st.session_state.page_num_color = "#8E24AA"
                st.session_state.page_num_text_color = "#FFFFFF"
                st.session_state.title_color = "#6A1B9A"
                st.session_state.letter_color = "#4A148C"
                st.session_state.wb_bg_color = "#F3E5F5"
                st.session_state.wb_border_color = "#AB47BC"
                st.session_state.grid_line_color = "#CE93D8"
                st.session_state.highlight_color = "#BA68C8"
                st.session_state.last_config = None
                st.rerun()

        with col_presets[3]:
            if st.button("🟠 Orange", use_container_width=True, key="orange_preset"):
                st.session_state.bg_color = "#FFF3E0"
                st.session_state.border_color = "#FF9800"
                st.session_state.page_num_color = "#F57C00"
                st.session_state.page_num_text_color = "#FFFFFF"
                st.session_state.title_color = "#E65100"
                st.session_state.letter_color = "#BF360C"
                st.session_state.wb_bg_color = "#FFF8E1"
                st.session_state.wb_border_color = "#FF9800"
                st.session_state.grid_line_color = "#FFCC80"
                st.session_state.highlight_color = "#FFB74D"
                st.session_state.last_config = None
                st.rerun()

        with col_presets[4]:
            if st.button("🩷 Pink", use_container_width=True, key="pink_preset"):
                st.session_state.bg_color = "#FCE4EC"
                st.session_state.border_color = "#EC407A"
                st.session_state.page_num_color = "#D81B60"
                st.session_state.page_num_text_color = "#FFFFFF"
                st.session_state.title_color = "#C2185B"
                st.session_state.letter_color = "#880E4F"
                st.session_state.wb_bg_color = "#F8BBD0"
                st.session_state.wb_border_color = "#EC407A"
                st.session_state.grid_line_color = "#F8BBD0"
                st.session_state.highlight_color = "#F48FB1"
                st.session_state.last_config = None
                st.rerun()

        st.markdown("---")

        # Color pickers - REMOVED ALL KEYS!
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### Page")
            st.session_state.bg_color = st.color_picker("Background", st.session_state.bg_color)
            st.session_state.border_color = st.color_picker("Border", st.session_state.border_color)
            st.session_state.page_num_color = st.color_picker("Page Number Box", st.session_state.page_num_color)
            st.session_state.page_num_text_color = st.color_picker("Page Number Text", st.session_state.page_num_text_color)

        with col2:
            st.markdown("##### Text")
            st.session_state.title_color = st.color_picker("Title", st.session_state.title_color)
            st.session_state.letter_color = st.color_picker("Letters", st.session_state.letter_color)

        with col3:
            st.markdown("##### Box & Grid")
            st.session_state.wb_bg_color = st.color_picker("Word Box BG", st.session_state.wb_bg_color)
            st.session_state.wb_border_color = st.color_picker("Word Box Border", st.session_state.wb_border_color)
            st.session_state.grid_line_color = st.color_picker("Grid Lines", st.session_state.grid_line_color)
            st.session_state.highlight_color = st.color_picker("Highlight", st.session_state.highlight_color)

    # TAB 6: Images & Extras
    with tab6:
        st.subheader("🖼️ Images & Extras")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Image Settings")
            show_images = st.checkbox("Show Images", config.get('images', 'show'))
            alternate_images = st.checkbox("Alternate", config.get('images', 'alternate'))
            image_height = st.slider("Max Height", 0.5, 3.0, 
                                      config.get('images', 'max_height'), 0.1)
            image_x_offset = st.slider("X Offset", 0.0, 1.0, 
                                        config.get('images', 'position_x_offset'), 0.05)
            image_y_offset = st.slider("Y Offset", 0.0, 1.0, 
                                        config.get('images', 'position_y_offset'), 0.05)

        with col2:
            st.markdown("##### Upload Images")

            left_uploaded = st.file_uploader("📤 Left Image (PNG)", type=["png"], key="left_img")
            if left_uploaded is not None:
                left_img_path = f"images/{left_uploaded.name}"
                with open(left_img_path, "wb") as f:
                    f.write(left_uploaded.read())
                left_image = left_img_path
                st.success(f"✅ {left_uploaded.name}")
            else:
                left_image = st.text_input("Or path", config.get('images', 'left_image'), key="left_path")

            right_uploaded = st.file_uploader("📤 Right Image (PNG)", type=["png"], key="right_img")
            if right_uploaded is not None:
                right_img_path = f"images/{right_uploaded.name}"
                with open(right_img_path, "wb") as f:
                    f.write(right_uploaded.read())
                right_image = right_img_path
                st.success(f"✅ {right_uploaded.name}")
            else:
                right_image = st.text_input("Or path", config.get('images', 'right_image'), key="right_path")

            preserve_aspect = st.checkbox("Preserve Aspect", 
                                           config.get('images', 'preserve_aspect_ratio'),
                                           key="preserve_aspect_ratio")

        st.markdown("---")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("##### Output")
            output_file = st.text_input("Filename", config.get('general', 'output_file'))

        with col4:
            st.markdown("##### Advanced")
            max_word_length = st.slider("Max Word Length", 10, 30, 
                                         config.get('puzzle_generation', 'grid_size'))

# Create config snapshot
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

current_config = {
    "puzzle_count": puzzle_count,
    "grid_size": grid_size,
    "seed": seed,
    "puzzle_data": config.get('general', 'puzzle_data'),
    "min_words": min_words,
    "page_width": page_width,
    "page_height": page_height,
    "margin": margin,
    "bg_color": st.session_state.bg_color,
    "border_color": st.session_state.border_color,
    "border_width": border_width,
    "border_radius": border_radius,
    "title_size": title_size,
    "title_color": st.session_state.title_color,
    "title_bold": title_bold,
    "title_position": title_position,
    "title_bold_offset": title_bold_offset,
    "wb_columns": wb_columns,
    "wb_rows": wb_rows,
    "wb_font_size": wb_font_size,
    "wb_min_font": wb_min_font,
    "wb_sort": wb_sort,
    "wb_bg_color": st.session_state.wb_bg_color,
    "wb_border_color": st.session_state.wb_border_color,
    "wb_position": wb_position,
    "wb_height": wb_height,
    "wb_margin_left": wb_margin_left,
    "wb_margin_right": wb_margin_right,
    "wb_border_width": wb_border_width,
    "wb_border_radius": wb_border_radius,
    "wb_vertical_align": wb_vertical_align,
    "grid_line_color": st.session_state.grid_line_color,
    "grid_line_width": grid_line_width,
    "letter_color": st.session_state.letter_color,
    "letter_font_factor": letter_font_factor,
    "letter_v_offset": letter_v_offset,
    "grid_position": grid_position,
    "show_solutions": show_solutions,
    "highlight_color": st.session_state.highlight_color,
    "highlight_thickness": highlight_thickness,
    "end_padding": end_padding,
    "show_page_nums": show_page_nums,
    "page_num_color": st.session_state.page_num_color,
    "page_num_text_color": st.session_state.page_num_text_color,
    "page_num_position": page_num_position,
    "page_num_width": page_num_width,
    "page_num_height": page_num_height,
    "page_num_font_size": page_num_font_size,
    "rounded_top_only": rounded_top_only,
    "show_images": show_images,
    "alternate_images": alternate_images,
    "image_height": image_height,
    "image_x_offset": image_x_offset,
    "image_y_offset": image_y_offset,
    "font_path": font_path,
    "output_file": output_file,
    "left_image": left_image,
    "right_image": right_image,
    "preserve_aspect": preserve_aspect,
}

# Save snapshot for book saving
st.session_state.current_config_snapshot = current_config

# Check for changes and regenerate
config_changed = st.session_state.last_config != current_config

# CRITICAL FIX: Call function directly instead of subprocess!
if live_mode and config_changed:
    st.session_state.last_config = current_config

    # AUTO-SAVE SESSION
    user_prefs.save_last_session(current_config)
    st.session_state.last_auto_save = time.time()

    # SHOW WHAT'S HAPPENING
    status_container = st.empty()
    status_container.info("🔄 Starting PDF generation...")

    try:
        # Update config
        config.data['puzzle_generation']['count'] = puzzle_count
        config.data['puzzle_generation']['grid_size'] = grid_size
        config.data['puzzle_generation']['seed'] = seed
        config.data['puzzle_generation']['min_words_per_puzzle'] = min_words

        config.data['page']['width'] = page_width
        config.data['page']['height'] = page_height
        config.data['page']['margin'] = margin
        config.data['page']['background_color'] = hex_to_rgb(st.session_state.bg_color)
        config.data['page']['border_color'] = hex_to_rgb(st.session_state.border_color)
        config.data['page']['border_width'] = border_width
        config.data['page']['border_radius'] = border_radius

        config.data['title']['font_size'] = title_size
        config.data['title']['color'] = hex_to_rgb(st.session_state.title_color)
        config.data['title']['bold_effect'] = title_bold
        config.data['title']['position_from_top'] = title_position
        config.data['title']['bold_offset'] = title_bold_offset

        config.data['word_box']['columns'] = wb_columns
        config.data['word_box']['rows_per_column'] = wb_rows
        config.data['word_box']['base_font_size'] = wb_font_size
        config.data['word_box']['min_font_size'] = wb_min_font
        config.data['word_box']['sort_by_length'] = wb_sort
        config.data['word_box']['background_color'] = hex_to_rgb(st.session_state.wb_bg_color)
        config.data['word_box']['border_color'] = hex_to_rgb(st.session_state.wb_border_color)
        config.data['word_box']['position_from_top'] = wb_position
        config.data['word_box']['height'] = wb_height
        config.data['word_box']['margin_left'] = wb_margin_left
        config.data['word_box']['margin_right'] = wb_margin_right
        config.data['word_box']['border_width'] = wb_border_width
        config.data['word_box']['border_radius'] = wb_border_radius
        config.data['word_box']['vertical_align'] = wb_vertical_align

        config.data['puzzle_grid']['grid_line_color'] = hex_to_rgb(st.session_state.grid_line_color)
        config.data['puzzle_grid']['grid_line_width'] = grid_line_width
        config.data['puzzle_grid']['letter_color'] = hex_to_rgb(st.session_state.letter_color)
        config.data['puzzle_grid']['letter_font_size_factor'] = letter_font_factor
        config.data['puzzle_grid']['letter_vertical_offset'] = letter_v_offset
        config.data['puzzle_grid']['position_from_top'] = grid_position

        config.data['solution']['highlight_color'] = hex_to_rgb(st.session_state.highlight_color)
        config.data['solution']['thickness_factor'] = highlight_thickness
        config.data['solution']['end_padding_factor'] = end_padding
        config.data['solution']['show_solutions'] = show_solutions

        config.data['page_number']['show'] = show_page_nums
        config.data['page_number']['box_color'] = hex_to_rgb(st.session_state.page_num_color)
        config.data['page_number']['text_color'] = hex_to_rgb(st.session_state.page_num_text_color)
        config.data['page_number']['position_from_bottom'] = page_num_position
        config.data['page_number']['box_width'] = page_num_width
        config.data['page_number']['box_height'] = page_num_height
        config.data['page_number']['font_size'] = page_num_font_size
        config.data['page_number']['rounded_top_only'] = rounded_top_only

        config.data['images']['show'] = show_images
        config.data['images']['alternate'] = alternate_images
        config.data['images']['max_height'] = image_height
        config.data['images']['position_x_offset'] = image_x_offset
        config.data['images']['position_y_offset'] = image_y_offset
        config.data['images']['left_image'] = left_image
        config.data['images']['right_image'] = right_image
        config.data['images']['preserve_aspect_ratio'] = preserve_aspect

        config.data['general']['font_path'] = font_path
        config.data['general']['output_file'] = output_file

        config.save()
        status_container.info("✅ Config saved. Generating PDF...")

        # CRITICAL FIX: Call function directly instead of subprocess!
        pdf_path = Path(config.get('general', 'output_file'))
        generate_pdf(
            output=pdf_path,
            count=puzzle_count,
            size=grid_size,
            seed=seed,
            biski_path=Path(font_path) if font_path else None,
            compact_solutions=False
        )

        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                st.session_state.pdf_bytes = f.read()
            status_container.success(f"✅ PDF Generated! ({len(st.session_state.pdf_bytes) / 1024:.1f} KB)")
        else:
            status_container.error(f"❌ PDF not found at: {pdf_path}")

    except Exception as e:
        status_container.error(f"❌ EXCEPTION: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

# PDF Preview Section (Cloud-compatible!)
with right:
    st.markdown("### 📄 Live PDF Preview")

    if st.session_state.pdf_bytes:
        # PDF generated successfully
        st.success(f"✅ PDF Generated! ({len(st.session_state.pdf_bytes) / 1024:.1f} KB)")

        # Show first page as image preview (works on cloud!)
        try:
            import fitz  # PyMuPDF
            pdf_document = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
            first_page = pdf_document[0]
            pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
            img_bytes = pix.tobytes("png")

            st.image(img_bytes, caption="📄 First Page Preview", use_container_width=True)
            st.info(f"📚 Showing page 1 of {len(pdf_document)}")
            pdf_document.close()
        except ImportError:
            st.warning("⚠️ PDF preview requires PyMuPDF. Download PDF to view!")
        except Exception as e:
            st.warning(f"⚠️ Preview unavailable: {str(e)}")

        # Download button
        st.download_button(
            label="📥 Download Full PDF",
            data=st.session_state.pdf_bytes,
            file_name=config.get('general', 'output_file'),
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

        st.markdown("---")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("File Size", f"{len(st.session_state.pdf_bytes) / 1024:.1f} KB")
        st.metric("Puzzles", puzzle_count)
        st.metric("Grid", f"{grid_size}×{grid_size}")
        pages = puzzle_count * 2 + (puzzle_count if show_solutions else 0)
        st.metric("Pages", pages)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # No PDF yet - show helpful message
        st.info("💡 **No PDF generated yet**")
        st.markdown("""
        **To generate your first PDF:**
        1. 🎨 Choose colors from presets or customize
        2. ⚡ Adjust settings in **Quick** tab
        3. 🔴 Make sure **LIVE PREVIEW** is ON
        4. 🔄 Click **Regenerate** to force generation

        **Or just change any setting and it will auto-generate!** ✨
        """)

        # Show a placeholder
        st.image("https://via.placeholder.com/400x600/667eea/ffffff?text=PDF+Preview+Here", 
                 caption="Waiting for PDF generation...", use_container_width=True)

# Footer
st.markdown("---")
st.caption("💡 **Pro Tip:** Use '♻️ Reset All' to restore defaults • Toggle LIVE MODE off to batch changes")
st.caption("Made with 🔥 for Word Search Puzzles")
