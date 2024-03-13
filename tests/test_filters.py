import pytest
from pyrogram.enums import MessageEntityType

from safebot.detect import filters
from tests.dataset import MessageData, TG_URL

_URL_WITHOUT_PROTOCOL = TG_URL.split("://")[1]
_PLACEHOLDER = "test"

# MessageData list with "url" entity type
_MESSAGES_WITH_URL = [
    MessageData.auto(text=TG_URL, expected=[TG_URL]),
    MessageData.auto(text=_URL_WITHOUT_PROTOCOL, expected=[TG_URL]),
    MessageData.auto(text=f"{TG_URL} {_URL_WITHOUT_PROTOCOL}", expected=[TG_URL] * 2),
]
# MessageData list with "text link" entity type
_MESSAGES_WITH_TEXT_LINK = [
    MessageData.auto(text=_PLACEHOLDER, expected=[TG_URL]),
    MessageData.auto(text=f"{_PLACEHOLDER} {_PLACEHOLDER}", expected=[TG_URL] * 2),
]
# Message entities both with "url" and "text link" type
_MESSAGES_COMBINED = [
    _MESSAGES_WITH_URL[0].generate_entities(MessageEntityType.URL)[0],
    _MESSAGES_WITH_TEXT_LINK[0].generate_entities(MessageEntityType.TEXT_LINK)[0],
]


def assert_urls(collection: list[MessageData], t: MessageEntityType) -> None:
    """
    Calls assert on each result of the ``retrieve_urls`` function and compares
    it with the expected result.
    """
    for ent in collection:
        result = filters.retrieve_urls(ent.text, ent.generate_entities(t))
        assert list(result) == ent.expected


def test_retrieve_urls_empty() -> None:
    """
    Should return empty generator if there are no entities.
    """
    assert len(list(filters.retrieve_urls("", None))) == 0


@pytest.mark.parametrize(
    "collection, t",
    [
        (_MESSAGES_WITH_URL, MessageEntityType.URL),
        (_MESSAGES_WITH_TEXT_LINK, MessageEntityType.TEXT_LINK),
    ],
)
def test_retrieve_urls(collection: list[MessageData], t: MessageEntityType) -> None:
    """
    Should be correctly parsed.
    """
    assert_urls(collection, t)


def test_retrieve_urls_combine() -> None:
    """
    Both types of links should be parsed.
    """
    assert list(filters.retrieve_urls(TG_URL, _MESSAGES_COMBINED)) == ([TG_URL] * 2)
