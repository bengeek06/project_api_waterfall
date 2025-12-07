# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.resources.member
--------------------

REST API resources for ProjectMember management.

Endpoints:
- GET /projects/{project_id}/members - List project members
- POST /projects/{project_id}/members - Add member to project
- GET /projects/{project_id}/members/{user_id} - Get specific member
- PUT /projects/{project_id}/members/{user_id} - Update member (full)
- PATCH /projects/{project_id}/members/{user_id} - Update member (partial)
- DELETE /projects/{project_id}/members/{user_id} - Remove member from project

Security:
- All endpoints require JWT authentication
- Create/Update/Delete require RBAC permissions
"""

from datetime import datetime, timezone

from flask import g, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.models.db import db
from app.models.project import Project, ProjectMember, ProjectRole
from app.schemas.project_schema import (
    ProjectMemberCreateSchema,
    ProjectMemberSchema,
    ProjectMemberUpdateSchema,
)
from app.utils import check_access_required, require_jwt_auth


class MemberListResource(Resource):
    """
    Resource for listing project members and adding new members.

    GET /projects/{project_id}/members
    POST /projects/{project_id}/members
    """

    @require_jwt_auth()
    def get(self, project_id):
        """
        List all members of a project.

        Returns:
            200: List of members (excluding soft-deleted)
            404: Project not found
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = Project.query.filter_by(
            id=project_id, company_id=company_id, removed_at=None
        ).first()

        if not project:
            return {"error": "Project not found"}, 404

        # Get all non-deleted members
        members = ProjectMember.query.filter_by(
            project_id=project_id, company_id=company_id, removed_at=None
        ).all()

        schema = ProjectMemberSchema(many=True)
        return schema.dump(members), 200

    @require_jwt_auth()
    @check_access_required("create")
    def post(self, project_id):
        """
        Add a new member to the project.

        Request body:
            {
                "user_id": "uuid",
                "role_id": "uuid"
            }

        Returns:
            201: Member added successfully
            400: Validation error
            404: Project or role not found
            409: Member already exists
        """
        company_id = g.company_id
        added_by = g.user_id

        # Verify project exists and belongs to company
        project = Project.query.filter_by(
            id=project_id, company_id=company_id, removed_at=None
        ).first()

        if not project:
            return {"error": "Project not found"}, 404

        # Parse and validate request data
        try:
            schema = ProjectMemberCreateSchema()
            data = request.get_json()

            # Inject authoritative values (project_id, company_id, added_by)
            data["project_id"] = project_id
            data["company_id"] = company_id
            data["added_by"] = added_by

            validated_data = schema.load(data)
        except ValidationError as e:
            return {"errors": e.messages}, 400

        # Verify role exists and belongs to this project
        role = ProjectRole.query.filter_by(
            id=validated_data["role_id"],
            project_id=project_id,
            company_id=company_id,
            removed_at=None,
        ).first()

        if not role:
            return {"error": "Role not found"}, 404

        # Check if member already exists (including soft-deleted)
        existing_member = ProjectMember.query.filter_by(
            project_id=project_id, user_id=validated_data["user_id"]
        ).first()

        if existing_member and existing_member.removed_at is None:
            return {"error": "Member already exists in this project"}, 409

        # If member was previously removed, restore instead of creating new
        if existing_member and existing_member.removed_at is not None:
            existing_member.removed_at = None
            existing_member.role_id = validated_data["role_id"]
            existing_member.added_by = added_by
            db.session.commit()
            schema = ProjectMemberSchema()
            return schema.dump(existing_member), 201

        # Create new member
        try:
            member = ProjectMember(**validated_data)
            db.session.add(member)
            db.session.commit()

            schema = ProjectMemberSchema()
            return schema.dump(member), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error"}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class MemberResource(Resource):
    """
    Resource for managing individual project members.

    GET /projects/{project_id}/members/{user_id}
    PUT /projects/{project_id}/members/{user_id}
    PATCH /projects/{project_id}/members/{user_id}
    DELETE /projects/{project_id}/members/{user_id}
    """

    @require_jwt_auth()
    def get(self, project_id, user_id):
        """
        Get a specific project member.

        Returns:
            200: Member details
            404: Member not found
        """
        company_id = g.company_id

        member = _get_member(project_id, user_id, company_id)
        if not member:
            return {"error": "Member not found"}, 404

        schema = ProjectMemberSchema()
        return schema.dump(member), 200

    @require_jwt_auth()
    @check_access_required("update")
    def put(self, project_id, user_id):
        """
        Update a project member (full replacement).

        Request body:
            {
                "role_id": "uuid"
            }

        Returns:
            200: Member updated successfully
            400: Validation error
            404: Member or role not found
        """
        return self._update_member(project_id, user_id, partial=False)

    @require_jwt_auth()
    @check_access_required("update")
    def patch(self, project_id, user_id):
        """
        Update a project member (partial update).

        Request body:
            {
                "role_id": "uuid"  # Optional
            }

        Returns:
            200: Member updated successfully
            400: Validation error
            404: Member or role not found
        """
        return self._update_member(project_id, user_id, partial=True)

    @require_jwt_auth()
    @check_access_required("delete")
    def delete(self, project_id, user_id):
        """
        Remove a member from the project (soft delete).

        Returns:
            204: Member removed successfully
            404: Member not found
        """
        company_id = g.company_id

        member = _get_member(project_id, user_id, company_id)
        if not member:
            return {"error": "Member not found"}, 404

        # Soft delete
        try:
            member.removed_at = datetime.now(timezone.utc)
            db.session.commit()
            return "", 204
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def _update_member(self, project_id, user_id, partial=False):
        """
        Helper method to update a member.

        Args:
            project_id: Project ID
            user_id: User ID
            partial: If True, allow partial updates (PATCH), else require all fields (PUT)

        Returns:
            Tuple of (response_data, status_code)
        """
        company_id = g.company_id

        member = _get_member(project_id, user_id, company_id)
        if not member:
            return {"error": "Member not found"}, 404

        # Parse and validate request data
        try:
            schema = ProjectMemberUpdateSchema(partial=partial)
            data = request.get_json()
            validated_data = schema.load(data)
        except ValidationError as e:
            return {"errors": e.messages}, 400

        # If role_id is being updated, verify it exists and belongs to project
        if "role_id" in validated_data:
            role = ProjectRole.query.filter_by(
                id=validated_data["role_id"],
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()

            if not role:
                return {"error": "Role not found"}, 404

        # Update member fields
        try:
            for key, value in validated_data.items():
                setattr(member, key, value)

            db.session.commit()

            schema = ProjectMemberSchema()
            return schema.dump(member), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


def _get_member(project_id, user_id, company_id):
    """
    Helper function to retrieve a non-deleted member.

    Args:
        project_id: Project ID
        user_id: User ID
        company_id: Company ID from JWT

    Returns:
        ProjectMember instance or None
    """
    return ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id,
        company_id=company_id,
        removed_at=None,
    ).first()
