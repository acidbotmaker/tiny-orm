from pydantic_settings import BaseSettings, SettingsConfigDict


# collecting connection data from environment variables
class Settings(BaseSettings):
    model_config = SettingsConfigDict(validation_default=False)

    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str


# instantiate settings at module load time.
db_settings = Settings()
