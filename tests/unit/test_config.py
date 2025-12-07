# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
test_config.py
--------------
This module contains tests for the /config endpoint to ensure it returns the
expected configuration values.
"""

import json
import uuid

from tests.conftest import create_jwt_token


def test_config_endpoit(client):
    """
    Test the /config endpoint to ensure it returns the correct configuration.
    """
    company_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token = create_jwt_token(company_id, user_id)
    client.set_cookie("access_token", token, domain="localhost")

    response = client.get("/config")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert "FLASK_ENV" in data
    assert "LOG_LEVEL" in data
    assert "DATABASE_URI" in data
