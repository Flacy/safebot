from math import ceil
from typing import Dict, Any

from pyrogram.errors import (
    FloodWait,
    InviteHashExpired,
    UserAlreadyParticipant,
)
from pyrogram.types import Chat

from safebot.client import client
from safebot.detect import filters
from safebot.detect.link import Link
from safebot.handlers import database
from safebot.handlers.chat.abc import MessageProtocol
from safebot.handlers.emitter import Emitter
from safebot.logger import logger


class PrivateMessage(MessageProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._emit: Emitter = Emitter(self.message)

    def _retrieve_invite_link(self) -> str | None:
        """
        Retrieves the first link from the message entities.

        :return: Text link, if found
        """
        for url in filters.retrieve_urls(self.message.text, self.message.entities):
            return url

    async def _join_chat(self, url: str) -> Chat | None:
        """
        Enters the chat through the provided link.
        If unsuccessful, a response message will be sent with a description
        of the error.

        :param url: Text link.
        :return: On success a ``Chat`` object.
        """
        fmt: Dict[str, Any] = {}

        try:
            return await client.join_chat(url)
        except UserAlreadyParticipant:
            locale_key = "already_in_chat"
        except InviteHashExpired:
            # Actually, this error occurs not only when the link is invalid.
            # It also happens if the bot failed to enter the chat due to some problem.
            # For example, if it's banned from the chat.
            locale_key = "invite_link_expired"
        except FloodWait as e:
            # This happens when we entered or attempted to enter a chat too frequently.
            # Normally, the cooldown lasts form 5 to 20 minutes,
            # so we explicitly inform that everything is fine,
            # just a temporary restriction is in place.
            locale_key = "error_flood"
            fmt["minutes"] = ceil(e.value / 60)

        # Raise any other errors.
        # It's not necessary for the user to know about an unknown error.
        # But it will be very helpful for debugging.

        await self._emit.send(locale_key, **fmt)

    async def process(self) -> None:
        """
        Scan the message for a link (only the first found is taken),
        and checks it for compliance with an invitation link.
        If it's an invitation, attempt to enter the chat.
        Otherwise, the message is skipped.

        Private chat simultaneously serves as feedback, so we don't send any
        unnecessary information.
        """
        if (
            (url := self._retrieve_invite_link())
            and Link(url).scanner.is_invite_link
            and (chat := await self._join_chat(url))
        ):
            await database.create_or_skip(chat.id)
            logger.info(f"Joined the chat: {chat.title} ({chat.id=})")
