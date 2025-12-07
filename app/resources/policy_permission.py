# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.resources.policy_permission
--------------------------------

This module implements the Policy-Permission association resources.
Manages the many-to-many relationship between policies and permissions.

A policy can have multiple permissions associated with it, and a permission
can be associated with multiple policies. This allows defining what actions
each policy grants.

Resources:
- PolicyPermissionListResource: GET (list), POST (add association)
- PolicyPermissionResource: DELETE (remove association)
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from app.models.db import db
from app.models.project import Project, ProjectPermission, ProjectPolicy
from app.schemas.project_schema import ProjectPermissionSchema
from app.utils import check_access_required, require_jwt_auth


class PolicyPermissionListResource(Resource):
    """
    Handles operations on the policy-permission association collection.

    GET: List all permissions associated with a policy
    POST: Add a permission to a policy
    """

    @require_jwt_auth()
    @check_access_required("LIST")
    def get(self, project_id, policy_id):
        """
        Get all permissions associated with a specific policy.

        Returns a list of permissions that are currently assigned to the policy.
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return {"error": "Project not found"}, 404

        # Verify policy exists and belongs to project
        policy = db.session.get(ProjectPolicy, policy_id)
        if not policy or policy.project_id != project_id or policy.removed_at:
            return {"error": "Policy not found"}, 404

        # Get associated permissions through the relationship
        # Filter out soft-deleted permissions
        permissions = [p for p in policy.permissions if not p.removed_at]

        # Serialize
        permission_schema = ProjectPermissionSchema(many=True)
        return permission_schema.dump(permissions), 200

    @require_jwt_auth()
    @check_access_required("CREATE")
    def post(self, project_id, policy_id):
        """
        Add a permission to a policy.

        Expects JSON body: {"permission_id": "uuid"}
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return {"error": "Project not found"}, 404

        # Verify policy exists and belongs to project
        policy = db.session.get(ProjectPolicy, policy_id)
        if not policy or policy.project_id != project_id or policy.removed_at:
            return {"error": "Policy not found"}, 404

        # Get permission_id from request
        data = request.get_json()
        if not data or "permission_id" not in data:
            return {"error": "permission_id is required"}, 400

        permission_id = data["permission_id"]

        # Verify permission exists and belongs to project
        permission = db.session.get(ProjectPermission, permission_id)
        if (
            not permission
            or permission.project_id != project_id
            or permission.removed_at
        ):
            return {"error": "Permission not found"}, 404

        # Check if association already exists
        if permission in policy.permissions:
            return {
                "error": "Permission is already assigned to this policy"
            }, 409

        try:
            # Add the association
            policy.permissions.append(permission)
            db.session.commit()

            # Return the added permission
            permission_schema = ProjectPermissionSchema()
            return permission_schema.dump(permission), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


class PolicyPermissionResource(Resource):
    """
    Handles operations on a specific policy-permission association.

    DELETE: Remove a permission from a policy
    """

    @require_jwt_auth()
    @check_access_required("DELETE")
    def delete(self, project_id, policy_id, permission_id):
        """
        Remove a permission from a policy.

        Returns 204 No Content on success.
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return {"error": "Project not found"}, 404

        # Verify policy exists and belongs to project
        policy = db.session.get(ProjectPolicy, policy_id)
        if not policy or policy.project_id != project_id or policy.removed_at:
            return {"error": "Policy not found"}, 404

        # Verify permission exists and belongs to project
        permission = db.session.get(ProjectPermission, permission_id)
        if (
            not permission
            or permission.project_id != project_id
            or permission.removed_at
        ):
            return {"error": "Permission not found"}, 404

        # Check if association exists
        if permission not in policy.permissions:
            return {"error": "Permission is not assigned to this policy"}, 404

        try:
            # Remove the association
            policy.permissions.remove(permission)
            db.session.commit()

            return "", 204

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500
