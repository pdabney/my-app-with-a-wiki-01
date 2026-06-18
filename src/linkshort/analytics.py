"""Click analytics for short links."""

from .store import LinkStore


def record_click(store: LinkStore, code: str) -> int:
    """Record one click on a short link and return the new total.

    @intent Click recording is separated from resolution so it can be turned off
        wholesale via a feature flag (e.g. for privacy modes) without affecting
        redirects. An unknown code is an error rather than a silent no-op.
    @param store the link store holding the link
    @param code the short code that was clicked
    @returns the link's click count after recording this click
    @raises LinkNotFound if no link exists for the code
    @feature click-analytics
    @flag enable_click_analytics
    """
    link = store._get(code)
    link.clicks += 1
    return link.clicks


def click_count(store: LinkStore, code: str) -> int:
    """Return the number of clicks recorded for a short link.

    @intent A read-only view of the click total; never mutates state.
    @param store the link store holding the link
    @param code the short code to report on
    @returns the recorded click count for the code
    @raises LinkNotFound if no link exists for the code
    """
    return store._get(code).clicks
