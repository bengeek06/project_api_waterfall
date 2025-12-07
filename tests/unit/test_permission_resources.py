# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
tests.unit.test_permission_resources
-------------------------------------

Unit tests for Permission resources (PermissionListResource).

Permissions are READ-ONLY predefined data seeded when project status becomes 'initialized'.

Tests cover:
- Listing permissions (empty list on new project, 10 permissions after initialization)
- Permission categories and names
- No POST/PUT/PATCH/DELETE operations allowed (405 Method Not Allowed)
- Authorization (401 on missing JWT)
"""

import uuid

import pytest

from tests.conftest import create_jwt_token


@pytest.fixture
def auth_client(client):
    """Client with JWT authentication set up."""
    company_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    token = create_jwt_token(company_id, user_id)
    client.set_cookie("access_token", token, domain="localhost")
    client.company_id = company_id
    client.user_id = user_id
    return client


@pytest.fixture
def project(auth_client):
    """Create a test project and return the full project data."""
    payload = {"name": "Test Project", "description": "For permission tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    return response.get_json()


class TestPermissionListResource:
    """Tests for PermissionListResource (GET only - read-only)"""

    def test_get_permissions_empty(self, auth_client, project):
        """Test GET /projects/{project_id}/permissions returns empty list for new project"""
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0  # New project has no permissions yet

    def test_get_permissions_after_initialization(self, auth_client, project):
        """Test GET /projects/{project_id}/permissions returns 10 permissions after initialization"""
        # Initialize the project (transition from 'created' to 'initialized')
        update_response = auth_client.put(
            f"/projects/{project['id']}",
            json={"name": project["name"], "status": "initialized"},
        )
        assert update_response.status_code == 200

        # Get permissions
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 10  # Should have 10 predefined permissions

        # Verify permission structure
        permission_names = [p["name"] for p in data]
        assert "read_files" in permission_names
        assert "write_files" in permission_names
        assert "delete_files" in permission_names
        assert "lock_files" in permission_names
        assert "validate_files" in permission_names
        assert "update_project" in permission_names
        assert "delete_project" in permission_names
        assert "manage_members" in permission_names
        assert "manage_roles" in permission_names
        assert "manage_policies" in permission_names

    def test_get_permissions_categories(self, auth_client, project):
        """Test that permissions are categorized correctly"""
        # Initialize the project
        auth_client.put(
            f"/projects/{project['id']}",
            json={"name": project["name"], "status": "initialized"},
        )

        # Get permissions
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        data = response.get_json()

        # Count by category
        file_ops = [p for p in data if p["category"] == "file_operations"]
        project_ops = [
            p for p in data if p["category"] == "project_operations"
        ]
        member_ops = [p for p in data if p["category"] == "member_operations"]

        assert len(file_ops) == 5
        assert len(project_ops) == 2
        assert len(member_ops) == 3

    def test_get_permissions_project_not_found(self, auth_client):
        """Test GET /projects/{project_id}/permissions with non-existent project"""
        response = auth_client.get(
            "/projects/00000000-0000-0000-0000-000000000000/permissions"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Project not found"

    def test_permissions_ordered_by_category(self, auth_client, project):
        """Test that permissions are returned ordered by category and name"""
        # Initialize the project
        auth_client.put(
            f"/projects/{project['id']}",
            json={"name": project["name"], "status": "initialized"},
        )

        # Get permissions
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        data = response.get_json()

        # Check ordering (file_operations, member_operations, project_operations alphabetically)
        categories = [p["category"] for p in data]

        # Verify all file_operations come before member_operations and project_operations
        file_ops_indices = [
            i for i, cat in enumerate(categories) if cat == "file_operations"
        ]
        member_ops_indices = [
            i for i, cat in enumerate(categories) if cat == "member_operations"
        ]
        project_ops_indices = [
            i
            for i, cat in enumerate(categories)
            if cat == "project_operations"
        ]

        if file_ops_indices and member_ops_indices:
            assert max(file_ops_indices) < min(member_ops_indices)
        if member_ops_indices and project_ops_indices:
            assert max(member_ops_indices) < min(project_ops_indices)

    def test_post_not_allowed(self, auth_client, project):
        """Test POST /projects/{project_id}/permissions returns 405 Method Not Allowed"""
        response = auth_client.post(
            f"/projects/{project['id']}/permissions",
            json={"name": "test_permission"},
        )
        assert response.status_code == 405  # Method Not Allowed

    def test_unauthorized_missing_jwt(self, client):
        """Test GET endpoint requires JWT authentication"""
        project_id = "00000000-0000-0000-0000-000000000000"

        # GET list
        response = client.get(f"/projects/{project_id}/permissions")
        assert response.status_code == 401

    def test_permissions_have_all_required_fields(self, auth_client, project):
        """Test that each permission has all required fields"""
        # Initialize the project
        auth_client.put(
            f"/projects/{project['id']}",
            json={"name": project["name"], "status": "initialized"},
        )

        # Get permissions
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        data = response.get_json()

        for permission in data:
            assert "id" in permission
            assert "name" in permission
            assert "description" in permission
            assert "category" in permission
            assert "project_id" in permission
            assert "company_id" in permission
            assert "created_at" in permission
            assert permission["project_id"] == project["id"]
            assert permission["company_id"] == project["company_id"]
