# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""JWT authentication utilities."""

import uuid
from functools import wraps

import jwt
from flask import current_app, g, request

from app.logger import logger


def extract_jwt_data():
    """
    Extract and decode JWT data from request cookies.

    Returns:
        dict: Dictionary containing user_id and company_id from JWT, or None if invalid/missing
    """
    jwt_token = request.cookies.get("access_token")
    if not jwt_token:
        logger.debug("JWT token not found in cookies")
        return None

    jwt_secret = current_app.config.get("JWT_SECRET")
    if not jwt_secret:
        logger.warning("JWT_SECRET not found in configuration")
        return None

    try:
        payload = jwt.decode(jwt_token, jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub") or payload.get("user_id")
        company_id = payload.get("company_id")

        logger.debug(
            f"JWT decoded successfully - user_id: {user_id}, company_id: {company_id}"
        )
        return {
            "user_id": user_id,
            "company_id": company_id,
            "payload": payload,
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.warning(f"JWT decode failed: {e}")
        return None


def require_jwt_auth():
    """
    Decorator to require JWT authentication and extract JWT information.
    Requires a valid JWT token in cookies - no fallback to headers.

    Always extracts and stores user_id, company_id, and jwt_data in Flask's g object
    for use in view functions. This ensures the JWT is decoded only once per request.

    Returns:
        Decorated function or error response

    Stores in g:
        - g.user_id: User ID from JWT
        - g.company_id: Company ID from JWT
        - g.jwt_data: Complete JWT payload
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            # Try JWT authentication first
            jwt_data = extract_jwt_data()

            # Fallback to headers for testing environment
            if not jwt_data:
                user_id = request.headers.get("X-User-ID")
                company_id = request.headers.get("X-Company-ID")

                if user_id:
                    # Create mock JWT data from headers (for testing)
                    jwt_data = {"user_id": user_id, "company_id": company_id}
                    logger.debug(
                        "Using headers for authentication (testing mode)"
                    )
                else:
                    return {"message": "Missing or invalid JWT token"}, 401

            # Extract company_id and user_id from JWT data
            company_id = jwt_data.get("company_id")
            user_id = jwt_data.get("user_id")

            if not user_id:
                logger.error("user_id missing in JWT token")
                return {"message": "Invalid JWT token: missing user_id"}, 401

            if not company_id:
                logger.error("company_id missing in JWT token")
                return {
                    "message": "Invalid JWT token: missing company_id"
                }, 401

            # Validate UUID format for company_id
            try:
                uuid.UUID(company_id)
            except (ValueError, TypeError):
                logger.error(f"Invalid company_id format in JWT: {company_id}")
                return {
                    "message": "Invalid JWT token: company_id must be a valid UUID"
                }, 401

            # Store company_id, user_id and jwt_data in g for use in view functions
            g.company_id = company_id
            g.user_id = user_id
            g.jwt_data = jwt_data

            return view_func(*args, **kwargs)

        return wrapped

    return decorator
