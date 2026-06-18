# 1. Resolution does not record clicks

**Status:** Accepted · 2026-06-18

## Context

A short link is both *resolved* (code → URL, for redirects) and *measured*
(click counts, for analytics). The simplest implementation records a click inside
`resolve()`. But resolution also happens for read-only purposes — link previews,
health checks, admin listings — and counting those would inflate the metrics.

## Decision

`resolve()` is a pure lookup and never mutates state. Click recording lives in a
separate `analytics.record_click()`, behind the `enable_click_analytics` flag.

## Consequences

- Read-only callers (previews, health checks) can resolve freely without skewing
  analytics.
- Recording clicks is an explicit, separately-toggleable step — analytics can be
  disabled wholesale (e.g. a privacy mode) without touching redirects.
- Callers that *do* want to count a redirect must call both `resolve()` and
  `record_click()`. That coupling is intentional and documented here so it isn't
  "fixed" by folding the two back together.
