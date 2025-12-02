"""
Authentication system for Word Search Generator
Handles user signup, login, and session management
"""

import streamlit as st
import json
from pathlib import Path
import hashlib
import re


class Auth:
    def __init__(self):
        self.users_file = Path("user_data/users.json")
        self.users_file.parent.mkdir(exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._save_users({})
    
    def _load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def signup(self, email, password, name):
        """Register a new user"""
        users = self._load_users()
        
        # Validate email
        if not self._validate_email(email):
            return False, "Invalid email format"
        
        # Check if user exists
        if email in users:
            return False, "Email already registered"
        
        # Validate password
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Create new user
        users[email] = {
            "name": name,
            "password": self._hash_password(password),
            "created_at": str(st.session_state.get('timestamp', 'unknown'))
        }
        
        self._save_users(users)
        return True, "Account created successfully!"
    
    def login(self, email, password):
        """Login existing user"""
        users = self._load_users()
        
        if email not in users:
            return False, "Email not found"
        
        if users[email]['password'] != self._hash_password(password):
            return False, "Incorrect password"
        
        return True, users[email]['name']
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return 'user_email' in st.session_state and st.session_state.user_email is not None
    
    def get_current_user(self):
        """Get current logged in user"""
        if self.is_logged_in():
            return {
                'email': st.session_state.user_email,
                'name': st.session_state.user_name
            }
        return None
    
    def logout(self):
        """Logout current user"""
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.logged_in = False


def show_auth_page():
    """Display login/signup page"""
    auth = Auth()
    
    st.markdown('<p class="main-header">🔍 Word Search PDF Generator PRO</p>', unsafe_allow_html=True)
    st.markdown("### Welcome! Please login or create an account")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🔓 Login", use_container_width=True, type="primary"):
            if email and password:
                success, message = auth.login(email, password)
                if success:
                    st.session_state.user_email = email
                    st.session_state.user_name = message
                    st.session_state.logged_in = True
                    st.success(f"Welcome back, {message}! 🎉")
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        
        if st.button("✨ Create Account", use_container_width=True, type="primary"):
            if name and email and password and password_confirm:
                if password != password_confirm:
                    st.error("Passwords don't match!")
                else:
                    success, message = auth.signup(email, password, name)
                    if success:
                        st.success(message + " Please login!")
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")
