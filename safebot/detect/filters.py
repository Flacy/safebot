from typing import Generator

from pyrogram.enums import MessageEntityType as EntityType
from pyrogram.types import MessageEntity, Message

from safebot.handlers.emitter import Emitter
from safebot.settings import config

# Potentially entities where unsafe content MAY be contained.
UNSAFE_ENTITIES = (
    EntityType.URL,
    EntityType.TEXT_LINK,
    EntityType.MENTION,
    EntityType.TEXT_MENTION,
)

# URL used as a replacement for unsafe links.
SAFE_URL = f"https://t.me/{config.username}"
# Localization key used to retrieve text to replace unsafe content.
LOCALE_REPLACE_ENTITY = "cut_unsafe"


class Filter:
    def __init__(self, message: Message) -> None:
        self.message: Message = message

        self.text: str = message.text or message.caption
        self.entities: list[MessageEntity] = (
            message.entities or message.caption_entities or []
        )

        # Offset relative to the previous entity.
        # Used for correct replacement of entity positions.
        self._entity_shift: int = 0

    def _replace_entity(self, target: MessageEntity) -> None:
        """
        Replaces the entity text (using ``LOCAL_REPLACE_ENTITY``),
        updating its formatting and length.
        Applies the ``_entity_shift`` offset, which needs to be
        added/subtracted for the next entity.
        """
        # Retrieve the text that we will insert instead.
        locale = Emitter.prepare_text(LOCALE_REPLACE_ENTITY)

        # Change formatting.
        target.type = EntityType.ITALIC
        # Trim the text on both sides and inserts the obtained localization.
        self.text = self.replace(target.offset, target.length, locale)

        # Update the shift to the next entity.
        # This can be either a positive or negative value.
        # Fortunately, Python automatically decrements the variable
        # if the value turns out to be negative.
        self._entity_shift += len(locale) - target.length
        # Finally, update the length of the entity itself.
        target.length = len(locale)

    def _shift_entity(self, target: MessageEntity) -> None:
        """
        Applies the current shift to the entity offset.
        """
        target.offset += self._entity_shift

    def slice(self, offset: int, length: int) -> str:
        """
        Gets a slice of text using the offset and length.
        """
        return self.text[offset:][:length]  # fmt: skip

    def replace(self, offset: int, length: int, data: str) -> str:
        """
        Cuts out the specified segment and inserts the provided data in its place.
        """
        return self.text[:offset] + data + self.text[offset + length:]  # fmt: skip

    @property
    def first_url(self) -> str | None:
        """
        First link encountered in the entities.
        """
        for ent in self.entities:
            if ent.type == EntityType.URL:
                # Telegram can send links without a protocol.
                # This breaks the "urlparse" algorithm, so standardize it to RFC format.
                return _standardize_url(self.slice(ent.offset, ent.length))
            elif ent.type == EntityType.TEXT_LINK:
                return ent.url

    @property
    def unsafe_entities(self) -> Generator[MessageEntity, bool, None]:
        """
        Generator that iterates through potentially unsafe entities.
        """
        for ent in self.entities:
            if ent.type in UNSAFE_ENTITIES:
                # Shift the entity's offset before yielding to ensure proper replacement.
                # This is safe, as if the shift is 0, nothing will change.
                self._shift_entity(ent)
                yield ent

    def make_entity_safe(self, entity: MessageEntity) -> None:
        """
        Ensures the entity is safe by replacing its content.
        Only available for entities of type:
        **URL**, **TEXT_LINK**, **MENTION**, **TEXT_MENTION**.

        :raise ValueError: If the type of entity isn't listed.
        """
        match entity.type:
            case EntityType.TEXT_LINK:
                self._replace_entity(entity)
                # Since the entity is being replaced,
                # it means that the link is no longer there.
                entity.url = None  # type: ignore
            case EntityType.TEXT_MENTION:
                # Sometimes, TEXT_LINK is present along with TEXT_MENTION.
                # In any case, if we replace the user, it will not lead to
                # any negative consequences (thanks, Pavel Durov <3)
                entity.user = self.message.from_user
            case EntityType.URL | EntityType.MENTION:
                # Replace the text, as removing it would be too costly.
                self._replace_entity(entity)
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
