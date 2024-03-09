from typing import Protocol

from pyrogram.types import Message, User


class MessageProtocol(Protocol):
    def __init__(self, message: Message) -> None:
        self.chat_id: int = message.chat.id
        self.message_id: int = message.id
        self.sender: User | None = message.forward_from or message.from_user

        self.message: Message = message

    async def process(self) -> None: ...
