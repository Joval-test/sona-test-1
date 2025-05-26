import streamlit as st
from pkg.admin.components.header import render_header  # Changed from relative to absolute import
from pkg.shared.core.stage_logger import stage_log

@stage_log(stage=4)
def render_page():
    render_header()
    
    st.write("")
    st.header("Welcome to Caze Bizcon AI!")
    
    st.markdown("""
    ### Getting Started
Make sure to do the following to ensure you get the most out of this tool:
- Upload both lead details and your company details in Settings
- Ensure that the material you upload about your company has all the relevant information about your products that you'd like to be conveyed
- Check summaries of conversations to instantly know what was discussed with any given user

If you need any help with using the product, or you run into any issues, you can contact our team at info@cazelabs.com!""")