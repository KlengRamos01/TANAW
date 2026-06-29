from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    openai_api_key: str = ""
    opencode_api_key: str = ""
    gemini_api_key: str = ""
    weather_api_key: str = ""
    pagasa_api_key: str = ""
    app_env: str = "development"
    secret_key: str = ""

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
