"""
test_role_resources.py
-----------------------
Tests for Role CRUD resources.
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
    """Create a test project and return its ID."""
    payload = {"name": "Test Project", "description": "For role tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    return response.json["id"]


class TestRoleListResource:
    """Tests for RoleListResource."""

    def test_get_roles_empty(self, auth_client, project):
        """Test GET /projects/{id}/roles with no roles."""
        response = auth_client.get(f"/projects/{project}/roles")
        assert response.status_code == 200
        assert response.json == []

    def test_get_roles_project_not_found(self, auth_client):
        """Test GET /projects/{id}/roles with non-existent project."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{fake_id}/roles")
        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    def test_create_role(self, auth_client, project):
        """Test POST /projects/{id}/roles."""
        payload = {
            "name": "custom_role",
            "description": "Custom role for testing",
        }

        response = auth_client.post(f"/projects/{project}/roles", json=payload)
        if response.status_code != 201:
            print(f"Error response: {response.json}")
        assert response.status_code == 201
        assert response.json["name"] == "custom_role"
        assert response.json["description"] == "Custom role for testing"
        assert response.json["is_default"] is False
        assert "id" in response.json
        assert response.json["project_id"] == project

    def test_create_role_missing_name(self, auth_client, project):
        """Test POST /projects/{id}/roles without name."""
        payload = {"description": "Missing name"}

        response = auth_client.post(f"/projects/{project}/roles", json=payload)
        assert response.status_code == 400
        assert "errors" in response.json

    def test_create_role_duplicate_name(self, auth_client, project):
        """Test creating role with duplicate name."""
        payload = {"name": "manager", "description": "First manager role"}

        # Create first role
        response1 = auth_client.post(
            f"/projects/{project}/roles", json=payload
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = auth_client.post(
            f"/projects/{project}/roles", json=payload
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json["error"].lower()

    def test_create_role_project_not_found(self, auth_client):
        """Test POST to non-existent project."""
        fake_id = str(uuid.uuid4())
        payload = {"name": "role1"}

        response = auth_client.post(f"/projects/{fake_id}/roles", json=payload)
        assert response.status_code == 404

    def test_get_roles_after_create(self, auth_client, project):
        """Test GET /projects/{id}/roles after creating roles."""
        # Create two roles
        auth_client.post(f"/projects/{project}/roles", json={"name": "role1"})
        auth_client.post(f"/projects/{project}/roles", json={"name": "role2"})

        # Get roles
        response = auth_client.get(f"/projects/{project}/roles")
        assert response.status_code == 200
        assert len(response.json) == 2


class TestRoleResource:
    """Tests for RoleResource."""

    def test_get_role(self, auth_client, project):
        """Test GET /projects/{project_id}/roles/{role_id}."""
        # Create role
        create_response = auth_client.post(
            f"/projects/{project}/roles",
            json={"name": "viewer", "description": "View only role"},
        )
        role_id = create_response.json["id"]

        # Get role
        response = auth_client.get(f"/projects/{project}/roles/{role_id}")
        assert response.status_code == 200
        assert response.json["id"] == role_id
        assert response.json["name"] == "viewer"

    def test_get_role_not_found(self, auth_client, project):
        """Test GET with non-existent role."""
        fake_role_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{project}/roles/{fake_role_id}")
        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    def test_update_role_put(self, auth_client, project):
        """Test PUT /projects/{project_id}/roles/{role_id}."""
        # Create role
        create_response = auth_client.post(
            f"/projects/{project}/roles",
            json={"name": "editor", "description": "Can edit"},
        )
        role_id = create_response.json["id"]

        # Update role
        update_payload = {
            "name": "editor_updated",
            "description": "Updated editor role",
        }
        response = auth_client.put(
            f"/projects/{project}/roles/{role_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "editor_updated"
        assert response.json["description"] == "Updated editor role"

    def test_update_role_patch(self, auth_client, project):
        """Test PATCH /projects/{project_id}/roles/{role_id}."""
        # Create role
        create_response = auth_client.post(
            f"/projects/{project}/roles",
            json={"name": "reviewer", "description": "Can review"},
        )
        role_id = create_response.json["id"]

        # Partial update
        update_payload = {"description": "Updated review role"}
        response = auth_client.patch(
            f"/projects/{project}/roles/{role_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "reviewer"  # Unchanged
        assert response.json["description"] == "Updated review role"

    def test_update_role_duplicate_name(self, auth_client, project):
        """Test updating role to duplicate name."""
        # Create two roles
        auth_client.post(f"/projects/{project}/roles", json={"name": "role1"})
        create_response2 = auth_client.post(
            f"/projects/{project}/roles", json={"name": "role2"}
        )
        role2_id = create_response2.json["id"]

        # Try to rename role2 to role1
        update_payload = {"name": "role1"}
        response = auth_client.put(
            f"/projects/{project}/roles/{role2_id}", json=update_payload
        )
        assert response.status_code == 409
        assert "already exists" in response.json["error"].lower()

    def test_update_default_role_forbidden(self, auth_client, project):
        """Test that default roles cannot be updated."""
        # Create a default role manually for testing
        from app.models.project import ProjectRole
        from app.models.db import db

        default_role = ProjectRole(
            project_id=project,
            company_id=auth_client.company_id,
            name="owner",
            description="Owner role",
            is_default=True,
        )
        db.session.add(default_role)
        db.session.commit()

        # Try to update it
        update_payload = {"name": "owner_modified"}
        response = auth_client.put(
            f"/projects/{project}/roles/{default_role.id}",
            json=update_payload,
        )
        assert response.status_code == 400
        assert "cannot modify" in response.json["error"].lower()

    def test_delete_role(self, auth_client, project):
        """Test DELETE /projects/{project_id}/roles/{role_id}."""
        # Create role
        create_response = auth_client.post(
            f"/projects/{project}/roles", json={"name": "temp_role"}
        )
        role_id = create_response.json["id"]

        # Delete role
        response = auth_client.delete(f"/projects/{project}/roles/{role_id}")
        assert response.status_code == 204

        # Verify role is gone
        get_response = auth_client.get(f"/projects/{project}/roles/{role_id}")
        assert get_response.status_code == 404

    def test_delete_role_not_found(self, auth_client, project):
        """Test DELETE with non-existent role."""
        fake_role_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project}/roles/{fake_role_id}"
        )
        assert response.status_code == 404

    def test_delete_default_role_forbidden(self, auth_client, project):
        """Test that default roles cannot be deleted."""
        # Create a default role
        from app.models.project import ProjectRole
        from app.models.db import db

        default_role = ProjectRole(
            project_id=project,
            company_id=auth_client.company_id,
            name="validator",
            description="Validator role",
            is_default=True,
        )
        db.session.add(default_role)
        db.session.commit()

        # Try to delete it
        response = auth_client.delete(
            f"/projects/{project}/roles/{default_role.id}"
        )
        assert response.status_code == 400
        assert "cannot delete" in response.json["error"].lower()

    def test_delete_role_in_use(self, auth_client, project):
        """Test that roles in use by members cannot be deleted."""
        # Create a role
        create_response = auth_client.post(
            f"/projects/{project}/roles",
            json={"name": "active_role", "description": "In use"},
        )
        role_id = create_response.json["id"]

        # Assign role to a member
        from app.models.project import ProjectMember
        from app.models.db import db

        member = ProjectMember(
            project_id=project,
            user_id=str(uuid.uuid4()),
            company_id=auth_client.company_id,
            role_id=role_id,
            added_by=auth_client.user_id,
        )
        db.session.add(member)
        db.session.commit()

        # Try to delete the role
        response = auth_client.delete(f"/projects/{project}/roles/{role_id}")
        assert response.status_code == 400
        assert (
            "in use" in response.json["error"].lower()
            or "assigned" in response.json["detail"].lower()
        )

    def test_unauthorized_missing_jwt(self, client):
        """Test that all endpoints require JWT authentication."""
        project_id = str(uuid.uuid4())
        role_id = str(uuid.uuid4())

        # GET list
        response = client.get(f"/projects/{project_id}/roles")
        assert response.status_code == 401

        # POST
        response = client.post(
            f"/projects/{project_id}/roles", json={"name": "role1"}
        )
        assert response.status_code == 401

        # GET single
        response = client.get(f"/projects/{project_id}/roles/{role_id}")
        assert response.status_code == 401

        # PUT
        response = client.put(
            f"/projects/{project_id}/roles/{role_id}", json={"name": "role1"}
        )
        assert response.status_code == 401

        # PATCH
        response = client.patch(
            f"/projects/{project_id}/roles/{role_id}",
            json={"description": "test"},
        )
        assert response.status_code == 401

        # DELETE
        response = client.delete(f"/projects/{project_id}/roles/{role_id}")
        assert response.status_code == 401
