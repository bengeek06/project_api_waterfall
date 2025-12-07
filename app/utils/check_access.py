# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""Access control utilities."""

from functools import wraps

import requests
from flask import current_app, g, has_app_context, request

from app.logger import logger
from app.service import SERVICE_NAME
from app.utils.helpers import camel_to_snake
from app.utils.jwt_auth import extract_jwt_data

# Constants
INTERNAL_SERVER_ERROR = "Internal server error"


def _handle_guardian_response(response):
    """
    Handle Guardian service response and extract access information.

    Args:
        response: Response object from Guardian service

    Returns:
        tuple: (access_granted (bool), reason (str), status (int))
    """
    if response.status_code == 200:
        response_data = response.json()
        logger.debug(f"Guardian service response: {response_data}")
        return (
            response_data.get("access_granted", False),
            response_data.get("reason", "Unknown error"),
            response_data.get("status", 200),
        )

    if response.status_code == 400:
        try:
            response_data = response.json()
            logger.warning(f"Guardian service returned 400: {response_data}")
            return (
                response_data.get("access_granted", False),
                response_data.get("reason", "Bad request"),
                400,
            )
        except (ValueError, KeyError) as json_error:
            logger.error(
                f"Failed to parse Guardian 400 response as JSON: {json_error}"
            )
            return False, f"Guardian service error: {response.text}", 400

    # Other error status codes
    logger.error(
        f"Guardian service returned status {response.status_code}: {response.text}"
    )
    return (
        False,
        f"Guardian service error (status {response.status_code})",
        response.status_code,
    )


def _get_resource_name(kwargs, args):
    """
    Extract resource name from kwargs, request, or class name.

    Args:
        kwargs: View function kwargs
        args: View function args

    Returns:
        str: Resource name or None
    """
    resource_name = kwargs.get("resource_name") or (
        request.view_args.get("resource_name") if request.view_args else None
    )
    # If not found, deduce from the resource class name
    if not resource_name:
        view_self = args[0] if args else None
        if view_self and hasattr(view_self, "__class__"):
            class_name = view_self.__class__.__name__
            if class_name.lower().endswith("resource"):
                base_name = class_name[:-8]
                resource_name = camel_to_snake(base_name)
    # Normalisation: si resource_name se termine par '_list', on retire ce suffixe
    if resource_name and resource_name.endswith("_list"):
        resource_name = resource_name[:-5]
    return resource_name


def _get_user_id():
    """
    Extract user_id from Flask g object or JWT cookie.

    Returns:
        str: User ID or None
    """
    user_id = getattr(g, "user_id", None)

    # Essayer d'utiliser les données JWT déjà décodées si disponibles
    if not user_id and hasattr(g, "jwt_data") and g.jwt_data:
        user_id = g.jwt_data.get("user_id")
        logger.debug(f"Using user_id from already decoded JWT: {user_id}")
    # Sinon, extraire user_id du cookie JWT
    elif not user_id:
        logger.debug("User ID not found in g or headers, checking JWT cookie")
        jwt_data = extract_jwt_data()
        if jwt_data:
            user_id = jwt_data.get("user_id")
            logger.debug(f"Extracted user_id from JWT: {user_id}")
        else:
            logger.warning("JWT token not found or invalid")
    return user_id


def check_access_required(operation):
    """
    Decorator to check if the user has the required access for an operation.

    Args:
        operation (str): The operation to check access for.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            resource_name = _get_resource_name(kwargs, args)
            user_id = _get_user_id()

            if not user_id or not resource_name:
                logger.warning(
                    "Missing user_id or resource_name for access check."
                )
                return {
                    "error": "Missing user_id or resource_name for access check."
                }, 400

            # Use CheckAccessResource logic
            access_granted, reason, status = check_access(
                user_id, resource_name, operation
            )
            if access_granted:
                return view_func(*args, **kwargs)
            return {"error": "Access denied", "reason": reason}, (
                status if isinstance(status, int) else 403
            )

        return wrapped

    return decorator


def check_access(user_id, resource_name, operation):
    """
    Check if the user has access to perform the operation on the resource.

    Args:
        user_id (str): The ID of the user.
        resource_name (str): The name of the resource.
        operation (str): The operation to check access for.
    Returns:
        tuple: (access_granted (bool), reason (str), status (int or str))
    """
    logger.debug(
        f"Checking access for user_id: {user_id}, "
        f"resource_name: {resource_name}, operation: {operation}"
    )

    # Get configuration values
    if not has_app_context():
        logger.error("check_access called without application context")
        return False, INTERNAL_SERVER_ERROR, 500

    use_guardian = current_app.config.get("USE_GUARDIAN_SERVICE", True)

    # Skip Guardian check if disabled
    if not use_guardian:
        logger.warning("check_access: Guardian service is disabled")
        return True, "Access granted (Guardian disabled)", 200

    guardian_url = current_app.config.get("GUARDIAN_SERVICE_URL")
    guardian_timeout = current_app.config.get("GUARDIAN_SERVICE_TIMEOUT", 5)

    try:
        timeout = guardian_timeout

        # Get JWT token from cookies to forward to Guardian service (if in request context)
        headers = {}
        try:
            jwt_token = request.cookies.get("access_token")
            if jwt_token:
                headers["Cookie"] = f"access_token={jwt_token}"
                logger.debug("Forwarding JWT cookie to Guardian service")
        except RuntimeError:
            # No request context available (e.g., during testing without Flask app context)
            logger.debug(
                "No request context available, skipping JWT cookie forwarding"
            )

        response = requests.post(
            f"{guardian_url}/check-access",
            json={
                "user_id": user_id,
                "service": SERVICE_NAME,
                "resource_name": resource_name,
                "operation": operation,
            },
            headers=headers,
            timeout=timeout,
        )

        # Handle response based on status code
        return _handle_guardian_response(response)

    except requests.exceptions.Timeout:
        logger.error("Timeout when checking access with guardian service")
        return False, "Guardian service timeout", 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking access: {e}")
        return False, INTERNAL_SERVER_ERROR, 500
    except (ValueError, KeyError) as e:
        logger.error(f"Unexpected error checking access: {e}")
        return False, INTERNAL_SERVER_ERROR, 500
