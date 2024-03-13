from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, InlineKeyboardMarkup

from safebot.detect import filters
from safebot.detect.link import Link


class Reader:
    def __init__(self, message: Message, *, deep_scan: bool = False) -> None:
        self.message: Message = message

        self.deep_scan: bool = deep_scan

    def _contain_reply_markup_link(self) -> bool:
        """
        Scans inline markup for any links.
        """
        if (context_menu := self.message.reply_markup) and isinstance(
            context_menu, InlineKeyboardMarkup
        ):
            if keyboard := context_menu.inline_keyboard:
                for button in keyboard:
                    for data in button:
                        if data.url is not None:
                            # TODO: detailed analyze
                            return True

        return False

    def _is_self_reference(self, link: Link) -> bool:
        """
        Checks if the link references to bot itself.
        """
        user = self.message.forward_from or self.message.from_user
        # Bots shouldn't forward messages,
        # so consider a forwarded message to be from a real user a priori.
        return link.scanner.is_references_to(user.username)

    def _contain_text_link(self) -> bool:
        """
        Scans for unsafe links in the message text.
        """
        for url in filters.retrieve_urls(self.message.text, self.message.entities):
            link = Link(url, deep_scan=self.deep_scan)
            if link.scan() and not self._is_self_reference(link):
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
        for data in self.message.entities or ():
            if data.type == MessageEntityType.TEXT_MENTION:
                # TODO: add comparisons to determine if the user is human or a bot
                return True

        return False

    def scan_link(self) -> bool:
        """
        Scans the message for unsafe links.

        :return: ``True`` if the message contains links, otherwise ``False``
        """
        # TODO: +scan mentions
        return self._contain_reply_markup_link() or self._contain_text_link()

    def quick_scan(self) -> bool:
        """
        Performs a superficial check of the message for unsafe links.
        Doesn't conduct in-depth analysis.

        :return: ``True`` if the message contains adv, otherwise ``False``
        """
        return self.scan_link()
