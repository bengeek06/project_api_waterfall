# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.utils
---------

This module provides utility functions for the Project Service.

Modules:
- auth: Authentication and authorization utilities
"""

from app.utils.check_access import (
    check_access,
    check_access_required,
    extract_jwt_data,
)
from app.utils.jwt_auth import (
    require_jwt_auth,
    extract_jwt_data
)

__all__ = [
    "check_access",
    "check_access_required",
    "extract_jwt_data",
    "require_jwt_auth",
]
