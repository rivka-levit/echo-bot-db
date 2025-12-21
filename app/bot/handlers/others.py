from aiogram import Router
from aiogram.types import Message
from psycopg import AsyncConnection

router = Router()


@router.message()
async def send_echo(message: Message, conn: AsyncConnection, i18n: dict):
    """Handles all the updates not caught by other handlers"""

    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=i18n.get("no_echo"))
