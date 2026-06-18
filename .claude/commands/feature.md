---
description: Contract-first feature workflow — turn the agreed plan into metadata contracts, then implement to them.
---

You are building a feature in this repo with the engineer. **Metadata is as
important as the code** — it feeds the Tier-1 gate and the wiki. The plan you and
the engineer just agreed on already contains the intent; capture it as contracts
*at that moment*, don't reconstruct it later.

The core move: the "here's my plan, do you agree?" checkpoint becomes a
**contract checkpoint**. Approving the contracts *is* approving the plan.

## Steps

1. **Source the intent — don't invent it.** Use what you and the engineer agreed
   in this conversation (and any ticket they named). If the plan is unclear on
   *why* a function exists or what it guarantees, ask before coding.

2. **Draft the contracts first, before the bodies.** For every public function
   you'll add or change, write the docstring contract and show it for approval
   *before* writing the implementation:
   - `@intent` — the guarantee / why, taken from the agreed plan
   - `@param` (every parameter) / `@returns` (if it returns a value) /
     `@raises` (every exception it can raise, including ones propagated from callees)
   - `@feature <name>` — the feature this implements
   - `@flag <flag>` — the flag that gates it, if any

3. **Resolve metadata gaps by asking — never guess:**
   - "What feature name should this belong to?" (if not already decided)
   - "Is this behind a feature flag? If so, what's its default and owning team?"
   - If it introduces a **new** flag, add it to `flags.yml` (description / default /
     owner) in the same change — the gate will reject an `@flag` that isn't registered.

4. **Present the contracts for approval.** "Here are the contracts I'll implement
   to — agree?" This is the same approval beat you already do; the artifact is just
   the metadata now.

5. **Implement to the approved contracts.** Write code that satisfies each one
   exactly — the contract is the spec.

6. **Verify before declaring done:**
   ```
   python3 .github/tools/check_metadata.py
   ```
   It must pass. A failure means the code and the agreed contract disagree — fix
   the code, or, if the intent genuinely changed during implementation, re-confirm
   the revised contract with the engineer (don't silently edit it to match).

## Why this works

The plan-approval conversation is where intent is richest and freshest. Capturing
it as contracts *then* — instead of reconstructing it after the fact — is what
keeps the metadata as true as the code. The gate keeps them in lockstep forever,
and the materializer projects them into the wiki on every merge.
