from langchain.schema import HumanMessage, AIMessage
from .chat_prompts import create_system_message
import json
import os

class ChatManager:
    def __init__(self, llm, embeddings, company_collection):
        self.llm = llm
        self.embeddings = embeddings
        self.company_collection = company_collection
        
    def load_chat_history(self, chat_file):
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_chat_history(self, chat_file, chat_history):
        with open(chat_file, 'w') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
    
    def convert_to_messages(self, chat_history, user_info=None):
        messages = []
        
        # Add system message with context
        context = self._get_context(chat_history, user_info)
        messages.append(create_system_message(context))
        
        # Add chat history
        for msg in chat_history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['message']))
            else:
                messages.append(AIMessage(content=msg['message']))
                
        return messages
    
    def _get_context(self, chat_history, user_info):
        context = ""
        
        if user_info:
            context += f"<< USER INFO >>\n"
            context += f"Name: {user_info.get('name', 'Unknown')}\n"
            context += f"Company: {user_info.get('company', 'Unknown')}\n"
            context += f"Email: {user_info.get('email', 'Unknown')}\n\n"
        
        context += "<< COMPANY INFO >>\n"
        if chat_history:
            # Get relevant company info based on last message
            search_results = self.company_collection.similarity_search(
                chat_history[-1]['message'], k=1
            )
        else:
            # Get general company info for initial message
            search_results = self.company_collection.similarity_search(
                "company general information", k=1
            )
            
        if search_results:
            context += search_results[0].page_content
            
        return context

    # Add to existing ChatManager class

    def is_conversation_ended(self, message):
        # Check if the message contains the closing phrase
        return "have a great day" in message.lower()
    
    def handle_conversation_end(self, uuid, chat_history):
        # Generate summary and status
        summary = generate_chat_summary(self.llm, chat_history)
        status = determine_interest_status(self.llm, chat_history)
        
        # Update report
        report_manager = ReportManager()
        report_manager.update_report(uuid, summary, status)
        
        return True