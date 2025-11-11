"""
app.resources.policy
--------------------

This module implements the Policy resources for the Project Service API.
Handles CRUD operations for project policies with RBAC protection.

Policies group related permissions together and are assigned to roles.
Example: "File Management" policy groups read_files, write_files, delete_files permissions.

Protection mechanisms:
- Cannot delete policies that are assigned to roles (referential integrity)
- Duplicate policy names within a project return 409 Conflict
- All operations require JWT authentication and RBAC authorization

Resources:
- PolicyListResource: GET (list), POST (create)
- PolicyResource: GET (retrieve), PUT (full update), PATCH (partial update), DELETE (soft delete)
"""

from datetime import datetime, timezone
from flask import request, g
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models.db import db
from app.models.project import ProjectPolicy, Project, role_policy_association
from app.schemas.project_schema import (
    ProjectPolicySchema,
    ProjectPolicyCreateSchema,
    ProjectPolicyUpdateSchema,
)
from app.utils import require_jwt_auth, check_access_required


class PolicyListResource(Resource):
    """
    Resource for listing and creating project policies.

    GET /projects/{project_id}/policies
    - Returns list of all policies for a project
    - Filters out soft-deleted policies
    - Requires JWT authentication and RBAC authorization

    POST /projects/{project_id}/policies
    - Creates a new policy for a project
    - Validates required fields (name)
    - Prevents duplicate policy names within a project
    - Auto-injects project_id and company_id
    - Requires JWT authentication and RBAC authorization
    """

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def get(self, project_id):
        """
        List all policies for a project.

        Returns:
            200: List of policies
            404: Project not found
        """
        try:
            company_id = g.company_id

            # Verify project exists and belongs to company
            project = Project.query.filter_by(
                id=project_id, company_id=company_id, removed_at=None
            ).first()

            if not project:
                return {"error": "Project not found"}, 404

            # Get all policies for project (filter soft-deleted)
            policies = ProjectPolicy.query.filter_by(
                project_id=project_id, company_id=company_id, removed_at=None
            ).all()

            schema = ProjectPolicySchema(many=True)
            return schema.dump(policies), 200

        except Exception as e:
            return {
                "error": "Failed to retrieve policies",
                "detail": str(e),
            }, 500

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def post(self, project_id):
        """
        Create a new policy for a project.

        Required fields:
        - name: Policy name (unique within project)

        Optional fields:
        - description: Policy description

        Returns:
            201: Policy created successfully
            400: Invalid input data
            404: Project not found
            409: Policy name already exists in project
        """
        try:
            company_id = g.company_id

            # Verify project exists and belongs to company
            project = Project.query.filter_by(
                id=project_id, company_id=company_id, removed_at=None
            ).first()

            if not project:
                return {"error": "Project not found"}, 404

            # Parse and validate input
            schema = ProjectPolicyCreateSchema()
            try:
                data = schema.load(request.get_json())
            except ValidationError as err:
                return {
                    "error": "Invalid input data",
                    "detail": err.messages,
                }, 400

            # Check for duplicate policy name in project
            existing_policy = ProjectPolicy.query.filter_by(
                project_id=project_id, name=data["name"], removed_at=None
            ).first()

            if existing_policy:
                return {
                    "error": "Policy name already exists in this project",
                    "detail": f"A policy named '{data['name']}' already exists",
                }, 409

            # Create new policy with authoritative values
            policy = ProjectPolicy(
                project_id=project_id,
                company_id=company_id,
                name=data["name"],
                description=data.get("description"),
            )

            db.session.add(policy)
            db.session.commit()

            # Return created policy
            response_schema = ProjectPolicySchema()
            return response_schema.dump(policy), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "detail": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to create policy", "detail": str(e)}, 500


