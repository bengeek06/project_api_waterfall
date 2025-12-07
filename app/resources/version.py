# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
version.py
----------

This module defines the VersionResource for exposing the current API version
through a REST endpoint.
"""

import os

from flask_restful import Resource

from app.utils import check_access_required, require_jwt_auth


def _read_version():
    """Read version from VERSION file."""
    version_file_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "VERSION"
    )
    try:
        with open(version_file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"
    except (OSError, UnicodeDecodeError):
        return "unknown"


API_VERSION = _read_version()


class VersionResource(Resource):
    """
    Resource for providing the API version.

    Methods:
        get():
            Retrieve the current API version.
    """

    @check_access_required("list")
    @require_jwt_auth()
    def get(self):
        """
        Retrieve the current API version.

        Returns:
            dict: A dictionary containing the API version and HTTP status
            code 200.
        """
        return {"version": API_VERSION}, 200
