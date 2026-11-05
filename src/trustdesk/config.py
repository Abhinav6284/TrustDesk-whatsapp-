from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") 

    evolution_url: str = "http://localhost:8080"
    evolution_api_key: SecretStr
    evolution_instance: str = "trustdesk"

    meta_access_token : SecretStr
    meta_phone_number_id : str
    meta_app_secret : SecretStr
    meta_verify_token : SecretStr
    meta_api_version : str = "v23.0"
    meta_allowed_numbers : str = ""
    

settings = Settings()


