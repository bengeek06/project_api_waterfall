# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
Tests for the WSGI entrypoint.

This module contains tests for the WSGI entrypoint to ensure the correct configuration
class is selected based on the FLASK_ENV environment variable.
"""

import importlib
import os
import sys


def test_wsgi_respects_flask_env(monkeypatch):
    """
    Test that the WSGI entrypoint respects FLASK_ENV environment variable.

    This test verifies that wsgi.py uses the configuration class based on
    FLASK_ENV and defaults to production if not set.
    """
    # Patch app.create_app BEFORE importing wsgi
    captured = {}

    def fake_create_app(config_class):
        captured["config_class"] = config_class

        class DummyApp:
            """Dummy Flask application for testing."""

            def run(self):
                """Mock run method to prevent actual server startup."""

        return DummyApp()

    monkeypatch.setattr("app.create_app", fake_create_app)

    # Clean up any existing wsgi module
    if "wsgi" in sys.modules:
        del sys.modules["wsgi"]

    # Test 1: With FLASK_ENV=development
    original_env = os.environ.get("FLASK_ENV")
    os.environ["FLASK_ENV"] = "development"

    try:
        wsgi = importlib.import_module("wsgi")

        # Verify the wsgi module has the app attribute
        assert hasattr(wsgi, "app")

        # Verify create_app was called with DevelopmentConfig
        assert "config_class" in captured, "create_app was not called"
        assert captured["config_class"] == "app.config.DevelopmentConfig"

        # Verify FLASK_ENV was respected
        assert os.environ["FLASK_ENV"] == "development"

    finally:
        # Restore original environment
        if original_env is not None:
            os.environ["FLASK_ENV"] = original_env
        elif "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]


def test_wsgi_defaults_to_production(monkeypatch):
    """
    Test that the WSGI entrypoint defaults to ProductionConfig when FLASK_ENV is not set.
    """
    # Patch app.create_app BEFORE importing wsgi
    captured = {}

    def fake_create_app(config_class):
        captured["config_class"] = config_class

        class DummyApp:
            """Dummy Flask application for testing."""

            def run(self):
                """Mock run method to prevent actual server startup."""

        return DummyApp()

    monkeypatch.setattr("app.create_app", fake_create_app)

    # Clean up any existing wsgi module
    if "wsgi" in sys.modules:
        del sys.modules["wsgi"]

    # Remove FLASK_ENV to test default behavior
    original_env = os.environ.get("FLASK_ENV")
    if "FLASK_ENV" in os.environ:
        del os.environ["FLASK_ENV"]

    try:
        wsgi = importlib.import_module("wsgi")

        # Verify the wsgi module has the app attribute
        assert hasattr(wsgi, "app")

        # Verify create_app was called with ProductionConfig (default)
        assert "config_class" in captured, "create_app was not called"
        assert captured["config_class"] == "app.config.ProductionConfig"

    finally:
        # Restore original environment
        if original_env is not None:
            os.environ["FLASK_ENV"] = original_env
