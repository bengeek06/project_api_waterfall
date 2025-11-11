"""
tests.unit.test_policy_resources
---------------------------------

Unit tests for Policy resources (PolicyListResource, PolicyResource).

Tests cover:
- Listing policies (empty list, with policies)
- Creating policies (valid, missing name, duplicate name)
- Retrieving single policy (found, not found)
- Updating policies (PUT full replacement, PATCH partial)
- Duplicate name detection on update
- Deleting policies (success, not found, in use by roles)
- Authorization (401 on missing JWT)
"""

import pytest
import uuid
from datetime import datetime, timezone
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
    payload = {"name": "Test Project", "description": "For policy tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    return response.get_json()


class TestPolicyListResource:
    """Tests for PolicyListResource (GET, POST /projects/{project_id}/policies)"""

    def test_get_policies_empty(self, auth_client, project):
        """Test GET /projects/{project_id}/policies returns empty list initially"""
        response = auth_client.get(f"/projects/{project['id']}/policies")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_policies_project_not_found(self, auth_client):
        """Test GET /projects/{project_id}/policies with non-existent project"""
        response = auth_client.get(
            "/projects/00000000-0000-0000-0000-000000000000/policies"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Project not found"

    def test_create_policy(self, auth_client, project):
        """Test POST /projects/{project_id}/policies creates a new policy"""
        policy_data = {
            "name": "File Management",
            "description": "Policies for file operations",
        }

        response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "File Management"
        assert data["description"] == "Policies for file operations"
        assert data["project_id"] == project["id"]
        assert "id" in data
        assert "created_at" in data

    def test_create_policy_missing_name(self, auth_client, project):
        """Test POST /projects/{project_id}/policies without name returns 400"""
        policy_data = {"description": "Missing name"}

        response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_policy_duplicate_name(self, auth_client, project):
        """Test POST /projects/{project_id}/policies with duplicate name returns 409"""
        policy_data = {
            "name": "File Management",
            "description": "First policy",
        }

        # Create first policy
        response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        assert response.status_code == 201

        # Try to create duplicate
        duplicate_data = {
            "name": "File Management",
            "description": "Duplicate policy",
        }

        response = auth_client.post(
            f"/projects/{project['id']}/policies", json=duplicate_data
        )
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_create_policy_project_not_found(self, auth_client):
        """Test POST /projects/{project_id}/policies with non-existent project"""
        policy_data = {"name": "Test Policy"}

        response = auth_client.post(
            "/projects/00000000-0000-0000-0000-000000000000/policies",
            json=policy_data,
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Project not found"

    def test_get_policies_after_create(self, auth_client, project):
        """Test GET /projects/{project_id}/policies returns created policies"""
        # Create two policies
        policy1 = {"name": "File Management", "description": "File operations"}
        policy2 = {
            "name": "Member Management",
            "description": "Member operations",
        }

        auth_client.post(f"/projects/{project['id']}/policies", json=policy1)
        auth_client.post(f"/projects/{project['id']}/policies", json=policy2)

        # Get all policies
        response = auth_client.get(f"/projects/{project['id']}/policies")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert any(p["name"] == "File Management" for p in data)
        assert any(p["name"] == "Member Management" for p in data)


class TestPolicyResource:
    """Tests for PolicyResource (GET, PUT, PATCH, DELETE /projects/{project_id}/policies/{policy_id})"""

    def test_get_policy(self, auth_client, project):
        """Test GET /projects/{project_id}/policies/{policy_id} returns policy details"""
        # Create a policy
        policy_data = {
            "name": "File Management",
            "description": "File operations",
        }

        create_response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        policy = create_response.get_json()

        # Get the policy
        response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == policy["id"]
        assert data["name"] == "File Management"
        assert data["description"] == "File operations"

    def test_get_policy_not_found(self, auth_client, project):
        """Test GET /projects/{project_id}/policies/{policy_id} with non-existent policy"""
        response = auth_client.get(
            f"/projects/{project['id']}/policies/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_update_policy_put(self, auth_client, project):
        """Test PUT /projects/{project_id}/policies/{policy_id} updates policy"""
        # Create a policy
        policy_data = {
            "name": "File Management",
            "description": "Old description",
        }

        create_response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        policy = create_response.get_json()

        # Update the policy (full replacement)
        update_data = {
            "name": "Updated File Management",
            "description": "New description",
        }

        response = auth_client.put(
            f"/projects/{project['id']}/policies/{policy['id']}",
            json=update_data,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated File Management"
        assert data["description"] == "New description"

    def test_update_policy_patch(self, auth_client, project):
        """Test PATCH /projects/{project_id}/policies/{policy_id} partially updates policy"""
        # Create a policy
        policy_data = {
            "name": "File Management",
            "description": "Original description",
        }

        create_response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        policy = create_response.get_json()

        # Partial update (only description)
        update_data = {"description": "Updated description"}

        response = auth_client.patch(
            f"/projects/{project['id']}/policies/{policy['id']}",
            json=update_data,
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "File Management"  # Unchanged
        assert data["description"] == "Updated description"  # Changed

    def test_update_policy_duplicate_name(self, auth_client, project):
        """Test updating policy to duplicate name returns 409"""
        # Create two policies
        policy1_data = {"name": "Policy 1"}
        policy2_data = {"name": "Policy 2"}

        response1 = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy1_data
        )
        policy1 = response1.get_json()

        response2 = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy2_data
        )
        policy2 = response2.get_json()

        # Try to rename policy2 to policy1's name
        update_data = {"name": "Policy 1"}

        response = auth_client.put(
            f"/projects/{project['id']}/policies/{policy2['id']}",
            json=update_data,
        )
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_delete_policy(self, auth_client, project):
        """Test DELETE /projects/{project_id}/policies/{policy_id} soft deletes policy"""
        # Create a policy
        policy_data = {"name": "Test Policy"}

        create_response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        policy = create_response.get_json()

        # Delete the policy
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{policy['id']}"
        )
        assert response.status_code == 204

        # Verify policy is not returned in list
        list_response = auth_client.get(f"/projects/{project['id']}/policies")
        policies = list_response.get_json()
        assert not any(p["id"] == policy["id"] for p in policies)

        # Verify policy cannot be retrieved
        get_response = auth_client.get(
            f"/projects/{project['id']}/policies/{policy['id']}"
        )
        assert get_response.status_code == 404

    def test_delete_policy_not_found(self, auth_client, project):
        """Test DELETE /projects/{project_id}/policies/{policy_id} with non-existent policy"""
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    def test_delete_policy_in_use(self, auth_client, project, app):
        """Test DELETE /projects/{project_id}/policies/{policy_id} fails if policy is assigned to roles"""
        from app.models.project import (
            ProjectRole,
            ProjectPolicy,
            role_policy_association,
        )
        from app.models.db import db

        # Create a policy
        policy_data = {"name": "Test Policy"}

        create_response = auth_client.post(
            f"/projects/{project['id']}/policies", json=policy_data
        )
        policy = create_response.get_json()

        # Create a role and assign the policy to it
        with app.app_context():
            role = ProjectRole(
                project_id=project["id"],
                company_id=project["company_id"],
                name="Test Role",
                is_default=False,
            )
            db.session.add(role)
            db.session.commit()

            # Assign policy to role
            policy_obj = ProjectPolicy.query.get(policy["id"])
            role.policies.append(policy_obj)
            db.session.commit()

        # Try to delete the policy (should fail)
        response = auth_client.delete(
            f"/projects/{project['id']}/policies/{policy['id']}"
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert (
            "assigned to roles" in data["error"].lower()
            or "in use" in data["detail"].lower()
        )

    def test_unauthorized_missing_jwt(self, client):
        """Test all endpoints require JWT authentication"""
        project_id = "00000000-0000-0000-0000-000000000000"
        policy_id = "00000000-0000-0000-0000-000000000000"

        # GET list
        response = client.get(f"/projects/{project_id}/policies")
        assert response.status_code == 401

        # POST create
        response = client.post(
            f"/projects/{project_id}/policies", json={"name": "Test"}
        )
        assert response.status_code == 401

        # GET single
        response = client.get(f"/projects/{project_id}/policies/{policy_id}")
        assert response.status_code == 401

        # PUT update
        response = client.put(
            f"/projects/{project_id}/policies/{policy_id}",
            json={"name": "Test"},
        )
        assert response.status_code == 401

        # PATCH update
        response = client.patch(
            f"/projects/{project_id}/policies/{policy_id}",
            json={"name": "Test"},
        )
        assert response.status_code == 401

        # DELETE
        response = client.delete(
            f"/projects/{project_id}/policies/{policy_id}"
        )
        assert response.status_code == 401
