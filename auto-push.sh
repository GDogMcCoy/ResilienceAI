#!/bin/bash
# Auto-commit and push script for ResilienceAI Agent Swarm
# Usage: ./auto-push.sh "Commit message"

set -e

COMMIT_MSG="${1:-Agent Swarm update: $(date '+%Y-%m-%d %H:%M')}"

cd /tmp/ResilienceAI

# Configure git (if not already done)
git config user.email "agent@resilienceai.io" 2>/dev/null || true
git config user.name "ResilienceAI Agent" 2>/dev/null || true

# Check if there are changes
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to commit"
    exit 0
fi

# Add all changes
git add -A

# Commit
git commit -m "$COMMIT_MSG"

# Push using the token from environment or GitHub Actions
git push https://${GITHUB_TOKEN}@github.com/GDogMcCoy/ResilienceAI.git KIMI-2.5-Agent-Swarm

echo "✅ Pushed: $COMMIT_MSG"
