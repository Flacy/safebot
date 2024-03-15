from typing import Generator

from pyrogram.enums import MessageEntityType as EntityType
from pyrogram.types import MessageEntity, Message

from safebot.settings import config

UNSAFE_ENTITIES = (
    EntityType.URL,
    EntityType.TEXT_LINK,
    EntityType.MENTION,
    EntityType.TEXT_MENTION,
)

SAFE_URL = f"https://t.me/{config.user_id}"


class Filter:
    def __init__(self, message: Message) -> None:
        self.message: Message = message

        self.text: str = message.text
        self.entities: list[MessageEntity] = message.entities or message.caption_entities or []

    def _delete_entity(self, target: MessageEntity) -> None:
        for i, ent in enumerate(self.entities):
            if ent == target:
                del self.entities[i]
                break

    def slice(self, offset: int, length: int) -> str:
        return self.text[offset:][:length]  # fmt: skip

    @property
    def first_url(self) -> str | None:
        for ent in self.entities:
            if ent.type == EntityType.URL:
                return _standardize_url(self.slice(ent.offset, ent.length))
            elif ent.type == EntityType.TEXT_LINK:
                return ent.url

    @property
    def unsafe_entities(self) -> Generator[MessageEntity, bool, None]:
        for ent in self.entities:
            if ent.type in UNSAFE_ENTITIES:
                yield ent

    # noinspection PyMethodMayBeStatic
    def make_entity_safe(self, entity: MessageEntity) -> None:
        match entity.type:
            case EntityType.URL:
                pass  # TODO
            case EntityType.TEXT_LINK:
                entity.url = SAFE_URL
            case EntityType.MENTION:
                pass  # TODO
            case EntityType.TEXT_MENTION:
                pass  # TODO


def _standardize_url(url: str) -> str:
    """
    Converts (if needed) the URL to a standard web URI (RFC 3986).

    :param url: String URL;
    :return: RFC-compliant URI.
    """
    if "://" not in url:
        return "https://" + url

    return url
