import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from shared.core.vector_store import query_collections
from langchain.schema import SystemMessage
from apps.utils.stage_logger import stage_log



context_instr = """
    Create an email message with only the content use the instruction below
        - Use the user information to personalize your greeting. Everything inside '[]' should be replaced with the actual information.
        - Format: "Hi [name] ! I'm an [Give a personal name of your choice based on the user info like regional to the user] from [provide company name]"
        - If no name is found, use the above greeting without the name parameter to make it generic.
        - Only discuss features/solutions mentioned in the company information.
        - Keep the content under 20 lines
        - Do not provide the regards or any best regards
        - End the message content with a prompt to click on this link to have a conversation with us, where i'll provide the link after this content message
"""
@stage_log(stage=2)
def create_email_message(context):
    base_instruction = """You are an AI cold calling/texting assistant. Here is the context for our interaction:

                {context}
                If there is << Previous Chat Summary >> in the context try to continue from the previous chat by letting them know the key points of previous chat and enquire them if they want to start fresh or continue from the previous.
                When generating the first message, use the user information provided above to personalize your introduction. If you can't find a name, use a generic greeting.
                """
    return SystemMessage(content=base_instruction.format(context=context) + context_instr)

@stage_log(stage=2)
def prepare_email_message(company_collection, user_info, llm, embeddings, product_link):
    company_has_docs = len(company_collection.get()['ids']) > 0
    print(user_info)
    if user_info:
        if company_has_docs:
            initial_context = query_collections("company information and user information, company information more related to the user information", company_collection, user_info, embeddings, llm)
            if initial_context:
                system_message = create_email_message(initial_context)
                initial_messages = [system_message]
                response = llm.invoke(initial_messages)
                print(response.content)
                return response.content

@stage_log(stage=1)
def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False