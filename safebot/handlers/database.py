from peewee_async import IntegrityErrors  # noqa

from database.client import manager
from database.models import Chat


async def create_or_skip(chat_id: int) -> None:
    try:
        await manager.create(Chat, t_id=chat_id)
    except IntegrityErrors:
        # Ignore errors if record already exists
        pass


async def is_silent_mode(chat_id: int) -> bool:
    """
    Retrieves silent mode status in the specified chat. Safe method.
    """
    return (await manager.get_or_create(Chat, t_id=chat_id))[0].silent_mode


async def is_echo_mode(chat_id: int) -> bool:
    """
    Retrieves echo mode status in the specified chat. Safe method.
    """
    return (await manager.get_or_create(Chat, t_id=chat_id))[0].echo_mode
