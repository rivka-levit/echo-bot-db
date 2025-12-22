import logging

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    """Extract and pass connection."""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        """
        Extract pool of connections from `workflow_data`, get one
        connection from this pool, open a transaction and put the connection
        to `workflow_data`.
        """

        db_pool: AsyncConnectionPool = data.get('db_pool')
        if db_pool is None:
            logger.error('Database pool is not provided in middleware data.')
            raise RuntimeError('Missing db_pool in middleware context.')

        async with db_pool.connection() as connection:
            try:
                data['conn'] = connection
                result = await handler(event, data)
            except Exception as e:
                logger.error('Transaction rolled back due to error: %s', e)
                raise

        # Some code for the case the transaction was completed successfully.

        return result
