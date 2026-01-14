import streamlit as st
from PIL import Image
import os
import torch
import time
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms
from efficientnet_pytorch import EfficientNet
from dotenv import load_dotenv
from login_page import check_authentication, logout

# Load environment variables
load_dotenv()

# Import chatbot
try:
    from chatbot import AlzheimerChatbot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    CHATBOT_AVAILABLE = False
    print(f"Chatbot not available: {e}")

# ============ DESIGN SYSTEM ============
COLORS = {
    'bg': '#0f0f0f',
    'surface': '#1a1a1a',
    'elevated': '#252525',
    'border': '#333333',
    'accent': '#ff6b35',
    'accent_light': '#ffa577',
    'text': '#ffffff',
    'text_muted': '#8a8a8a',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
}

# SVG Icons (monochrome)
ICONS = {
    'brain': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>''',
    'upload': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>''',
    'search': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>''',
    'microscope': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2"/><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/></svg>''',
    'chat': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>''',
    'info': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>''',
    'home': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>''',
    'zap': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>''',
    'chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>''',
    'help': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
    'folder': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>''',
    'image': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>''',
    'clipboard': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>''',
    'refresh': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>''',
    'settings': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>''',
    'target': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>''',
    'warning': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
    'robot': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>''',
}

def icon(name, size=20, color=None):
    """Return an SVG icon with custom size and color."""
    if color is None:
        color = COLORS['accent']
    svg = ICONS.get(name, ICONS['info'])
    svg = svg.replace('currentColor', color)
    svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    return svg

# Set page configuration
st.set_page_config(
    page_title="Alzheimer's Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check authentication first
check_authentication()

# ============ GLOBAL STYLES ============
st.markdown(f"""
<style>
    /* Reset and base */
    .stApp {{
        background: {COLORS['bg']};
    }}
    
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    
    [data-testid="stSidebar"] {{
        display: none;
    }}
    
    .block-container {{
        padding: 1rem 2rem 2rem 2rem;
        max-width: 1200px;
    }}
    
    /* Top bar */
    .top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    .logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLORS['text']};
    }}
    
    .logo-icon {{
        font-size: 1.5rem;
    }}
    
    .user-menu {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: {COLORS['surface']};
        padding: 8px 16px;
        border-radius: 50px;
        border: 1px solid {COLORS['border']};
    }}
    
    .user-name {{
        color: {COLORS['text']};
        font-weight: 500;
        font-size: 0.9rem;
    }}
    
    .user-role {{
        color: {COLORS['accent']};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 4px;
        border: 1px solid {COLORS['border']};
        width: 100%;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {COLORS['text_muted']};
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        flex: 1;
        justify-content: center;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLORS['text']};
        background: {COLORS['elevated']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COLORS['accent']} !important;
        color: white !important;
    }}
    
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none;
    }}
    
    .stTabs [data-baseweb="tab-border"] {{
        display: none;
    }}
    
    /* Cards */
    .card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }}
    
    .card-header {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {COLORS['text']};
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .card-content {{
        color: {COLORS['text_muted']};
        line-height: 1.6;
    }}
    
    /* Hero section */
    .hero {{
        text-align: center;
        padding: 60px 20px;
    }}
    
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {COLORS['text']};
        margin-bottom: 16px;
        line-height: 1.2;
    }}
    
    .hero-subtitle {{
        font-size: 1.1rem;
        color: {COLORS['text_muted']};
        max-width: 500px;
        margin: 0 auto 32px auto;
    }}
    
    .hero-icon {{
        font-size: 4rem;
        margin-bottom: 20px;
    }}
    
    /* Feature grid */
    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 40px;
    }}
    
    .feature-card {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        transition: all 0.2s ease;
    }}
    
    .feature-card:hover {{
        border-color: {COLORS['accent']};
        transform: translateY(-4px);
    }}
    
    .feature-icon {{
        font-size: 2rem;
        margin-bottom: 16px;
    }}
    
    .feature-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS['text']};
        margin-bottom: 8px;
    }}
    
    .feature-desc {{
        font-size: 0.875rem;
        color: {COLORS['text_muted']};
    }}
    
    /* Result boxes */
    .result-box {{
        padding: 20px 24px;
        border-radius: 12px;
        margin: 20px 0;
        border-left: 4px solid;
    }}
    
    .result-normal {{
        background: rgba(16, 185, 129, 0.1);
        border-color: {COLORS['success']};
        color: {COLORS['success']};
    }}
    
    .result-mild {{
        background: rgba(245, 158, 11, 0.1);
        border-color: {COLORS['warning']};
        color: {COLORS['warning']};
    }}
    
    .result-moderate {{
        background: rgba(255, 107, 53, 0.1);
        border-color: {COLORS['accent']};
        color: {COLORS['accent']};
    }}
    
    .result-severe {{
        background: rgba(239, 68, 68, 0.1);
        border-color: {COLORS['error']};
        color: {COLORS['error']};
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['accent']};
        border-color: {COLORS['accent']};
        color: white;
    }}
    
    /* File uploader */
    [data-testid="stFileUploader"] {{
        background: {COLORS['surface']};
        border: 2px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        border-color: {COLORS['accent']};
    }}
    
    /* Chat styling */
    .stChatMessage {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {COLORS['accent']}, {COLORS['accent_light']});
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Section headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    /* Selectbox and inputs */
    .stSelectbox > div > div {{
        background: {COLORS['surface']};
        border-color: {COLORS['border']};
    }}
    
    .stTextInput > div > div > input {{
        background: {COLORS['surface']};
        border-color: {COLORS['border']};
        color: {COLORS['text']};
    }}
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chatbot' not in st.session_state and CHATBOT_AVAILABLE:
    try:
        st.session_state.chatbot = AlzheimerChatbot()
    except Exception:
        st.session_state.chatbot = None
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None
if 'last_probabilities' not in st.session_state:
    st.session_state.last_probabilities = None
if 'stored_image' not in st.session_state:
    st.session_state.stored_image = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# ============ TOP BAR ============
user = st.session_state.get('user_data', {})
st.markdown(f"""
<div class="top-bar">
    <div class="logo">
        <span class="logo-icon">{icon('brain', 28, COLORS['accent'])}</span>
        <span>Alzheimer's Detection</span>
    </div>
    <div class="user-menu">
        <div>
            <div class="user-name">{user.get('full_name', 'User')}</div>
            <div class="user-role">{user.get('role', 'doctor')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Logout button
col1, col2, col3 = st.columns([10, 1, 1])
with col3:
    if st.button("Logout", key="logout_btn"):
        logout()

# ============ NAVIGATION TABS ============
tab_home, tab_analyze, tab_chat, tab_about = st.tabs([
    "Home",
    "Analyze",
    "Chat",
    "About"
])

# ============ MODEL FUNCTIONS ============
MODEL_PATH = os.path.join('Src', 'alzheimer_efficientnet_model.pth')

def preprocess(image):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0)

def predict(image, model):
    with torch.no_grad():
        output = model(image)
        probabilities = torch.nn.functional.softmax(output, dim=1)[0]
        _, predicted = torch.max(output, 1)
    return predicted.item(), probabilities.numpy()

def create_prediction_chart(probabilities, labels):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [COLORS['success'], COLORS['warning'], COLORS['accent'], COLORS['error']]
    bars = ax.barh(labels, probabilities, color=colors, height=0.6)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.1%}',
                va='center', fontsize=14, fontweight='bold', color=COLORS['text'])
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=12)
    
    ax.set_xlim(0, 1.15)
    ax.set_xlabel('Probability', fontsize=10, color=COLORS['text_muted'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.tick_params(colors=COLORS['text_muted'])
    fig.patch.set_facecolor(COLORS['surface'])
    ax.set_facecolor(COLORS['surface'])
    plt.tight_layout()
    return fig

# ============ HOME TAB ============
with tab_home:
    st.markdown(f"""
    <div class="hero">
        <div class="hero-icon">{icon('brain', 64, COLORS['accent'])}</div>
        <h1 class="hero-title">AI-Powered MRI Analysis</h1>
        <p class="hero-subtitle">
            Upload brain MRI scans to receive instant AI-powered assessment 
            of cognitive impairment stages using deep learning.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon('microscope', 32, COLORS['accent'])}</div>
            <div class="feature-title">Deep Analysis</div>
            <div class="feature-desc">EfficientNet-B0 architecture trained on thousands of MRI scans</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon('zap', 32, COLORS['accent'])}</div>
            <div class="feature-title">Instant Results</div>
            <div class="feature-desc">Get predictions in seconds with detailed probability scores</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon('chat', 32, COLORS['accent'])}</div>
            <div class="feature-title">AI Assistant</div>
            <div class="feature-desc">Ask questions and get explanations about your results</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How it works
    st.markdown(f"""
    <div class="card">
        <div class="card-header">{icon('clipboard', 20, COLORS['accent'])} How It Works</div>
        <div class="card-content">
            <ol style="margin: 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;"><strong>Upload</strong> — Select a brain MRI scan image</li>
                <li style="margin-bottom: 8px;"><strong>Analyze</strong> — Our AI processes the image using deep learning</li>
                <li style="margin-bottom: 8px;"><strong>Results</strong> — View classification with probability scores</li>
                <li style="margin-bottom: 0;"><strong>Understand</strong> — Chat with AI to understand your results</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============ ANALYZE TAB ============
with tab_analyze:
    st.markdown(f'<div class="section-header">{icon("microscope", 24, COLORS["accent"])} MRI Analysis</div>', unsafe_allow_html=True)
    
    # Load model
    model_loaded = False
    try:
        model = EfficientNet.from_pretrained('efficientnet-b0', num_classes=4)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        model.eval()
        model_loaded = True
    except FileNotFoundError:
        st.error(f"Model not found at {MODEL_PATH}")
    
    # Upload section - two columns only for upload
    upload_col1, upload_col2 = st.columns([1, 1], gap="large")
    
    with upload_col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('upload', 20, COLORS['accent'])} Upload MRI Scan</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an MRI image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
    
    with upload_col2:
        # Sample images section
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('folder', 20, COLORS['accent'])} Or Try a Sample</div>
        </div>
        """, unsafe_allow_html=True)
        
        sample_dir = "train"
        if os.path.exists(sample_dir):
            categories = ["No Impairment", "Very Mild Impairment", "Mild_Impairment", "Moderate Impairment"]
            cat = st.selectbox("Category", categories, label_visibility="collapsed")
            cat_path = os.path.join(sample_dir, cat)
            
            if os.path.exists(cat_path):
                samples = [f for f in os.listdir(cat_path) if f.endswith(('.jpg', '.jpeg', '.png'))][:10]
                if samples:
                    sample = st.selectbox("Sample Image", samples, label_visibility="collapsed")
                    if st.button("Use This Sample", use_container_width=True):
                        st.session_state.stored_image = Image.open(os.path.join(cat_path, sample)).convert('RGB')
                        st.session_state.analysis_complete = False
                        st.rerun()
    
    # Handle upload
    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get('last_file_id') != file_id:
            st.session_state.stored_image = Image.open(uploaded_file).convert('RGB')
            st.session_state.last_file_id = file_id
            st.session_state.analysis_complete = False
    
    # ============ RESULTS SECTION - FULL WIDTH CENTERED ============
    if st.session_state.stored_image is not None and model_loaded:
        st.markdown("---")
        
        image = st.session_state.stored_image
        labels = ["Mild Alzheimer's", "Moderate Alzheimer's", "Non-demented", "Very Mild Alzheimer's"]
        
        # Run analysis if needed
        if not st.session_state.analysis_complete:
            progress = st.progress(0)
            status = st.empty()
            
            status.text("Preprocessing image...")
            progress.progress(30)
            preprocessed = preprocess(image)
            time.sleep(0.15)
            
            status.text("Running analysis...")
            progress.progress(60)
            label_idx, probs = predict(preprocessed, model)
            time.sleep(0.15)
            
            progress.progress(100)
            status.empty()
            
            st.session_state.last_prediction = labels[label_idx]
            st.session_state.last_probabilities = {labels[i]: float(probs[i]) for i in range(len(labels))}
            st.session_state.last_label_idx = label_idx
            st.session_state.analysis_complete = True
            
            if CHATBOT_AVAILABLE and st.session_state.get('chatbot'):
                st.session_state.chatbot.set_prediction_context(
                    st.session_state.last_prediction,
                    st.session_state.last_probabilities
                )
        
        # Display results - centered layout
        if st.session_state.analysis_complete:
            result_label = st.session_state.last_prediction
            label_idx = st.session_state.get('last_label_idx', 0)
            
            # Image preview and result side by side
            img_col, result_col = st.columns([1, 2], gap="large")
            
            with img_col:
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">{icon('image', 20, COLORS['accent'])} Scanned Image</div>
                </div>
                """, unsafe_allow_html=True)
                st.image(image, use_container_width=True)
            
            with result_col:
                result_classes = {2: "result-normal", 3: "result-mild", 0: "result-moderate", 1: "result-severe"}
                result_class = result_classes.get(label_idx, "result-mild")
                
                st.markdown(f"""
                <div class="result-box {result_class}" style="padding: 30px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 12px 0; font-size: 1.75rem;">{icon('brain', 28)} {result_label}</h2>
                    <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">The AI analysis indicates this scan shows signs of <strong>{result_label}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                cached_probs = st.session_state.last_probabilities
                prob_values = [cached_probs[l] for l in labels]
                
                st.markdown(f'''
                <div class="card">
                    <div class="card-header">{icon('chart', 20, COLORS['accent'])} Probability Distribution</div>
                </div>
                ''', unsafe_allow_html=True)
                
                fig = create_prediction_chart(prob_values, labels)
                st.pyplot(fig, use_container_width=True)
            
            # Inline chat section - full width below
            if CHATBOT_AVAILABLE and st.session_state.get('chatbot'):
                st.markdown(f'''
                <div class="card" style="margin-top: 24px; border-color: {COLORS['accent']};">
                    <div class="card-header">{icon('chat', 20, COLORS['accent'])} Have Questions About Your Result?</div>
                    <div class="card-content">Ask our AI assistant to explain your results or get guidance on next steps.</div>
                </div>
                ''', unsafe_allow_html=True)
                
                chatbot = st.session_state.chatbot
                
                # Quick action buttons - 3 columns
                qcol1, qcol2, qcol3 = st.columns(3)
                with qcol1:
                    if st.button("Explain This Result", key="inline_explain", use_container_width=True):
                        with st.spinner("Generating explanation..."):
                            response = chatbot.explain_result()
                            st.session_state.inline_chat_response = response
                            st.session_state.inline_chat_question = "Explain my result"
                        st.rerun()
                with qcol2:
                    if st.button("What Should I Do Next?", key="inline_next", use_container_width=True):
                        with st.spinner("Getting recommendations..."):
                            response = chatbot.get_next_steps()
                            st.session_state.inline_chat_response = response
                            st.session_state.inline_chat_question = "What should I do next?"
                        st.rerun()
                with qcol3:
                    if st.button("Analyze New Scan", key="new_scan", use_container_width=True):
                        st.session_state.stored_image = None
                        st.session_state.analysis_complete = False
                        st.session_state.inline_chat_response = None
                        st.rerun()
                
                # Show response if exists
                if st.session_state.get('inline_chat_response'):
                    st.markdown(f"""
                    <div class="card" style="margin-top: 16px;">
                        <div class="card-header">{icon('robot', 20, COLORS['accent'])} AI Response</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**You asked:** {st.session_state.get('inline_chat_question', '')}")
                    st.markdown(st.session_state.inline_chat_response)
                
                # Custom question
                st.markdown("<br>", unsafe_allow_html=True)
                ask_col1, ask_col2 = st.columns([4, 1])
                with ask_col1:
                    inline_question = st.text_input(
                        "Ask a question:",
                        placeholder="e.g., Is this result concerning? What does this mean for my patient?",
                        key="inline_question_input",
                        label_visibility="collapsed"
                    )
                with ask_col2:
                    if st.button("Ask AI", key="inline_ask_btn", use_container_width=True):
                        if inline_question:
                            with st.spinner("Thinking..."):
                                response = chatbot.get_response(inline_question)
                                st.session_state.inline_chat_response = response
                                st.session_state.inline_chat_question = inline_question
                                st.rerun()

# ============ CHAT TAB ============
with tab_chat:
    st.markdown(f'<div class="section-header">{icon("chat", 24, COLORS["accent"])} AI Assistant</div>', unsafe_allow_html=True)
    
    if not CHATBOT_AVAILABLE:
        st.warning("Chatbot is not available. Please check your configuration.")
    elif not st.session_state.get('chatbot'):
        st.error("Chatbot failed to initialize. Check your GEMINI_API_KEY in .env")
    else:
        chatbot = st.session_state.chatbot
        
        # Context info
        if st.session_state.last_prediction:
            st.info(f"Context: Your last analysis result was **{st.session_state.last_prediction}**")
        
        # Quick questions
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('help', 20, COLORS['accent'])} Quick Questions</div>
        </div>
        """, unsafe_allow_html=True)
        
        faq_questions = [
            "What is Alzheimer's disease?",
            "What are early warning signs?",
            "How is it diagnosed?",
            "What treatments exist?",
        ]
        
        cols = st.columns(2)
        for i, q in enumerate(faq_questions):
            with cols[i % 2]:
                if st.button(q, key=f"faq_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    with st.spinner("Thinking..."):
                        response = chatbot.get_response(q)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
        
        st.markdown("---")
        
        # Chat messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if user_input := st.chat_input("Ask about Alzheimer's disease..."):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                response = chatbot.get_response(user_input)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        # Clear button
        if st.session_state.chat_history:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                chatbot.clear_history()
                st.rerun()

# ============ ABOUT TAB ============
with tab_about:
    st.markdown(f'<div class="section-header">{icon("info", 24, COLORS["accent"])} About This Tool</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('brain', 20, COLORS['accent'])} Overview</div>
            <div class="card-content">
                This tool uses deep learning to analyze brain MRI scans for signs of 
                Alzheimer's disease. The EfficientNet architecture identifies patterns 
                indicative of different cognitive impairment stages.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('target', 20, COLORS['accent'])} Classification Categories</div>
            <div class="card-content">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Non-demented</strong> — No signs of cognitive impairment</li>
                    <li><strong>Very Mild</strong> — Early stage with subtle changes</li>
                    <li><strong>Mild</strong> — Noticeable cognitive decline</li>
                    <li><strong>Moderate</strong> — Significant impairment</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon('settings', 20, COLORS['accent'])} Technical Details</div>
            <div class="card-content">
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Model:</strong> EfficientNet-B0</li>
                    <li><strong>Framework:</strong> PyTorch</li>
                    <li><strong>AI Chat:</strong> Google Gemini</li>
                    <li><strong>Input:</strong> 224×224 RGB images</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card" style="background: rgba(245, 158, 11, 0.1); border-color: {COLORS['warning']};">
            <div class="card-header" style="color: {COLORS['warning']};">{icon('warning', 20, COLORS['warning'])} Disclaimer</div>
            <div class="card-content" style="color: {COLORS['warning']};">
                This tool is for educational and research purposes only. It is not a 
                substitute for professional medical advice. Always consult qualified 
                healthcare providers for medical decisions.
            </div>
        </div>
        """, unsafe_allow_html=True)
