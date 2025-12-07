# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
milestone.py
------------
Milestone CRUD resource endpoints.

Endpoints:
- GET /projects/{project_id}/milestones - List project milestones
- POST /projects/{project_id}/milestones - Create a new milestone
- GET /milestones/{id} - Get milestone details
- PUT /milestones/{id} - Update milestone
- PATCH /milestones/{id} - Partially update milestone
- DELETE /milestones/{id} - Delete milestone (soft delete)
"""

import uuid
from datetime import datetime, timezone

from flask import g, request
from marshmallow import ValidationError

from app.logger import logger
from app.models.db import db
from app.models.project import Milestone, Project
from app.resources.base import BaseResource, error_response, validate_uuid
from app.schemas.project_schema import (
    MilestoneCreateSchema,
    MilestoneSchema,
    MilestoneUpdateSchema,
)
from app.utils import check_access_required, require_jwt_auth

# Constants
ERROR_MILESTONE_NOT_FOUND = "Milestone not found"
ERROR_PROJECT_NOT_FOUND = "Project not found"
ERROR_VALIDATION = "Validation error"


class MilestoneListResource(BaseResource):
    """Resource for listing and creating milestones within a project."""

    @require_jwt_auth()
    @check_access_required("LIST")
    def get(self, project_id):
        """List all milestones for a specific project."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = str(uuid.UUID(g.company_id))

            # Verify project exists and belongs to company
            project = Project.query.filter(
                Project.id == project_id,
                Project.company_id == company_id,
            ).first()

            if not project or project.removed_at:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            # Get milestones for this project
            milestones = Milestone.query.filter(
                Milestone.project_id == project_id
            ).all()

            # Filter out soft-deleted milestones
            milestones = [m for m in milestones if not m.removed_at]

            schema = MilestoneSchema(many=True)
            return schema.dump(milestones), 200

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("CREATE")
    def post(self, project_id):
        """Create a new milestone for a project."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = str(uuid.UUID(g.company_id))

            # Verify project exists and belongs to company
            project = Project.query.filter(
                Project.id == project_id,
                Project.company_id == company_id,
            ).first()

            if not project or project.removed_at:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            data = request.get_json()

            # Security: check if client tries to override URL/JWT parameters
            if "project_id" in data and str(data["project_id"]) != project_id:
                logger.warning(
                    "Security: Client attempted to override project_id",
                    url_project_id=project_id,
                    payload_project_id=str(data.get("project_id")),
                    user_id=g.user_id,
                    company_id=str(company_id),
                )

            if "company_id" in data and str(data["company_id"]) != str(
                company_id
            ):
                logger.warning(
                    "Security: Client attempted to override company_id",
                    jwt_company_id=str(company_id),
                    payload_company_id=str(data.get("company_id")),
                    user_id=g.user_id,
                )

            # Set authoritative values from URL and JWT
            data["project_id"] = project_id
            data["company_id"] = str(company_id)

            schema = MilestoneCreateSchema()
            validated_data = schema.load(data)

            # Create milestone instance
            milestone = Milestone(**validated_data)
            db.session.add(milestone)

            if not self.commit_or_rollback():
                return error_response("Failed to create milestone", 500)

            result_schema = MilestoneSchema()
            return result_schema.dump(milestone), 201

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)


class MilestoneResource(BaseResource):
    """Resource for individual milestone operations."""

    @require_jwt_auth()
    @check_access_required("READ")
    def get(self, milestone_id):
        """Get milestone details."""
        try:
            validate_uuid(milestone_id, "milestone_id")
            company_id = str(uuid.UUID(g.company_id))

            milestone = self._get_milestone(milestone_id, company_id)
            if not milestone:
                return error_response(ERROR_MILESTONE_NOT_FOUND, 404)

            schema = MilestoneSchema()
            return schema.dump(milestone), 200

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def put(self, milestone_id):
        """Fully update a milestone."""
        return self._update(milestone_id, partial=False)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def patch(self, milestone_id):
        """Partially update a milestone."""
        return self._update(milestone_id, partial=True)

    @require_jwt_auth()
    @check_access_required("DELETE")
    def delete(self, milestone_id):
        """Delete a milestone (soft delete)."""
        try:
            validate_uuid(milestone_id, "milestone_id")
            company_id = str(uuid.UUID(g.company_id))

            milestone = self._get_milestone(milestone_id, company_id)
            if not milestone:
                return error_response(ERROR_MILESTONE_NOT_FOUND, 404)

            milestone.removed_at = datetime.now(timezone.utc)

            if not self.commit_or_rollback():
                return error_response("Failed to delete milestone", 500)

            return "", 204

        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    def _update(self, milestone_id, partial=False):
        """Internal method to update a milestone."""
        try:
            validate_uuid(milestone_id, "milestone_id")
            company_id = str(uuid.UUID(g.company_id))

            milestone = self._get_milestone(milestone_id, company_id)
            if not milestone:
                return error_response(ERROR_MILESTONE_NOT_FOUND, 404)

            schema = MilestoneUpdateSchema(partial=partial)
            data = schema.load(request.get_json())

            # Update fields
            for field, value in data.items():
                if hasattr(milestone, field):
                    setattr(milestone, field, value)

            if not self.commit_or_rollback():
                return error_response("Failed to update milestone", 500)

            result_schema = MilestoneSchema()
            return result_schema.dump(milestone), 200

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except ValueError as error:
            return error_response(str(error), 400)
        except Exception as error:
            return self.handle_error(error)

    @staticmethod
    def _get_milestone(milestone_id, company_id):
        """Get milestone by ID and company."""
        # Ensure string UUIDs for comparison (db.String(36))
        if not isinstance(milestone_id, str):
            milestone_id = str(milestone_id)
        if not isinstance(company_id, str):
            company_id = str(company_id)

        milestone = Milestone.query.filter(
            Milestone.id == milestone_id,
            Milestone.company_id == company_id,
        ).first()

        # Check if soft-deleted
        if milestone and milestone.removed_at:
            return None

        return milestone
