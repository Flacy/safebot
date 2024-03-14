from typing import Callable

from pyrogram.enums import MessageEntityType as EntityType
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    MessageEntity,
)

from safebot.detect.filters import Filter
from safebot.detect.link import Link

InlineKeyboardType = list[list[InlineKeyboardButton]]


class Reader:
    def __init__(self, message: Message, *, deep_scan: bool = False) -> None:
        self.message: Message = message
        self.deep_scan: bool = deep_scan

        self.filter: Filter = Filter(message)

        # Naturally, the bot must always have a username,
        # but this protection won't be excessive.
        self._from_username: str = (message.from_user.username or "").lower()
        # Not the most reliable check, but the most optimized one.
        self._is_reply_message: bool = (
            message.reply_to_message is not None
        ) or self._contain_text_mention()

    def _contain_unsafe_inline_button(self) -> bool:
        """
        Scans inline keyboard buttons for any unsafe link.
        """
        for line in self.inline_keyboard:
            for button in line:
                if button.url is None:
                    continue
                elif self._is_unsafe_link(button.url):
                    return True

        return False

    def _contain_text_mention(self) -> bool:
        """
        Checks if there is any text mention in the entities.
        """
        for data in self.message.entities or ():
            if (data.type == EntityType.TEXT_MENTION) or (
                data.type == EntityType.MENTION
            ):
                return True

        return False

    def _is_unsafe_link(self, url: str) -> bool:
        """
        Checks if the link is **unsafe** by running a scanner.
        """
        link = Link(url, deep_scan=self.deep_scan)
        return link.scan() and not self._is_self_reference(link)

    def _is_self_reference(self, link: Link) -> bool:
        """
        Checks if the link references to itself.
        """
        return link.scanner.is_references_to(self.from_username)

    def _scan_entity_url(self, entity: MessageEntity) -> bool:
        return self._is_unsafe_link(self.filter.slice(entity.offset, entity.length))

    def _scan_entity_text_link(self, entity: MessageEntity) -> bool:
        return self._is_unsafe_link(entity.url)

    def _scan_entity_mention(self, entity: MessageEntity) -> bool:
        username = self.filter.slice(entity.offset, entity.length)[1:].lower()
        return username.endswith("bot") and username != self.from_username

    def _scan_entity_text_mention(self, entity: MessageEntity) -> bool:
        return entity.user.is_bot and (entity.user.username != self.from_username)

    @property
    def inline_keyboard(self) -> InlineKeyboardType:
        """
        Returns an inline keyboard if exists, otherwise returns an empty list.
        """
        context_menu = self.message.reply_markup

        if context_menu and isinstance(context_menu, InlineKeyboardMarkup):
            return context_menu.inline_keyboard
        else:
            return []

    @property
    def is_reply_message(self) -> bool:
        """
        Returns the presence of a user mention or a reply,
        thereby determining whether the message is an address or just text.
        """
        return self._is_reply_message

    @property
    def from_username(self) -> str:
        """
        Returns the sender's username.
        """
        return self._from_username

    def scan_entity(self, entity: MessageEntity) -> bool:
        """
        Matches the unsafe entity type with its check method and invokes it.

        :return: Result of scanning, or ``False`` if no suitable method is found.
        """
        method: Callable[[MessageEntity], bool]

        match entity.type:
            case EntityType.URL:
                method = self._scan_entity_url
            case EntityType.TEXT_LINK:
                method = self._scan_entity_text_link
            case EntityType.MENTION:
                method = self._scan_entity_mention
            case EntityType.TEXT_MENTION:
                method = self._scan_entity_text_mention
            case _:
                return False

        return method(entity)

    def secure_filter(self, *, cut_unsafe: bool) -> bool:
        """
        Iterates through potentially unsafe message entities
        (such as links or mentions) and checks for unrelated content.

        The ``cut_unsafe`` argument determines whether to **remove unsafe** content.
        If enabled, the result of the filtering will be available in the
        ``filter`` attribute **after completing** the check for all entities.
        If disabled, it will return **True** upon encountering the first unsafe content.

        :return: Whether unsafe content was found.
        """
        found: bool = False

        for suspicion in self.filter.unsafe_entities:
            if self.scan_entity(suspicion):
                if cut_unsafe:
                    self.filter.make_entity_safe(suspicion)
                else:
                    return True
                if not found:
                    found = True

        return found

    def quick_scan(self) -> bool:
        """
        Performs a superficial check of the message for unsafe links.
        Doesn't conduct in-depth analysis.

        :return: ``True`` if the message contains adv, otherwise ``False``
        """
        return self.secure_filter(cut_unsafe=True)
