"""Create short links."""

import hashlib

from .store import AliasTaken, InvalidURL, LinkStore, ShortLink

_CODE_LEN = 7


def create_short_link(store: LinkStore, url: str, alias: str = "") -> ShortLink:
    """Create a short link for a URL, optionally with a custom alias.

    @intent A URL gets a deterministic short code derived from its content, so the
        same URL always yields the same code. A caller may instead request a custom
        alias; that path is guarded by a feature flag because it is a paid feature.
        A taken alias is rejected rather than silently overwriting an existing link.
    @param store the link store to create the link in
    @param url the destination URL; must be a well-formed http(s) URL
    @param alias an optional custom short code; empty means auto-generate
    @returns the created ShortLink
    @raises InvalidURL if url is not a well-formed http(s) URL
    @raises AliasTaken if alias is already in use
    @feature custom-aliases
    @flag enable_custom_aliases
    """
    if not (url.startswith("http://") or url.startswith("https://")):
        raise InvalidURL(f"{url!r} is not an http(s) URL")
    code = alias or hashlib.sha1(url.encode()).hexdigest()[:_CODE_LEN]
    if store._has(code):
        if alias:
            raise AliasTaken(f"alias {alias!r} is already in use")
        return store._get(code)
    link = ShortLink(code=code, url=url)
    store._put(link)
    return link
