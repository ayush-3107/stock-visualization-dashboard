import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import re
import os

# Page configuration
st.set_page_config(
    page_title="Register - Stock Dashboard",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .register-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .register-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_username(username, existing_users):
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if username in existing_users:
        return False, "Username already exists"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

# Load and save config
def load_config():
    with open('config.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

# Main header
st.markdown('<h1 class="register-header">📝 Create Account</h1>', unsafe_allow_html=True)

# Back to login button
if st.button("← Back to Login", type="secondary"):
    st.switch_page("main.py")

# Registration form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    
    # Initialize registration state
    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False
    if 'new_user_data' not in st.session_state:
        st.session_state.new_user_data = {}
    
    # Show registration form if not successful
    if not st.session_state.registration_success:
        with st.form("registration_form"):
            st.markdown("### User Information")
            
            full_name = st.text_input("Full Name *", placeholder="Enter your full name")
            username = st.text_input("Username *", placeholder="Choose a username")
            email = st.text_input("Email *", placeholder="Enter your email address")
            password = st.text_input("Password *", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
            
            agree_terms = st.checkbox("I agree to the Terms and Conditions")
            
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if submitted:
                config = load_config()
                existing_users = config.get('credentials', {}).get('usernames', {})
                
                # Validation
                errors = []
                
                if not full_name.strip():
                    errors.append("Full name is required")
                
                if not username.strip():
                    errors.append("Username is required")
                else:
                    valid_username, username_msg = validate_username(username.lower(), existing_users)
                    if not valid_username:
                        errors.append(username_msg)
                
                if not email.strip():
                    errors.append("Email is required")
                elif not validate_email(email):
                    errors.append("Please enter a valid email address")
                
                if not password:
                    errors.append("Password is required")
                else:
                    valid_password, password_msg = validate_password(password)
                    if not valid_password:
                        errors.append(password_msg)
                
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if not agree_terms:
                    errors.append("You must agree to the Terms and Conditions")
                
                # Check if email already exists
                for user_data in existing_users.values():
                    if user_data.get('email', '').lower() == email.lower():
                        errors.append("Email address already registered")
                        break
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        # Hash password
                        hasher = stauth.Hasher([password])
                        hashed_passwords = hasher.generate()
                        hashed_password = hashed_passwords[0]
                        
                        # Add new user to config
                        config['credentials']['usernames'][username.lower()] = {
                            'email': email.lower(),
                            'name': full_name.strip(),
                            'password': hashed_password
                        }
                        
                        # Save updated config
                        save_config(config)
                        
                        # Store user data and mark success
                        st.session_state.new_user_data = {
                            'name': full_name.strip(),
                            'username': username.lower(),
                            'email': email.lower()
                        }
                        st.session_state.registration_success = True
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error creating account: {str(e)}")
    
    # Show success message and navigation buttons (outside form)
    else:
        st.success("Account created successfully!")
        
        user_data = st.session_state.new_user_data
        st.markdown(f"""
        <div class="success-message">
            <h4>Welcome to Stock Dashboard!</h4>
            <p><strong>Name:</strong> {user_data.get('name', '')}</p>
            <p><strong>Username:</strong> {user_data.get('username', '')}</p>
            <p><strong>Email:</strong> {user_data.get('email', '')}</p>
            <p>Your account has been created successfully. You can now log in with your credentials.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons (outside form)
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Login Now", type="primary", use_container_width=True):
                # Auto-login the user
                st.session_state['authentication_status'] = True
                st.session_state['name'] = user_data['name']
                st.session_state['username'] = user_data['username']
                st.session_state['manual_navigation'] = True  # Prevent auto-redirect
                
                # Clear registration state
                st.session_state.registration_success = False
                st.session_state.new_user_data = {}
                
                st.switch_page("pages/Dashboard.py")
        
        with col_b:
            if st.button("🏠 Go to Login Page", use_container_width=True):
                # Clear registration state
                st.session_state.registration_success = False
                st.session_state.new_user_data = {}
                st.switch_page("main.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Password requirements (only show if not successful)
if not st.session_state.get('registration_success', False):
    st.markdown("---")
    st.markdown("### 🔒 Password Requirements")
    st.markdown("""
    - At least 6 characters long
    - Must contain at least one letter
    - Must contain at least one number
    - Use a mix of uppercase and lowercase letters for better security
    """)
