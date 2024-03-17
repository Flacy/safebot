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
REMOVED_TEXT = "**removed**"


class Filter:
    def __init__(self, message: Message) -> None:
        self.message: Message = message

        self.text: str = message.text or message.caption
        self.entities: list[MessageEntity] = (
            message.entities or message.caption_entities or []
        )

        self._entity_shift: int = 0

    def _replace_entity(self, target: MessageEntity) -> None:
        target.type = EntityType.ITALIC
        self.text = self.concat(target.offset, target.length, REMOVED_TEXT)

        target.offset += self._entity_shift
        target.length = len(REMOVED_TEXT)
        self._entity_shift += len(REMOVED_TEXT) - target.length

    def _shift_entity(self, target: MessageEntity) -> None:
        target.offset += self._entity_shift

    def slice(self, offset: int, length: int) -> str:
        return self.text[offset:][:length]  # fmt: skip

    def concat(self, offset: int, length: int, data: str) -> str:
        return self.text[:offset] + data + self.text[offset + length :]

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
                self._shift_entity(ent)
                yield ent

    # noinspection PyMethodMayBeStatic
    def make_entity_safe(self, entity: MessageEntity) -> None:
        match entity.type:
            case EntityType.URL:
                self._replace_entity(entity)
            case EntityType.TEXT_LINK:
                self._replace_entity(entity)
                entity.url = None
            case EntityType.MENTION:
                self._replace_entity(entity)
            case EntityType.TEXT_MENTION:
                entity.user = self.message.from_user
            case _:
                raise ValueError(f"Unsupported entity type: {entity.type}")


def _standardize_url(url: str) -> str:
    """
    Converts (if needed) the URL to a standard web URI (RFC 3986).

    :param url: String URL;
    :return: RFC-compliant URI.
    """
    if "://" not in url:
        return "https://" + url

    return url
