import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# Page configuration
st.set_page_config(
    page_title="Stock Dashboard - Login",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-list {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load configuration
@st.cache_data
def load_config():
    if os.path.exists('config.yaml'):
        with open('config.yaml') as file:
            return yaml.load(file, Loader=SafeLoader)
    else:
        # Create default config
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@stockdashboard.com',
                        'name': 'Administrator',
                        'password': '$2b$12$3HbBuSN0/y2pRWQtN7ivKeBQdqQ.vG5RHfZ7z0ShIwAeIT7ik7p2i'  # admin123
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'stock_dashboard_auth_key',
                'name': 'stock_dashboard_cookie'
            }
        }
        with open('config.yaml', 'w') as file:
            yaml.dump(default_config, file)
        return default_config

config = load_config()

# Initialize authenticator
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

authenticator = st.session_state.authenticator

# Check for logout flag and clear session if needed
if st.session_state.get('logout_flag'):
    # Clear all authentication-related session state
    for key in ['authentication_status', 'name', 'username', 'logout_flag']:
        if key in st.session_state:
            st.session_state[key] = None
    
    # Clear any other session variables
    dashboard_keys = ['search_query', 'selected_period', 'chart_type', 'show_ma', 'dark_mode', 'selected_stock']
    for key in dashboard_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

# Main header
st.markdown('<h1 class="main-header">📈 Stock Dashboard</h1>', unsafe_allow_html=True)

# Check authentication status
authentication_status = st.session_state.get("authentication_status")

# If user is already logged in
if authentication_status == True:
    st.markdown("""
    <div class="success-box">
        <h4>✅ Successfully Logged In!</h4>
        <p>Welcome back, <strong>{}</strong>! You are already authenticated.</p>
    </div>
    """.format(st.session_state.get('name', 'User')), unsafe_allow_html=True)
    
    # Dashboard access button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/Dashboard.py")
    
    # Logout option
    st.markdown("---")
    st.markdown("### Account Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 View Profile", use_container_width=True):
            st.switch_page("pages/profile.py")
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            # Set logout flag and clear session
            st.session_state.logout_flag = True
            st.rerun()

# If authentication failed
elif authentication_status == False:
    st.error('❌ Username/password is incorrect. Please try again.')
    
    # Show login form again
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        try:
            name, authentication_status, username = authenticator.login('Login', 'main')
        except Exception as e:
            st.error(f"Login error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Registration link
        st.markdown("---")
        st.markdown("**Don't have an account?**")
        if st.button("📝 Create New Account", use_container_width=True):
            st.switch_page("pages/register.py")

# If no authentication attempt yet (default state)
else:
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        try:
            name, authentication_status, username = authenticator.login('Login', 'main')
        except Exception as e:
            st.error(f"Login error: {e}")
        
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Registration link
        st.markdown("---")
        st.markdown("**Don't have an account?**")
        if st.button("📝 Create New Account", use_container_width=True):
            st.switch_page("pages/register.py")

# Features section (only show if not logged in)
if not st.session_state.get("authentication_status"):
    st.markdown("---")
    st.markdown("## 🚀 Dashboard Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-list">
        <h4>📊 Analysis Tools</h4>
        <ul>
            <li>🔍 Smart stock search</li>
            <li>📈 Interactive charts</li>
            <li>📊 Technical indicators</li>
            <li>⏰ Multiple time periods</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-list">
        <h4>🌍 Global Markets</h4>
        <ul>
            <li>🇺🇸 US Stock Markets</li>
            <li>🇮🇳 Indian Stock Markets</li>
            <li>💱 Multi-currency support</li>
            <li>🔄 Real-time data</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick tips
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    - **Search Stocks**: Use company names like "Apple" or tickers like "AAPL"
    - **Indian Stocks**: Search "Reliance" or use "RELIANCE.NS" 
    - **Multi-Currency**: Prices automatically display in correct currency (₹, $, etc.)
    - **Technical Analysis**: Enable moving averages for trend analysis
    """)
    
    

