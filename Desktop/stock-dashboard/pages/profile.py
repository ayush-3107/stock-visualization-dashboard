import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt
import os
import re
import shutil

# Page configuration
st.set_page_config(
    page_title="Profile - Stock Dashboard",
    page_icon="👤",
    layout="wide"
)

# Authentication check
if not st.session_state.get("authentication_status"):
    st.error(" Please log in to access this page")
    if st.button("Go to Login"):
        st.switch_page("main.py")
    st.stop()

# Custom CSS for better styling and dark theme compatibility
st.markdown("""
<style>
    .profile-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Info card styling for both light and dark themes */
    .info-card {
        background-color: var(--secondary-background-color, #f8f9fa);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color, #dee2e6);
        margin: 1rem 0;
        color: var(--text-color, #262730);
    }
    
    /* Dark theme specific styles */
    [data-theme="dark"] .info-card {
        background-color: #262730 !important;
        border: 1px solid #404040 !important;
        color: #FAFAFA !important;
    }
    
    /* Force visibility in dark theme */
    .stMarkdown .info-card h4 {
        color: inherit !important;
    }
    
    .stMarkdown .info-card p {
        color: inherit !important;
    }
    
    /* Account stats styling */
    .stats-container {
        background-color: var(--secondary-background-color, #f8f9fa);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color, #dee2e6);
        margin: 0.5rem 0;
        text-align: center;
        color: var(--text-color, #262730);
    }
    
    [data-theme="dark"] .stats-container {
        background-color: #262730 !important;
        border: 1px solid #404040 !important;
        color: #FAFAFA !important;
    }
</style>
""", unsafe_allow_html=True)

