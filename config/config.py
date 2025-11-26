import logging
import os
import sys

from dataclasses import dataclass
from environs import Env
from io import TextIOWrapper

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseConfig:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int
    password: str
    username: str


@dataclass
class LogConfig:
    level: str
    format: str
    stream: TextIOWrapper | None = None


@dataclass
class Config:
    bot: BotConfig
    db: DatabaseConfig
    redis: RedisConfig
    log: LogConfig


def load_config(path: str | None = None) -> Config:
    env = Env()

    if not os.path.exists(path):
        logger.warning(".env file not found at '%s', skipping...", path)
        env.read_env()
    else:
        logger.info("Loading .env from '%s'", path)
        env.read_env(path)

    token = env.str('BOT_TOKEN')
    if not token:
        raise ValueError('BOT_TOKEN must not be empty')

    raw_ids = env.list('ADMIN_IDS', default=[])
    try:
        admin_ids = [int(x) for x in raw_ids]
    except ValueError as e:
        raise ValueError(f"ADMIN_IDS must be integers, got: {raw_ids}") from e

    db = DatabaseConfig(
        name=env.str("POSTGRES_DB"),
        host=env.str("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env.str("POSTGRES_USER"),
        password=env.str("POSTGRES_PASSWORD")
    )

    redis = RedisConfig(
        host=env.str("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        db=env.int("REDIS_DATABASE"),
        password=env.str("REDIS_PASSWORD", default=""),
        username=env.str("REDIS_USERNAME", default="")
    )

    log_settings = LogConfig(
        level=env.str("LOG_LEVEL"),
        format=env.str("LOG_FORMAT"),
        stream=sys.stdout
    )

    logger.info("Configuration loaded successfully")

    return Config(
        bot=BotConfig(token=token, admin_ids=admin_ids),
        db=db,
        redis=redis,
        log=log_settings
    )
