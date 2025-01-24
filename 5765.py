version: 0.2

phases:
  pre_build:
    commands:
      - echo "Starting pre-build phase..."
      
      # Define variables
      - |
        GITHUB_API_URL="https://api.github.com"
        REPO_OWNER="techdecipher"
        REPO_NAME="dummy"
        GITHUB_PAT="$GITHUB_PAT"

      # Fetch latest commit SHA
      - echo "Fetching latest commit SHA from GitHub..."
      - |
        LATEST_COMMIT_SHA=$(curl -s -H "Authorization: token $GITHUB_PAT" \
          "$GITHUB_API_URL/repos/$REPO_OWNER/$REPO_NAME/commits?per_page=1" | jq -r '.[0].sha')
        echo "Latest commit SHA: $LATEST_COMMIT_SHA"

      # Find branch name containing the latest commit
      - echo "Checking which branch contains the latest commit..."
      - |
        UPDATED_BRANCH=$(curl -s -H "Authorization: token $GITHUB_PAT" \
          "$GITHUB_API_URL/repos/$REPO_OWNER/$REPO_NAME/branches" | \
          jq -r --arg sha "$LATEST_COMMIT_SHA" '.[] | select(.commit.sha == $sha) | .name')

      - echo "Branch that was updated $UPDATED_BRANCH"

      # Deployment logic based on detected branch
      - |
        if [ "$UPDATED_BRANCH" = "dev" ]; then
          echo "Changes detected in DEV branch, running deployment...";
        elif [ "$UPDATED_BRANCH" = "main" ]; then
          echo "Changes detected in MAIN branch, running deployment...";
        else
          echo "Unknown branch detected, exiting...";
          exit 1;
        fi

artifacts:
  files:
    - '**/*'

