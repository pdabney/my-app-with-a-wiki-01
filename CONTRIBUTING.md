# Contributing — metadata is part of "done"

In this repo, a change isn't done until its **metadata** is done. Every public
function carries a colocated contract; the Tier-1 gate (`.github/tools/check_metadata.py`)
enforces it in CI, and the materializer projects it into the [wiki](../../wiki)
on every merge. Stale or missing metadata is a build failure, the same as a
failing test.

## Definition of Done (metadata)

For every public function you add or change:

- [ ] **`@intent`** — what it guarantees and *why* (not what the code obviously does)
- [ ] **`@param`** for every parameter
- [ ] **`@returns`** if it returns a value
- [ ] **`@raises`** for every exception it can raise — *including ones propagated
      from callees* (the gate only checks the ones it can see lexically; you own the rest)
- [ ] **`@feature <name>`** if it implements a user-facing feature
- [ ] **`@flag <flag>`** if it's gated — and the flag exists in `flags.yml`
      (with `description` / `default` / `owner`)
- [ ] `python3 .github/tools/check_metadata.py` passes

## Capture it at plan time, not after

Use **`/feature`** (`.claude/commands/feature.md`). The plan you and the agent
agree on *is* the intent — write it as contracts, get approval on the contracts,
then implement to them. Reconstructing intent after the fact is how it drifts.

## Decisions go in `decisions/`

If a change embodies a cross-cutting decision ("why X over Y", an ordering
constraint), add or supersede an ADR in `decisions/`. The wiki surfaces those too.

## Why

This is the front door of a "distributed brain": author metadata *with* the code,
gate it so it can't go stale, and materialize it into a read model (the wiki).
The gate and materializer are the back half; this standard is the front half —
without consistent capture, there's nothing accurate to project.
