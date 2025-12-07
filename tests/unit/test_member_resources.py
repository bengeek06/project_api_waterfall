# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
test_member_resources.py
-------------------------
Tests for Member CRUD resources.
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
    # Store company_id for later use in fixtures
    client.company_id = company_id
    client.user_id = user_id
    return client


@pytest.fixture
def project_with_role(auth_client):
    """Create a test project with a default role and return project_id and role_id."""
    # Create project
    payload = {"name": "Test Project", "description": "For member tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    project_id = response.json["id"]

    # Create a role for the project - use company_id from auth_client
    from app.models.db import db
    from app.models.project import ProjectRole

    role = ProjectRole(
        project_id=project_id,
        company_id=auth_client.company_id,
        name="contributor",
        description="Contributor role",
        is_default=True,
    )
    db.session.add(role)
    db.session.commit()

    return {"project_id": project_id, "role_id": role.id}


class TestMemberListResource:
    """Tests for MemberListResource."""

    def test_get_members_empty(self, auth_client, project_with_role):
        """Test GET /projects/{id}/members with no members."""
        project_id = project_with_role["project_id"]
        response = auth_client.get(f"/projects/{project_id}/members")
        assert response.status_code == 200
        assert response.json == []

    def test_get_members_project_not_found(self, auth_client):
        """Test GET /projects/{id}/members with non-existent project."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{fake_id}/members")
        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    def test_add_member(self, auth_client, project_with_role):
        """Test POST /projects/{id}/members."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        new_user_id = str(uuid.uuid4())

        payload = {"user_id": new_user_id, "role_id": role_id}

        response = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        if response.status_code != 201:
            print(f"Error response: {response.json}")
        assert response.status_code == 201
        assert response.json["user_id"] == new_user_id
        assert response.json["role_id"] == role_id
        assert response.json["project_id"] == project_id

    def test_add_member_missing_user_id(self, auth_client, project_with_role):
        """Test POST /projects/{id}/members without user_id."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]

        payload = {"role_id": role_id}

        response = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        assert response.status_code == 400
        assert "errors" in response.json

    def test_add_member_missing_role_id(self, auth_client, project_with_role):
        """Test POST /projects/{id}/members without role_id."""
        project_id = project_with_role["project_id"]
        new_user_id = str(uuid.uuid4())

        payload = {"user_id": new_user_id}

        response = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        assert response.status_code == 400
        assert "errors" in response.json

    def test_add_member_invalid_role(self, auth_client, project_with_role):
        """Test POST /projects/{id}/members with non-existent role."""
        project_id = project_with_role["project_id"]
        new_user_id = str(uuid.uuid4())
        fake_role_id = str(uuid.uuid4())

        payload = {"user_id": new_user_id, "role_id": fake_role_id}

        response = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        assert response.status_code == 404
        assert "role" in response.json["error"].lower()

    def test_add_member_duplicate(self, auth_client, project_with_role):
        """Test adding the same member twice."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        new_user_id = str(uuid.uuid4())

        payload = {"user_id": new_user_id, "role_id": role_id}

        # Add member first time
        response1 = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        assert response1.status_code == 201

        # Try to add same member again
        response2 = auth_client.post(
            f"/projects/{project_id}/members", json=payload
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json["error"].lower()

    def test_get_members_after_add(self, auth_client, project_with_role):
        """Test GET /projects/{id}/members after adding members."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]

        # Add two members
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())

        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user1_id, "role_id": role_id},
        )
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user2_id, "role_id": role_id},
        )

        # Get members
        response = auth_client.get(f"/projects/{project_id}/members")
        assert response.status_code == 200
        assert len(response.json) == 2


class TestMemberResource:
    """Tests for MemberResource."""

    def test_get_member(self, auth_client, project_with_role):
        """Test GET /projects/{project_id}/members/{user_id}."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        user_id = str(uuid.uuid4())

        # Add member
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )

        # Get member
        response = auth_client.get(f"/projects/{project_id}/members/{user_id}")
        assert response.status_code == 200
        assert response.json["user_id"] == user_id
        assert response.json["role_id"] == role_id

    def test_get_member_not_found(self, auth_client, project_with_role):
        """Test GET /projects/{project_id}/members/{user_id} with non-existent member."""
        project_id = project_with_role["project_id"]
        fake_user_id = str(uuid.uuid4())

        response = auth_client.get(
            f"/projects/{project_id}/members/{fake_user_id}"
        )
        assert response.status_code == 404
        assert "not found" in response.json["error"].lower()

    def test_update_member_put(self, auth_client, project_with_role):
        """Test PUT /projects/{project_id}/members/{user_id}."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        user_id = str(uuid.uuid4())

        # Add member
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )

        # Create a new role - use company_id from auth_client
        from app.models.db import db
        from app.models.project import ProjectRole

        new_role = ProjectRole(
            project_id=project_id,
            company_id=auth_client.company_id,
            name="viewer",
            description="Viewer role",
            is_default=True,
        )
        db.session.add(new_role)
        db.session.commit()

        # Update member's role
        update_payload = {"role_id": new_role.id}
        response = auth_client.put(
            f"/projects/{project_id}/members/{user_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["role_id"] == new_role.id

    def test_update_member_patch(self, auth_client, project_with_role):
        """Test PATCH /projects/{project_id}/members/{user_id}."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        user_id = str(uuid.uuid4())

        # Add member
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )

        # Create a new role - use company_id from auth_client
        from app.models.db import db
        from app.models.project import ProjectRole

        new_role = ProjectRole(
            project_id=project_id,
            company_id=auth_client.company_id,
            name="validator",
            description="Validator role",
            is_default=True,
        )
        db.session.add(new_role)
        db.session.commit()

        # Partial update member's role
        update_payload = {"role_id": new_role.id}
        response = auth_client.patch(
            f"/projects/{project_id}/members/{user_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["role_id"] == new_role.id

    def test_update_member_invalid_role(self, auth_client, project_with_role):
        """Test updating member with non-existent role."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        user_id = str(uuid.uuid4())

        # Add member
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )

        # Try to update with fake role
        fake_role_id = str(uuid.uuid4())
        update_payload = {"role_id": fake_role_id}
        response = auth_client.put(
            f"/projects/{project_id}/members/{user_id}", json=update_payload
        )
        assert response.status_code == 404
        assert "role" in response.json["error"].lower()

    def test_delete_member(self, auth_client, project_with_role):
        """Test DELETE /projects/{project_id}/members/{user_id}."""
        project_id = project_with_role["project_id"]
        role_id = project_with_role["role_id"]
        user_id = str(uuid.uuid4())

        # Add member
        auth_client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )

        # Delete member
        response = auth_client.delete(
            f"/projects/{project_id}/members/{user_id}"
        )
        assert response.status_code == 204

        # Verify member is gone
        get_response = auth_client.get(
            f"/projects/{project_id}/members/{user_id}"
        )
        assert get_response.status_code == 404

    def test_delete_member_not_found(self, auth_client, project_with_role):
        """Test DELETE with non-existent member."""
        project_id = project_with_role["project_id"]
        fake_user_id = str(uuid.uuid4())

        response = auth_client.delete(
            f"/projects/{project_id}/members/{fake_user_id}"
        )
        assert response.status_code == 404

    def test_unauthorized_missing_jwt(self, client):
        """Test that all endpoints require JWT authentication."""
        project_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        role_id = str(uuid.uuid4())

        # GET list
        response = client.get(f"/projects/{project_id}/members")
        assert response.status_code == 401

        # POST
        response = client.post(
            f"/projects/{project_id}/members",
            json={"user_id": user_id, "role_id": role_id},
        )
        assert response.status_code == 401

        # GET single
        response = client.get(f"/projects/{project_id}/members/{user_id}")
        assert response.status_code == 401

        # PUT
        response = client.put(
            f"/projects/{project_id}/members/{user_id}",
            json={"role_id": role_id},
        )
        assert response.status_code == 401

        # PATCH
        response = client.patch(
            f"/projects/{project_id}/members/{user_id}",
            json={"role_id": role_id},
        )
        assert response.status_code == 401

        # DELETE
        response = client.delete(f"/projects/{project_id}/members/{user_id}")
        assert response.status_code == 401
