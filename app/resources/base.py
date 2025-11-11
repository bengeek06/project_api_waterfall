"""
base.py
-------
Base resource classes and utilities for API resources.

This module provides common functionality for all API resources including:
- Error response formatting
- Common database operations
- UUID validation

Note: JWT authentication is handled by the @require_jwt_auth() decorator
from app.utils.auth. User ID and Company ID are available in Flask's g object:
- g.user_id: Current user's UUID
- g.company_id: Current user's company UUID
"""

import uuid as uuid_module
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models.db import db
from app.logger import logger


class BaseResource(Resource):
    """
    Base class for all API resources.

    Provides common functionality:
    - Error response formatting
    - Database session handling

    Authentication is handled by @require_jwt_auth() decorator.
    Access user_id and company_id via Flask's g object:
        from flask import g
        user_id = g.user_id
        company_id = g.company_id
    """

    def handle_error(self, error, status_code=500):
        """
        Format error response consistently.

        Args:
            error: The error object or message
            status_code: HTTP status code

        Returns:
            tuple: (error_dict, status_code)
        """
        if isinstance(error, ValidationError):
            return {
                "message": "Validation error",
                "errors": error.messages,
            }, 400

        if isinstance(error, SQLAlchemyError):
            logger.error(f"Database error: {str(error)}")
            db.session.rollback()
            return {"message": "Database error occurred"}, 500

        if isinstance(error, ValueError):
            return {"message": str(error)}, status_code

        logger.error(f"Unexpected error: {str(error)}")
        return {"message": "Internal server error"}, 500

    def commit_or_rollback(self):
        """
        Commit database changes or rollback on error.

        Returns:
            bool: True if commit succeeded, False otherwise
        """
        try:
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            logger.error(f"Commit failed: {str(error)}")
            db.session.rollback()
            return False


def error_response(message, status_code=400, errors=None):
    """
    Create a standardized error response.

    Args:
        message: Error message string
        status_code: HTTP status code
        errors: Optional dict of field-specific errors

    Returns:
        tuple: (error_dict, status_code)
    """
    response = {"message": message}
    if errors:
        response["errors"] = errors
    return response, status_code


def success_response(data, status_code=200):
    """
    Create a standardized success response.

    Args:
        data: Response data (dict, list, or None)
        status_code: HTTP status code

    Returns:
        tuple: (data, status_code)
    """
    return data, status_code


def validate_uuid(uuid_string, field_name="id"):
    """
    Validate that a string is a valid UUID.

    Args:
        uuid_string: String to validate
        field_name: Name of the field (for error messages)

    Returns:
        str: The validated UUID string

    Raises:
        ValueError: If the UUID is invalid
    """
    try:
        uuid_module.UUID(uuid_string)
        return uuid_string
    except (ValueError, AttributeError) as error:
        raise ValueError(
            f"Invalid {field_name}: must be a valid UUID"
        ) from error
