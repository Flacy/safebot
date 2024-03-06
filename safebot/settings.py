from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    # Variable responsible for determining the mode in which app will be launched.
    # When enabled, all debug information will be hidden.
    production: bool = False
    user_id: str

    # Telegram data
    api_id: int
    api_hash: str
    phone_number: str

    # Database
    postgres_host: str
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str


config = _Settings()
