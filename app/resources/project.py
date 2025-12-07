# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
project.py
----------
Project CRUD resource endpoints.

Endpoints:
- GET /projects - List all projects
- POST /projects - Create a new project
- GET /projects/{id} - Get project details
- PUT /projects/{id} - Update project
- PATCH /projects/{id} - Partially update project
- DELETE /projects/{id} - Delete project (soft delete)
"""

import uuid
from datetime import datetime, timezone

from flask import g, request
from marshmallow import ValidationError

from app.logger import logger
from app.models.db import db
from app.models.project import Project, ProjectHistory
from app.resources.base import BaseResource, error_response, validate_uuid
from app.resources.permission import seed_project_permissions
from app.schemas.project_schema import (
    ProjectCreateSchema,
    ProjectSchema,
    ProjectUpdateSchema,
)
from app.utils import check_access_required, require_jwt_auth

# Constants
ERROR_PROJECT_NOT_FOUND = "Project not found"
ERROR_VALIDATION = "Validation error"


class ProjectListResource(BaseResource):
    """Resource for listing and creating projects."""

    @require_jwt_auth()
    @check_access_required("LIST")
    def get(self):
        """List all projects for the authenticated user's company."""
        try:
            company_id = str(uuid.UUID(g.company_id))

            projects = Project.query.filter(
                Project.company_id == company_id
            ).all()

            # Filter out soft-deleted projects
            projects = [p for p in projects if not p.removed_at]

            schema = ProjectSchema(many=True)
            return schema.dump(projects), 200

        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("CREATE")
    def post(self):
        """Create a new project."""
        try:
            company_id = str(uuid.UUID(g.company_id))
            user_id = g.user_id  # Keep as string for external reference

            data = request.get_json()

            # Security: check if client tries to override JWT parameters
            if "company_id" in data and str(data["company_id"]) != str(
                company_id
            ):
                logger.warning(
                    "Security: Client attempted to override company_id",
                    jwt_company_id=str(company_id),
                    payload_company_id=str(data.get("company_id")),
                    user_id=user_id,
                )

            if "created_by" in data and str(data["created_by"]) != user_id:
                logger.warning(
                    "Security: Client attempted to override created_by",
                    jwt_user_id=user_id,
                    payload_created_by=str(data.get("created_by")),
                    company_id=str(company_id),
                )

            # Set authoritative values from JWT
            data["company_id"] = str(company_id)
            data["created_by"] = user_id

            schema = ProjectCreateSchema()
            validated_data = schema.load(data)

            # Create project instance
            project = Project(**validated_data)
            project.status = "created"  # Force initial status

            db.session.add(project)

            # Flush to generate project.id before creating history
            db.session.flush()

            # Create history entry for project creation
            history = ProjectHistory(
                project_id=project.id,
                company_id=str(company_id),
                changed_by=str(user_id),
                action="created",
                field_name="status",
                new_value="created",
                comment=f"Project '{validated_data['name']}' created",
            )
            db.session.add(history)

            if not self.commit_or_rollback():
                return error_response("Failed to create project", 500)

            # Manually build response to avoid session issues
            result = {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "company_id": str(project.company_id),
                "customer_id": project.customer_id,
                "created_by": project.created_by,
                "consultation_date": (
                    project.consultation_date.isoformat()
                    if project.consultation_date
                    else None
                ),
                "submission_deadline": (
                    project.submission_deadline.isoformat()
                    if project.submission_deadline
                    else None
                ),
                "contract_amount": (
                    float(project.contract_amount)
                    if project.contract_amount
                    else None
                ),
                "budget_currency": project.budget_currency,
                "created_at": (
                    project.created_at.isoformat()
                    if project.created_at
                    else None
                ),
                "updated_at": (
                    project.updated_at.isoformat()
                    if project.updated_at
                    else None
                ),
            }
            return result, 201

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except Exception as error:
            return self.handle_error(error)


