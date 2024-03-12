from dataclasses import dataclass
from typing import Callable
from urllib.parse import ParseResult, urlparse

from logger import logger

_DOMAINS_TG = (
    "t.me",
    "telegram.org",
)
_DOMAIN_TG_LINK = _DOMAINS_TG[0]

_ScannerMethods = tuple[Callable[["Scanner"], bool], ...]


@dataclass
class _LinkCheck:
    # Quick checks that are not highly resource-intensive
    quick: _ScannerMethods
    # Deep checks that conduct detailed analysis and,
    # accordingly, are more resource-intensive
    deep: _ScannerMethods


class Scanner:
    # For the sake of conciseness, it is updated in the "init" function.
    # Maps a domain to its validation methods.
    methods: dict[str, _LinkCheck]

    def __init__(self, domain: str, path: str, *, deep_scan: bool = False) -> None:
        self.domain: str = domain
        self.path: str = path

        self._deep_scan: bool = deep_scan

    def is_tg_bot(self) -> bool:
        """
        Telegram validation method.

        Determines whether the bot username is specified in the path.
        """
        return self.path.split("?")[0].lower().endswith("bot")

    def is_tg_invite_link(self) -> bool:
        """
        Telegram validation method.

        Determines whether the path matches the pattern of an invitation link.
        """
        if self.path == "":
            return False

        return self.path[0] == "+" or self.path.startswith("joinchat/")

    def _call_and_check(self, methods: _ScannerMethods) -> bool:
        """
        Invokes each passed method in turn.

        :param methods: Check methods;
        :return: ``True``, if any of the methods return True,
            otherwise ``False``.
        """
        for check in methods:
            logger.debug(check(self))
            if check(self):
                return True

        return False

    def find(self) -> bool:
        """
        Performs a series of checks on the specified domain.
        If the domain is not found, it will return True.

        :return: Whether any prohibited content was found in the link.
        """
        if not (checkers := self.methods.get(self.domain)):
            return True

        return self._call_and_check(
            checkers.deep if self._deep_scan else checkers.quick
        )


class Link:
    def __init__(self, url: str, *, deep_scan: bool = False) -> None:
        self.url: str = url
        self.parsed_url: ParseResult = urlparse(url)

        self._deep_scan: bool = deep_scan
        self._is_safe: bool = False

        # Scanner is not designed to handle tg protocol links
        self._scanner: Scanner | None = (
            Scanner(
                self.parsed_url.netloc,
                self.parsed_url.path[1:],  # Cut "/"
                deep_scan=deep_scan,
            )
            if "." in self.parsed_url.netloc
            else None
        )

    def _is_broken(self) -> bool:
        """ "
        Verifies if the link matches the pattern: "tg://openmessage?chat_id=".
        This is ignored as its reliability remains questionable.
        It often (or always?) doesn't work, so we consider it safe.
        Additionally, there is a functional alternative: "tg://user?id="
        """
        return self.parsed_url.scheme == "tg" and self.parsed_url.netloc.startswith(
            "openmessage"
        )

    @property
    def is_safe(self) -> bool:
        """
        Link is considered safe only if it:

        - leads to a user or a channel;
        - is not a link to an external website;
        - is being ignored.
        """
        return self._is_safe

    @property
    def is_invite(self) -> bool:
        """
        Checks if the link is an invitation to join a chat.
        """
        if self._scanner and self.parsed_url.netloc == _DOMAIN_TG_LINK:
            return self._scanner.is_tg_invite_link()

    def scan(self) -> bool:
        """
        Scans the link for advertising using the selected scanning mode
        *(quick or deep)*. If the link is in the ignore list,
        it will be marked as safe without any scanning.
        If there are no checks for a domain, the link will be marked as unsafe.

        :return: Whether the link is considered unsafe.
        """
        if self._is_broken():
            self._is_safe = True
        elif self.parsed_url.path != "":
            self._is_safe = not self._scanner.find()

        logger.debug(f"Link scan complete: {self.url=} {self._is_safe=}")
        return not self._is_safe


def _init_scanner_methods() -> None:
    """
    Adds validation methods to the ``Scanner`` corresponding to each domain.
    """
    Scanner.methods = {
        _DOMAIN_TG_LINK: _LinkCheck(
            quick=(
                Scanner.is_tg_bot,
                Scanner.is_tg_invite_link,
            ),
            deep=(),
        ),
    }


def _add_scanner_aliases() -> None:
    """
    Adds aliases to the domains by creating references to the original.
    """
    for service in (_DOMAINS_TG,):
        original = service[0]

        for domain in service[1:]:
            Scanner.methods[domain] = Scanner.methods[original]


def init() -> None:
    _init_scanner_methods()
    _add_scanner_aliases()

    logger.info(f"{len(Scanner.methods)} domains added to link scanner")
