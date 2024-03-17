from typing import Type

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from safebot.client import client
from safebot.handlers.chat.abc import MessageProtocol
from safebot.handlers.chat.private import PrivateMessage
from safebot.handlers.chat.public import PublicMessage
from safebot.logger import logger


@logger.catch
async def _message_handler(_: Client, message: Message) -> None:
    """
    Routes the message to be processed by the appropriate class
    based on the chat type.
    """
    handler: Type[MessageProtocol]
    chat_type = message.chat.type

    if (chat_type == ChatType.SUPERGROUP) or (chat_type == ChatType.GROUP):
        handler = PublicMessage
    elif chat_type == ChatType.PRIVATE:
        handler = PrivateMessage
    else:
        return

    await handler(message).process()


def init() -> None:
    client.add_handler(MessageHandler(_message_handler))

    logger.info("Handlers successfully initialized")
