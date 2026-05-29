from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chroma_host: str = "localhost"
    chroma_port: int = 8100
    chroma_collection_name: str = "cover_letters"
    embedding_model_name: str = "BAAI/bge-m3"
    openai_api_key: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
