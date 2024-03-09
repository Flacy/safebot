from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from client import client
from handlers import sender, database
from handlers.chat.abc import MessageProtocol
from handlers.chat.private import PrivateMessage
from handlers.chat.public import PublicMessage
from logger import logger


@logger.catch
async def _message_handler(_: Client, message: Message) -> None:
    """
    Performs a quick scan of messages from bots for any links and proceeds
    with further processing logic.

    Quick scan implies a superficial scanning of links that contains in a message.
    If any link is found in the message, it is deleted.
    If echo mode is enabled in the chat, the message will be sent on behalf
    of the application with all links replaced.

    If echo mode is enabled, silent mode will be applied forcibly.
    """
    handler: MessageProtocol
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
