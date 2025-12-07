# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
deliverable.py
--------------
Deliverable CRUD resource endpoints.

Endpoints:
- GET /projects/{project_id}/deliverables - List project deliverables
- POST /projects/{project_id}/deliverables - Create a new deliverable
- GET /deliverables/{id} - Get deliverable details
- PUT /deliverables/{id} - Update deliverable
- PATCH /deliverables/{id} - Partially update deliverable
- DELETE /deliverables/{id} - Delete deliverable (soft delete)
"""

import uuid
from datetime import datetime, timezone

from flask import g, request
from marshmallow import ValidationError

from app.logger import logger
from app.models.db import db
from app.models.project import Deliverable, Project
from app.resources.base import BaseResource, error_response, validate_uuid
from app.schemas.project_schema import (
    DeliverableCreateSchema,
    DeliverableSchema,
    DeliverableUpdateSchema,
)
from app.utils import check_access_required, require_jwt_auth

# Constants
ERROR_DELIVERABLE_NOT_FOUND = "Deliverable not found"
ERROR_PROJECT_NOT_FOUND = "Project not found"
ERROR_VALIDATION = "Validation error"


class DeliverableListResource(BaseResource):
    """Resource for listing and creating deliverables within a project."""

    @require_jwt_auth()
    @check_access_required("LIST")
    def get(self, project_id):
        """List all deliverables for a specific project."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = g.company_id

            # Verify project exists and belongs to company
            project = Project.query.filter(
                Project.id == project_id,
                Project.company_id == company_id,
            ).first()

            if not project or project.removed_at:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            # Get deliverables for this project
            deliverables = Deliverable.query.filter(
                Deliverable.project_id == project_id
            ).all()

            # Filter out soft-deleted deliverables
            deliverables = [d for d in deliverables if not d.removed_at]

            schema = DeliverableSchema(many=True)
            return schema.dump(deliverables), 200

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("CREATE")
    def post(self, project_id):
        """Create a new deliverable for a project."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = g.company_id

            # Verify project exists and belongs to company
            project = Project.query.filter(
                Project.id == project_id,
                Project.company_id == company_id,
            ).first()

            if not project or project.removed_at:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            data = request.get_json()

            # Security: Detect if client tries to override URL/JWT parameters
            if "project_id" in data and str(data["project_id"]) != str(
                project_id
            ):
                logger.warning(
                    "Security: Client attempted to override project_id",
                    client_value=data["project_id"],
                    url_value=project_id,
                )
            if "company_id" in data and str(data["company_id"]) != str(
                company_id
            ):
                logger.warning(
                    "Security: Client attempted to override company_id",
                    client_value=data["company_id"],
                    jwt_value=company_id,
                )

            # Force authoritative values from URL and JWT (before validation)
            data["project_id"] = project_id
            data["company_id"] = company_id

            # Validate and deserialize
            schema = DeliverableCreateSchema()
            validated_data = schema.load(data)

            # Create deliverable
            deliverable = Deliverable(**validated_data)
            db.session.add(deliverable)

            if not self.commit_or_rollback():
                return error_response("Failed to create deliverable", 500)

            # Return created deliverable
            return_schema = DeliverableSchema()
            return return_schema.dump(deliverable), 201

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)


class DeliverableResource(BaseResource):
    """Resource for individual deliverable operations."""

    @require_jwt_auth()
    @check_access_required("READ")
    def get(self, deliverable_id):
        """Get a specific deliverable by ID."""
        try:
            validate_uuid(deliverable_id, "id")
            company_id = g.company_id

            deliverable = self._get_deliverable(deliverable_id, company_id)
            if not deliverable:
                return error_response(ERROR_DELIVERABLE_NOT_FOUND, 404)

            schema = DeliverableSchema()
            return schema.dump(deliverable), 200

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def put(self, deliverable_id):
        """Update a deliverable (full replacement)."""
        return self._update_deliverable(deliverable_id, partial=False)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def patch(self, deliverable_id):
        """Partially update a deliverable."""
        return self._update_deliverable(deliverable_id, partial=True)

    @require_jwt_auth()
    @check_access_required("DELETE")
    def delete(self, deliverable_id):
        """Delete a deliverable (soft delete)."""
        try:
            validate_uuid(deliverable_id, "id")
            company_id = g.company_id

            deliverable = self._get_deliverable(deliverable_id, company_id)
            if not deliverable:
                return error_response(ERROR_DELIVERABLE_NOT_FOUND, 404)

            deliverable.removed_at = datetime.now(timezone.utc)

            if not self.commit_or_rollback():
                return error_response("Failed to delete deliverable", 500)

            return "", 204

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    def _update_deliverable(self, deliverable_id, partial=False):
        """Internal method to handle both PUT and PATCH updates."""
        try:
            validate_uuid(deliverable_id, "id")
            company_id = g.company_id

            deliverable = self._get_deliverable(deliverable_id, company_id)
            if not deliverable:
                return error_response(ERROR_DELIVERABLE_NOT_FOUND, 404)

            # Validate and deserialize
            schema = DeliverableUpdateSchema(partial=partial)
            validated_data = schema.load(request.get_json())

            # Update deliverable fields
            for key, value in validated_data.items():
                if hasattr(deliverable, key):
                    setattr(deliverable, key, value)

            if not self.commit_or_rollback():
                return error_response("Failed to update deliverable", 500)

            return_schema = DeliverableSchema()
            return return_schema.dump(deliverable), 200

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @staticmethod
    def _get_deliverable(deliverable_id, company_id):
        """Get deliverable by ID and company."""
        # Ensure string UUIDs for comparison (db.String(36))
        if not isinstance(deliverable_id, str):
            deliverable_id = str(deliverable_id)
        if not isinstance(company_id, str):
            company_id = str(company_id)

        deliverable = Deliverable.query.filter(
            Deliverable.id == deliverable_id,
            Deliverable.company_id == company_id,
        ).first()

        # Check if soft-deleted
        if deliverable and deliverable.removed_at:
            return None

        return deliverable
