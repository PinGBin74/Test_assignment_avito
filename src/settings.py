from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = ""
    DB_PORT: int = 0
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DRIVER: str = ""
    DB_NAME: str = ""
    DATABASE_URL: str = ""

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
