import streamlit as st
import threading
import time

# Import backend components directly to avoid modifying main.py
from main import build_pipeline
from src.display.streamlit_display import StreamlitTranscriptDisplay
# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="EchoNote AI",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'display_provider' not in st.session_state:
    st.session_state.display_provider = None
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if "pipeline_thread" not in st.session_state:
    st.session_state.pipeline_thread = None

# ==========================================
# CUSTOM CSS FOR PREMIUM DESIGN
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .title-text {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.2;
    }
    .subtitle-text {
        font-size: 0.9rem !important;
        color: #64748B !important;
        margin-top: 0.25rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .status-badge-ready {
        display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
        background-color: #F0FDF4; border: 1px solid #BBF7D0; color: #15803D;
        padding: 0.35rem 1rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;
        float: right; margin-top: 1rem;
    }
    .status-badge-recording {
        display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
        background-color: #FEF2F2; border: 1px solid #FECACA; color: #DC2626;
        padding: 0.35rem 1rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;
        float: right; margin-top: 1rem;
    }
    .status-dot-ready { height: 8px; width: 8px; background-color: #22C55E; border-radius: 50%; display: inline-block; box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2); }
    .status-dot-recording { height: 8px; width: 8px; background-color: #EF4444; border-radius: 50%; display: inline-block; box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2); animation: pulse 1.5s infinite; }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    
    .dashboard-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 1rem;
    }
    
    .transcript-box {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 1.5rem; min-height: 400px; color: #0F172A;
        font-size: 1.1rem; line-height: 1.6; margin-top: 1rem;
        white-space: pre-wrap;
    }
    .transcript-placeholder {
        color: #94A3B8; font-style: italic; display: flex; align-items: center; justify-content: center; text-align: center; height: 100%; min-height: 350px;
    }
    
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 600 !important; color: #0F172A !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem !important; color: #64748B !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# TOP NAVIGATION HEADER
# ==========================================
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown('<p class="title-text">EchoNote AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Real-Time Meeting Intelligence</p>', unsafe_allow_html=True)

with header_col2:
    if st.session_state.is_recording:
        st.markdown("""
            <div class="status-badge-recording">
                <span class="status-dot-recording"></span> Recording
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="status-badge-ready">
                <span class="status-dot-ready"></span> Ready
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# ==========================================
# MAIN DASHBOARD LAYOUT
# ==========================================
main_col, stats_col = st.columns([2.5, 1.5])

# LEFT COLUMN: Controls & Live Transcript
with main_col:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Live Session")
    
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    
    with btn_col1:
        if st.button("🟢 Start Recording", type="primary", use_container_width=True, disabled=st.session_state.is_recording):
            st.session_state.is_recording = True
            
            st.session_state.display_provider = StreamlitTranscriptDisplay()
            
            # Build the pipeline directly using the existing components
            st.session_state.display_provider = StreamlitTranscriptDisplay()

            st.session_state.pipeline = build_pipeline(
            display=st.session_state.display_provider)
            # Run the pipeline in a daemon thread so it doesn't block Streamlit
            pipeline = st.session_state.pipeline

            def run_pipeline():
               try:
                   pipeline.run()
               except Exception as e:
                   print(f"Pipeline exception: {e}")
            st.session_state.pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
            st.session_state.pipeline_thread.start()
            
            st.rerun()
            
    with btn_col2:
        if st.button("⏹️ Stop Recording", use_container_width=True, disabled=not st.session_state.is_recording):
            st.session_state.is_recording = False
            
            # Cleanly stop the pipeline and audio source to release the microphone
            if st.session_state.pipeline:
                try:
              
                    st.session_state.pipeline._audio_source.stop()
                except Exception as e:
                    print(f"Unable to stop microphone: {e}")

            st.session_state.pipeline = None
            st.session_state.pipeline_thread = None
                        
            st.rerun()
            
    # Fetch current transcript safely
    current_transcript = ""
    if st.session_state.display_provider:
        current_transcript = st.session_state.display_provider.get_transcript()
        
    # Render Transcript Area
    if current_transcript.strip():
        st.markdown(f'<div class="transcript-box">{current_transcript}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="transcript-box">
                <div class="transcript-placeholder">Waiting for transcription...</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN: Statistics
with stats_col:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Meeting Statistics")
    st.write("")
    st.write("")
    
    # Calculate words processed
    words_processed = len(current_transcript.split()) if current_transcript else 0
    current_status = "Active" if st.session_state.is_recording else "Idle"
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(label="Status", value=current_status)
    with m_col2:
        st.metric(label="Words", value=str(words_processed))
        
    st.write("")
    st.write("")
    
    # Use dynamic model configuration instead of hardcoded strings
    m_col3, m_col4 = st.columns(2)
    with m_col3:
        st.metric(label="Language", value="Auto-detect")
    with m_col4:
        # Dynamically fetch the provider configuration from config, fallback to Unknown
        st.metric(label="Model", value="Whisper")
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("System Info")
    st.caption("Backend Architecture: Python Provider Pattern")
    st.caption("Audio Capture: PyAudio & FFmpeg")
    st.caption("Processing: Local faster-whisper")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# AUTO-REFRESH LOOP
# ==========================================
# If recording, pause briefly and force a rerun to fetch the latest display data
if st.session_state.is_recording:
    time.sleep(1.0)
    st.rerun()