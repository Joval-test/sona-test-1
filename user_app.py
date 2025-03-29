import streamlit as st
import os
import base64
import json
import config
from core.llm import (
    initialize_llm_azure,
    initialize_llm_llama,
    initialize_llm_phi,
    initialize_llm_mistral,
    initialize_llm_deepseek,
    initialize_embeddings_azure
)
from core.vector_store import initialize_collections
from apps.utils.state import initialize_session_state
from apps.utils.chat_interface import handle_chat_interface
from apps.utils.data_loader import load_user_data
from apps.utils.data_matcher import match_user_data

def get_llm_function():
    with open("config.json", "r") as file:
        config_data = json.load(file)
    
    llm_functions = {
        "Azure OpenAI": initialize_llm_azure,
        "Llama 3.1": initialize_llm_llama,
        "Phi3.5": initialize_llm_phi,
        "Mistral": initialize_llm_mistral,
        "Deepseek": initialize_llm_deepseek
    }
    
    selected_llm = config_data.get("llm")
    if selected_llm in llm_functions:
        return llm_functions[selected_llm]
    raise ValueError(f"Invalid LLM selected: {selected_llm}")



def main():
    try:
        initialize_session_state()
        
        embeddings = initialize_embeddings_azure()
        company_collection = initialize_collections(embeddings)
        st.session_state.company_collection = company_collection
        
        # Display header
        with open(config.ICON_PATH, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        
        st.write("")
        st.write("")
        st.write("")
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
        </h1>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)
        
        llm = get_llm_function()()
        load_user_data()
        
        user_content = match_user_data()
        
        if user_content:
            company_has_docs = len(company_collection.get()['ids']) > 0
            if company_has_docs:
                handle_chat_interface(llm, embeddings, company_collection, user_content)
            else:
                st.error("Please upload and process at least one company file/URL")
        else:
            st.warning("You do not have access to this chat. Please contact the admin for access.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()