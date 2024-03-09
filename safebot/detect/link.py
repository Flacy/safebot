from dataclasses import dataclass
from typing import Callable

from logger import logger

_DOMAIN_TG = "t.me"

_DOMAIN_ALIASES: dict[str, tuple[str]] = {
    _DOMAIN_TG: ("telegram.org",),
}
_SAFE_DEEP_LINKS: dict[str, tuple[str]] = {
    "tg": (
        # Some developers use this path to create a link to the chat.
        # Its functionality is often unclear, and it frequently doesn't work.
        # However, it is considered to be safe, as there is a specific path
        # for chat links: "tg://user?id="
        "openmessage",
    ),
}

_ScannerMethods = list[Callable]


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

        :return: Result indicating whether the link is a bot link.
        """
        return self.path.split("?")[0].lower().endswith("bot")

    def _call_and_check(self, methods: _ScannerMethods) -> bool:
        """
        Invokes each passed method in turn.

        :param methods:
        :return: ``True``, if any of the methods return True,
            otherwise ``False``.
        """
        for check in methods:
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
    def __init__(self, url: str, *, deep_scan: bool = False):
        self.url: str = url
        self.protocol: str = ""
        self.domain: str = ""
        self.path: str = ""

        self._deep_scan: bool = deep_scan
        self._is_safe: bool = False

        self._parse()

    def _parse(self) -> None:
        """
        Parses the link into protocol, domain, and path.
        """
        if "://" in self.url:
            self.protocol, self.domain = self.url.split("://", 1)
        else:
            self.domain = self.url

        if "/" in self.domain:
            self.domain, self.path = self.domain.split("/", 1)

    def _is_ignore(self) -> bool:
        """
        Checks for the presence of the protocol in safe deep links.
        If the protocol is found, then it checks for the inclusion of
        the domain (in deep links, this is the path) as a safe one.

        :return: Is the link in the ignored list.
        """
        for path in _SAFE_DEEP_LINKS.get(self.protocol, ()):
            if self.domain.startswith(path):
                return True

        return False

    @property
    def is_safe(self) -> bool:
        return self._is_safe

    def scan(self) -> bool:
        """
        Scans the link for advertising using the selected scanning mode
        *(quick or deep)*. If the link is in the ignore list,
        it will be marked as safe without any scanning.
        If there are no checks for a domain, the link will be marked as unsafe.

        :return: Whether the link is considered unsafe.
        """
        if self._is_ignore():
            self._is_safe = True
        elif self.domain in _DOMAIN_ALIASES:
            self._is_safe = not Scanner(
                self.domain, self.path, deep_scan=self._deep_scan
            ).find()

        logger.debug(f"Link scan complete: {self.url=} {self._is_safe=}")
        return not self._is_safe


def _init_scanner_methods() -> None:
    """
    Adds validation methods to the ``Scanner`` corresponding to each domain.
    """
    Scanner.methods = {
        _DOMAIN_TG: _LinkCheck(
            quick=[Scanner.is_tg_bot],
            deep=[],
        ),
    }


def _add_scanner_aliases() -> None:
    """
    Adds aliases to the domains by creating references to the original.
    """
    for domain, aliases in _DOMAIN_ALIASES.items():
        for alias in aliases:
            Scanner.methods[alias] = Scanner.methods[domain]


def init() -> None:
    _init_scanner_methods()
    _add_scanner_aliases()

    logger.info(f"{len(Scanner.methods)} domains added to link scanner")
