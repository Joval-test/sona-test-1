from langchain_openai import ChatOpenAI, AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_chroma import Chroma
import config

def initialize_llm():
    return AzureChatOpenAI(
        azure_endpoint=config.AZURE_ENDPOINT,
        azure_deployment=config.AZURE_DEPLOYMENT,
        api_version=config.AZURE_API_VERSION,
        api_key=config.AZURE_API_KEY,
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

def initialize_embeddings():
    return AzureOpenAIEmbeddings(
        azure_endpoint=config.AZURE_ENDPOINT,
        azure_deployment=config.AZURE_EMBEDDING_DEPLOYMENT,
        openai_api_version=config.AZURE_API_VERSION,
        api_key=config.AZURE_API_KEY
    )

def initialize_collections(embeddings):
    company_collection = Chroma(
        collection_name="company_info_store",
        persist_directory=config.PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    # user_collection = Chroma(
    #     collection_name="user_info_store",
    #     persist_directory=config.PERSIST_DIRECTORY,
    #     embedding_function=embeddings,
    #     collection_metadata={"hnsw:space": "cosine"}
    # )
    
    return company_collection