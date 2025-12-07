# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
constants.py
------------

This module defines constant values used throughout the application.
These constants help avoid code duplication and make the codebase easier to maintain.
"""

# Configuration error messages
ERROR_JWT_SECRET_NOT_SET = "JWT_SECRET environment variable is not set."
ERROR_DATABASE_URL_NOT_SET = "DATABASE_URL environment variable is not set."
ERROR_GUARDIAN_URL_REQUIRED = (
    "GUARDIAN_SERVICE_URL is required when USE_GUARDIAN_SERVICE is enabled."
)
ERROR_IDENTITY_URL_REQUIRED = (
    "IDENTITY_SERVICE_URL is required when USE_IDENTITY_SERVICE is enabled."
)

# Default configuration values
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_GUARDIAN_TIMEOUT = "5"
DEFAULT_USE_GUARDIAN = "true"
DEFAULT_USE_IDENTITY = "false"

# Boolean value representations
BOOLEAN_TRUE_VALUES = ("true", "yes", "1")

# Waterfall service names
SERVICE_IDENTITY = "identity"
SERVICE_GUARDIAN = "guardian"

# Service configuration errors
ERROR_SERVICE_URL_NOT_SET = (
    "{service}_SERVICE_URL environment variable is not set."
)
ERROR_INVALID_SERVICE = "Invalid service name. Must be one of: {services}"
