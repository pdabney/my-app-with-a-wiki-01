"""Resolve short codes back to their destination URLs."""

from .store import LinkStore


def resolve(store: LinkStore, code: str) -> str:
    """Resolve a short code to its destination URL.

    @intent Resolving is a pure, side-effect-free lookup; it does not record a click
        (that is the analytics module's job) so that read-only previews and health
        checks don't inflate counts. An unknown code is an error, not an empty
        result, so callers can't redirect to nowhere.
    @param store the link store to look in
    @param code the short code to resolve
    @returns the destination URL for the code
    @raises LinkNotFound if no link exists for the code
    """
    return store._get(code).url
