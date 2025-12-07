# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.models.db
-------------

This module initializes the SQLAlchemy instance (db) for the
PM Guardian API. The db object is used throughout the application
for ORM operations and database management.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
