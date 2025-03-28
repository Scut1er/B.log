from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_URL: str

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_SENDER: str
    SMTP_PASSWORD: str

    VERIFICATION_TOKEN_EXPIRE_TIME_MINUTES: str

    ACCESS_TOKEN_EXPIRE_TIME_MINUTES: str
    ACCESS_PRIVATE_KEY: str
    ACCESS_PUBLIC_KEY: str
    PREVIOUS_ACCESS_PUBLIC_KEY: str

    REFRESH_TOKEN_EXPIRE_TIME_MINUTES: str
    REFRESH_PRIVATE_KEY: str
    REFRESH_PUBLIC_KEY: str
    PREVIOUS_REFRESH_PUBLIC_KEY: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=(".env", ".env.keys", ".env.oauth"))


settings = Settings()
