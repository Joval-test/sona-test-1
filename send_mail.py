import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from vector_store import query_collections
from prompts import create_system_message

def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to the Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)  # Log in
            server.send_message(msg)  # Send the email

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        
        
def prepare_email_message(company_collection,user_info,llm,embeddings,product_link):
    company_has_docs = len(company_collection.get()['ids']) > 0
    print(user_info)
    if user_info:
        if company_has_docs:
            initial_context = query_collections("company information and user information, company information more related to the user information", company_collection, user_info, embeddings,llm)
            if initial_context:
                system_message=f"""
                            You are an AI cold chatting assistant. Here is the context for our interaction: 
                            {initial_context}
                            Create an email message with only the content use the instruction below
                            - Use the user information to personalize your greeting
                            - Format: "Hi [name]! I'm an [Give a personal name of your choice based on the user info like regional to the user] from [company]. Do you have a few minutes to chat?"
                            - If no name is found, use the above greeting without the name parameter to make it generic.
                            - Only discuss features/solutions mentioned in the company information.
                            - Keep the content under 20 lines
                            - Do not provide the regards or any best regards
                            - End the message content with a prompt to click on this link to have a conversation with us, where i'll provide the link after this content message
                        """
                initial_messages = [system_message]
                response = llm.invoke(initial_messages)
                print(response.content)
                return response.content