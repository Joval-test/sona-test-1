import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
import config
import plotly.express as px
from io import BytesIO


def classify_lead(email):
    # Get status from selected_users.xlsx
    status_file_path = os.path.join(os.path.dirname(config.REPORT_PATH), "selected_users.xlsx")
    status_col = "Status (Hot/Warm/Cold/Not Responded)"
    
    try:
        if os.path.exists(status_file_path):
            status_df = pd.read_excel(status_file_path)
            if status_col in status_df.columns and 'Email' in status_df.columns:
                # Look for the email in the status file
                matching_status = status_df[status_df['Email'] == email]
                if not matching_status.empty:
                    status = matching_status[status_col].iloc[0]
                    if pd.notna(status):
                        return status.strip().title()
    except Exception as e:
        st.warning(f"Error reading status file: {e}")
    
    return "Not Responded"

def generate_private_link(user_id):
    base_link=config.BASE_LINK
    return f"http://{base_link}?user={user_id}"


def render_page(report_path=None):
    if report_path is None:
        report_path = config.REPORT_PATH

    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
            </h1>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)

    if not os.path.exists(report_path):
        st.warning("No reports available. Start conversations with leads to generate reports.")
        return

    try:
        df = pd.read_excel(report_path)
        
        # Initialize required columns with default values
        required_columns = {
            'Name': '',
            'Company': '',
            'Email': '',
            'ID': '',
            'Sent Date': pd.NaT,
            'Chat Summary': '',
            'Private Link': '',
            'Status (Hot/Warm/Cold/Not Responded)': 'Not Responded'  # Added status column
        }
        
        # Add missing columns with default values
        for col, default_value in required_columns.items():
            if col not in df.columns:
                df[col] = default_value
        
        # Remove duplicates and classify leads using the new logic
        df = df.drop_duplicates(subset=['Email'], keep='last')
        df['Lead Status'] = df['Email'].apply(classify_lead)
        
        # Generate private links if missing
        if 'Private Link' not in df.columns or df['Private Link'].isna().any():
            df['Private Link'] = df['ID'].apply(generate_private_link)
            df.to_excel(report_path, index=False)
        
        # Initialize session state for selected leads
        if 'selected_report_leads' not in st.session_state:
            st.session_state.selected_report_leads = set()

        # Dashboard Overview with Lead Classification
        st.header("Lead Engagement Dashboard")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_leads = len(df)
            st.metric("Total Leads", total_leads)
        with col2:
            hot_leads = len(df[df['Lead Status'] == 'Hot'])
            st.metric("Hot Leads", hot_leads)
        with col3:
            warm_leads = len(df[df['Lead Status'] == 'Warm'])
            st.metric("Warm Leads", warm_leads)
        with col4:
            cold_leads = len(df[df['Lead Status'] == 'Cold'])
            st.metric("Cold Leads", cold_leads)
        with col5:
            not_responded = len(df[df['Lead Status'] == 'Not Responded'])
            st.metric("Not Responded", not_responded)


        # Timeline Analysis
        st.subheader("Contact Timeline")
        df['Sent Date'] = pd.to_datetime(df['Sent Date'])
        timeline_data = df.groupby(df['Sent Date'].dt.date).size().reset_index(name='count')
        if not timeline_data.empty:
            fig_timeline = px.line(timeline_data, x='Sent Date', y='count', 
                                 title="Daily Contact Trend",
                                 labels={'count': 'Number of Contacts', 'Sent Date': 'Date'})
            st.plotly_chart(fig_timeline)

        # Lead Selection Controls
        st.header("Lead Selection")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Select All", use_container_width=True):
                st.session_state.selected_report_leads = set(df.index)
        with col2:
            if st.button("Clear Selection", use_container_width=True):
                st.session_state.selected_report_leads.clear()
        st.write(f"Selected: {len(st.session_state.selected_report_leads)} leads")

        # Lead Classification Tabs
        tabs = st.tabs(["All Leads", "Hot Leads", "Warm Leads", "Cold Leads", "Not Responded"])
        
        # Add custom CSS for consistent spacing
        st.markdown("""
            <style>
                .list-row {
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }
                .list-item {
                    line-height: 36px;
                }
                .detail-row {
                    padding: 15px 0;
                    border-bottom: 1px solid #eee;
                }
            </style>
        """, unsafe_allow_html=True)
        
        for tab, status in zip(tabs, ["All", "Hot", "Warm", "Cold", "Not Responded"]):
            with tab:
                filtered_df = df if status == "All" else df[df['Lead Status'] == status]
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{status} Leads ({len(filtered_df)})")
                with col2:
                    view_key = f"detailed_view_{status.lower().replace(' ', '_')}"
                    if view_key not in st.session_state:
                        st.session_state[view_key] = False
                    st.session_state[view_key] = st.toggle(
                        "Detailed View",
                        value=st.session_state[view_key],
                        key=f"toggle_{status.lower().replace(' ', '_')}"
                    )
                
                if len(filtered_df) > 0:
                    if st.session_state[view_key]:
                        # Detailed view
                        for idx, row in filtered_df.iterrows():
                            st.markdown('<div class="detail-row">', unsafe_allow_html=True)
                            col1, col2 = st.columns([0.1, 0.9])
                            with col1:
                                if st.checkbox("", key=f"lead_{status}_{idx}", 
                                             value=idx in st.session_state.selected_report_leads):
                                    st.session_state.selected_report_leads.add(idx)
                                else:
                                    st.session_state.selected_report_leads.discard(idx)
                            
                            with col2:
                                st.markdown(f"""
                                **{row['Name']}** - {row['Company']}  
                                📧 {row['Email']}  
                                📅 Last Contact: {row['Sent Date'].strftime('%Y-%m-%d') if pd.notna(row['Sent Date']) else 'Not Contacted'}  
                                💬 Summary: {row['Chat Summary'] if pd.notna(row['Chat Summary']) else 'No interaction yet'}  
                                🔗 [Chat Link]({row['Private Link'] if pd.notna(row['Private Link']) else generate_private_link(row['ID'])})
                                """)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # List view header
                        cols = st.columns([0.1, 1, 1.5, 2])
                        with cols[1]:
                            st.markdown('<p class="list-item"><strong>Name</strong></p>', unsafe_allow_html=True)
                        with cols[2]:
                            st.markdown('<p class="list-item"><strong>Company</strong></p>', unsafe_allow_html=True)
                        with cols[3]:
                            st.markdown('<p class="list-item"><strong>Email</strong></p>', unsafe_allow_html=True)
                        
                        # List view rows
                        for idx, row in filtered_df.iterrows():
                            st.markdown('<div class="list-row">', unsafe_allow_html=True)
                            cols = st.columns([0.1, 1, 1.5, 2])
                            with cols[0]:
                                if st.checkbox("", key=f"lead_list_{status}_{idx}", 
                                             value=idx in st.session_state.selected_report_leads):
                                    st.session_state.selected_report_leads.add(idx)
                                else:
                                    st.session_state.selected_report_leads.discard(idx)
                            with cols[1]:
                                st.markdown(f'<p class="list-item">{row["Name"]}</p>', unsafe_allow_html=True)
                            with cols[2]:
                                st.markdown(f'<p class="list-item">{row["Company"]}</p>', unsafe_allow_html=True)
                            with cols[3]:
                                st.markdown(f'<p class="list-item">{row["Email"]}</p>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info(f"No {status.lower()} leads available.")

        # Export and Delete Selected Leads
        if st.session_state.selected_report_leads:
            selected_df = df.loc[list(st.session_state.selected_report_leads)]
            
            # Add custom CSS for full-width buttons
            st.markdown("""
                <style>
                    .stButton > button {
                        width: 100%;
                    }
                    div[data-testid="column"] {
                        width: 100%;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Create columns with equal width and spacing
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📥 Export Selected Leads", use_container_width=True):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        selected_df.to_excel(writer, index=False)
                    
                    output.seek(0)
                    st.download_button(
                        label="Download Selected Leads",
                        data=output.getvalue(),
                        file_name=f"selected_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🗑️ Delete Selected Leads", type="primary", use_container_width=True):
                    if st.session_state.selected_report_leads:
                        df = df.drop(index=list(st.session_state.selected_report_leads))
                        df.to_excel(report_path, index=False)
                        st.session_state.selected_report_leads.clear()
                        st.success("Selected leads have been deleted.")
                        st.rerun()

    except Exception as e:
        st.error(f"An error occurred while processing the report: {str(e)}")

if __name__ == "__main__":
    render_page()