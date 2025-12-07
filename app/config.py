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

This module defines configuration classes for the Flask application based on
the environment.

Classes:
    - Config: Base configuration common to all environments.
    - DevelopmentConfig: Configuration for development.
    - TestingConfig: Configuration for testing.
    - StagingConfig: Configuration for staging.
    - ProductionConfig: Configuration for production.

Each class defines main parameters such as the secret key, database URL,
debug mode, and SQLAlchemy modification tracking.
"""

import os

from dotenv import load_dotenv

from app.constants import (
    BOOLEAN_TRUE_VALUES,
    DEFAULT_GUARDIAN_TIMEOUT,
    DEFAULT_USE_GUARDIAN,
    DEFAULT_USE_IDENTITY,
    ERROR_GUARDIAN_URL_REQUIRED,
    ERROR_IDENTITY_URL_REQUIRED,
    ERROR_JWT_SECRET_NOT_SET,
)

# Load .env file ONLY if not running in Docker
# This hook ensures environment variables are loaded for flask commands
if not os.environ.get("IN_DOCKER_CONTAINER") and not os.environ.get(
    "APP_MODE"
):
    env = os.environ.get("FLASK_ENV", "development")
    ENV_FILE = f".env.{env}"
    if os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
    # Fallback to generic .env if environment-specific file doesn't exist
    elif os.path.exists(".env"):
        load_dotenv(".env")


class Config:
    """Base configuration common to all environments."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET = os.environ.get("JWT_SECRET")
    if not JWT_SECRET:
        raise ValueError(ERROR_JWT_SECRET_NOT_SET)

    # Guardian Service Configuration
    USE_GUARDIAN_SERVICE = (
        os.environ.get("USE_GUARDIAN_SERVICE", DEFAULT_USE_GUARDIAN).lower()
        in BOOLEAN_TRUE_VALUES
    )
    GUARDIAN_SERVICE_URL = os.environ.get("GUARDIAN_SERVICE_URL")
    GUARDIAN_SERVICE_TIMEOUT = float(
        os.environ.get("GUARDIAN_SERVICE_TIMEOUT", DEFAULT_GUARDIAN_TIMEOUT)
    )

    # Validate GUARDIAN_SERVICE_URL if Guardian is enabled
    if USE_GUARDIAN_SERVICE and not GUARDIAN_SERVICE_URL:
        raise ValueError(ERROR_GUARDIAN_URL_REQUIRED)

    # Identity Service
    USE_IDENTITY_SERVICE = (
        os.environ.get("USE_IDENTITY_SERVICE", DEFAULT_USE_IDENTITY).lower()
        in BOOLEAN_TRUE_VALUES
    )
    IDENTITY_SERVICE_URL = os.environ.get("IDENTITY_SERVICE_URL")
    if USE_IDENTITY_SERVICE and not IDENTITY_SERVICE_URL:
        raise ValueError(ERROR_IDENTITY_URL_REQUIRED)

class DevelopmentConfig(Config):
    """Configuration for the development environment."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set.")


class TestingConfig(Config):
    """Configuration for the testing environment."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    JWT_SECRET = os.environ.get("JWT_SECRET")
    GUARDIAN_SERVICE_URL = os.environ.get("GUARDIAN_SERVICE_URL")
    USE_GUARDIAN_SERVICE = (
        os.environ.get("USE_GUARDIAN_SERVICE", "True").lower() == "true"
    )
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set.")


class StagingConfig(Config):
    """Configuration for the staging environment."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set.")


class ProductionConfig(Config):
    """Configuration for the production environment."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set.")
