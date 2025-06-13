from core.chat_logic import setup_llm_and_embeddings, setup_company_collection

class ProductExtractorAgent:
    def __init__(self):
        self.llm, self.embeddings = setup_llm_and_embeddings()
        self.company_collection = setup_company_collection(self.embeddings)

    def extract_products(self, company_info: str) -> list:
        """
        Extract product names from the entire company document using LLM.
        Args:
            company_info (str): The company information text.
        Returns:
            list: List of product names (strings).
        """
        # Retrieve all documents from Chroma
        try:
            all_docs = self.company_collection.get()
            context = "\n".join(all_docs['documents']) if all_docs and 'documents' in all_docs else ""
        except Exception:
            context = ""
        if not context:
            context = company_info
        prompt = f"""
        From the following company information, extract a comma-separated list of product names that the company offers. Only return the product names, separated by commas.
        
        Company Info:
        {context}
        """
        try:
            response = self.llm.invoke(prompt)
            products = [p.strip() for p in response.content.split(',') if p.strip()]
            return products
        except Exception:
            return [] 