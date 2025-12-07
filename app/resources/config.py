# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
config.py
---------

This module defines the ConfigResource for exposing the current application
configuration through a REST endpoint.
"""

import os

from flask_restful import Resource

from app.utils import check_access_required, require_jwt_auth


class ConfigResource(Resource):
    """
    Resource for providing the application configuration.

    Methods:
        get():
            Retrieve the current application configuration.
    """

    @require_jwt_auth()
    @check_access_required("read")
    def get(self):
        """
        Retrieve the current application configuration.

        Returns:
            dict: A dictionary containing the application configuration and
            HTTP status code 200.
        """
        jwt_secret_is_set = os.getenv("JWT_SECRET_KEY") is not None
        internal_secret_is_set = os.getenv("INTERNAL_SECRET_KEY") is not None

        config = {
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL"),
            "DATABASE_URI": os.getenv("DATABASE_URI"),
            "GUARDIAN_SERVICE_URL": os.getenv("GUARDIAN_SERVICE_URL"),
            "JWT_SECRET": jwt_secret_is_set,
            "INTERNAL_AUTH_TOKEN": internal_secret_is_set,
        }
        return config, 200
