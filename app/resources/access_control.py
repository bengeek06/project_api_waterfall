"""
app.resources.access_control
-----------------------------

This module implements Access Control endpoints for cross-service authorization.

These endpoints evaluate the complete RBAC permission chain:
User → Member → Role → Policy → Permission

Used by other services to check if a user has permission to perform
specific actions on files or projects.

Resources:
- CheckFileAccessResource: POST /check-file-access (single file authorization)
- CheckProjectAccessResource: POST /check-project-access (single project authorization)
- CheckFileAccessBatchResource: POST /check-file-access-batch (batch file authorization)
- CheckProjectAccessBatchResource: POST /check-project-access-batch (batch project authorization)
"""

from flask import g, request
from flask_restful import Resource
from app.models.db import db
from app.models.project import Project, ProjectMember
from app.utils import require_jwt_auth


class CheckFileAccessResource(Resource):
    """
    Check if user has permission to access files.

    POST: Batch check file access permissions
    Expected JSON body:
    {
        "file_checks": [
            {"file_id": "uuid", "project_id": "uuid", "action": "read_files"},
            {"file_id": "uuid", "project_id": "uuid", "action": "write_files"}
        ]
    }

    Returns:
    {
        "results": [
            {"file_id": "uuid", "project_id": "uuid", "action": "read_files", "allowed": true},
            {"file_id": "uuid", "project_id": "uuid", "action": "write_files", "allowed": false}
        ]
    }
    """

    @require_jwt_auth()
    def post(self):
        """
        Batch check file access permissions for the authenticated user.

        Evaluates the complete permission chain for each file check.
        """
        company_id = g.company_id
        user_id = g.user_id

        data = request.get_json()
        if not data or "file_checks" not in data:
            return {"error": "file_checks array is required"}, 400

        file_checks = data["file_checks"]
        if not isinstance(file_checks, list):
            return {"error": "file_checks must be an array"}, 400

        results = []

        for check in file_checks:
            # Validate check structure
            if not all(
                key in check for key in ["file_id", "project_id", "action"]
            ):
                results.append(
                    {
                        "file_id": check.get("file_id"),
                        "project_id": check.get("project_id"),
                        "action": check.get("action"),
                        "allowed": False,
                        "reason": "Invalid check format",
                    }
                )
                continue

            file_id = check["file_id"]
            project_id = check["project_id"]
            action = check["action"]

            # Check permission
            allowed = self._check_user_permission(
                user_id, company_id, project_id, action
            )

            results.append(
                {
                    "file_id": file_id,
                    "project_id": project_id,
                    "action": action,
                    "allowed": allowed,
                }
            )

        return {"results": results}, 200

    def _check_user_permission(self, user_id, company_id, project_id, action):
        """
        Check if user has permission to perform action on project.

        Evaluates the complete RBAC chain:
        1. Project exists and belongs to company
        2. User is a member of the project
        3. Member has roles
        4. Roles have policies
        5. Policies have the required permission

        Args:
            user_id: User ID
            company_id: Company ID
            project_id: Project ID
            action: Permission action (e.g., 'read_files', 'write_files')

        Returns:
            bool: True if user has permission, False otherwise
        """
        # 1. Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return False

        # 2. Get user's membership in the project
        member = (
            db.session.query(ProjectMember)
            .filter_by(project_id=project_id, user_id=user_id)
            .filter(ProjectMember.removed_at.is_(None))
            .first()
        )

        if not member:
            return False

        # 3. Get member's roles (through member.role relationship)
        role = member.role
        if not role or role.removed_at:
            return False

        # 4. Get policies associated with the role
        policies = [p for p in role.policies if not p.removed_at]

        # 5. Check if any policy has the required permission
        for policy in policies:
            permissions = [p for p in policy.permissions if not p.removed_at]
            for permission in permissions:
                if permission.name == action:
                    return True

        return False


