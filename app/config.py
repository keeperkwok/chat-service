from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-08-01-preview"
    auth_service_url: str = "http://localhost:8002"
    auth_service_introspect_key: str
    app_env: str = "development"
    port: int = 8003


settings = Settings()
