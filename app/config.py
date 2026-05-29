from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chroma_collection_name: str = "cover_letters"
    chroma_path: str = ""  # 비워두면 프로젝트 루트의 chroma_db 폴더 자동 사용
    embedding_model_name: str = "BAAI/bge-m3"
    openrouter_api_key: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
