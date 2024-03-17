from plate import Plate
from pyrogram.types import Message

from safebot.client import client
from safebot.logger import logger


class Emitter:
    localizator: Plate

    def __init__(self, message: Message) -> None:
        self.message: Message = message

    def prepare_text(self, key: str, **kwargs) -> str:
        """
        Retrieves a text from the locale's dictionary using the specified key.

        :param key: Locale key;
        :param kwargs: Named arguments to interpolate text.
        :return: Localized text
        """
        # TODO: one language is temporarily solution.
        return self.localizator(key, "en_US", **kwargs)

    async def send(self, key: str, *, reply: bool = False, **fmt) -> None:
        """
        Sends a message with the localized text to the chat.

        :param key: Locale key;
        :param reply: Whether this message will be a reply;
        :param fmt: Named arguments to interpolate text.
        """
        await client.send_message(
            self.message.chat.id,
            self.prepare_text(key, **fmt),
            reply_to_message_id=self.message.id if reply else None,  # type: ignore
        )

    async def send_delete_message(self, deleted: bool) -> None:
        """
        Sends a different info message based on the ``deleted`` argument.

        :param deleted: Whether the message was deleted.
        """
        if deleted:
            await self.send("message_deleted", mention=self.message.from_user.mention)
        else:
            await self.send("not_enough_rights", reply=True)


def _decode_plate_exception(exc: ValueError) -> str:
    """
    Since Plate doesn't have its own exceptions,
    it is necessary to check for the specific type of error for proper information.

    Essentially, this method only formats the error text,
    which contains all supported language codes (others will be returned unchanged).
    This error occurs when a file with an incorrect code appears in locales directory.

    :param exc: Plate exception.
    :return: Formatted to string error text.
    """
    # We know that the description of the error comes before the sentence starting
    # with "Possible" (method: Plate._check_valid_locale)
    return (t := str(exc))[: i - 1 if (i := t.find("Possible")) != -1 else None]


def _init_localizator() -> None:
    try:
        Emitter.localizator = Plate()
    except ValueError as e:
        logger.critical(f"Unable to load locales: {_decode_plate_exception(e)}")
        exit(1)


def init() -> None:
    _init_localizator()

    language_codes = Emitter.localizator.locales.keys()
    logger.info(
        f"{len(language_codes)} locales initialized: ({', '.join(language_codes)})"
    )