# Load and save config functions
def load_config():
    with open('config.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

# Password validation function
def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

PROFILE_PIC_DIR = "profile_pics"

def get_profile_pic_path(username):
    return os.path.join(PROFILE_PIC_DIR, f"{username}.png")

def ensure_profile_pic_dir():
    if not os.path.exists(PROFILE_PIC_DIR):
        os.makedirs(PROFILE_PIC_DIR)

st.title("👤 User Profile")
st.markdown(f"Welcome, **{st.session_state['name']}**!")

# Sidebar navigation
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    if st.button("Home", use_container_width=True):
        st.switch_page("main.py")
    if st.button("Logout", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logout_flag = True
        st.session_state.manual_navigation = True
        st.switch_page("main.py")

# Initialize profile settings in session state 
if 'profile_settings' not in st.session_state:
    st.session_state.profile_settings = {
        'theme_preference': 'Light',
        'default_period': '1 Month',
        'default_chart': 'Line Chart',
        'show_ma_default': False
    }

# Main content container
st.markdown('<div class="profile-container">', unsafe_allow_html=True)

# Profile tabs
tab1, tab2, tab3 = st.tabs(["Profile Info", "Change Password", "Dashboard Settings"])

# TAB 1: Profile Information
with tab1:
    st.subheader("Profile Information")

    col1, col2 = st.columns([1, 2])

    with col1:
        ensure_profile_pic_dir()
        config = load_config()
        user_data = config['credentials']['usernames'][st.session_state['username']]
        profile_pic_path = user_data.get('profile_pic', None)
        if profile_pic_path and os.path.exists(profile_pic_path):
            st.image(profile_pic_path, width=150)
        else:
            st.image("https://via.placeholder.com/150x150.png?text=👤", width=150)
        st.caption("Profile Picture")

        uploaded_pic = st.file_uploader("Upload New Profile Picture", type=["png", "jpg", "jpeg"], key="profile_pic_upload")
        if uploaded_pic is not None:
            # Save uploaded image
            ext = uploaded_pic.name.split('.')[-1]
            save_path = os.path.join(PROFILE_PIC_DIR, f"{st.session_state['username']}.{ext}")
            with open(save_path, "wb") as f:
                f.write(uploaded_pic.getbuffer())
            # Update config with new path
            config['credentials']['usernames'][st.session_state['username']]['profile_pic'] = save_path
            save_config(config)
            st.success("Profile picture updated!")
            st.rerun()

    with col2:
        # Load current user info
        config = load_config()
        user_data = config['credentials']['usernames'][st.session_state['username']]
        
        # Use Streamlit components instead of HTML for better theme compatibility
        st.markdown("#### Account Details")
        
        # Create info display using Streamlit components
        info_col1, info_col2 = st.columns([1, 2])
        
        with info_col1:
            st.write("**Full Name:**")
            st.write("**Username:**")
            st.write("**Email:**")
        
        with info_col2:
            st.write(st.session_state['name'])
            st.write(st.session_state['username'])
            st.write(user_data['email'])

# TAB 2: Change Password
with tab2:
    st.subheader("Change Password")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("change_password_form"):
            st.markdown("### Update Your Password")
            
            current_password = st.text_input("Current Password", type="password", placeholder="Enter your current password")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_new_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            submitted = st.form_submit_button("Update Password", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                
                if not current_password:
                    errors.append("Current password is required")
                if not new_password:
                    errors.append("New password is required")
                if not confirm_new_password:
                    errors.append("Password confirmation is required")
                
                if new_password != confirm_new_password:
                    errors.append("New passwords do not match")
                
                # Validate new password strength
                if new_password:
                    is_valid, message = validate_password(new_password)
                    if not is_valid:
                        errors.append(message)
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        # Load config
                        config = load_config()
                        username = st.session_state['username']
                        user_data = config['credentials']['usernames'][username]
                        
                        # Verify current password using bcrypt
                        stored_hash = user_data['password']
                        if bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
                            # Hash new password
                            new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            
                            # Update config
                            config['credentials']['usernames'][username]['password'] = new_hashed
                            
                            # Save config
                            save_config(config)
                            
                            st.success("Password updated successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Current password is incorrect")
                            
                    except Exception as e:
                        st.error(f"❌ Error updating password: {str(e)}")
        
        # Password requirements
        st.markdown("---")
        st.markdown("### 🔒 Password Requirements")
        st.markdown("""
        - At least 6 characters long
        - Must contain at least one letter
        - Must contain at least one number
        - Use a mix of uppercase and lowercase letters
        - Avoid common passwords
        """)

# TAB 3: Dashboard Settings (Simplified)
with tab3:
    st.subheader("Dashboard Settings")
    
    # Theme preference
    theme_preference = st.selectbox(
        "Default Theme",
        ["Light", "Dark", "Auto"],
        index=["Light", "Dark", "Auto"].index(st.session_state.profile_settings['theme_preference']),
        help="Choose your preferred theme for the dashboard"
    )
    st.session_state.profile_settings['theme_preference'] = theme_preference
    
    # Default time period
    default_period = st.selectbox(
        "Default Time Period",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"],
        index=["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"].index(st.session_state.profile_settings['default_period']),
        help="Default time period for stock charts"
    )
    st.session_state.profile_settings['default_period'] = default_period
    
    # Default chart type
    default_chart = st.selectbox(
        "Default Chart Type",
        ["Line Chart", "Candlestick Chart"],
        index=["Line Chart", "Candlestick Chart"].index(st.session_state.profile_settings['default_chart']),
        help="Default chart type for stock visualization"
    )
    st.session_state.profile_settings['default_chart'] = default_chart
    
    # Moving averages default
    show_ma_default = st.checkbox(
        "Show Moving Averages by Default",
        value=st.session_state.profile_settings['show_ma_default'],
        help="Automatically show moving averages on charts"
    )
    st.session_state.profile_settings['show_ma_default'] = show_ma_default
    
    # Save and Reset buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Save Settings", type="primary", use_container_width=True):
            st.success("✅ Settings saved successfully!")
            st.balloons()
    
    with col3:
        if st.button("Reset to Defaults", help="Reset all settings to default values", use_container_width=True):
            st.session_state.profile_settings = {
                'theme_preference': 'Light',
                'default_period': '1 Month',
                'default_chart': 'Line Chart',
                'show_ma_default': False
            }
            st.success("Settings reset to defaults!")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
