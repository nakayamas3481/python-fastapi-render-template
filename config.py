from pydantic_settings import BaseSettings
from pydantic import AnyUrl, SecretStr

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl
    PRODUCTION: bool
    SUPABASE_URL: AnyUrl
    SUPABASE_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    RESEND_API_KEY: str
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_URL: AnyUrl
   
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
       
settings = Settings()