class ProjectResource(BaseResource):
    """Resource for individual project operations."""

    @require_jwt_auth()
    @check_access_required("READ")
    def get(self, project_id):
        """Get project details."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = str(uuid.UUID(g.company_id))

            project = self._get_project(project_id, company_id)
            if not project:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            schema = ProjectSchema()
            return schema.dump(project), 200

        except ValueError as error:
            return self._handle_value_error(error)
        except Exception as error:
            return self.handle_error(error)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def put(self, project_id):
        """Fully update a project."""
        return self._update(project_id, partial=False)

    @require_jwt_auth()
    @check_access_required("UPDATE")
    def patch(self, project_id):
        """Partially update a project."""
        return self._update(project_id, partial=True)

    @require_jwt_auth()
    @check_access_required("DELETE")
    def delete(self, project_id):
        """Delete a project (soft delete)."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = str(uuid.UUID(g.company_id))
            user_id = g.user_id  # Keep as string for external reference

            project = self._get_project(project_id, company_id)
            if not project:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            project.removed_at = datetime.now(timezone.utc)

            history = ProjectHistory(
                project_id=project.id,
                company_id=str(company_id),
                changed_by=str(user_id),
                action="deleted",
                field_name="removed_at",
                new_value=project.removed_at.isoformat(),
            )
            db.session.add(history)

            if not self.commit_or_rollback():
                return error_response("Failed to delete project", 500)

            return "", 204

        except ValueError as error:
            return self._handle_value_error(error)
        except Exception as error:
            return self.handle_error(error)

    def _update(
        self, project_id, partial=False
    ):  # pylint: disable=too-many-locals
        """Internal method to update a project."""
        try:
            validate_uuid(project_id, "project_id")
            company_id = str(uuid.UUID(g.company_id))
            user_id = g.user_id  # Keep as string for external reference

            project = self._get_project(project_id, company_id)
            if not project:
                return error_response(ERROR_PROJECT_NOT_FOUND, 404)

            schema = ProjectUpdateSchema(partial=partial)
            data = schema.load(request.get_json())

            changes = {}
            for field, value in data.items():
                if hasattr(project, field):
                    old_value = getattr(project, field)
                    if old_value != value:
                        changes[field] = {"from": old_value, "to": value}
                        setattr(project, field, value)

            # Seed permissions when project transitions to 'initialized'
            if (
                "status" in changes
                and changes["status"]["to"] == "initialized"
            ):
                seed_project_permissions(project.id, company_id)

            # Create history entries for each changed field
            if changes:
                action = "status_changed" if "status" in changes else "updated"
                for field_name, change in changes.items():
                    # Convert values to string for storage
                    old_val = (
                        str(change["from"])
                        if change["from"] is not None
                        else None
                    )
                    new_val = (
                        str(change["to"]) if change["to"] is not None else None
                    )

                    history = ProjectHistory(
                        project_id=project.id,
                        company_id=str(company_id),
                        changed_by=str(user_id),
                        action=action,
                        field_name=field_name,
                        old_value=old_val,
                        new_value=new_val,
                    )
                    db.session.add(history)

            if not self.commit_or_rollback():
                return error_response("Failed to update project", 500)

            return_schema = ProjectSchema()
            return return_schema.dump(project), 200

        except ValidationError as error:
            return error_response(ERROR_VALIDATION, 400, errors=error.messages)
        except ValueError as error:
            return self._handle_value_error(error)
        except Exception as error:
            return self.handle_error(error)

    @staticmethod
    def _get_project(project_id, company_id):
        """Get project by ID and company."""
        # Ensure string UUIDs for comparison (db.String(36))
        if not isinstance(project_id, str):
            project_id = str(project_id)
        if not isinstance(company_id, str):
            company_id = str(company_id)

        project = Project.query.filter(
            Project.id == project_id, Project.company_id == company_id
        ).first()

        # Check if soft-deleted
        if project and project.removed_at:
            return None

        return project

    @staticmethod
    def _handle_value_error(error):
        """Handle ValueError with appropriate status code."""
        if "UUID" in str(error):
            return error_response(str(error), 400)
        return error_response(str(error), 401)
