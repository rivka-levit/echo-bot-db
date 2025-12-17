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


@router.message(Command('statistics'))
async def process_admin_statistics_command(
        message: Message,
        conn: AsyncConnection,
        i18n: dict[str, str]
):
    """Handles `/statistics` command for users with role `ADMIN`"""

    statistics = await get_statistics(conn)
    await message.answer(
        text=i18n.get('statistics').format(
            '\n'.join(
                f'{i}. <b>{stat[0]}</b>: {stat[1]}'
                for i, stat in enumerate(statistics, 1)
            )
        )
    )


@router.message(Command("ban"))
async def process_ban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str]
) -> None:
    """Handles `/ban` command for users with role `ADMIN`"""

    args = command.args

    if not args:
        await message.reply(text=i18n.get('empty_ban_answer'))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(
            conn,
            user_id=int(arg_user)
        )
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(
            conn,
            username=arg_user[1:]
        )
    else:
        await message.reply(text=i18n.get('incorrect_ban_arg'))
        return

    if banned_status is None:
        await message.reply(text=i18n.get('no_user'))
    elif banned_status:
        await message.reply(text=i18n.get('already_banned'))
    else:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(
                conn,
                banned=True,
                user_id=int(arg_user)
            )
        else:
            await change_user_banned_status_by_username(
                conn,
                banned=True,
                username=arg_user[1:]
            )
        await message.reply(text=i18n.get('successfully_banned'))


@router.message(Command('unban'))
async def process_unban_command(
    message: Message,
    command: CommandObject,
    conn: AsyncConnection,
    i18n: dict[str, str]
) -> None:
    """Handles `/unban` command for users with role `ADMIN`"""

    args = command.args

    if not args:
        await message.reply(i18n.get('empty_unban_answer'))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(
            conn,
            user_id=int(arg_user)
        )
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(
            conn,
            username=arg_user[1:]
        )
    else:
        await message.reply(text=i18n.get('incorrect_unban_arg'))
        return

    if banned_status is None:
        await message.reply(text=i18n.get('no_user'))
    elif banned_status:
        if arg_user.isdigit():
            await change_user_banned_status_by_id(
                conn,
                banned=False,
                user_id=int(arg_user)
            )
        else:
            await change_user_banned_status_by_username(
                conn,
                banned=False,
                username=arg_user[1:]
            )
        await message.reply(text=i18n.get('successfully_unbanned'))

    await message.reply(text=i18n.get('not_banned'))