class PolicyResource(Resource):
    """
    Resource for retrieving, updating, and deleting individual policies.

    GET /projects/{project_id}/policies/{policy_id}
    - Returns a single policy by ID
    - Requires JWT authentication and RBAC authorization

    PUT /projects/{project_id}/policies/{policy_id}
    - Full replacement update of a policy
    - Validates all fields
    - Prevents duplicate policy names within a project
    - Requires JWT authentication and RBAC authorization

    PATCH /projects/{project_id}/policies/{policy_id}
    - Partial update of a policy
    - Only updates provided fields
    - Prevents duplicate policy names within a project
    - Requires JWT authentication and RBAC authorization

    DELETE /projects/{project_id}/policies/{policy_id}
    - Soft deletes a policy
    - Prevents deletion if policy is assigned to any roles
    - Requires JWT authentication and RBAC authorization
    """

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def get(self, project_id, policy_id):
        """
        Retrieve a single policy by ID.

        Returns:
            200: Policy details
            404: Policy not found
        """
        try:
            company_id = g.company_id

            policy = self._get_policy(policy_id, project_id, company_id)
            if not policy:
                return {"error": "Policy not found"}, 404

            schema = ProjectPolicySchema()
            return schema.dump(policy), 200

        except Exception as e:
            return {
                "error": "Failed to retrieve policy",
                "detail": str(e),
            }, 500

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def put(self, project_id, policy_id):
        """
        Full replacement update of a policy.

        Required fields:
        - name: Policy name

        Optional fields:
        - description: Policy description

        Returns:
            200: Policy updated successfully
            400: Invalid input data
            404: Policy not found
            409: Policy name already exists in project
        """
        return self._update_policy(project_id, policy_id, partial=False)

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def patch(self, project_id, policy_id):
        """
        Partial update of a policy.

        Optional fields:
        - name: Policy name
        - description: Policy description

        Returns:
            200: Policy updated successfully
            400: Invalid input data
            404: Policy not found
            409: Policy name already exists in project
        """
        return self._update_policy(project_id, policy_id, partial=True)

    @require_jwt_auth()
    @check_access_required("manage_policies")
    def delete(self, project_id, policy_id):
        """
        Soft delete a policy.

        Protection: Cannot delete policies assigned to roles.

        Returns:
            204: Policy deleted successfully
            400: Policy is in use by roles
            404: Policy not found
        """
        try:
            company_id = g.company_id

            policy = self._get_policy(policy_id, project_id, company_id)
            if not policy:
                return {"error": "Policy not found"}, 404

            # Check if policy is assigned to any roles
            role_count = (
                db.session.query(role_policy_association)
                .filter_by(policy_id=policy_id)
                .count()
            )

            if role_count > 0:
                return {
                    "error": "Cannot delete policy that is assigned to roles",
                    "detail": (
                        f"This policy is currently assigned to {role_count} "
                        f"role(s). Remove the policy from all roles before "
                        f"deleting."
                    ),
                }, 400

            # Soft delete the policy
            policy.removed_at = datetime.now(timezone.utc)
            db.session.commit()

            return "", 204

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "detail": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to delete policy", "detail": str(e)}, 500

    def _update_policy(self, project_id, policy_id, partial=True):
        """
        Helper method to update a policy (shared by PUT and PATCH).

        Args:
            project_id: Project ID from URL
            policy_id: Policy ID from URL
            partial: If True, allows partial updates (PATCH). If False, requires all fields (PUT).

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            company_id = g.company_id

            policy = self._get_policy(policy_id, project_id, company_id)
            if not policy:
                return {"error": "Policy not found"}, 404

            # Parse and validate input
            schema = ProjectPolicyUpdateSchema(partial=partial)
            try:
                data = schema.load(request.get_json())
            except ValidationError as err:
                return {
                    "error": "Invalid input data",
                    "detail": err.messages,
                }, 400

            # Check for duplicate policy name if name is being changed
            if "name" in data and data["name"] != policy.name:
                existing_policy = ProjectPolicy.query.filter_by(
                    project_id=project_id, name=data["name"], removed_at=None
                ).first()

                if existing_policy:
                    return {
                        "error": "Policy name already exists in this project",
                        "detail": f"A policy named '{data['name']}' already exists",
                    }, 409

            # Update policy fields
            if "name" in data:
                policy.name = data["name"]
            if "description" in data:
                policy.description = data["description"]

            db.session.commit()

            # Return updated policy
            response_schema = ProjectPolicySchema()
            return response_schema.dump(policy), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "detail": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": "Failed to update policy", "detail": str(e)}, 500

    @staticmethod
    def _get_policy(policy_id, project_id, company_id):
        """
        Helper method to retrieve a policy with authorization checks.

        Args:
            policy_id: Policy ID
            project_id: Project ID (for authorization)
            company_id: Company ID (for multi-tenancy)

        Returns:
            ProjectPolicy object or None
        """
        return ProjectPolicy.query.filter_by(
            id=policy_id,
            project_id=project_id,
            company_id=company_id,
            removed_at=None,
        ).first()
