from pydantic import BaseModel
from pydantic_settings import BaseSettings


class MySQLConfig(BaseModel):
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "password"
    db: str = "test_db"


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    WS_PREFIX: str = "/ws"
    SENRTY_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    MYSQL: MySQLConfig = MySQLConfig()
    Q_ACCOUNT: str = ""
    Q_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


settings = Settings()
