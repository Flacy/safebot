from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, InlineKeyboardMarkup, MessageEntity


def _contain_reply_markup_link(message: Message) -> bool:
    """
    Scans inline markup for any links.
    """
    if (context_menu := message.reply_markup) and isinstance(context_menu, InlineKeyboardMarkup):
        if keyboard := context_menu.inline_keyboard:
            for button in keyboard:
                for data in button:
                    if data.url is not None:
                        return True

    return False


def _contain_text_link(message: Message) -> bool:
    """
    Scans any links in the message text.
    """
    if entities := message.entities:
        for data in entities:
            if data.type == MessageEntityType.TEXT_LINK:
                return True

    return False


def contain_text_mention(entities: list[MessageEntity]) -> bool:
    """
    Checks if there is any text mention in the entities.
    """
    for data in entities:
        if data.type == MessageEntityType.TEXT_MENTION:
            return True


def scan_link(message: Message) -> bool:
    """
    Scans the message for any links.

    :return: ``True`` if the message contains links, otherwise ``False``
    """
    return _contain_reply_markup_link(message) or _contain_text_link(message)


def quick_scan(message: Message) -> bool:
    """
    Performs a superficial check of the message for links.
    Doesn't conduct in-depth analysis.

    :return: ``True`` if the message contains adv, otherwise ``False``
    """
    return scan_link(message)
