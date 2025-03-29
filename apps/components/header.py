import streamlit as st
import base64
import config

def render_header():
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        
    image_and_heading_html = f"""
    <div style="display: flex; justify-content:center;background:white">
        <img src="data:image/png;base64,{encoded_image}" 
             style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
        <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                Caze <span style="color: #304654;">BizConAI</span>
        </h1>
    </div>
    """
    st.markdown(image_and_heading_html, unsafe_allow_html=True)
    st.write("")