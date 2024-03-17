from math import ceil
from typing import Dict, Any

from pyrogram.errors import (
    FloodWait,
    InviteHashExpired,
    UserAlreadyParticipant,
)
from pyrogram.types import Chat

from safebot.client import client
from safebot.detect.filters import Filter
from safebot.detect.link import Link
from safebot.handlers import database
from safebot.handlers.chat.abc import MessageProtocol
from safebot.handlers.emitter import Emitter
from safebot.logger import logger


class PrivateMessage(MessageProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._url: str | None = Filter(self.message).first_url
        self._emit: Emitter = Emitter(self.message)

    async def _is_already_in_chat(self) -> bool:
        """
        Checks for the presence in the chat (using an invitation link)
        by sending a request to Telegram.
        """
        chat = await client.get_chat(self._url)
        # If we are in the chat, an instance of `Chat` will be returned.
        # Otherwise, `ChatPreview` is returned.
        return isinstance(chat, Chat)

    async def _join_chat(self) -> Chat | None:
        """
        Attempts to join the chat using the invitation link.
        If successful, it returns a ``Chat`` object.
        If, for some reason, joining the chat is unsuccessful,
        a message with the error description is sent to the user.

        Note: Exceptions are handled only if we're **already in the chat**,
        **the link is invalid**, or we're temporary **restricted by Telegram**.
        """
        fmt: Dict[str, Any] = {}

        try:
            if await self._is_already_in_chat():
                # Doing this to protect ourselves from unnecessary failed requests.
                # This helps reduce the likelihood of temporary restrictions.
                raise UserAlreadyParticipant()

            return await client.join_chat(self._url)
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
            self._url
            and Link(self._url).is_invite
            and (chat := await self._join_chat())
        ):
            await database.create_or_skip(chat.id)
            logger.info(f"Joined the chat: {chat.title} ({chat.id=})")