class CheckProjectAccessResource(Resource):
    """
    Check if user has permission to access projects.

    POST: Batch check project access permissions
    Expected JSON body:
    {
        "project_checks": [
            {"project_id": "uuid", "action": "update_project"},
            {"project_id": "uuid", "action": "delete_project"}
        ]
    }

    Returns:
    {
        "results": [
            {"project_id": "uuid", "action": "update_project", "allowed": true},
            {"project_id": "uuid", "action": "delete_project", "allowed": false}
        ]
    }
    """

    @require_jwt_auth()
    def post(self):
        """
        Batch check project access permissions for the authenticated user.

        Evaluates the complete permission chain for each project check.
        """
        company_id = g.company_id
        user_id = g.user_id

        data = request.get_json()
        if not data or "project_checks" not in data:
            return {"error": "project_checks array is required"}, 400

        project_checks = data["project_checks"]
        if not isinstance(project_checks, list):
            return {"error": "project_checks must be an array"}, 400

        results = []

        for check in project_checks:
            # Validate check structure
            if not all(key in check for key in ["project_id", "action"]):
                results.append(
                    {
                        "project_id": check.get("project_id"),
                        "action": check.get("action"),
                        "allowed": False,
                        "reason": "Invalid check format",
                    }
                )
                continue

            project_id = check["project_id"]
            action = check["action"]

            # Check permission
            allowed = self._check_user_permission(
                user_id, company_id, project_id, action
            )

            results.append(
                {
                    "project_id": project_id,
                    "action": action,
                    "allowed": allowed,
                }
            )

        return {"results": results}, 200

    def _check_user_permission(self, user_id, company_id, project_id, action):
        """
        Check if user has permission to perform action on project.

        Evaluates the complete RBAC chain:
        1. Project exists and belongs to company
        2. User is a member of the project
        3. Member has roles
        4. Roles have policies
        5. Policies have the required permission

        Args:
            user_id: User ID
            company_id: Company ID
            project_id: Project ID
            action: Permission action (e.g., 'update_project', 'delete_project')

        Returns:
            bool: True if user has permission, False otherwise
        """
        # 1. Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return False

        # 2. Get user's membership in the project
        member = (
            db.session.query(ProjectMember)
            .filter_by(project_id=project_id, user_id=user_id)
            .filter(ProjectMember.removed_at.is_(None))
            .first()
        )

        if not member:
            return False

        # 3. Get member's role
        role = member.role
        if not role or role.removed_at:
            return False

        # 4. Get policies associated with the role
        policies = [p for p in role.policies if not p.removed_at]

        # 5. Check if any policy has the required permission
        for policy in policies:
            permissions = [p for p in policy.permissions if not p.removed_at]
            for permission in permissions:
                if permission.name == action:
                    return True

        return False


class CheckFileAccessBatchResource(Resource):
    """
    Check if user has permission to access files (batch).

    POST: Batch check file access permissions
    Expected JSON body per OpenAPI spec:
    {
        "checks": [
            {"project_id": "uuid", "action": "read_files"},
            {"project_id": "uuid", "action": "write_files"}
        ]
    }

    Returns:
    {
        "results": [
            {
                "project_id": "uuid",
                "action": "read_files",
                "allowed": true,
                "role": "owner",
                "reason": null
            },
            {
                "project_id": "uuid",
                "action": "write_files",
                "allowed": false,
                "role": "viewer",
                "reason": "Permission denied"
            }
        ]
    }
    """

    @require_jwt_auth()
    def post(self):
        """
        Batch check file access permissions for the authenticated user.

        Evaluates the complete permission chain for each file check.
        """
        company_id = g.company_id
        user_id = g.user_id

        data = request.get_json()
        if not data or "checks" not in data:
            return {"error": "checks array is required"}, 400

        checks = data["checks"]
        if not isinstance(checks, list):
            return {"error": "checks must be an array"}, 400

        results = []

        for check in checks:
            # Validate check structure
            if not all(key in check for key in ["project_id", "action"]):
                results.append(
                    {
                        "project_id": check.get("project_id"),
                        "action": check.get("action"),
                        "allowed": False,
                        "role": None,
                        "reason": "Invalid check format",
                    }
                )
                continue

            project_id = check["project_id"]
            action = check["action"]

            # Check permission and get role info
            allowed, role_name, reason = self._check_user_permission(
                user_id, company_id, project_id, action
            )

            results.append(
                {
                    "project_id": project_id,
                    "action": action,
                    "allowed": allowed,
                    "role": role_name,
                    "reason": reason,
                }
            )

        return {"results": results}, 200

    def _check_user_permission(self, user_id, company_id, project_id, action):
        """
        Check if user has permission to perform action on project.

        Args:
            user_id: User ID
            company_id: Company ID
            project_id: Project ID
            action: Permission action (e.g., 'read_files', 'write_files')

        Returns:
            tuple: (allowed: bool, role_name: str|None, reason: str|None)
        """
        # 1. Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return False, None, "Project not found"

        # 2. Get user's membership in the project
        member = (
            db.session.query(ProjectMember)
            .filter_by(project_id=project_id, user_id=user_id)
            .filter(ProjectMember.removed_at.is_(None))
            .first()
        )

        if not member:
            return False, None, "User is not a member of the project"

        # 3. Get member's role
        role = member.role
        if not role or role.removed_at:
            return False, None, "No valid role assigned"

        # 4. Get policies associated with the role
        policies = [p for p in role.policies if not p.removed_at]

        # 5. Check if any policy has the required permission
        for policy in policies:
            permissions = [p for p in policy.permissions if not p.removed_at]
            for permission in permissions:
                if permission.name == action:
                    return True, role.name, None

        return False, role.name, "Permission denied"


