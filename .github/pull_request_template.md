<!-- The plan you agreed on is the intent — capture it as contracts. See CONTRIBUTING.md and /feature. -->

## What & why

<!-- The change-level intent: what does this do, and why? -->

## Metadata Definition of Done

- [ ] Public functions have `@intent` / `@param` / `@returns` / `@raises` (incl. propagated exceptions)
- [ ] `@feature` / `@flag` set where applicable; any new flag registered in `flags.yml` (description / default / owner)
- [ ] `python3 .github/tools/check_metadata.py` passes
- [ ] If this embodies a cross-cutting decision, an ADR was added/updated in `decisions/`
