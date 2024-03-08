from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, InlineKeyboardMarkup, MessageEntity

from detect.link import Link


class Reader:
    def __init__(self, message: Message, *, deep_scan: bool = False) -> None:
        self.message: Message = message
        self._entities = message.entities or ()

        self.deep_scan: bool = deep_scan

    def _has_adv_entity(self, entity: MessageEntity) -> bool:
        """
        Checks message entity for bad links.

        :param entity: Telegram message entity.
        :return: Whether entity contains a bad link.
        """
        if entity.type == MessageEntityType.TEXT_LINK:
            return Link(entity.url, deep_scan=self.deep_scan).scan()

        return False

    def _contain_reply_markup_link(self) -> bool:
        """
        Scans inline markup for any links.
        """
        if (context_menu := self.message.reply_markup) and isinstance(context_menu, InlineKeyboardMarkup):
            if keyboard := context_menu.inline_keyboard:
                for button in keyboard:
                    for data in button:
                        if data.url is not None:
                            return True

        return False

    def _contain_text_link(self) -> bool:
        """
        Scans any links in the message text.

        :return: Whether the message contains bad links.
        """
        for ent in self._entities:
            if self._has_adv_entity(ent):
                return True

        return False

    @property
    def can_echo_message(self) -> bool:
        """
        Checks for the presence of a user mention,
        thereby determining whether the message is an address or just text.

        :return: ``True`` if the message contains a mention, otherwise ``False``
        """
        return self.contain_text_mention()

    def contain_text_mention(self) -> bool:
        """
        Checks if there is any text mention in the entities.
        """
        for data in self._entities:
            if data.type == MessageEntityType.TEXT_MENTION:
                # TODO: add comparisons to determine if the user is human or a bot
                return True

        return False

    def scan_link(self) -> bool:
        """
        Scans the message for any links.

        :return: ``True`` if the message contains links, otherwise ``False``
        """
        # TODO: +scan mentions
        return self._contain_reply_markup_link() or self._contain_text_link()

    def quick_scan(self) -> bool:
        """
        Performs a superficial check of the message for links.
        Doesn't conduct in-depth analysis.

        :return: ``True`` if the message contains adv, otherwise ``False``
        """
        return self.scan_link()
