from openai import OpenAI
from langchain_openai import ChatOpenAI
import chromadb
import constants
from config import Config
import os

class Clients:
    def __init__(self):
        self.openai_client = OpenAI(api_key=constants.APIKEY2)
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=constants.APIKEY2,
            temperature=Config.TEMPERATURE
        )
        os.makedirs(Config.PERSIST_DIRECTORY, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=Config.PERSIST_DIRECTORY)
        self.company_collection = self.chroma_client.get_or_create_collection(
            name="company_info_store",
            metadata={"hnsw:space": "cosine"}
        )
        self.user_collection = self.chroma_client.get_or_create_collection(
            name="user_info_store",
            metadata={"hnsw:space": "cosine"}
        )