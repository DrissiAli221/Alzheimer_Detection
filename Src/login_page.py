"""
Page de Login et Register pour l'application Alzheimer Detection
"""

import streamlit as st
from auth import AuthSystem

# Couleurs du thème
COLORS = {
    'bg': '#1a1a1a',
    'surface': '#262626',
    'accent': '#bf4904',
    'highlight': '#f7b657',
    'text': '#FFFFFF',
}

def render_login_page():
    """Affiche la page de connexion/inscription."""
    
    # Style CSS
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg']} 0%, #2d1810 100%);
        }}
        
        .login-container {{
            max-width: 450px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .login-header {{
            text-align: center;
            color: {COLORS['text']};
            margin-bottom: 40px;
        }}
        
        .login-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, {COLORS['highlight']}, {COLORS['accent']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .login-subtitle {{
            font-size: 1rem;
            color: #9CA3AF;
        }}
        
        .login-card {{
            background: {COLORS['surface']};
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .tab-header {{
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #404040;
        }}
        
        .tab-btn {{
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            color: #9CA3AF;
            font-weight: 600;
            border: none;
            background: none;
            transition: all 0.3s;
        }}
        
        .tab-btn.active {{
            color: {COLORS['highlight']};
            border-bottom: 3px solid {COLORS['highlight']};
        }}
        
        .form-label {{
            color: {COLORS['text']};
            font-weight: 500;
            margin-bottom: 8px;
            display: block;
        }}
        
        .stTextInput input {{
            background: {COLORS['bg']} !important;
            border: 1px solid #404040 !important;
            color: {COLORS['text']} !important;
            border-radius: 8px !important;
            padding: 12px !important;
        }}
        
        .stTextInput input:focus {{
            border-color: {COLORS['accent']} !important;
            box-shadow: 0 0 0 1px {COLORS['accent']} !important;
        }}
        
        .stButton > button {{
            width: 100%;
            background: linear-gradient(135deg, {COLORS['accent']}, #d45505) !important;
            color: white !important;
            border: none !important;
            padding: 12px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            margin-top: 20px !important;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, #d45505, {COLORS['accent']}) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(191, 73, 4, 0.4) !important;
        }}
        
        .info-box {{
            background: rgba(191, 73, 4, 0.1);
            border-left: 4px solid {COLORS['accent']};
            padding: 16px;
            border-radius: 8px;
            margin-top: 20px;
            color: {COLORS['text']};
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Container principal
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <div class="login-title">🧠 Alzheimer Detection</div>
        <div class="login-subtitle">Système d'analyse MRI pour la détection précoce</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs Login/Register
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = 'login'
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Connexion", use_container_width=True, 
                    type="primary" if st.session_state.auth_tab == 'login' else "secondary"):
            st.session_state.auth_tab = 'login'
            st.rerun()
    
    with col2:
        if st.button("📝 Inscription", use_container_width=True,
                    type="primary" if st.session_state.auth_tab == 'register' else "secondary"):
            st.session_state.auth_tab = 'register'
            st.rerun()
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    auth = AuthSystem()
    
    # TAB LOGIN
    if st.session_state.auth_tab == 'login':
        st.markdown('<h3 style="color: white; margin-bottom: 20px;">Connexion</h3>', 
                   unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur", key="login_username")
            password = st.text_input("🔒 Mot de passe", type="password", key="login_password")
            
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if username and password:
                    success, result = auth.login_user(username, password)
                    
                    if success:
                        # Stocker les données utilisateur dans la session
                        st.session_state.logged_in = True
                        st.session_state.user_data = result
                        st.success(f"✅ Bienvenue, {result['full_name']} !")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        
        st.markdown("""
        <div class="info-box">
            <strong>🔐 Première visite ?</strong><br/>
            Cliquez sur "Inscription" pour créer un compte docteur.
        </div>
        """, unsafe_allow_html=True)
    
    # TAB REGISTER
    else:
        st.markdown('<h3 style="color: white; margin-bottom: 20px;">Inscription</h3>', 
                   unsafe_allow_html=True)
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("👨‍⚕️ Nom complet", key="reg_fullname")
                username = st.text_input("👤 Nom d'utilisateur", key="reg_username")
            
            with col2:
                email = st.text_input("📧 Email", key="reg_email")
                password = st.text_input("🔒 Mot de passe", type="password", key="reg_password")
            
            role = st.selectbox("🎭 Rôle", ["doctor", "admin"], key="reg_role")
            
            st.markdown("""
            <p style="color: #9CA3AF; font-size: 0.85rem; margin-top: 10px;">
                ⚠️ Le mot de passe doit contenir au moins 6 caractères
            </p>
            """, unsafe_allow_html=True)
            
            submit = st.form_submit_button("Créer un compte", use_container_width=True)
            
            if submit:
                if all([full_name, username, email, password]):
                    success, message = auth.register_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name,
                        role=role
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.info("👉 Cliquez sur 'Connexion' pour vous connecter")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
    
    st.markdown('</div></div>', unsafe_allow_html=True)


def render_user_profile():
    """Affiche le profil utilisateur dans la sidebar."""
    if st.session_state.get('logged_in'):
        user = st.session_state.user_data
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        <div style="padding: 15px; background: {COLORS['surface']}; border-radius: 8px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: {COLORS['highlight']}; margin-bottom: 8px;">
                👤 {user['full_name']}
            </div>
            <div style="font-size: 0.85rem; color: #9CA3AF;">
                @{user['username']}<br/>
                🎭 {user['role'].capitalize()}<br/>
                📧 {user['email']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Déconnexion", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def check_authentication():
    """Vérifie si l'utilisateur est connecté."""
    if not st.session_state.get('logged_in', False):
        render_login_page()
        st.stop()