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

# Load environment variables
load_dotenv()

# Import chatbot
try:
    from chatbot import AlzheimerChatbot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    CHATBOT_AVAILABLE = False
    print(f"Chatbot not available: {e}")

# Color palette - Dark mode
COLORS = {
    'bg': '#1a1a1a',
    'surface': '#262626',
    'border': '#404040',
    'accent': '#bf4904',
    'highlight': '#f7b657',
    'text': '#FFFFFF',
    'text_muted': '#9CA3AF',
}

# SVG Icons (monochrome)
ICONS = {
    'brain': '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>''',
    'upload': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>''',
    'search': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>''',
    'chat': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>''',
    'info': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>''',
    'clipboard': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>''',
    'compass': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>''',
    'zap': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>''',
    'chart': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>''',
    'help': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
    'home': '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>''',
}

def icon(name, size=20, color=COLORS['accent']):
    """Return an SVG icon with custom color."""
    svg = ICONS.get(name, ICONS['info'])
    svg = svg.replace('currentColor', color)
    svg = svg.replace('width="20"', f'width="{size}"').replace('height="20"', f'height="{size}"')
    svg = svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    return svg

# Set page configuration
st.set_page_config(
    page_title="Alzheimer's Disease Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with custom color palette - Force dark mode
st.markdown(f"""
<style>
    /* FORCE DARK MODE ON ALL ELEMENTS */
    .stApp, .main, .block-container, [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], [data-testid="stToolbar"], 
    .stApp > header, .stApp > div {{
        background-color: {COLORS['bg']} !important;
    }}
    
    /* Main content area */
    .main .block-container {{
        background-color: {COLORS['bg']} !important;
        padding-top: 2rem !important;
    }}
    
    /* Remove any white backgrounds */
    div[data-testid="stVerticalBlock"], 
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"],
    .element-container {{
        background-color: transparent !important;
    }}
    
    /* Main header */
    .main-header {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['text']} !important;
        text-align: center;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }}
    
    .sub-header {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS['text']} !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    /* Card styling */
    .card {{
        background: var(--white);
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
    }}
    
    .card-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #E5E5E5;
    }}
    
    /* Result boxes */
    .result-box {{
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid;
    }}
    
    .normal-result {{
        background-color: #F0FDF4;
        color: #166534;
        border-left-color: #22C55E;
    }}
    
    .mild-result {{
        background-color: #FFFBEB;
        color: #92400E;
        border-left-color: {COLORS['highlight']};
    }}
    
    .moderate-result {{
        background-color: #FEF3C7;
        color: #78350F;
        border-left-color: {COLORS['accent']};
    }}
    
    .severe-result {{
        background-color: #FEE2E2;
        color: #991B1B;
        border-left-color: #DC2626;
    }}
    
    /* Feature cards */
    .feature-card {{
        background: var(--light-gray);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        border: 1px solid #E5E5E5;
    }}
    
    .feature-card h4 {{
        color: var(--dark);
        margin: 12px 0 8px 0;
        font-size: 1rem;
    }}
    
    .feature-card p {{
        color: var(--text-light);
        font-size: 0.875rem;
        margin: 0;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {COLORS['accent']} 0%, {COLORS['highlight']} 100%);
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background: {COLORS['surface']};
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: #E5E5E5;
    }}
    
    section[data-testid="stSidebar"] .stRadio label {{
        color: #E5E5E5 !important;
    }}
    
    /* Chat styling */
    .chat-header {{
        background: {COLORS['surface']};
        color: white;
        padding: 14px 20px;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .chat-container {{
        background: var(--light-gray);
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        margin-top: 20px;
    }}
    
    /* Button accent color override */
    .stButton > button {{
        border-color: {COLORS['accent']} !important;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['accent']} !important;
        color: white !important;
        border-color: {COLORS['accent']} !important;
    }}
    
    /* Hide streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* FAQ buttons */
    .faq-btn {{
        background: var(--white);
        border: 1px solid #E5E5E5;
        border-radius: 6px;
        padding: 10px 16px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.875rem;
        color: var(--dark);
    }}
    
    .faq-btn:hover {{
        border-color: {COLORS['accent']};
        color: {COLORS['accent']};
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chatbot' not in st.session_state and CHATBOT_AVAILABLE:
    try:
        st.session_state.chatbot = AlzheimerChatbot()
    except Exception as e:
        st.session_state.chatbot = None
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None
if 'last_probabilities' not in st.session_state:
    st.session_state.last_probabilities = None
if 'stored_image' not in st.session_state:
    st.session_state.stored_image = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False
if 'chat_context_message' not in st.session_state:
    st.session_state.chat_context_message = None

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div style="display: inline-flex; align-items: center; gap: 10px;">
            {icon('brain', 36, COLORS['highlight'])}
            <span style="font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Alzheimer's<br/>Detection</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    page = st.radio("Navigation", ["Home", "Analyze", "Chat", "About"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #9CA3AF; padding: 0 10px;">
        <strong style="color: {COLORS['highlight']};">Model</strong><br/>
        EfficientNet-B0<br/><br/>
        <strong style="color: {COLORS['highlight']};">Classes</strong><br/>
        Non-demented, Very Mild,<br/>Mild, Moderate
    </div>
    """, unsafe_allow_html=True)

# Load model
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
    fig, ax = plt.subplots(figsize=(8, 3.5))
    colors = ['#22C55E', COLORS['highlight'], COLORS['accent'], '#DC2626']
    bars = ax.barh(labels, probabilities, color=colors, height=0.5)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.1%}',
                va='center', fontsize=10, color=COLORS['surface'])
    ax.set_xlim(0, 1.15)
    ax.set_xlabel('Probability', fontsize=10, color=COLORS['surface'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E5E5E5')
    ax.spines['bottom'].set_color('#E5E5E5')
    ax.tick_params(colors=COLORS['surface'])
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    plt.tight_layout()
    return fig

def render_chat_interface(context_message=None):
    """Render the chat interface."""
    if not CHATBOT_AVAILABLE:
        st.warning("Chatbot unavailable. Install: pip install google-generativeai python-dotenv")
        return
    
    if not st.session_state.get('chatbot'):
        st.error("Chatbot failed to initialize. Check your GEMINI_API_KEY in .env")
        return
    
    chatbot = st.session_state.chatbot
    
    # Process context message
    if context_message:
        if context_message == "explain" and st.session_state.last_prediction:
            with st.spinner("Generating explanation..."):
                response = chatbot.explain_result()
                st.session_state.chat_history.append({"role": "user", "content": "Please explain my result"})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        elif context_message == "next_steps" and st.session_state.last_prediction:
            with st.spinner("Generating guidance..."):
                response = chatbot.get_next_steps()
                st.session_state.chat_history.append({"role": "user", "content": "What should I do next?"})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Show context if available
    if st.session_state.last_prediction:
        st.info(f"Context: Last prediction was **{st.session_state.last_prediction}**")
    
    # Quick questions
    st.markdown(f"""
    <div class="sub-header">
        {icon('help', 18)}
        Quick Questions
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

# ============ HOME PAGE ============
if page == "Home":
    st.markdown(f"""
    <div class="main-header">
        {icon('brain', 32)}
        Alzheimer's Disease Detection
    </div>
    <p style="text-align: center; color: {COLORS['text_muted']}; margin-bottom: 2rem;">
        AI-powered MRI analysis for early detection
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                {icon('info', 22)}
                <span style="font-weight: 600;">About This Tool</span>
            </div>
            <p style="color: {COLORS['text_muted']}; line-height: 1.7;">
                Upload brain MRI scans to receive AI-powered assessment of cognitive impairment stages.
            </p>
            <div style="margin-top: 16px;">
                <strong>How it works:</strong>
                <ol style="color: {COLORS['text_muted']}; margin-top: 8px; line-height: 1.8;">
                    <li>Upload a brain MRI scan</li>
                    <li>AI analyzes structural patterns</li>
                    <li>Receive probability scores</li>
                    <li>Get AI-powered explanations</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            {icon('search', 28)}
            <h4>Deep Analysis</h4>
            <p>EfficientNet architecture</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="feature-card" style="margin-top: 12px;">
            {icon('zap', 28)}
            <h4>Fast Results</h4>
            <p>Predictions in seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="feature-card" style="margin-top: 12px;">
            {icon('chat', 28)}
            <h4>AI Assistant</h4>
            <p>Get explanations & guidance</p>
        </div>
        """, unsafe_allow_html=True)

# ============ ANALYZE PAGE ============
elif page == "Analyze":
    st.markdown(f"""
    <div class="main-header">
        {icon('search', 28)}
        MRI Analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    model_loaded = False
    try:
        model = EfficientNet.from_pretrained('efficientnet-b0', num_classes=4)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        model.eval()
        model_loaded = True
    except FileNotFoundError:
        st.error(f"Model not found at {MODEL_PATH}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="sub-header">
            {icon('upload', 18)}
            Upload MRI
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose MRI image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        st.markdown(f"""
        <div class="sub-header" style="margin-top: 20px;">
            {icon('clipboard', 18)}
            Or Try Sample
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
                    sample = st.selectbox("Image", samples, label_visibility="collapsed")
                    if st.button("Use Sample", use_container_width=True):
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
    
    # Display and analyze
    if st.session_state.stored_image is not None and model_loaded:
        image = st.session_state.stored_image
        
        with col2:
            st.markdown(f"""
            <div class="sub-header">
                {icon('chart', 18)}
                Preview
            </div>
            """, unsafe_allow_html=True)
            st.image(image, use_container_width=True)
        
        labels = ["Mild Alzheimer's", "Moderate Alzheimer's", "Non-demented", "Very Mild Alzheimer's"]
        
        if not st.session_state.analysis_complete:
            progress = st.progress(0)
            status = st.empty()
            
            status.text("Preprocessing...")
            progress.progress(30)
            preprocessed = preprocess(image)
            time.sleep(0.15)
            
            status.text("Analyzing...")
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
        
        if st.session_state.analysis_complete:
            result_label = st.session_state.last_prediction
            label_idx = st.session_state.get('last_label_idx', 0)
            
            result_classes = {2: "normal-result", 3: "mild-result", 0: "moderate-result", 1: "severe-result"}
            result_class = result_classes.get(label_idx, "mild-result")
            
            st.markdown(f"""
            <div class="result-box {result_class}">
                <h3 style="margin: 0 0 8px 0;">Result: {result_label}</h3>
                <p style="margin: 0; opacity: 0.85;">Analysis indicates <strong>{result_label}</strong>.</p>
            </div>
            """, unsafe_allow_html=True)
            
            cached_probs = st.session_state.last_probabilities
            prob_values = [cached_probs[l] for l in labels]
            fig = create_prediction_chart(prob_values, labels)
            st.pyplot(fig)
            
            # Action buttons
            if CHATBOT_AVAILABLE:
                st.markdown(f"""
                <div class="sub-header" style="margin-top: 20px;">
                    {icon('help', 18)}
                    Understand Results
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("Explain Result", use_container_width=True):
                        st.session_state.show_chat = True
                        st.session_state.chat_context_message = "explain"
                        st.rerun()
                with c2:
                    if st.button("Next Steps", use_container_width=True):
                        st.session_state.show_chat = True
                        st.session_state.chat_context_message = "next_steps"
                        st.rerun()
                with c3:
                    if st.button("Ask Question", use_container_width=True):
                        st.session_state.show_chat = True
                        st.rerun()
            
            # Inline chat
            if st.session_state.show_chat:
                st.markdown("---")
                st.markdown(f"""
                <div class="chat-header">
                    {icon('chat', 18, '#FFFFFF')}
                    <span style="font-weight: 600;">AI Assistant</span>
                </div>
                """, unsafe_allow_html=True)
                
                context = st.session_state.chat_context_message
                st.session_state.chat_context_message = None
                render_chat_interface(context)

# ============ CHAT PAGE ============
elif page == "Chat":
    st.markdown(f"""
    <div class="main-header">
        {icon('chat', 28)}
        AI Assistant
    </div>
    <p style="text-align: center; color: {COLORS['text_muted']}; margin-bottom: 1.5rem;">
        Ask questions about Alzheimer's disease
    </p>
    """, unsafe_allow_html=True)
    
    render_chat_interface()

# ============ ABOUT PAGE ============
elif page == "About":
    st.markdown(f"""
    <div class="main-header">
        {icon('info', 28)}
        About
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            {icon('brain', 22)}
            <span style="font-weight: 600;">Overview</span>
        </div>
        <p style="color: {COLORS['text_muted']}; line-height: 1.7;">
            This tool uses deep learning to analyze brain MRI scans for signs of Alzheimer's disease.
            EfficientNet architecture identifies patterns indicative of cognitive impairment stages.
        </p>
    </div>
    
    <div class="card">
        <div class="card-header">
            {icon('zap', 22)}
            <span style="font-weight: 600;">Technical</span>
        </div>
        <ul style="color: {COLORS['text_muted']}; line-height: 1.8;">
            <li><strong>Model:</strong> EfficientNet-B0</li>
            <li><strong>Framework:</strong> PyTorch</li>
            <li><strong>AI Chat:</strong> Google Gemini</li>
        </ul>
    </div>
    
    <div class="card" style="background: #FFFBEB; border-color: {COLORS['highlight']};">
        <div class="card-header" style="border-bottom-color: {COLORS['highlight']};">
            {icon('info', 22, COLORS['accent'])}
            <span style="font-weight: 600; color: {COLORS['accent']};">Disclaimer</span>
        </div>
        <p style="color: #78350F; line-height: 1.7;">
            For educational and research purposes only. Not a substitute for professional medical advice.
            Always consult qualified healthcare providers.
        </p>
    </div>
    """, unsafe_allow_html=True)
