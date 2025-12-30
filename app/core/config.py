from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DEBUG: bool = True

    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1/"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    RABBITMQ_QUEUE_NAME: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
