#!/bin/bash

WEBHOOK_URL="https://dash-fight-package-telecharger.trycloudflare.com/webhook/github"
USERNAME="Karthik80-hub"

echo "Updating/Creating MCP webhook for all repositories"
echo "Webhook URL: $WEBHOOK_URL"
echo "Username: $USERNAME"
echo

if ! gh auth status &>/dev/null; then
      echo "GitHub CLI is not authenticated. Run 'gh auth login' first."
  exit 1
fi

REPOS=$(gh repo list "$USERNAME" --limit 100 --json name --jq '.[].name')
REPO_COUNT=$(echo "$REPOS" | wc -l)
echo "Found $REPO_COUNT repositories"
echo

for repo in $REPOS; do
  echo "Checking: $repo"
  # Find existing webhook ID for this URL
  webhook_id=$(gh api repos/$USERNAME/$repo/hooks --jq ".[] | select(.config.url == \"$WEBHOOK_URL\") | .id" 2>/dev/null | head -1)

  if [[ -n "$webhook_id" ]]; then
    echo "Updating existing webhook (ID: $webhook_id) for $repo"
    gh api -X PATCH repos/$USERNAME/$repo/hooks/$webhook_id \
      -f name="web" \
      -F active=true \
      -F events[]=push \
      -F events[]=pull_request \
      -F events[]=issues \
      -F events[]=workflow_run \
      -F events[]=check_run \
      -F config[url]="$WEBHOOK_URL" \
      -F config[content_type]=json \
      --silent
    if [[ $? -eq 0 ]]; then
              echo "Webhook updated for $repo"
    else
        echo "Failed to update webhook for $repo"
    fi
  else
    echo "➕ Creating webhook for $repo"
    gh api -X POST repos/$USERNAME/$repo/hooks \
      -f name="web" \
      -F active=true \
      -F events[]=push \
      -F events[]=pull_request \
      -F events[]=issues \
      -F events[]=workflow_run \
      -F events[]=check_run \
      -F config[url]="$WEBHOOK_URL" \
      -F config[content_type]=json \
      --silent
    if [[ $? -eq 0 ]]; then
              echo "Webhook created for $repo"
    else
        echo "Failed to create webhook for $repo"
    fi
  fi
  echo
done

echo "Webhook update/create complete for all repositories!" 