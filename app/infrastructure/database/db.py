import logging
from datetime import datetime, timezone
from typing import Any

from app.bot.enums.roles import UserRole
from psycopg import AsyncConnection

logger = logging.getLogger(__name__)


async def add_user(
    conn: AsyncConnection,
    *,
    user_id: int,
    username: str | None = None,
    language: str = "ru",
    role: UserRole = UserRole.USER,
    is_alive: bool = True,
    banned: bool = False,
) -> None:
    """Add a new user to the database."""

    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                  INSERT INTO users(user_id, username, language, role, is_alive, banned)
                  VALUES (%(user_id)s,
                          %(username)s,
                          %(language)s,
                          %(role)s,
                          %(is_alive)s,
                          %(banned)s)
                  ON CONFLICT DO NOTHING;
                  """,
            params={
                "user_id": user_id,
                "username": username,
                "language": language,
                "role": role,
                "is_alive": is_alive,
                "banned": banned,
            },
        )
        logger.info(
            "User added. Table=`%s`, user_id=%d, created_at='%s', "
            "language='%s', role=%s, is_alive=%s, banned=%s",
            "users",
            user_id,
            datetime.now(timezone.utc),
            language,
            role,
            is_alive,
            banned,
        )
