import logging

import psycopg_pool

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.others import router as others_router
from app.bot.handlers.settings import router as settings_router
from app.bot.handlers.user import router as user_router

from app.bot.i18n.translator import get_translations

from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.i18n import TranslatorMiddleware
from app.bot.middlewares.lang_settings import LangSettingsMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware

from app.infrastructure.database.connection import get_pg_pool

from config import Config
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def main(config: Config) -> None:
    """Initialize the bot and start the bot."""

    logger.info("Starting bot...")

    storage = RedisStorage(
        redis=Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            password=config.redis.password,
            username=config.redis.username,
        )
    )

    #Initialize the bot
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Create connection pool with Postgres
    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password
    )

    # Get translations dictionary
    translations = get_translations()

    # Create locales list from translations dictionary
    locales = list(translations.keys())

    logger.info('Including routers...')
    dp.include_routers(
        settings_router,
        admin_router,
        user_router,
        others_router
    )

    logger.info('Including middlewares...')
    dp.update.middleware(DataBaseMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(ActivityCounterMiddleware())
    dp.update.middleware(LangSettingsMiddleware())
    dp.update.middleware(TranslatorMiddleware())

    # Run polling
    try:
        await dp.start_polling(
            bot, db_pool=db_pool,
            translations=translations,
            locales=locales,
            admin_ids=config.bot.admin_ids
        )
    except Exception as e:
        logger.exception(e)
    finally:
        await db_pool.close()
        logger.info('Connection to Postgres closed')
