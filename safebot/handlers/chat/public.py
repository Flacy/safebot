from safebot.client import client
from safebot.detect import scan, filters
from safebot.handlers.chat.abc import MessageProtocol
from safebot.handlers.emitter import Emitter
from safebot.logger import logger


class PublicMessage(MessageProtocol):
    async def _delete_message(self, force_silent: bool = False) -> None:
        """
        Deletes the message and sends the result of the operation.

        :param force_silent: Forcefully do not send the message.
        """
        deleted = bool(await client.delete_messages(self.chat_id, self.message_id))
        logger.debug(f"Delete message ({self.message_id=}, {self.chat_id=}): {deleted}")

        if not force_silent:
            await Emitter(self.message).send_delete_message(deleted)

    async def _echo_message(self) -> None:
        """
        Sends an echo message, replacing all text links with its own.
        Unsafe method
        """
        filters.replace_text_links(self.message.entities)
        await client.send_message(
            self.chat_id,
            self.message.text,
            entities=self.message.entities,
            disable_web_page_preview=True,
        )

    async def process(self) -> None:
        if self.sender and self.sender.is_bot:
            reader = scan.Reader(self.message)

            if reader.quick_scan():
                logger.debug(f"Found adv in ({self.message_id=}, {self.chat_id=})")

                can_echo = reader.can_echo_message
                await self._delete_message(force_silent=can_echo)

                if can_echo:
                    await self._echo_message()
