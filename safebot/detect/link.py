from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse

from safebot.logger import logger

INVITE_HASH_LENGTH = 16

DOMAINS_TG = (
    "t.me",
    "telegram.org",
)
DOMAIN_TG_SHORT = DOMAINS_TG[0]

_ScannerMethods = tuple[[property, bool], ...]


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
        self.path: str = path.lower()

        self._deep_scan: bool = deep_scan
        self._is_tg_shortlink: bool = domain == DOMAIN_TG_SHORT

    @property
    def is_tg_shortlink(self) -> bool:
        """
        Whether the domain belongs to Telegram and it is short.
        """
        return self._is_tg_shortlink

    @property
    def is_bot(self) -> bool:
        """
        Determines whether the bot username is specified in the path.
        """
        return self.path.split("?")[0].endswith("bot")

    @property
    def is_invite_link(self) -> bool:
        """
        Determines whether the path matches the pattern of an invitation link.
        """
        offset = -1

        if 20 > (length := len(self.path)) > 0:
            if self.path[0] == "+":
                offset = 1
            elif self.path[:9] == "joinchat/":
                offset = 9

        return (length - offset) == INVITE_HASH_LENGTH if offset != -1 else False

    def is_references_to(self, username: str) -> bool:
        """
        Determines if the path corresponds to the username.

        :param username: Text user ID.
        """
        return self.path == username.lower()

    def _call_and_check(self, methods: _ScannerMethods) -> bool:
        """
        Invokes each passed method in turn.

        :param methods: Check methods;
        :return: ``True``, if any of the methods return True,
            otherwise ``False``.
        """
        for check in methods:
            if check.fget(self):
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
            checkers.quick if not self._deep_scan else checkers.deep
        )


class Link:
    def __init__(self, url: str, *, deep_scan: bool = False) -> None:
        self.url: str = url
        self.parsed_url: ParseResult = urlparse(url)
        self.scanner: Scanner = Scanner(
            self.parsed_url.netloc,
            self.parsed_url.path[1:100],  # Cut "/"
            deep_scan=deep_scan,
        )

        self._deep_scan: bool = deep_scan
        self._is_safe: bool = False

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
        Whether the link is an invitation.
        """
        return self.scanner.is_tg_shortlink and self.scanner.is_invite_link

    def scan(self) -> bool:
        """
        Scans the link for advertising using the selected scanning mode
        *(quick or deep)*.
        If the link is broken, it will be marked as safe without any scanning.
        If there are no checks for a domain, the link will be marked as unsafe.

        :return: Whether the link is considered unsafe.
        """
        if self._is_broken():
            self._is_safe = True
        elif self.scanner.is_tg_shortlink and self.parsed_url.path != "":
            self._is_safe = not self.scanner.find()

        logger.debug(f"Link scan complete: {self.url=} {self._is_safe=}")
        return not self._is_safe


def _init_scanner_methods() -> None:
    """
    Adds validation methods to the ``Scanner`` corresponding to each domain.
    """
    Scanner.methods = {
        DOMAIN_TG_SHORT: _LinkCheck(
            quick=(
                Scanner.is_bot,
                Scanner.is_invite_link,
            ),
            deep=(),
        ),
    }


def _add_scanner_aliases() -> None:
    """
    Adds aliases to the domains by creating references to the original.
    """
    for service in (DOMAINS_TG,):
        original = service[0]

        for domain in service[1:]:
            Scanner.methods[domain] = Scanner.methods[original]


def init() -> None:
    _init_scanner_methods()
    _add_scanner_aliases()

    logger.info(f"{len(Scanner.methods)} domains added to link scanner")
