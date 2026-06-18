import pytest

from linkshort.store import AliasTaken, InvalidURL, LinkNotFound, LinkStore
from linkshort.shorten import create_short_link
from linkshort.resolve import resolve
from linkshort.analytics import click_count, record_click


def test_create_and_resolve():
    s = LinkStore()
    link = create_short_link(s, "https://example.com")
    assert resolve(s, link.code) == "https://example.com"


def test_same_url_is_idempotent():
    s = LinkStore()
    assert create_short_link(s, "https://x.com").code == create_short_link(s, "https://x.com").code


def test_invalid_url_rejected():
    s = LinkStore()
    with pytest.raises(InvalidURL):
        create_short_link(s, "ftp://nope")


def test_custom_alias_collision():
    s = LinkStore()
    create_short_link(s, "https://a.com", alias="aa")
    with pytest.raises(AliasTaken):
        create_short_link(s, "https://b.com", alias="aa")


def test_clicks_recorded():
    s = LinkStore()
    link = create_short_link(s, "https://x.com")
    assert record_click(s, link.code) == 1
    assert record_click(s, link.code) == 2
    assert click_count(s, link.code) == 2


def test_unknown_code_raises():
    s = LinkStore()
    with pytest.raises(LinkNotFound):
        resolve(s, "zzz")
