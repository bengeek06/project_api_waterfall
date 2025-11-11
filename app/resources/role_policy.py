"""
app.resources.role_policy
--------------------------

This module implements the Role-Policy association resources.
Manages the many-to-many relationship between roles and policies.

A role can have multiple policies associated with it, and a policy
can be associated with multiple roles. This allows defining permissions
for roles by grouping policies.

Resources:
- RolePolicyListResource: GET (list), POST (add association)
- RolePolicyResource: DELETE (remove association)
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from app.models.db import db
from app.models.project import Project, ProjectRole, ProjectPolicy
from app.schemas.project_schema import ProjectPolicySchema
from app.utils import require_jwt_auth, check_access_required


class RolePolicyListResource(Resource):
    """
    Handles operations on the role-policy association collection.

    GET: List all policies associated with a role
    POST: Add a policy to a role
    """

    @require_jwt_auth()
    @check_access_required("update_project")
    def get(self, project_id, role_id):
        """
        Get all policies associated with a specific role.

        Returns a list of policies that are currently assigned to the role.
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

        # Verify role exists and belongs to project
        role = db.session.get(ProjectRole, role_id)
        if not role or role.project_id != project_id or role.removed_at:
            return {"error": "Role not found"}, 404

        # Get associated policies through the relationship
        # Filter out soft-deleted policies
        policies = [p for p in role.policies if not p.removed_at]

        # Serialize
        policy_schema = ProjectPolicySchema(many=True)
        return policy_schema.dump(policies), 200

    @require_jwt_auth()
    @check_access_required("update_project")
    def post(self, project_id, role_id):
        """
        Add a policy to a role.

        Expects JSON body: {"policy_id": "uuid"}
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

        # Verify role exists and belongs to project
        role = db.session.get(ProjectRole, role_id)
        if not role or role.project_id != project_id or role.removed_at:
            return {"error": "Role not found"}, 404

        # Get policy_id from request
        data = request.get_json()
        if not data or "policy_id" not in data:
            return {"error": "policy_id is required"}, 400

        policy_id = data["policy_id"]

        # Verify policy exists and belongs to project
        policy = db.session.get(ProjectPolicy, policy_id)
        if not policy or policy.project_id != project_id or policy.removed_at:
            return {"error": "Policy not found"}, 404

        # Check if association already exists
        if policy in role.policies:
            return {"error": "Policy is already assigned to this role"}, 409

        try:
            # Add the association
            role.policies.append(policy)
            db.session.commit()

            # Return the added policy
            policy_schema = ProjectPolicySchema()
            return policy_schema.dump(policy), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500


class RolePolicyResource(Resource):
    """
    Handles operations on a specific role-policy association.

    DELETE: Remove a policy from a role
    """

    @require_jwt_auth()
    @check_access_required("update_project")
    def delete(self, project_id, role_id, policy_id):
        """
        Remove a policy from a role.

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

        # Verify role exists and belongs to project
        role = db.session.get(ProjectRole, role_id)
        if not role or role.project_id != project_id or role.removed_at:
            return {"error": "Role not found"}, 404

        # Verify policy exists and belongs to project
        policy = db.session.get(ProjectPolicy, policy_id)
        if not policy or policy.project_id != project_id or policy.removed_at:
            return {"error": "Policy not found"}, 404

        # Check if association exists
        if policy not in role.policies:
            return {"error": "Policy is not assigned to this role"}, 404

        try:
            # Remove the association
            role.policies.remove(policy)
            db.session.commit()

            return "", 204

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}, 500
