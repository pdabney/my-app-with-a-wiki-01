"""Delete short links (gated, destructive)."""

from .store import LinkStore


def delete_link(store: LinkStore, code: str) -> None:
    """Permanently remove a short link.

    @intent Deletion is hard (the link is gone, not soft-hidden) and gated behind a
        flag because it's destructive and irreversible. Deleting a code that doesn't
        exist is an error, not a silent no-op, so a caller can't believe it removed
        something it didn't.
    @param store the link store to delete from
    @param code the short code to remove
    @raises LinkNotFound if no link exists for the code
    @feature link-deletion
    @flag enable_link_deletion
    """
    store._get(code)  # raises LinkNotFound if the code is unknown
    del store._links[code]
