#!/bin/bash

# Script to set up git remote for Informatica Data Intelligence App
# Usage: ./setup_repo.sh YOUR_GITHUB_USERNAME

if [ $# -eq 0 ]; then
    echo "Usage: ./setup_repo.sh YOUR_GITHUB_USERNAME"
    echo "Example: ./setup_repo.sh ankit.yadav"
    exit 1
fi

USERNAME=$1
REPO_URL="https://github.com/$USERNAME/informatica_data_app.git"

echo "Setting up git remote for Informatica Data Intelligence App..."
echo "Repository URL: $REPO_URL"
echo ""

# Add the remote
git remote add origin $REPO_URL

# Set the branch to main
git branch -M main

# Push to the repository
echo "Pushing code to repository..."
git push -u origin main

echo ""
echo "✅ Repository setup complete!"
echo "Your Informatica Data Intelligence App is now available at:"
echo "https://github.com/$USERNAME/informatica_data_app"
echo ""
echo "You can now deploy this to Databricks Apps using:"
echo "databricks apps deploy"
