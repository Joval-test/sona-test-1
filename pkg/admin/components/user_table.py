import streamlit as st
import pandas as pd
from pkg.shared.core.stage_logger import stage_log


@stage_log(stage=2)
def render_user_table(data: pd.DataFrame, selectable: bool = True):
    if data is None or data.empty:
        st.warning("No user data available")
        return
    
    cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])
    cols[0].markdown("**Select**" if selectable else "**Status**")
    cols[1].markdown("**ID**")
    cols[2].markdown("**Name**")
    cols[3].markdown("**Company**")
    cols[4].markdown("**Email**")


    for index, row in data.iterrows():
        cols = st.columns([0.1, 0.1, 0.2, 0.2, 0.2, 0.1])
        
        if selectable:
            if index not in st.session_state.selected_users:
                st.session_state.selected_users[index] = False
            
            is_selected = st.session_state.selected_users[index]
            st.session_state.selected_users[index] = cols[0].checkbox(
                "",
                value=is_selected,
                key=f"user_select_{index}"
            )
        else:
            cols[0].markdown("✓" if row.get("Status", False) else "")
            
        cols[1].markdown(str(row["ID"]))
        cols[2].markdown(row["Name"])
        cols[3].markdown(row["Company"])
        cols[4].markdown(str(row["Email"]))
