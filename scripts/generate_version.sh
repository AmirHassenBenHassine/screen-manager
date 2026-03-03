#!/bin/bash
# Generate version file based on git commit

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$REPO_DIR/.version"

# Get git commit hash
VERSION=$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo "dev-$(date +%Y%m%d)")

# Write to .version file
echo "$VERSION" > "$VERSION_FILE"
echo "Version file created: $VERSION"
