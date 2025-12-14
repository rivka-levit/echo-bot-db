import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from app.bot.enums.roles import UserRole
from app.bot.filters import UserRoleFilter
from app.infrastructure.database.db import (
    change_user_banned_status_by_id,
    change_user_banned_status_by_username,
    get_statistics,
    get_user_banned_status_by_id,
    get_user_banned_status_by_username,
)
from psycopg import AsyncConnection

logger = logging.getLogger(__name__)

router = Router()

router.message.filter(UserRoleFilter(UserRole.ADMIN))


@router.message(Command('help'))
async def process_admin_help_command(message: Message, i18n: dict):
    """Handles `/help` command for users with role `ADMIN`"""

    await message.answer(
        text=i18n.get('/help_admin')
    )
