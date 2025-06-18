import pandas as pd
import os

class ReportManager:
    def __init__(self, report_path='data/report.xlsx'):
        self.report_path = report_path
    
    def update_report(self, uuid, summary, status):
        if not os.path.exists(self.report_path):
            raise FileNotFoundError(f"Report file not found at {self.report_path}")
        
        df = pd.read_excel(self.report_path)
        mask = df['ID'].astype(str) == str(uuid)
        
        if not mask.any():
            raise ValueError(f"UUID {uuid} not found in report")
        
        df.loc[mask, 'Chat Summary'] = summary
        df.loc[mask, 'Status'] = status
        
        df.to_excel(self.report_path, index=False)

def generate_chat_summary(llm, messages):
    messages_content = [f"{msg['role']}: {msg['message']}" for msg in messages]
    prompt = f"From this conversation between the AI agent and the consumer prepare a summary in 50 words, provide everything including the contact details: {messages_content}"
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content

def determine_interest_status(llm, messages):
    messages_content = [f"{msg['role']}: {msg['message']}" for msg in messages]
    prompt = f"Based on the following conversation {messages_content}, categorize the user's interest level as one of: 'Hot' (very interested), 'Warm' (partially interested), or 'Cold' (not interested). Give just one word answer."
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content.strip()