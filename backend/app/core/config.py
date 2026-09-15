from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./app/.env")

    APP_NAME: str = "ATS Backend"
    DATABASE_URL: str

    JWT_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480


settings = Settings()