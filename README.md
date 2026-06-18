# my-app-with-a-wiki-01

A demo where a small app's **colocated metadata is projected into this repo's
GitHub wiki on every merge to `main`** — so the wiki is always an accurate,
auto-generated view of the code, never a hand-maintained doc that rots.

It's a working instance of the [distributed-brain](https://github.com/pdabney/code-samples-with-ai-metadata)
idea: author metadata *with* the code, gate it so it can't go stale, and
materialize it into a read model (here, the wiki) driven by the git WAL.

## The app

`linkshort` — a tiny in-memory URL shortener (`src/linkshort/`):

- `shorten.create_short_link` — create a link (custom aliases behind a flag)
- `resolve.resolve` — code → URL (pure lookup; see [ADR 0001](decisions/0001-resolve-does-not-record-clicks.md))
- `analytics.record_click` / `click_count` — click metrics (behind a flag)

Every public function carries a colocated contract in its docstring:

```python
@intent  ...what it guarantees and why...
@param   name ...
@returns ...
@raises  SomeError if ...
@feature custom-aliases          # which feature this implements
@flag    enable_custom_aliases   # the flag that toggles it (must exist in flags.yml)
```

## The two gates

| Tier | Checks | How |
|---|---|---|
| **1 — deterministic** (`tools/check_metadata.py`) | `@param`s match the signature; every *lexical* raise is in `@raises`; `@returns` present when returning; `@intent` present; every `@flag` exists in `flags.yml` | `ast`, in CI on every PR |
| **2 — semantic** | whether the prose still matches behavior, incl. propagated exceptions a parser can't see | an LLM reviewer (see the parent project) |

## The materializer → wiki

On merge to `main`, `.github/workflows/wiki.yml` runs `tools/publish_wiki.sh`,
which clones the wiki, runs `materializer/materialize.py` into it, and pushes.
The wiki gets:

- **Home** — index of modules + links
- **One page per module** — every function's intent, params/returns/raises, provenance
- **Features** — the feature → flag map (description, default, owner, what each flag gates, how to toggle)
- **Changelog** — append-only history of what changed, with intents

The brain's state (graph + changelog history) lives **in the wiki repo**, not in
`main` — so it persists across runs without a trigger loop, and `main` stays
purely human-authored. `brain/` is gitignored.

## Run it locally

```bash
python3 tools/check_metadata.py        # the gate (stdlib only)
python3 materializer/materialize.py    # writes ./brain/*.md (the wiki pages)

# tests
pip install pytest && PYTHONPATH=src pytest -q
```

## Enabling the wiki publish (one-time manual setup)

1. **Initialize the wiki:** GitHub → this repo → **Wiki** tab → create one page.
   (`<repo>.wiki.git` doesn't exist until you do.)
2. **Add a `WIKI_TOKEN` secret:** a PAT with `repo` scope (the default
   `GITHUB_TOKEN` generally can't push to wikis). Settings → Secrets and variables
   → Actions → New repository secret → `WIKI_TOKEN`.

Until both are done, the `wiki` workflow skips publishing cleanly; everything
else (gate, tests, local materialize) works regardless.
