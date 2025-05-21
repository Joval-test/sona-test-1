import os
import pandas as pd
import streamlit as st
from shared import config
from apps.utils.stage_logger import stage_log

@stage_log(stage=2)
def load_user_data():
    data_path = config.REPORT_PATH
    if os.path.exists(data_path):
        print("data path opened")
        df = pd.read_excel(data_path)
        st.session_state.user_data_df = df
    else:
        print("File path doesn't exist")
        # st.warning("You do not have access to this chat. Please contact the admin for access.")