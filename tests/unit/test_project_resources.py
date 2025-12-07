# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
test_project_resources.py
------------------------
Tests for Project CRUD resources.
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
    return client


class TestProjectListResource:
    """Tests for ProjectListResource."""

    def test_get_projects_empty(self, auth_client):
        """Test GET /projects with no projects."""
        response = auth_client.get("/projects")
        assert response.status_code == 200
        assert response.json == []

    def test_create_project(self, auth_client):
        """Test POST /projects."""
        payload = {"name": "Test Project", "description": "A test project"}

        response = auth_client.post("/projects", json=payload)
        assert response.status_code == 201
        assert response.json["name"] == "Test Project"
        assert response.json["status"] == "created"
        assert "id" in response.json

    def test_create_project_missing_name(self, auth_client):
        """Test POST /projects without name."""
        payload = {"description": "Missing name"}

        response = auth_client.post("/projects", json=payload)
        assert response.status_code == 400
        assert "message" in response.json

    def test_get_projects_after_create(self, auth_client):
        """Test GET /projects after creating a project."""
        # Create project
        payload = {"name": "Test Project"}
        auth_client.post("/projects", json=payload)

        # Get projects
        response = auth_client.get("/projects")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["name"] == "Test Project"


class TestProjectResource:
    """Tests for ProjectResource."""

    def test_get_project(self, auth_client):
        """Test GET /projects/{id}."""
        # Create project
        payload = {"name": "Test Project"}
        create_response = auth_client.post("/projects", json=payload)
        project_id = create_response.json["id"]

        # Get project
        response = auth_client.get(f"/projects/{project_id}")
        assert response.status_code == 200
        assert response.json["id"] == project_id
        assert response.json["name"] == "Test Project"

    def test_get_project_not_found(self, auth_client):
        """Test GET /projects/{id} with non-existent ID."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json["message"].lower()

    def test_get_project_invalid_uuid(self, auth_client):
        """Test GET /projects/{id} with invalid UUID."""
        response = auth_client.get("/projects/invalid-uuid")
        assert response.status_code == 400
        assert "UUID" in response.json["message"]

    def test_update_project_put(self, auth_client):
        """Test PUT /projects/{id}."""
        # Create project
        create_response = auth_client.post(
            "/projects", json={"name": "Original Name"}
        )
        project_id = create_response.json["id"]

        # Update project
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
        }
        response = auth_client.put(
            f"/projects/{project_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Updated Name"
        assert response.json["description"] == "Updated description"

    def test_update_project_patch(self, auth_client):
        """Test PATCH /projects/{id}."""
        # Create project
        create_response = auth_client.post(
            "/projects", json={"name": "Original Name"}
        )
        project_id = create_response.json["id"]

        # Partial update
        update_payload = {"description": "Partial update"}
        response = auth_client.patch(
            f"/projects/{project_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Original Name"
        assert response.json["description"] == "Partial update"

    def test_delete_project(self, auth_client):
        """Test DELETE /projects/{id}."""
        # Create project
        create_response = auth_client.post(
            "/projects", json={"name": "To Delete"}
        )
        project_id = create_response.json["id"]

        # Delete project
        response = auth_client.delete(f"/projects/{project_id}")
        assert response.status_code == 204

        # Verify project is soft-deleted
        get_response = auth_client.get(f"/projects/{project_id}")
        assert get_response.status_code == 404

    def test_unauthorized_missing_jwt(self, client):
        """Test endpoints without JWT."""
        response = client.get("/projects")
        assert response.status_code == 401
