#!/usr/bin/env python3
"""
Script to add license headers to all Python source files.

This script adds a copyright and license notice to all .py files in the project
that don't already have one.
"""

import sys
from pathlib import Path

LICENSE_HEADER = """# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro

"""


def has_license_header(content: str) -> bool:
    """Check if file already has a license header."""
    return "Copyright (c) 2025 Waterfall" in content or "Copyright (c)" in content[:500]


def add_license_header(file_path: Path, dry_run: bool = False) -> bool:
    """
    Add license header to a Python file.
    
    Args:
        file_path: Path to the Python file
        dry_run: If True, only print what would be done without modifying files
        
    Returns:
        True if header was added, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False
    
    # Skip if already has license header
    if has_license_header(content):
        print(f"⏭️  Skip {file_path} (already has license header)")
        return False
    
    # Handle shebang if present
    lines = content.split('\n')
    new_content = []
    start_idx = 0
    
    if lines and lines[0].startswith('#!'):
        new_content.append(lines[0])
        new_content.append('')
        start_idx = 1
    
    # Add license header
    new_content.append(LICENSE_HEADER.rstrip())
    
    # Add rest of file
    remaining = '\n'.join(lines[start_idx:])
    if remaining.strip():  # Only add if there's actual content
        new_content.append(remaining)
    
    final_content = '\n'.join(new_content)
    
    if dry_run:
        print(f"🔍 Would add header to: {file_path}")
        return True
    
    # Write modified content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"✅ Added header to: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing {file_path}: {e}")
        return False


def find_python_files(root_dir: Path) -> list[Path]:
    """
    Find all Python files in the project.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of Python file paths
    """
    python_files = []
    
    # Directories to exclude
    exclude_dirs = {
        '__pycache__',
        '.git',
        'venv',
        '.venv',
        'env',
        '.env',
        'node_modules',
        '.pytest_cache',
        '.mypy_cache',
        'instance',
    }
    
    for py_file in root_dir.rglob('*.py'):
        # Skip if in excluded directory
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        python_files.append(py_file)
    
    return sorted(python_files)


def main():
    """Main function."""
    # Get project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Parse arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    print(f"📁 Project root: {project_root}\n")
    
    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files\n")
    
    # Add license headers
    modified_count = 0
    for py_file in python_files:
        if add_license_header(py_file, dry_run=dry_run):
            modified_count += 1
    
    # Summary
    print(f"\n{'Would modify' if dry_run else 'Modified'} {modified_count} file(s)")
    
    if dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()
