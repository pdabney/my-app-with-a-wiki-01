"""Contract verification tests — generated from colocated metadata.

Do not edit the STRUCTURE by hand. Change the @intent/@raises contract or run:
  python3 dist-brain-metadata-tooling/engine/generate_verification.py --root .

These tests are the verification checkpoint for /feature and long-running agents:
if contracts say it, a test must prove it.
"""
# fmt: off — generated file
import pytest

from linkshort.store import AliasTaken, InvalidURL, LinkNotFound, LinkStore
from linkshort.analytics import click_count, record_click
from linkshort.delete import delete_link
from linkshort.resolve import resolve
from linkshort.shorten import create_short_link


# --- src/linkshort/analytics.py#record_click ---
# @intent Click recording is separated from resolution so it can be turned off wholesale via a feature flag (e.g. for privacy mode...
# @feature click-analytics
# @flag enable_click_analytics
def test_linkshort_analytics_record_click_raises_linknotfound():
    """Contract @raises LinkNotFound — src/linkshort/analytics.py#record_click"""
    s = LinkStore()
    with pytest.raises(LinkNotFound):
        record_click(s, "zzz")

def test_linkshort_analytics_record_click_returns_contract():
    """Contract @returns — src/linkshort/analytics.py#record_click"""
    s = LinkStore()
    link = create_short_link(s, "https://x.com")
    assert record_click(s, link.code) == 1


# --- src/linkshort/analytics.py#click_count ---
# @intent A read-only view of the click total; never mutates state.
def test_linkshort_analytics_click_count_raises_linknotfound():
    """Contract @raises LinkNotFound — src/linkshort/analytics.py#click_count"""
    s = LinkStore()
    with pytest.raises(LinkNotFound):
        click_count(s, "zzz")

def test_linkshort_analytics_click_count_returns_contract():
    """Contract @returns — src/linkshort/analytics.py#click_count"""
    s = LinkStore()
    link = create_short_link(s, "https://x.com")
    assert click_count(s, link.code) == 0


# --- src/linkshort/delete.py#delete_link ---
# @intent Deletion is hard (the link is gone, not soft-hidden) and gated behind a flag because it's destructive and irreversible. ...
# @feature link-deletion
# @flag enable_link_deletion
def test_linkshort_delete_delete_link_raises_linknotfound():
    """Contract @raises LinkNotFound — src/linkshort/delete.py#delete_link"""
    s = LinkStore()
    with pytest.raises(LinkNotFound):
        delete_link(s, "zzz")


# --- src/linkshort/resolve.py#resolve ---
# @intent Resolving is a pure, side-effect-free lookup; it does not record a click (that is the analytics module's job) so that re...
def test_linkshort_resolve_resolve_raises_linknotfound():
    """Contract @raises LinkNotFound — src/linkshort/resolve.py#resolve"""
    s = LinkStore()
    with pytest.raises(LinkNotFound):
        resolve(s, "zzz")

def test_linkshort_resolve_resolve_returns_contract():
    """Contract @returns — src/linkshort/resolve.py#resolve"""
    s = LinkStore()
    link = create_short_link(s, "https://example.com")
    assert resolve(s, link.code) == "https://example.com"


# --- src/linkshort/shorten.py#create_short_link ---
# @intent A URL gets a deterministic short code derived from its content, so the same URL always yields the same code. A caller ma...
# @feature custom-aliases
# @flag enable_custom_aliases
def test_linkshort_shorten_create_short_link_raises_invalidurl():
    """Contract @raises InvalidURL — src/linkshort/shorten.py#create_short_link"""
    s = LinkStore()
    with pytest.raises(InvalidURL):
        create_short_link(s, "ftp://nope")

def test_linkshort_shorten_create_short_link_raises_aliastaken():
    """Contract @raises AliasTaken — src/linkshort/shorten.py#create_short_link"""
    s = LinkStore()
    create_short_link(s, "https://a.com", alias="aa")
    with pytest.raises(AliasTaken):
        create_short_link(s, "https://b.com", alias="aa")

def test_linkshort_shorten_create_short_link_returns_contract():
    """Contract @returns — src/linkshort/shorten.py#create_short_link"""
    s = LinkStore()
    link = create_short_link(s, "https://example.com")
    assert link.url == "https://example.com"
    assert link.code

