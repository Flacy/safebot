from typing import Generator

from pyrogram.enums import MessageEntityType
from pyrogram.types import MessageEntity


def _standardize_url(url: str) -> str:
    """
    Converts (if needed) the URL to a standard web URI (RFC 3986).

    :param url: String URL;
    :return: RFC-compliant URI.
    """
    if ":" not in url:
        return "https://" + url

    return url


def retrieve_urls(
    text: str, entities: list[MessageEntity] | None
) -> Generator[str, None, None]:
    """
    Traverses all entities and filters them by links.

    :param text: Raw message text;
    :param entities: Message entities.
    :return: A generator containing only text links.
    """
    for ent in entities or ():
        if ent.type == MessageEntityType.URL:
            # Telegram can send links without a protocol.
            # This breaks the "urlparse" algorithm,
            # so standardize it to RFC format.
            yield _standardize_url(text[ent.offset:][:ent.length])
        elif ent.type == MessageEntityType.TEXT_LINK:
            yield ent.url
