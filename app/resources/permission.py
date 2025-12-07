# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.resources.permission
-------------------------

This module implements the Permission resources for the Project Service API.
Handles READ-ONLY operations for project permissions.

Permissions are predefined and seeded automatically when a project is initialized.
They cannot be created, updated, or deleted via the API.

10 Predefined Permissions:
File Operations:
- read_files: Read files in Storage Service
- write_files: Write/upload files in Storage Service
- delete_files: Delete files in Storage Service
- lock_files: Lock files in Storage Service
- validate_files: Validate files in Storage Service

Project Operations:
- update_project: Update project metadata
- delete_project: Delete/archive project

Member Operations:
- manage_members: Add/remove project members
- manage_roles: Create/modify project roles
- manage_policies: Create/modify project policies

Resources:
- PermissionListResource: GET (list only) - READ-ONLY
"""

from flask import g
from flask_restful import Resource

from app.models.db import db
from app.models.project import Project, ProjectPermission
from app.schemas.project_schema import ProjectPermissionSchema
from app.utils import check_access_required, require_jwt_auth


class PermissionListResource(Resource):
    """
    Resource for listing project permissions (READ-ONLY).

    GET /projects/{project_id}/permissions
    - Returns list of all permissions for a project
    - Filters out soft-deleted permissions
    - Requires JWT authentication and RBAC authorization

    NOTE: Permissions are read-only. No POST/PUT/PATCH/DELETE operations allowed.
    Permissions are seeded automatically when project status transitions to 'initialized'.
    """

    @require_jwt_auth()
    @check_access_required("list")  # Same permission as policies
    def get(self, project_id):
        """
        List all permissions for a project.

        Returns:
            200: List of permissions
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

            # Get all permissions for project (filter soft-deleted)
            permissions = (
                ProjectPermission.query.filter_by(
                    project_id=project_id,
                    company_id=company_id,
                    removed_at=None,
                )
                .order_by(ProjectPermission.category, ProjectPermission.name)
                .all()
            )

            schema = ProjectPermissionSchema(many=True)
            return schema.dump(permissions), 200

        except Exception as e:
            return {
                "error": "Failed to retrieve permissions",
                "detail": str(e),
            }, 500


def seed_project_permissions(project_id, company_id):
    """
    Seed the 10 predefined permissions for a project.

    This function should be called when a project transitions to 'initialized' status.

    Args:
        project_id: The project ID to seed permissions for
        company_id: The company ID for multi-tenancy

    Returns:
        List of created ProjectPermission objects
    """
    # Define the 10 predefined permissions
    predefined_permissions = [
        # File Operations (5)
        {
            "name": "read_files",
            "description": "Read files in Storage Service",
            "category": "file_operations",
        },
        {
            "name": "write_files",
            "description": "Write/upload files in Storage Service",
            "category": "file_operations",
        },
        {
            "name": "delete_files",
            "description": "Delete files in Storage Service",
            "category": "file_operations",
        },
        {
            "name": "lock_files",
            "description": "Lock files in Storage Service",
            "category": "file_operations",
        },
        {
            "name": "validate_files",
            "description": "Validate files in Storage Service",
            "category": "file_operations",
        },
        # Project Operations (2)
        {
            "name": "update_project",
            "description": "Update project metadata",
            "category": "project_operations",
        },
        {
            "name": "delete_project",
            "description": "Delete/archive project",
            "category": "project_operations",
        },
        # Member Operations (3)
        {
            "name": "manage_members",
            "description": "Add/remove project members",
            "category": "member_operations",
        },
        {
            "name": "manage_roles",
            "description": "Create/modify project roles",
            "category": "member_operations",
        },
        {
            "name": "manage_policies",
            "description": "Create/modify project policies",
            "category": "member_operations",
        },
    ]

    created_permissions = []

    for perm_data in predefined_permissions:
        # Check if permission already exists (avoid duplicates)
        existing = ProjectPermission.query.filter_by(
            project_id=project_id, name=perm_data["name"], removed_at=None
        ).first()

        if not existing:
            permission = ProjectPermission(
                project_id=project_id,
                company_id=company_id,
                name=perm_data["name"],
                description=perm_data["description"],
                category=perm_data["category"],
            )
            db.session.add(permission)
            created_permissions.append(permission)

    db.session.commit()
    return created_permissions
