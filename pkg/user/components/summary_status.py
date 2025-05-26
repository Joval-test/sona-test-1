import pandas as pd
import streamlit as st
from pkg.shared import config
from pkg.shared.core.stage_logger import stage_log

@stage_log(stage=2)
def prepare_summary(llm, prompt, df, user_id):
    try:
        summary = llm.invoke(prompt)
        df['ID'] = df['ID'].astype(str)
        matched_row = df[df['ID'] == user_id]
        
        if not matched_row.empty:
            index = matched_row.index[0]
            df.at[index, 'Chat Summary'] = summary.content
            df.to_excel(config.REPORT_PATH, index=False)
            return True
    except Exception as e:
        print(f"Error updating summary: {e}")
        return False

@stage_log(stage=2)
def prepare_status(llm, prompt, df, user_id):
    try:
        status = llm.invoke(prompt)
        df['ID'] = df['ID'].astype(str)
        matched_row = df[df['ID'] == user_id]
        
        if not matched_row.empty:
            index = matched_row.index[0]
            df.at[index, 'Status (Hot/Warm/Cold/Not Responded)'] = status.content
            df.to_excel(config.REPORT_PATH, index=False)
            return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False