from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
import streamlit as st
from shared import config
from apps.utils.stage_logger import stage_log

@stage_log(stage=1)
@st.cache_resource
def initialize_llm_azure():
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

@stage_log(stage=2)
@st.cache_resource
def initialize_embeddings_azure():
    return AzureOpenAIEmbeddings(
        azure_endpoint=config.AZURE_ENDPOINT,
        azure_deployment=config.AZURE_EMBEDDING_DEPLOYMENT,
        openai_api_version=config.AZURE_API_VERSION,
        api_key=config.AZURE_API_KEY
    )

@stage_log(stage=2)
@st.cache_resource
def initialize_llm_llama():
    return ChatOllama(
        model="llama3.1",
        base_url="13.201.59.104:11434",
        temperature=0.1
    )

@stage_log(stage=2)
@st.cache_resource
def initialize_llm_phi():
    return ChatOllama(
        model="phi3.5",
        base_url="13.201.59.104:11434",
        temperature=0.1
    )

@stage_log(stage=2)
@st.cache_resource
def initialize_llm_mistral():
    return ChatOllama(
        model="mistral",
        base_url="13.201.59.104:11434",
        temperature=0.1
    )

@stage_log(stage=2)
@st.cache_resource
def initialize_llm_deepseek():
    return ChatOllama(
        model="deepseek-r1",
        base_url="13.201.59.104:11434",
        temperature=0.0
    )

@stage_log(stage=2)
@st.cache_resource
def initialize_embeddings_ollama():
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="13.201.59.104:11434"
    )