"""
app.resources.role
------------------

REST API resources for ProjectRole management.

Endpoints:
- GET /projects/{project_id}/roles - List project roles
- POST /projects/{project_id}/roles - Create custom role
- GET /projects/{project_id}/roles/{role_id} - Get specific role
- PUT /projects/{project_id}/roles/{role_id} - Update role (full)
- PATCH /projects/{project_id}/roles/{role_id} - Update role (partial)
- DELETE /projects/{project_id}/roles/{role_id} - Delete role

Security:
- All endpoints require JWT authentication
- Create/Update/Delete require RBAC permissions
- Default roles (is_default=True) cannot be modified or deleted
"""

from datetime import datetime, timezone
from flask import request, g
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.models.db import db
from app.models.project import Project, ProjectRole, ProjectMember
from app.schemas.project_schema import (
    ProjectRoleCreateSchema,
    ProjectRoleSchema,
    ProjectRoleUpdateSchema,
)
from app.utils import (
    require_jwt_auth,
    check_access_required,
)


class RoleListResource(Resource):
    """
    Resource for listing project roles and creating new roles.

    GET /projects/{project_id}/roles
    POST /projects/{project_id}/roles
    """

    @require_jwt_auth()
    def get(self, project_id):
        """
        List all roles for a project.

        Returns:
            200: List of roles (excluding soft-deleted)
            404: Project not found
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = Project.query.filter_by(
            id=project_id, company_id=company_id, removed_at=None
        ).first()

        if not project:
            return {"error": "Project not found"}, 404

        # Get all non-deleted roles
        roles = ProjectRole.query.filter_by(
            project_id=project_id, company_id=company_id, removed_at=None
        ).all()

        schema = ProjectRoleSchema(many=True)
        return schema.dump(roles), 200

    @require_jwt_auth()
    @check_access_required("create")
    def post(self, project_id):
        """
        Create a new custom role for the project.

        Request body:
            {
                "name": "string",
                "description": "string"  # Optional
            }

        Returns:
            201: Role created successfully
            400: Validation error
            404: Project not found
            409: Role name already exists in project
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = Project.query.filter_by(
            id=project_id, company_id=company_id, removed_at=None
        ).first()

        if not project:
            return {"error": "Project not found"}, 404

        # Parse and validate request data
        try:
            schema = ProjectRoleCreateSchema()
            data = request.get_json()

            # Inject authoritative values
            data["project_id"] = project_id
            data["company_id"] = company_id
            data["is_default"] = False  # Custom roles are never default

            validated_data = schema.load(data)
        except ValidationError as e:
            return {"errors": e.messages}, 400

        # Check for duplicate role name in project
        existing_role = ProjectRole.query.filter_by(
            project_id=project_id,
            name=validated_data["name"],
            removed_at=None,
        ).first()

        if existing_role:
            return {
                "error": f"Role '{validated_data['name']}' already exists in this project"
            }, 409

        # Create new role
        try:
            role = ProjectRole(**validated_data)
            db.session.add(role)
            db.session.commit()

            schema = ProjectRoleSchema()
            return schema.dump(role), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error"}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class RoleResource(Resource):
    """
    Resource for managing individual project roles.

    GET /projects/{project_id}/roles/{role_id}
    PUT /projects/{project_id}/roles/{role_id}
    PATCH /projects/{project_id}/roles/{role_id}
    DELETE /projects/{project_id}/roles/{role_id}
    """

    @require_jwt_auth()
    def get(self, project_id, role_id):
        """
        Get a specific project role.

        Returns:
            200: Role details
            404: Role not found
        """
        company_id = g.company_id

        role = _get_role(project_id, role_id, company_id)
        if not role:
            return {"error": "Role not found"}, 404

        schema = ProjectRoleSchema()
        return schema.dump(role), 200

    @require_jwt_auth()
    @check_access_required("update")
    def put(self, project_id, role_id):
        """
        Update a project role (full replacement).

        Request body:
            {
                "name": "string",
                "description": "string"
            }

        Returns:
            200: Role updated successfully
            400: Validation error or attempt to modify default role
            404: Role not found
            409: Role name already exists
        """
        return self._update_role(project_id, role_id, partial=False)

    @require_jwt_auth()
    @check_access_required("update")
    def patch(self, project_id, role_id):
        """
        Update a project role (partial update).

        Request body:
            {
                "name": "string",  # Optional
                "description": "string"  # Optional
            }

        Returns:
            200: Role updated successfully
            400: Validation error or attempt to modify default role
            404: Role not found
            409: Role name already exists
        """
        return self._update_role(project_id, role_id, partial=True)

    @require_jwt_auth()
    @check_access_required("delete")
    def delete(self, project_id, role_id):
        """
        Delete a role from the project (soft delete).

        Returns:
            204: Role deleted successfully
            400: Cannot delete default role or role in use
            404: Role not found
        """
        company_id = g.company_id

        role = _get_role(project_id, role_id, company_id)
        if not role:
            return {"error": "Role not found"}, 404

        # Protect default roles from deletion
        if role.is_default:
            return {
                "error": "Cannot delete default role",
                "detail": "Default roles (owner, validator, contributor, viewer) cannot be deleted",
            }, 400

        # Check if role is in use by any members
        members_using_role = ProjectMember.query.filter_by(
            role_id=role_id, removed_at=None
        ).count()

        if members_using_role > 0:
            return {
                "error": "Cannot delete role",
                "detail": f"Role is currently assigned to {members_using_role} member(s)",
            }, 400

        # Soft delete
        try:
            role.removed_at = datetime.now(timezone.utc)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def _update_role(self, project_id, role_id, partial=False):
        """
        Helper method to update a role.

        Args:
            project_id: Project ID
            role_id: Role ID
            partial: If True, allow partial updates (PATCH), else require all fields (PUT)

        Returns:
            Tuple of (response_data, status_code)
        """
        company_id = g.company_id

        role = _get_role(project_id, role_id, company_id)
        if not role:
            return {"error": "Role not found"}, 404

        # Protect default roles from modification
        if role.is_default:
            return {
                "error": "Cannot modify default role",
                "detail": (
                    "Default roles (owner, validator, contributor, viewer) "
                    "cannot be modified"
                ),
            }, 400

        # Parse and validate request data
        try:
            schema = ProjectRoleUpdateSchema(partial=partial)
            data = request.get_json()
            validated_data = schema.load(data)
        except ValidationError as e:
            return {"errors": e.messages}, 400

        # If name is being updated, check for duplicates
        if "name" in validated_data and validated_data["name"] != role.name:
            existing_role = ProjectRole.query.filter_by(
                project_id=project_id,
                name=validated_data["name"],
                removed_at=None,
            ).first()

            if existing_role:
                return {
                    "error": f"Role '{validated_data['name']}' already exists in this project"
                }, 409

        # Update role fields
        try:
            for key, value in validated_data.items():
                setattr(role, key, value)

            db.session.commit()

            schema = ProjectRoleSchema()
            return schema.dump(role), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


def _get_role(project_id, role_id, company_id):
    """
    Helper function to retrieve a non-deleted role.

    Args:
        project_id: Project ID
        role_id: Role ID
        company_id: Company ID from JWT

    Returns:
        ProjectRole instance or None
    """
    return ProjectRole.query.filter_by(
        id=role_id,
        project_id=project_id,
        company_id=company_id,
        removed_at=None,
    ).first()
