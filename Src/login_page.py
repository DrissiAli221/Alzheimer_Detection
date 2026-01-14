"""
Login and Registration page for Alzheimer Detection app
With persistent session using cookies
"""

import streamlit as st
from auth import AuthSystem
import extra_streamlit_components as stx
import json
from datetime import datetime, timedelta

# Design tokens (shared with main app)
COLORS = {
    'bg': '#0f0f0f',
    'surface': '#1a1a1a',
    'elevated': '#252525',
    'border': '#333333',
    'accent': '#ff6b35',
    'accent_light': '#ffa577',
    'text': '#ffffff',
    'text_muted': '#8a8a8a',
}

# SVG Icons
ICONS = {
    'brain': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>''',
    'user': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
    'lock': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>''',
    'mail': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>''',
}

def icon(name, size=20, color=None):
    if color is None:
        color = COLORS['accent']
    svg = ICONS.get(name, ICONS['user'])
    svg = svg.replace('currentColor', color)
    svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    return svg

# Cookie manager
@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()


def save_session_cookie(user_data):
    """Save user session to cookie."""
    session_data = json.dumps({
        'user_data': user_data,
        'logged_in': True,
        'expires': (datetime.now() + timedelta(days=7)).isoformat()
    })
    cookie_manager.set('alzheimer_session', session_data, expires_at=datetime.now() + timedelta(days=7))


def clear_session_cookie():
    """Clear the session cookie."""
    cookie_manager.delete('alzheimer_session')


def load_session_from_cookie():
    """Load session from cookie if exists and valid."""
    try:
        session_cookie = cookie_manager.get('alzheimer_session')
        if session_cookie:
            session_data = json.loads(session_cookie)
            expires = datetime.fromisoformat(session_data.get('expires', '2000-01-01'))
            if expires > datetime.now():
                return session_data
    except Exception:
        pass
    return None


def render_login_page():
    """Renders the login/registration page."""
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: {COLORS['bg']};
        }}
        
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        
        [data-testid="stSidebar"] {{
            display: none;
        }}
        
        /* Hide cookie manager */
        iframe[title="extra_streamlit_components.CookieManager.cookie_manager"],
        iframe[title*="CookieManager"],
        .element-container:has(iframe[title*="cookie"]),
        .stMarkdown:empty,
        div[data-testid="stMarkdownContainer"]:empty {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        .block-container {{
            padding-top: 40px;
            padding-bottom: 20px;
            max-width: 420px;
            margin: 0 auto;
        }}
        
        /* Prevent scrolling */
        .stApp {{
            overflow: hidden;
            height: 100vh;
        }}
        
        section[data-testid="stSidebar"] {{
            display: none;
        }}
        
        /* Auth header */
        .auth-header {{
            text-align: center;
            margin-bottom: 28px;
        }}
        
        .auth-logo {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_light']} 100%);
            border-radius: 16px;
            margin-bottom: 16px;
        }}
        
        .auth-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLORS['text']};
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}
        
        .auth-subtitle {{
            color: {COLORS['text_muted']};
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background: {COLORS['surface']};
            border-radius: 12px;
            padding: 6px;
            margin-bottom: 32px;
            border: 1px solid {COLORS['border']};
            width: 100%;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            color: {COLORS['text_muted']};
            border-radius: 8px;
            padding: 14px 24px;
            font-weight: 600;
            font-size: 0.95rem;
            flex: 1;
            justify-content: center;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: {COLORS['text']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {COLORS['accent']} !important;
            color: white !important;
        }}
        
        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {{
            display: none;
        }}
        
        /* Form card */
        .form-card {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 32px;
        }}
        
        .form-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {COLORS['text']};
            margin-bottom: 24px;
        }}
        
        /* Input fields */
        .stTextInput > label {{
            color: {COLORS['text']} !important;
            font-weight: 500;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }}
        
        .stTextInput > div > div > input {{
            background: {COLORS['bg']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 10px !important;
            color: {COLORS['text']} !important;
            padding: 14px 16px !important;
            font-size: 1rem !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLORS['accent']} !important;
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.15) !important;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: {COLORS['text_muted']} !important;
            opacity: 0.6 !important;
        }}
        
        .stSelectbox > label {{
            color: {COLORS['text']} !important;
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .stSelectbox > div > div {{
            background: {COLORS['bg']} !important;
            border-color: {COLORS['border']} !important;
            border-radius: 10px !important;
        }}
        
        .stCheckbox > label {{
            color: {COLORS['text']} !important;
        }}
        
        /* Button */
        .stButton > button {{
            width: 100%;
            background: linear-gradient(135deg, {COLORS['accent']}, #e55a2b) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 16px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            margin-top: 8px !important;
            transition: all 0.2s ease !important;
            letter-spacing: 0.3px;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(255, 107, 53, 0.35) !important;
        }}
        
        /* Info box */
        .info-box {{
            background: {COLORS['elevated']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 16px 20px;
            margin-top: 24px;
            color: {COLORS['text_muted']};
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        .info-box strong {{
            color: {COLORS['text']};
        }}
        
        /* Form spacing */
        .form-row {{
            margin-bottom: 20px;
        }}
        
        .form-row-half {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }}
        
        /* Hide streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Divider */
        hr {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 24px 0;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="auth-header">
        <div class="auth-logo">
            {icon('brain', 36, '#ffffff')}
        </div>
        <div class="auth-title">Alzheimer's Detection</div>
        <div class="auth-subtitle">AI-powered MRI analysis for early detection</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth tabs
    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])
    
    auth = AuthSystem()
    
    # LOGIN TAB
    with tab_login:
        st.markdown('<h3 style="margin-bottom: 24px; color: white;">Welcome back</h3>', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        remember_me = st.checkbox("Remember me for 7 days", value=True, key="remember_me")
        
        if st.button("Sign In", key="login_submit", use_container_width=True):
            if username and password:
                with st.spinner("Signing in..."):
                    success, result = auth.login_user(username, password)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_data = result
                        
                        if remember_me:
                            save_session_cookie(result)
                        
                        st.success(f"Welcome back, {result['full_name']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(result)
            else:
                st.warning("Please fill in all fields")
        
        st.markdown("""
        <div class="info-box">
            <strong>New to the platform?</strong><br>
            Switch to "Create Account" to register.
        </div>
        """, unsafe_allow_html=True)
    
    # REGISTER TAB
    with tab_register:
        st.markdown('<h3 style="margin-bottom: 24px; color: white;">Create your account</h3>', unsafe_allow_html=True)
        
        full_name = st.text_input("Full Name", key="reg_fullname", placeholder="Dr. John Smith")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", key="reg_username", placeholder="johnsmith")
        with col2:
            email = st.text_input("Email", key="reg_email", placeholder="john@hospital.com")
        
        password = st.text_input("Password", type="password", key="reg_password", placeholder="Minimum 6 characters")
        
        role = st.selectbox("Account Type", ["Doctor", "Administrator"], key="reg_role")
        role_value = "doctor" if role == "Doctor" else "admin"
        
        if st.button("Create Account", key="register_submit", use_container_width=True):
            if all([full_name, username, email, password]):
                with st.spinner("Creating your account..."):
                    success, message = auth.register_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name,
                        role=role_value
                    )
                    
                    if success:
                        st.success(message)
                        st.info("Switch to 'Sign In' to access your account")
                        st.balloons()
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")
        
        st.markdown("""
        <div class="info-box">
            Password must be at least 6 characters long.
        </div>
        """, unsafe_allow_html=True)


def render_user_menu():
    """Renders user info in top bar - kept for compatibility."""
    pass


def logout():
    """Logout user and clear session."""
    clear_session_cookie()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def check_authentication():
    """Check if user is authenticated - supports persistent sessions."""
    if st.session_state.get('logged_in', False):
        return True
    
    saved_session = load_session_from_cookie()
    if saved_session and saved_session.get('logged_in'):
        st.session_state.logged_in = True
        st.session_state.user_data = saved_session.get('user_data', {})
        return True
    
    render_login_page()
    st.stop()