from yaml import safe_load
from functools import lru_cache
from pydantic import BaseModel, SecretStr, PostgresDsn, RedisDsn
from typing import Any, Dict, Optional

class Bot(BaseModel):
    token: SecretStr
    max_connections: int
    local_api: bool
    local_base: Optional[str]

class Coomer(BaseModel):
    url: str
    backup_url: str
    proxy: SecretStr

class Postgres(BaseModel):
    user: str
    password: SecretStr
    name: str
    host: str
    port: int

    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.name
        )

class Redis(BaseModel):
    dsn: RedisDsn
    max_connections: int

class Database(BaseModel):
    postgres: Postgres
    redis: Redis

class Config(BaseModel):
    bot: Bot
    coomer: Coomer
    database: Database
    logging: Dict[str, Any]

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(file=path, mode="r", encoding="utf-8") as file:
            data = safe_load(stream=file)
        return cls.model_validate(obj=data)

@lru_cache(maxsize=1)
def get_config(path: str = "bot/config.yaml") -> Config:
    return Config.from_yaml(path=path)

config: Config = get_config()
