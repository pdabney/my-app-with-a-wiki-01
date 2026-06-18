#!/usr/bin/env bash
# Publish the materialized brain to this repo's GitHub wiki.
#
# Clones <repo>.wiki.git, runs the materializer *into* that clone (so the previous
# graph + the append-only changelog persist between runs — the brain's state lives
# in the wiki, outside the source tree), then commits and pushes.
#
# Usage: tools/publish_wiki.sh <owner/repo> [token]
#   token: a PAT with repo scope. The default GITHUB_TOKEN generally cannot push
#          to a wiki, so CI passes a WIKI_TOKEN secret here.
#
# Prereq: the wiki must already exist — create one page via the GitHub UI once,
# otherwise <repo>.wiki.git does not exist yet and the clone fails.
set -euo pipefail

SLUG="${1:?usage: publish_wiki.sh <owner/repo> [token]}"
TOKEN="${2:-}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

URL="https://github.com/${SLUG}.wiki.git"
[ -n "$TOKEN" ] && URL="https://x-access-token:${TOKEN}@github.com/${SLUG}.wiki.git"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

if ! git clone --quiet "$URL" "$WORK"; then
  echo "ERROR: could not clone ${SLUG}.wiki.git."
  echo "Has the wiki been initialized? Create one page in the GitHub UI first."
  exit 1
fi

echo "Materializing into the wiki clone…"
BRAIN_DIR="$WORK" python3 "$ROOT/.github/materializer/materialize.py"

cd "$WORK"
git add -A
if git diff --cached --quiet; then
  echo "Wiki already up to date — nothing to publish."
  exit 0
fi
git -c user.name="materializer-bot" \
    -c user.email="materializer-bot@users.noreply.github.com" \
    commit -q -m "Materialize wiki from ${GITHUB_SHA:-local}"
git push --quiet
echo "Wiki updated → https://github.com/${SLUG}/wiki"
