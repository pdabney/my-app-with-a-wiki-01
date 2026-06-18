"""Shared types and in-memory store for linkshort."""

from dataclasses import dataclass, field


@dataclass
class ShortLink:
    code: str
    url: str
    clicks: int = 0


class InvalidURL(Exception):
    """A URL was rejected because it is not a well-formed http(s) URL."""


class AliasTaken(Exception):
    """A requested custom alias is already in use."""


class LinkNotFound(Exception):
    """An operation referenced a short code that does not exist."""


@dataclass
class LinkStore:
    """In-memory store mapping short codes to links."""

    _links: dict[str, ShortLink] = field(default_factory=dict)

    def _get(self, code: str) -> ShortLink:
        if code not in self._links:
            raise LinkNotFound(f"no link for code {code!r}")
        return self._links[code]

    def _put(self, link: ShortLink) -> None:
        self._links[link.code] = link

    def _has(self, code: str) -> bool:
        return code in self._links
