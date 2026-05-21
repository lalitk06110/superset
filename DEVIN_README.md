# Devin Issue Automation Setup Guide

This guide walks you through configuring the [Devin Issue Automation workflow](.github/workflows/devin-issue-automation.yml) for this repository.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Files to Copy to a New Fork](#files-to-copy-to-a-new-fork)
3. [Repository Permissions](#repository-permissions)
4. [Secrets](#secrets)
5. [Variables](#variables)
6. [Labels](#labels)
7. [Full Setup Script](#full-setup-script)
8. [How It Works](#how-it-works)

---

## Prerequisites

Before you begin, you need:

- A [Devin](https://devin.ai) account with API access
- Your Devin **Organization ID**
- Your Devin **API Key**
- Devin connected to GitHub with access to your Superset fork so it can create branches and open pull requests
- The [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated
- Admin access to this repository (to create secrets, variables, and labels)

---

## Files to Copy to a New Fork

If you are starting from a fresh fork of the original Superset repository, copy these files into your fork:

| File | Purpose |
|------|---------|
| `.github/workflows/devin-issue-automation.yml` | GitHub Actions workflow that starts Devin sessions and updates issue labels |
| `.github/DEVIN_PR_TEMPLATE.md` | Devin pull request template used by Devin when opening PRs |
| `scripts/setup_devin_labels.sh` | Helper script that configures the required repository secret, variable, and labels |
| `DEVIN_README.md` | Setup guide for maintainers configuring Devin issue automation |

Commit these files and push them to the fork's `master` branch. GitHub Actions only activates workflows after the workflow file exists on the default branch, so pushing `.github/workflows/devin-issue-automation.yml` to `master` is required before the `devin` issue label can trigger automation.

### Enable Issues on Your Fork

GitHub disables issues on forked repositories by default. Since the Devin automation is triggered by issue events, you must enable issues:

1. Go to your fork on GitHub.
2. Click **Settings**.
3. Under **General** -> **Features**, check **Issues**.
4. Click **Save**.

### Enable GitHub Actions on Your Fork

GitHub may require you to enable workflows on a fork before issue automation can run:

1. Go to the **Actions** tab on your fork.
2. If prompted, click **I understand my workflows, go ahead and enable them**.
3. Confirm the workflow appears under **Devin Issue Automation**.

---

## Repository Permissions

The workflow requires the following permissions (already declared in the workflow file):

| Permission | Level | Purpose |
|------------|-------|---------|
| `issues` | `write` | Add/remove labels, post comments |
| `contents` | `read` | Read repository metadata |
| `pull-requests` | `read` | Detect linked issues in PRs |

No additional setup is needed for permissions unless you are running this in a private repository with custom token settings.

### Devin GitHub Access

In Devin, connect GitHub and grant Devin access to your fork or the organization that owns it. The workflow starts a Devin session, but Devin still needs repository access to inspect code, push branches, and open pull requests.

---

## Secrets

### `DEVIN_API_KEY`

Your Devin API key used to authenticate session creation requests.

1. Navigate to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. Name: `DEVIN_API_KEY`
4. Secret: Paste your Devin API key.
5. Click **Add secret**.

---

## Variables

### `DEVIN_ORG_ID`

Your Devin organization ID.

1. Navigate to **Settings** -> **Secrets and variables** -> **Actions**.
2. Switch to the **Variables** tab.
3. Click **New repository variable**.
4. Name: `DEVIN_ORG_ID`
5. Value: Your Devin organization ID.
6. Click **Add variable**.

---

## Labels

The workflow uses the following labels to track automation state. You should create them with descriptive colors before enabling the workflow.

| Label | Color Suggestion | Purpose |
|-------|-----------------|---------|
| `devin` | `#0052CC` (blue) | Triggers the automation when added to an issue |
| `devin-running` | `#0E8A16` (green) | Indicates an active Devin session is in progress |
| `devin-blocked` | `#B60205` (red) | Prevents automation from starting on this issue |
| `blocked` | `#B60205` (red) | Alternative to `devin-blocked`; also prevents automation |
| `devin-pr-opened` | `#FEF2C0` (yellow) | Indicates a Devin PR has been opened for the issue |
| `devin-resolved` | `#5319E7` (purple) | Marks the issue as resolved after closure |
| `devin-failed` | `#B60205` (red) | Indicates the automation failed to start a Devin session |
| `automation` | `#C2E0C6` (light green) | Generic automation tag applied alongside `devin-running` |

### Creating Labels via GitHub Web UI

1. Navigate to the repository's **Issues** tab.
2. Click **Labels** on the right sidebar.
3. Click **New label**.
4. Enter the name, select a color, and add a description.
5. Click **Create label**.
6. Repeat for each label in the table above.

---

## Full Setup Script

Run [`scripts/setup_devin_labels.sh`](scripts/setup_devin_labels.sh) from inside the repository to configure secrets, variables, and labels in one go. The script reads the forked repository from `git remote origin`, so it targets the correct repo.

Before running the script, verify that `gh` is authenticated with an account that can manage repository secrets, variables, and labels:

```bash
gh auth status
```

Make it executable, then run it with your credentials via environment variables or positional arguments:

```bash
chmod +x scripts/setup_devin_labels.sh

# via environment variables
DEVIN_API_KEY="your-api-key" DEVIN_ORG_ID="your-org-id" ./scripts/setup_devin_labels.sh

# or via positional arguments
./scripts/setup_devin_labels.sh "your-api-key" "your-org-id"
```

---

## How It Works

Once configured, the workflow behaves as follows:

1. **Trigger**: Adding the `devin` label to an issue starts the automation.
2. **Eligibility Check**: The workflow verifies the issue is not blocked, already running, already resolved, or already has a PR open.
3. **Session Start**: A Devin session is created via the Devin API with a prompt scoped to the issue.
4. **State Labels**: The issue is labeled `devin-running` + `automation` while the session is active.
5. **PR Detection**: When a linked PR is opened, the label changes to `devin-pr-opened`. The PR title or body must reference the issue number, such as `Fixes #123`, `Closes #123`, or `#123`.
6. **Resolution**: Closing the issue labels it `devin-resolved` and removes `devin-running`.
7. **Reopen**: Reopening an issue restores the `devin` label so automation can be retriggered.
8. **Failure Handling**: If session creation fails, the issue is labeled `devin-failed`.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Workflow fails at "Validate config" | Missing secret or variable | Check `DEVIN_API_KEY` and `DEVIN_ORG_ID` in repository settings |
| Issue labeled `devin` but nothing happens | Issue is blocked or already running | Remove `devin-blocked` / `blocked` labels, or verify no `devin-running` label exists |
| `devin-failed` label appears | Devin API error (bad key, invalid org, etc.) | Verify your API key and organization ID are correct |
| PR opened but issue not updated | PR does not reference the issue with `#N` | Ensure the PR title or body contains the issue number (e.g., `Fixes #123`) |
