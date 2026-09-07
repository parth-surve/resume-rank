from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./app/.env")

    APP_NAME: str = "ATS Backend"
    # ... your other fields with sensible defaults
    DATABASE_URL: str 
    
    
settings = Settings()