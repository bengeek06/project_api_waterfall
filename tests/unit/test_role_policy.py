"""
tests.unit.test_role_policy
----------------------------

Unit tests for Role-Policy association resources.

Tests cover:
- Listing associated policies (empty list, with associations)
- Creating associations (valid, duplicate, invalid IDs)
- Removing associations (success, not found, non-existent association)
- Cross-project validation (cannot associate policies from different projects)
- Authorization (401 on missing JWT)
"""

import pytest
import uuid
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
    return response.get_json()


@pytest.fixture
def role(auth_client, project):
    """Create a test role."""
    payload = {"name": "Test Role", "description": "Test role"}
    response = auth_client.post(f"/projects/{project['id']}/roles", json=payload)
    assert response.status_code == 201
    return response.get_json()


@pytest.fixture
def policy(auth_client, project):
    """Create a test policy."""
    payload = {"name": "Test Policy", "description": "Test policy"}
    response = auth_client.post(f"/projects/{project['id']}/policies", json=payload)
    assert response.status_code == 201
    return response.get_json()


class TestRolePolicyListResource:
    """Tests for RolePolicyListResource (GET, POST)"""

    def test_get_policies_empty(self, auth_client, project, role):
        """Test GET returns empty list when no policies are associated"""
        response = auth_client.get(
            f"/projects/{project['id']}/roles/{role['id']}/policies"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_add_policy_association(self, auth_client, project, role, policy):
        """Test POST creates association between role and policy"""
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy["id"]},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["id"] == policy["id"]
        assert data["name"] == policy["name"]

    def test_get_policies_after_association(self, auth_client, project, role, policy):
        """Test GET returns associated policies"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy["id"]},
        )

        # Get associated policies
        response = auth_client.get(
            f"/projects/{project['id']}/roles/{role['id']}/policies"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["id"] == policy["id"]

    def test_add_duplicate_association(self, auth_client, project, role, policy):
        """Test POST returns 409 when trying to create duplicate association"""
        # Create first association
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy["id"]},
        )
        assert response.status_code == 201

        # Try to create duplicate
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy["id"]},
        )
        assert response.status_code == 409
        data = response.get_json()
        assert "already" in data["error"].lower()

    def test_add_policy_missing_id(self, auth_client, project, role):
        """Test POST returns 400 when policy_id is missing"""
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_policy_not_found(self, auth_client, project, role):
        """Test POST returns 404 when policy doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": fake_id},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_add_policy_from_different_project(self, auth_client, project, role):
        """Test POST returns 404 when policy belongs to different project"""
        # Create another project
        other_project_response = auth_client.post(
            "/projects", json={"name": "Other Project"}
        )
        other_project = other_project_response.get_json()

        # Create policy in other project
        policy_response = auth_client.post(
            f"/projects/{other_project['id']}/policies",
            json={"name": "Other Policy"},
        )
        other_policy = policy_response.get_json()

        # Try to associate it with role from first project
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": other_policy["id"]},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_role_not_found(self, auth_client, project):
        """Test GET/POST returns 404 when role doesn't exist"""
        fake_role_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{project['id']}/roles/{fake_role_id}/policies"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{project['id']}/roles/{fake_role_id}/policies",
            json={"policy_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_project_not_found(self, auth_client):
        """Test GET/POST returns 404 when project doesn't exist"""
        fake_project_id = str(uuid.uuid4())
        fake_role_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{fake_project_id}/roles/{fake_role_id}/policies"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{fake_project_id}/roles/{fake_role_id}/policies",
            json={"policy_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_multiple_policies_association(self, auth_client, project, role):
        """Test that a role can have multiple policies"""
        # Create two policies
        policy1_response = auth_client.post(
            f"/projects/{project['id']}/policies",
            json={"name": "Policy 1"},
        )
        policy1 = policy1_response.get_json()

        policy2_response = auth_client.post(
            f"/projects/{project['id']}/policies",
            json={"name": "Policy 2"},
        )
        policy2 = policy2_response.get_json()

        # Associate both with role
        auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy1["id"]},
        )
        auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy2["id"]},
        )

        # Get all associated policies
        response = auth_client.get(
            f"/projects/{project['id']}/roles/{role['id']}/policies"
        )
        data = response.get_json()
        assert len(data) == 2
        policy_ids = [p["id"] for p in data]
        assert policy1["id"] in policy_ids
        assert policy2["id"] in policy_ids


class TestRolePolicyResource:
    """Tests for RolePolicyResource (DELETE)"""

    def test_remove_association(self, auth_client, project, role, policy):
        """Test DELETE removes association between role and policy"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/roles/{role['id']}/policies",
            json={"policy_id": policy["id"]},
        )

        # Remove association
        response = auth_client.delete(
            f"/projects/{project['id']}/roles/{role['id']}/policies/{policy['id']}"
        )
        assert response.status_code == 204

        # Verify association is removed
        get_response = auth_client.get(
            f"/projects/{project['id']}/roles/{role['id']}/policies"
        )
        data = get_response.get_json()
        assert len(data) == 0

    def test_remove_non_existent_association(self, auth_client, project, role, policy):
        """Test DELETE returns 404 when association doesn't exist"""
        # Don't create association, just try to delete
        response = auth_client.delete(
            f"/projects/{project['id']}/roles/{role['id']}/policies/{policy['id']}"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not assigned" in data["error"].lower()

    def test_remove_association_policy_not_found(self, auth_client, project, role):
        """Test DELETE returns 404 when policy doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/roles/{role['id']}/policies/{fake_id}"
        )
        assert response.status_code == 404

    def test_remove_association_role_not_found(self, auth_client, project, policy):
        """Test DELETE returns 404 when role doesn't exist"""
        fake_role_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/roles/{fake_role_id}/policies/{policy['id']}"
        )
        assert response.status_code == 404

    def test_unauthorized_missing_jwt(self, client):
        """Test all endpoints require JWT authentication"""
        project_id = str(uuid.uuid4())
        role_id = str(uuid.uuid4())
        policy_id = str(uuid.uuid4())

        # GET list
        response = client.get(f"/projects/{project_id}/roles/{role_id}/policies")
        assert response.status_code == 401

        # POST create
        response = client.post(
            f"/projects/{project_id}/roles/{role_id}/policies",
            json={"policy_id": policy_id},
        )
        assert response.status_code == 401

        # DELETE remove
        response = client.delete(
            f"/projects/{project_id}/roles/{role_id}/policies/{policy_id}"
        )
        assert response.status_code == 401
