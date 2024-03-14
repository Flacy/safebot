import abc

from pyrogram.types import Message, User


class MessageProtocol(abc.ABC):
    def __init__(self, message: Message) -> None:
        self.chat_id: int = message.chat.id
        self.message_id: int = message.id
        self.from_bot: bool = message.from_user and message.from_user.is_bot

        self.message: Message = message

    @abc.abstractmethod
    async def process(self) -> None: ...
