import os

class Config:
    PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
    OPENAI_MODEL = "gpt-4-turbo-preview"
    EMBEDDING_MODEL = "text-embedding-ada-002"
    TEMPERATURE = 0.2

