import json
from pathlib import Path
from random import sample

from pyrogram.types import Message

from client import client
from handlers import database
from logger import logger


class Emitter:
    locales: dict[str, dict[str, list[str]]] = {}

    def __init__(self, message: Message) -> None:
        self.message: Message = message

    def _get_text(self, lang_code: str, key: str) -> str:
        """
        Retrieves random locale from the locale's dictionary
        using the specified key and language code.
        If the language code is not found, "en" will be used.

        :param lang_code: Two-letter language code
        :param key: Locale key
        :return: Locale text
        """
        loc = self.locales.get(lang_code, self.locales.get("en"))
        return sample(loc[key], 1)[0]  # type: ignore

    async def send(
        self,
        key: str,
        *,
        reply: bool = False,
        **fmt,
    ) -> None:
        """
        Sends a message with the localized text to the chat.

        :param key: Locale key;
        :param reply: Whether this message will be a reply;
        """
        text = self._get_text(self.message.from_user.language_code, key)
        if fmt:
            text = text.format(**fmt)

        await client.send_message(
            self.message.chat.id,
            text,
            reply_to_message_id=self.message.id if reply else None,
        )

    async def send_delete_message(self, deleted: bool) -> None:
        """
        Checks the chat for silent mode.
        If it is disabled, then send a message about the result of the operation.

        :param deleted: Whether the message was deleted.
        """
        if not (await database.is_silent_mode(self.message.chat.id)):
            if deleted:
                await self.send(
                    "message_deleted", mention=self.message.from_user.mention
                )
            else:
                await self.send("not_enough_rights", reply=True)


def __load_locales() -> int:
    """
    Loads localization files (stored in "locales" and are of type json)
    into ``Emitter.locales``.

    :return: Count of successfully loaded locales
    """
    count = 0

    for file in Path("locales").glob("*.json"):
        code = file.name[:2]

        try:
            with file.open() as f:
                Emitter.locales[code] = json.load(f)

            logger.debug(f"Locale '{code}' loaded")
            count += 1
        except Exception as e:
            logger.error(f"Locale '{code}' was failed to load: {e}")

    return count


def init() -> None:
    logger.info(f"{__load_locales()} locales initialized")
