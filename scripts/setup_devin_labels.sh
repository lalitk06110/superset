#!/usr/bin/env bash
set -euo pipefail

# Read from environment or positional args
API_KEY="${DEVIN_API_KEY:-${1:-}}"
ORG_ID="${DEVIN_ORG_ID:-${2:-}}"

if [ -z "$API_KEY" ] || [ -z "$ORG_ID" ]; then
  echo "Usage: DEVIN_API_KEY=<key> DEVIN_ORG_ID=<id> $0"
  echo "   or: $0 <api-key> <org-id>"
  exit 1
fi

# Resolve the current repository from git origin (handles forks correctly)
REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$REMOTE_URL" ]; then
    echo "Error: No git remote 'origin' found. Run this from inside the repository."
    exit 1
fi

REPO="$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[/:]([^/]+/[^/]+)(\.git)?|\1|' | sed 's|\.git$||')"

echo "Configuring Devin automation for: $REPO"

# --- Secrets ---
gh secret set DEVIN_API_KEY --repo "$REPO" --body "$API_KEY"

# --- Variables ---
gh variable set DEVIN_ORG_ID --repo "$REPO" --body "$ORG_ID"

# --- Labels ---
gh label create devin           --repo "$REPO" --color "0052CC" --description "Trigger Devin automation on this issue"            2>/dev/null || echo "Label 'devin' already exists"
gh label create devin-running   --repo "$REPO" --color "0E8A16" --description "Devin session is currently running"                2>/dev/null || echo "Label 'devin-running' already exists"
gh label create devin-blocked   --repo "$REPO" --color "B60205" --description "Prevent Devin from picking up this issue"          2>/dev/null || echo "Label 'devin-blocked' already exists"
gh label create blocked         --repo "$REPO" --color "B60205" --description "Prevents automation (generic blocked label)"       2>/dev/null || echo "Label 'blocked' already exists"
gh label create devin-pr-opened --repo "$REPO" --color "FEF2C0" --description "Devin has opened a PR for this issue"              2>/dev/null || echo "Label 'devin-pr-opened' already exists"
gh label create devin-resolved  --repo "$REPO" --color "5319E7" --description "Issue resolved via Devin automation"               2>/dev/null || echo "Label 'devin-resolved' already exists"
gh label create devin-failed    --repo "$REPO" --color "B60205" --description "Devin session failed to start"                     2>/dev/null || echo "Label 'devin-failed' already exists"
gh label create automation      --repo "$REPO" --color "C2E0C6" --description "Managed by automation workflow"                    2>/dev/null || echo "Label 'automation' already exists"

echo "Done! Devin automation is configured for $REPO."
