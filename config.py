from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "9a30fe7d5a4861f31dcf00740a2f3b3f1434890bba232f84f71c977d50b77c85")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()