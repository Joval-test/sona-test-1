import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime, timedelta
import base64
# Change these lines
from pkg.admin.components.email import send_email, prepare_email_message
from pkg.shared import config
from pkg.shared.core.stage_logger import stage_log

@stage_log(stage=2)
def generate_private_link(user_id):
    base_url = config.BASE_LINK
    return f"{base_url}?user={user_id}"

@stage_log(stage=1)
def render_page(llm, embeddings):
    
    # Display header
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center; background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
            </h1>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)

    try:
        if not os.path.exists(config.MASTER_PATH):
            st.info("No leads found. Please upload the leads in the settings section.")
            return
        df = pd.read_excel(config.MASTER_PATH)
        df = df.sort_values('source')  # Sort all leads by source
        if df.empty:
            st.info("No leads found. Please upload the leads in the settings section.")
            return
        sources = sorted(df['source'].unique())  # Sorted tab order
        
        # Add custom CSS for table styling
        st.markdown("""
            <style>
                .stDataFrame {
                    width: 100% !important;
                    background-color: transparent !important;
                }
                .stDataFrame table {
                    width: 100% !important;
                    background-color: transparent !important;
                    border-collapse: collapse !important;
                    border-spacing: 0 !important;
                }
                .stDataFrame td {
                    border: none !important;
                    background-color: transparent !important;
                    padding: 8px 12px !important;
                }
                .stDataFrame th {
                    border: none !important;
                    background-color: transparent !important;
                    padding: 8px 12px !important;
                    color: #6c757d !important;
                    font-weight: 500 !important;
                }
                .stDataFrame tr {
                    background-color: transparent !important;
                    border: none !important;
                }
                div[data-testid="stHorizontalBlock"] {
                    width: 100% !important;
                    background-color: transparent !important;
                }
                /* Remove any additional borders */
                .element-container, .stDataFrame div {
                    border: none !important;
                    background-color: transparent !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize session state for selected leads
        if 'selected_leads' not in st.session_state:
            st.session_state.selected_leads = set()

        # Create tabs for each source
        tabs = st.tabs(sources)
        
        for source, tab in zip(sources, tabs):
            with tab:
                source_df = df[df['source'] == source].copy()
                st.write(f"### {source} Leads")
                
                # Add Select All and Clear All buttons side by side with full width
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select All", key=f"select_all_{source}", use_container_width=True):
                        for idx in source_df.index:
                            st.session_state.selected_leads.add(idx)
                with col2:
                    if st.button("Clear All", key=f"clear_all_{source}", use_container_width=True):
                        st.session_state.selected_leads = st.session_state.selected_leads - set(source_df.index)
                
                # Create selection column for this source
                source_df['Select'] = False
                for idx in st.session_state.selected_leads:
                    if idx in source_df.index:
                        source_df.loc[idx, 'Select'] = True

                # Custom row display instead of data_editor
                for idx, row in source_df.iterrows():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1, 1.5, 1.5, 3, 1, 1])
                    
                    with col1:
                        if st.checkbox(
                            "Select", 
                            key=f"select_{source}_{idx}", 
                            value=row['Select'],
                            label_visibility="collapsed"
                        ):
                            st.session_state.selected_leads.add(idx)
                        else:
                            if idx in st.session_state.selected_leads:
                                st.session_state.selected_leads.remove(idx)
                    
                    with col2:
                        st.write("", row['ID'])  # Added empty string as label
                    with col3:
                        st.write("", row['Name'])
                    with col4:
                        st.write("", row['Company'])
                    with col5:
                        st.write("", row['Description'])
                    with col6:
                        st.write("Sent" if row.get('Email Sent', False) else "Not Sent")
                    with col7:
                        st.write(row.get('Email Sent Count', 0))
                # Update selected leads from this source
                selected_df = None
                if st.session_state.selected_leads:
                    selected_df = df.loc[list(st.session_state.selected_leads)]
                
                if st.button("Send Email to Selected Leads", key=f"send_email_{source}"):
                    if selected_df is None or selected_df.empty:
                        st.error("Please select at least one lead to send emails.")
                        return
                    try:
                        # Replace the st.secrets usage with environment variables
                        sender_email = st.session_state.get("EMAIL_SENDER", "")
                        sender_password = st.session_state.get("EMAIL_PASSWORD", "")
                        if not sender_email or not sender_password:
                            st.error("Email credentials not configured. Please set them up in the settings section.")
                            return
                        company_collection = st.session_state.company_collection
                        report_dir = os.path.dirname(config.REPORT_PATH)
                        if not os.path.exists(report_dir):
                            os.makedirs(report_dir)
                        if os.path.exists(config.REPORT_PATH):
                            report_df = pd.read_excel(config.REPORT_PATH)
                        else:
                            report_df = pd.DataFrame(columns=[
                                'ID', 'Name', 'Company', 'Email', 'Description', 
                                'Private Link', 'Sent Date', 'Chat Summary',
                                'Status (Hot/Warm/Cold/Not Responded)', 'source', 'Connected'
                            ])
                            report_df.to_excel(config.REPORT_PATH, index=False)
                        # --- Update master file for email sent status/count ---
                        master_df = pd.read_excel(config.MASTER_PATH)
                        if 'Last Email Sent' not in master_df.columns:
                            master_df['Last Email Sent'] = pd.NaT
                        if 'Email Sent' not in master_df.columns:
                            master_df['Email Sent'] = False
                        if 'Email Sent Count' not in master_df.columns:
                            master_df['Email Sent Count'] = 0
                        for _, row in selected_df.iterrows():
                            # Check if lead already exists in report
                            existing_lead = pd.DataFrame()  # Initialize as empty DataFrame
                            
                            if not report_df.empty and 'Email' in report_df.columns:
                                existing_lead = report_df[report_df['Email'] == row['Email']]
                                
                            if not existing_lead.empty:
                                if pd.notna(existing_lead['Sent Date'].iloc[0]):
                                    st.warning(f"Email already sent to {row['Email']}")
                                    continue
                                # Use existing ID if lead exists
                                lead_id = existing_lead['ID'].iloc[0]
                            else:
                                # Generate new ID only for new leads
                                lead_id = str(uuid.uuid4())
                            
                            private_link = generate_private_link(lead_id)
                            
                            user_info = {
                                'name': row['Name'],
                                'company': row['Company'],
                                'email': row['Email']
                            }
                            
                            message_content = prepare_email_message(
                                company_collection,
                                user_info,
                                llm,
                                embeddings,
                                private_link
                            )
                            
                            if message_content:
                                message_content += f"\n\nClick here to chat with us: {private_link}"
                                
                                # --- Check cooldown before sending email ---
                                idx = master_df[master_df['Email'] == row['Email']].index
                                if not idx.empty:
                                    last_sent = master_df.loc[idx, 'Last Email Sent'].values[0]
                                    if pd.notna(last_sent):
                                        last_sent_time = pd.to_datetime(last_sent)
                                        if datetime.now() - last_sent_time < timedelta(hours=5):
                                            st.warning(f"Email already sent to {row['Email']} within the last 5 hours.")
                                            continue  # Skip sending email
                                
                                print(f"About to send email to {row['Email']} with sender {sender_email}")
                                success = send_email(
                                    sender_email,
                                    sender_password,
                                    row['Email'],
                                    "Invitation to Chat with Caze BizConAI",
                                    message_content
                                )
                                
                                if success:
                                    st.success(f"Email sent to {row['Email']}")
                                    # Update master file for this email
                                    if not idx.empty:
                                        master_df.loc[idx, 'Email Sent'] = True
                                        master_df.loc[idx, 'Email Sent Count'] = master_df.loc[idx, 'Email Sent Count'].fillna(0) + 1
                                        master_df.loc[idx, 'Last Email Sent'] = datetime.now()
                                        master_df.to_excel(config.MASTER_PATH, index=False)
                                    if existing_lead.empty:
                                        # Only add new lead if it doesn't exist
                                        new_lead = {
                                            'ID': lead_id,
                                            'Name': row['Name'],
                                            'Company': row['Company'],
                                            'Email': row['Email'],
                                            'Description': row['Description'],
                                            'Private Link': private_link,
                                            'Sent Date': datetime.now(),
                                            'Chat Summary': '',
                                            'Status (Hot/Warm/Cold/Not Responded)': 'Not Responded',
                                            'source': row['source'],  # Added source field
                                            'Connected': row.get('Connected', False)  # Add default value if field doesn't exist
                                        }
                                        report_df = pd.concat([report_df, pd.DataFrame([new_lead])], ignore_index=True)
                                    else:
                                        # Update existing lead's sent date
                                        report_df.loc[report_df['Email'] == row['Email'], 'Sent Date'] = datetime.now()
                                    
                                    report_df.to_excel(config.REPORT_PATH, index=False)
                                else:
                                    st.error(f"Failed to send email to {row['Email']}")
                            else:
                                st.error(f"Failed to generate email content for {row['Email']}")
                                    
                    except Exception as e:
                        st.error(f"Error sending emails: {str(e)}")
                            
    except Exception as e:
        st.error(f"An error occurred: {e}")