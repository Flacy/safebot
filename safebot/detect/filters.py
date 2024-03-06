from pyrogram.enums import MessageEntityType
from pyrogram.types import MessageEntity

from settings import config


def replace_text_links(entities: list[MessageEntity]) -> None:
    """
    Replaces all text links in the entities with a link that leads
    to the ``config.user_id``.
    """
    for data in entities:
        if data.type == MessageEntityType.TEXT_LINK:
            data.url = f"https://t.me/{config.user_id}"
