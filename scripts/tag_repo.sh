#!/bin/bash

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 --version=TAG"
    echo "Example: $0 --version=1.0.0"
    echo "Example: $0 --version=0.1.1-beta1"
    exit 1
}

# Function to validate version (basic check)
validate_version() {
    local version=$1
    if [ -z "$version" ]; then
        echo -e "${RED}Error: Version cannot be empty${NC}"
        exit 1
    fi
}

# Parse arguments
VERSION=""
for arg in "$@"; do
    case $arg in
        --version=*)
            VERSION="${arg#*=}"
            shift
            ;;
        *)
            usage
            ;;
    esac
done

# Check if version is provided
if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: --version parameter is required${NC}"
    usage
fi

# Validate version format
validate_version "$VERSION"

# Get the repository root directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# Check if we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $RPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Tagging repository with version: ${VERSION}${NC}"

# Update VERSION file
echo "$VERSION" > "$REPO_ROOT/VERSION"
echo -e "${GREEN}✓ Updated VERSION file${NC}"

# Update openapi.yml
if [ -f "$REPO_ROOT/openapi.yml" ]; then
    # Use sed to update the version in openapi.yml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^  version: .*/  version: $VERSION/" "$REPO_ROOT/openapi.yml"
    else
        # Linux
        sed -i "s/^  version: .*/  version: $VERSION/" "$REPO_ROOT/openapi.yml"
    fi
    echo -e "${GREEN}✓ Updated openapi.yml${NC}"
else
    echo -e "${YELLOW}Warning: openapi.yml not found${NC}"
fi

# Add files to git
git add "$REPO_ROOT/VERSION"
if [ -f "$REPO_ROOT/openapi.yml" ]; then
    git add "$REPO_ROOT/openapi.yml"
fi

# Commit changes
git commit -m "chore: bump version to $VERSION"
echo -e "${GREEN}✓ Committed version bump${NC}"

# Create git tag
git tag -a "v$VERSION" -m "Release version $VERSION"
echo -e "${GREEN}✓ Created tag v${VERSION}${NC}"

echo ""
echo -e "${GREEN}Success! Version ${VERSION} has been tagged.${NC}"
echo ""
echo "Next steps:"
echo "  1. Push the commit: git push origin $(git branch --show-current)"
echo "  2. Push the tag: git push origin v${VERSION}"
echo "  Or push both: git push origin $(git branch --show-current) --tags"
