import streamlit as st
from pkg.shared import config
from pkg.shared.core.stage_logger import stage_log


@stage_log(stage=2)
def render_sidebar():
    st.sidebar.image(config.LOGO_PATH, width=300)
    st.sidebar.write("")
    st.sidebar.write("")
    
    if "page" not in st.session_state:
        st.session_state.page = "Connect"
        
    if st.sidebar.button("📊 Connect"):
        st.session_state.page = "Connect"
    if st.sidebar.button("💻 Report"):
        st.session_state.page = "Report"
    if st.sidebar.button("🛠️ Settings"):
        st.session_state.page = "Settings"
    if st.sidebar.button("❔ Help"):
        st.session_state.page = "Help"
        
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.image(config.CAZE_PATH, use_container_width=True)