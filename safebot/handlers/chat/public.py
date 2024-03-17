from safebot.client import client
from safebot.detect.scan import Reader
from safebot.handlers import database
from safebot.handlers.chat.abc import MessageProtocol
from safebot.handlers.emitter import Emitter
from safebot.logger import logger


class PublicMessage(MessageProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reader: Reader | None = Reader(self.message) if self.from_bot else None

    async def _delete_message(self) -> bool:
        """
        Deletes message and returns status of whether message has been deleted.
        """
        deleted = bool(await client.delete_messages(self.chat_id, self.message_id))
        logger.debug(f"Delete message ({self.message_id=}, {self.chat_id=}): {deleted}")

        return deleted

    async def _event_message_deleted(self, deleted: bool) -> None:
        """
        Event called when a message deletion occurs.

        Checks the **silent mode** status for this chat.
        If it's disabled, send a message with the deletion result.

        :param deleted: Whether the message was deleted.
        """
        if not (await database.is_silent_mode(self.message.chat.id)):
            await Emitter(self.message).send_delete_message(deleted)

    async def _echo_message(self) -> None:
        """
        Sends a message by completely copying the text
        and replacing links with safe ones.
        """
        await client.send_message(
            self.chat_id,
            self.reader.filter.text,
            entities=self.message.entities,
            disable_web_page_preview=True,
        )

    async def process(self) -> None:
        if self.reader and self.reader.quick_scan():
            logger.info(
                f"Advertisement detected during quick scanning ({self.message_id=}, {self.chat_id=})"
            )
            is_deleted = await self._delete_message()

            if is_deleted and self.reader.is_reply_message:
                await self._echo_message()
            else:
                await self._event_message_deleted(is_deleted)
