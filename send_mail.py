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
            initial_context = query_collections("company information and user information", company_collection, user_info, embeddings,llm)
            if initial_context:
                system_message=f"""
                    You are an agent to send and email to the client with this informations about the company and the user {initial_context}. Based on this information ur are supposed to curate a message body which decribes the company information in upto 4 sentences and provide the introduction like Dear [user name].
                    if the company name is not being able to be fetched then do not add the company name. You only have to provide the body and do not provide anything other than the context provided do not give any end note or conclusions like best regards and company name or company team etc.
                """
                initial_messages = [system_message]
                response = llm.invoke(initial_messages)
                print(response.content)
                return response.content