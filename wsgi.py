# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
WSGI entry point for Flask application.

This module creates the Flask application instance based on the current
environment. For production deployment with Gunicorn, set FLASK_ENV=production.
"""

import os

from app import create_app

# Detect environment (defaults to production for safety)
env = os.environ.get("FLASK_ENV", "production")

# Configuration mapping
config_classes = {
    "development": "app.config.DevelopmentConfig",
    "testing": "app.config.TestingConfig",
    "staging": "app.config.StagingConfig",
    "production": "app.config.ProductionConfig",
}

config_class = config_classes.get(env, "app.config.ProductionConfig")

# Create application instance
app = create_app(config_class)

if __name__ == "__main__":
    app.run()
