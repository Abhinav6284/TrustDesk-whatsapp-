from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") 

    evolution_url: str = "http://localhost:8080"
    evolution_api_key: SecretStr
    evolution_instance: str = "trustdesk"

settings = Settings()