class CheckProjectAccessBatchResource(Resource):
    """
    Check if user has permission to access projects (batch).

    POST: Batch check project access permissions
    Expected JSON body per OpenAPI spec:
    {
        "checks": [
            {"project_id": "uuid", "action": "read"},
            {"project_id": "uuid", "action": "write"}
        ]
    }

    Returns:
    {
        "results": [
            {
                "project_id": "uuid",
                "action": "read",
                "allowed": true,
                "role": "owner",
                "reason": null
            },
            {
                "project_id": "uuid",
                "action": "write",
                "allowed": false,
                "role": "viewer",
                "reason": "Permission denied"
            }
        ]
    }
    """

    @require_jwt_auth()
    def post(self):
        """
        Batch check project access permissions for the authenticated user.

        Evaluates the complete permission chain for each project check.
        """
        company_id = g.company_id
        user_id = g.user_id

        data = request.get_json()
        if not data or "checks" not in data:
            return {"error": "checks array is required"}, 400

        checks = data["checks"]
        if not isinstance(checks, list):
            return {"error": "checks must be an array"}, 400

        results = []

        for check in checks:
            # Validate check structure
            if not all(key in check for key in ["project_id", "action"]):
                results.append(
                    {
                        "project_id": check.get("project_id"),
                        "action": check.get("action"),
                        "allowed": False,
                        "role": None,
                        "reason": "Invalid check format",
                    }
                )
                continue

            project_id = check["project_id"]
            action = check["action"]

            # Check permission and get role info
            allowed, role_name, reason = self._check_user_permission(
                user_id, company_id, project_id, action
            )

            results.append(
                {
                    "project_id": project_id,
                    "action": action,
                    "allowed": allowed,
                    "role": role_name,
                    "reason": reason,
                }
            )

        return {"results": results}, 200

    def _check_user_permission(self, user_id, company_id, project_id, action):
        """
        Check if user has permission to perform action on project.

        Args:
            user_id: User ID
            company_id: Company ID
            project_id: Project ID
            action: Permission action (e.g., 'read', 'write', 'manage')

        Returns:
            tuple: (allowed: bool, role_name: str|None, reason: str|None)
        """
        # 1. Verify project exists and belongs to company
        project = db.session.get(Project, project_id)
        if (
            not project
            or project.company_id != company_id
            or project.removed_at
        ):
            return False, None, "Project not found"

        # 2. Get user's membership in the project
        member = (
            db.session.query(ProjectMember)
            .filter_by(project_id=project_id, user_id=user_id)
            .filter(ProjectMember.removed_at.is_(None))
            .first()
        )

        if not member:
            return False, None, "User is not a member of the project"

        # 3. Get member's role
        role = member.role
        if not role or role.removed_at:
            return False, None, "No valid role assigned"

        # Map generic actions to specific permissions
        action_map = {
            "read": "read_files",
            "write": "write_files",
            "manage": "manage_project",
        }
        permission_name = action_map.get(action, action)

        # 4. Get policies associated with the role
        policies = [p for p in role.policies if not p.removed_at]

        # 5. Check if any policy has the required permission
        for policy in policies:
            permissions = [p for p in policy.permissions if not p.removed_at]
            for permission in permissions:
                if permission.name == permission_name:
                    return True, role.name, None

        return False, role.name, "Permission denied"
