from dataclasses import dataclass
from typing import Any

from pyrogram.enums import MessageEntityType
from pyrogram.types import MessageEntity


@dataclass
class MessageData:
    # Telegram values
    text: str
    # Alternative storage to avoid creating multiple "MessageEntity" objects
    positions: list[tuple[int, int]] | None

    # Test values
    expected: Any

    @classmethod
    def auto(cls, *, text: str, expected: Any) -> "MessageData":
        """
        Automatically splits words into start indexes and length.
        """
        i = 0
        pos = []

        for word in text.split():
            pos.append((i, len(word)))
            i += len(word) + 1

        return cls(text=text, positions=pos, expected=expected)

    def generate_entities(self, t: MessageEntityType) -> list[MessageEntity]:
        """
        Generates message entities with the specified type.
        """
        return [
            MessageEntity(
                client=None,
                type=t,
                offset=pos[0],
                length=pos[1],
                url=self.expected[i] if t == MessageEntityType.TEXT_LINK else None,
            )
            for i, pos in enumerate(self.positions)
        ]


TG_URL = "https://t.me"
TG_URL_ALIAS = "https://telegram.org"
