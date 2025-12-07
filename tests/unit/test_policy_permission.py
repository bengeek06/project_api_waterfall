# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
tests.unit.test_policy_permission
----------------------------------

Unit tests for Policy-Permission association resources.

Tests cover:
- Listing associated permissions (empty list, with associations)
- Creating associations (valid, duplicate, invalid IDs)
- Removing associations (success, not found, non-existent association)
- Cross-project validation (cannot associate permissions from different projects)
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
    payload = {"name": "Test Project", "description": "For association tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    project_data = response.get_json()

    # Initialize project to seed permissions
    response = auth_client.patch(
        f"/projects/{project_data['id']}", json={"status": "initialized"}
    )
    assert response.status_code == 200

    return project_data


@pytest.fixture
def policy(auth_client, project):
    """Create a test policy."""
    payload = {"name": "Test Policy", "description": "Test policy"}
    response = auth_client.post(
        f"/projects/{project['id']}/policies", json=payload
    )
    assert response.status_code == 201
    return response.get_json()


@pytest.fixture
def permission(auth_client, project):
    """Get a seeded permission (project is already initialized)."""
    response = auth_client.get(f"/projects/{project['id']}/permissions")
    assert response.status_code == 200
    permissions = response.get_json()
    assert len(permissions) > 0
    return permissions[0]  # Return first permission


class TestPolicyPermissionListResource:
    """Tests for PolicyPermissionListResource (GET, POST)"""

    def test_get_permissions_empty(self, auth_client, project, policy):
        """Test GET returns empty list when no permissions are associated"""
        response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_add_permission_association(
        self, auth_client, project, policy, permission
    ):
        """Test POST creates association between policy and permission"""
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission["id"]},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["id"] == permission["id"]
        assert data["name"] == permission["name"]

    def test_get_permissions_after_association(
        self, auth_client, project, policy, permission
    ):
        """Test GET returns associated permissions"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission["id"]},
        )

        # Get associated permissions
        response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["id"] == permission["id"]

    def test_add_duplicate_association(
        self, auth_client, project, policy, permission
    ):
        """Test POST returns 409 when trying to create duplicate association"""
        # Create first association
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission["id"]},
        )
        assert response.status_code == 201

        # Try to create duplicate
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission["id"]},
        )
        assert response.status_code == 409
        data = response.get_json()
        assert "already" in data["error"].lower()

    def test_add_permission_missing_id(self, auth_client, project, policy):
        """Test POST returns 400 when permission_id is missing"""
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_permission_not_found(self, auth_client, project, policy):
        """Test POST returns 404 when permission doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": fake_id},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_add_permission_from_different_project(
        self, auth_client, project, policy
    ):
        """Test POST returns 404 when permission belongs to different project"""
        # Create another project and initialize it to seed permissions
        other_project_response = auth_client.post(
            "/projects", json={"name": "Other Project"}
        )
        other_project = other_project_response.get_json()

        # Initialize the other project to seed permissions
        auth_client.patch(
            f"/projects/{other_project['id']}", json={"status": "initialized"}
        )

        # Get permission from other project
        permissions_response = auth_client.get(
            f"/projects/{other_project['id']}/permissions"
        )
        other_permissions = permissions_response.get_json()
        other_permission = other_permissions[0]

        # Try to associate it with policy from first project
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": other_permission["id"]},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_policy_not_found(self, auth_client, project):
        """Test GET/POST returns 404 when policy doesn't exist"""
        fake_policy_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{project['id']}/policies/{fake_policy_id}/permissions"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{project['id']}/policies/{fake_policy_id}/permissions",
            json={"permission_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_project_not_found(self, auth_client):
        """Test GET/POST returns 404 when project doesn't exist"""
        fake_project_id = str(uuid.uuid4())
        fake_policy_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{fake_project_id}/policies/{fake_policy_id}/permissions"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{fake_project_id}/policies/{fake_policy_id}/permissions",
            json={"permission_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_multiple_permissions_association(
        self, auth_client, project, policy
    ):
        """Test that a policy can have multiple permissions"""
        # Get two seeded permissions
        response = auth_client.get(f"/projects/{project['id']}/permissions")
        permissions = response.get_json()
        assert len(permissions) >= 2
        permission1 = permissions[0]
        permission2 = permissions[1]

        # Associate both with policy
        auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission1["id"]},
        )
        auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission2["id"]},
        )

        # Get all associated permissions
        response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions"
        )
        data = response.get_json()
        assert len(data) == 2
        permission_ids = [p["id"] for p in data]
        assert permission1["id"] in permission_ids
        assert permission2["id"] in permission_ids


class TestPolicyPermissionResource:
    """Tests for PolicyPermissionResource (DELETE)"""

    def test_remove_association(
        self, auth_client, project, policy, permission
    ):
        """Test DELETE removes association between policy and permission"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions",
            json={"permission_id": permission["id"]},
        )

        # Remove association
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions/{permission['id']}"
        )
        assert response.status_code == 204

        # Verify association is removed
        get_response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions"
        )
        data = get_response.get_json()
        assert len(data) == 0

    def test_remove_non_existent_association(
        self, auth_client, project, policy, permission
    ):
        """Test DELETE returns 404 when association doesn't exist"""
        # Don't create association, just try to delete
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions/{permission['id']}"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not assigned" in data["error"].lower()

    def test_remove_association_permission_not_found(
        self, auth_client, project, policy
    ):
        """Test DELETE returns 404 when permission doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{policy['id']}/permissions/{fake_id}"
        )
        assert response.status_code == 404

    def test_remove_association_policy_not_found(
        self, auth_client, project, permission
    ):
        """Test DELETE returns 404 when policy doesn't exist"""
        fake_policy_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{fake_policy_id}/permissions/{permission['id']}"
        )
        assert response.status_code == 404

    def test_unauthorized_missing_jwt(self, client):
        """Test all endpoints require JWT authentication"""
        project_id = str(uuid.uuid4())
        policy_id = str(uuid.uuid4())
        permission_id = str(uuid.uuid4())

        # GET list
        response = client.get(
            f"/projects/{project_id}/policies/{policy_id}/permissions"
        )
        assert response.status_code == 401

        # POST create
        response = client.post(
            f"/projects/{project_id}/policies/{policy_id}/permissions",
            json={"permission_id": permission_id},
        )
        assert response.status_code == 401

        # DELETE remove
        response = client.delete(
            f"/projects/{project_id}/policies/{policy_id}/permissions/{permission_id}"
        )
        assert response.status_code == 401
