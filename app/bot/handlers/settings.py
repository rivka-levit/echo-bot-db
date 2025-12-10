"""
Handlers for user's settings of the bot.
"""

import logging

from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.enums import BotCommandScopeType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, CallbackQuery, Message

from app.bot.filters.filters import LocaleFilter
from app.bot.keyboards.keyboards import get_lang_settings_kb
from app.bot.keyboards.menu_button import get_main_menu_commands
from app.bot.states.states import LangSG
from app.infrastructure.database.db import (
    get_user_lang,
    get_user_role,
    update_user_lang,
)

from psycopg import AsyncConnection

logger = logging.getLogger(__name__)

router = Router()


@router.message(StateFilter(LangSG.lang), ~CommandStart())
async def process_any_message_when_lang(
    message: Message,
    bot: Bot,
    i18n: dict[str, str],
    state: FSMContext,
    locales: list[str],
):
    """Works with any message except command `/start` in lang choice state."""

    user_id = message.from_user.id
    data = await state.get_data()
    user_lang = data.get("user_lang")

    with suppress(TelegramBadRequest):
        msg_id = data.get("lang_settings_msg_id")
        if msg_id:
            await bot.edit_message_reply_markup(chat_id=user_id, message_id=msg_id)

    msg = await message.answer(
        text=i18n.get("/lang"),
        reply_markup=get_lang_settings_kb(i18n=i18n, locales=locales, checked=user_lang),
    )

    await state.update_data(lang_settings_msg_id=msg.message_id)


@router.message(Command(commands=['lang']))
async def process_lang_command(
    message: Message,
    conn: AsyncConnection,
    i18n: dict[str, str],
    state: FSMContext,
    locales: list[str],
):
    """Handles command `/lang`."""

    await state.set_state(LangSG.lang)
    user_lang = await get_user_lang(conn, user_id=message.from_user.id)

    msg = await message.answer(
        text=i18n.get("/lang"),
        reply_markup=get_lang_settings_kb(
            i18n=i18n, locales=locales, checked=user_lang
        )
    )

    await state.update_data(
        lang_settings_msg_id=msg.message_id,
        user_lang=user_lang
    )
