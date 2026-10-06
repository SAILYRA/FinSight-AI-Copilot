import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinSight AI"
    VERSION: str = "1.0.0"
    
    # Base paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR: str = Field(default_factory=lambda: os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data"))
    PDF_DIR: str = Field(default_factory=lambda: os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data", "pdfs"))
    DATABASE_PATH: str = Field(default_factory=lambda: os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data", "sales_data.db"))
    CHROMA_PERSIST_DIR: str = Field(default_factory=lambda: os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data", "chroma_db"))
    
    # LLM Settings
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    TEMPERATURE: float = 0.0
    
    # RAG Settings
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    DENSE_WEIGHT: float = 0.6
    SPARSE_WEIGHT: float = 0.4
    TOP_K: int = 4

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
