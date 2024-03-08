from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from client import client
from detect import scan, filters
from handlers import messages, database
from logger import logger


async def _delete_message(message: Message, force_silent: bool = False) -> None:
    """
    Deletes the message and sends the result of the operation.

    :param message: Input bot message;
    :param force_silent: Forcefully do not send the message.
    """
    deleted = bool(await client.delete_messages(message.chat.id, message.id))
    logger.debug(f"Delete message ({message.id=}, {message.chat.id=}): {deleted}")

    if not force_silent:
        await messages.send_delete_message(message, deleted)


async def _echo_message(message: Message) -> None:
    """
    Sends an echo message, replacing all text links with its own.
    Unsafe method
    """
    filters.replace_text_links(message.entities)
    await client.send_message(message.chat.id, message.text, entities=message.entities, disable_web_page_preview=True)


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
    sender = message.forward_from or message.from_user

    if sender and sender.is_bot:
        reader = scan.Reader(message)

        if reader.quick_scan():
            logger.debug(f"Found adv in ({message}, {message.chat.id=})")

            can_echo = reader.can_echo_message
            await _delete_message(message, force_silent=can_echo)

            if can_echo:
                await _echo_message(message)


def init() -> None:
    client.add_handler(MessageHandler(_message_handler))

    logger.info("Handlers successfully initialized")
