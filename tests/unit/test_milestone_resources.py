# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
test_milestone_resources.py
---------------------------
Tests for Milestone CRUD resources.
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


@pytest.fixture
def project(auth_client):
    """Create a test project and return its ID."""
    payload = {"name": "Test Project", "description": "For milestone tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    return response.json["id"]


class TestMilestoneListResource:
    """Tests for MilestoneListResource."""

    def test_get_milestones_empty(self, auth_client, project):
        """Test GET /projects/{id}/milestones with no milestones."""
        response = auth_client.get(f"/projects/{project}/milestones")
        assert response.status_code == 200
        assert response.json == []

    def test_get_milestones_project_not_found(self, auth_client):
        """Test GET /projects/{id}/milestones with non-existent project."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{fake_id}/milestones")
        assert response.status_code == 404
        assert "not found" in response.json["message"].lower()

    def test_create_milestone(self, auth_client, project):
        """Test POST /projects/{id}/milestones."""
        payload = {
            "name": "Milestone 1",
            "description": "First milestone",
            "status": "planned",
        }

        response = auth_client.post(
            f"/projects/{project}/milestones", json=payload
        )
        if response.status_code != 201:
            print(f"Error response: {response.json}")
        assert response.status_code == 201
        assert response.json["name"] == "Milestone 1"
        assert response.json["status"] == "planned"
        assert "id" in response.json
        assert response.json["project_id"] == project

    def test_create_milestone_missing_name(self, auth_client, project):
        """Test POST /projects/{id}/milestones without name."""
        payload = {"description": "Missing name"}

        response = auth_client.post(
            f"/projects/{project}/milestones", json=payload
        )
        assert response.status_code == 400
        assert "message" in response.json

    def test_create_milestone_project_not_found(self, auth_client):
        """Test POST to non-existent project."""
        fake_id = str(uuid.uuid4())
        payload = {"name": "Milestone 1"}

        response = auth_client.post(
            f"/projects/{fake_id}/milestones", json=payload
        )
        assert response.status_code == 404

    def test_get_milestones_after_create(self, auth_client, project):
        """Test GET /projects/{id}/milestones after creating milestones."""
        # Create two milestones
        auth_client.post(
            f"/projects/{project}/milestones", json={"name": "Milestone 1"}
        )
        auth_client.post(
            f"/projects/{project}/milestones", json={"name": "Milestone 2"}
        )

        # Get milestones
        response = auth_client.get(f"/projects/{project}/milestones")
        assert response.status_code == 200
        assert len(response.json) == 2
        names = [m["name"] for m in response.json]
        assert "Milestone 1" in names
        assert "Milestone 2" in names


class TestMilestoneResource:
    """Tests for MilestoneResource."""

    def test_get_milestone(self, auth_client, project):
        """Test GET /milestones/{id}."""
        # Create milestone
        payload = {"name": "Test Milestone"}
        create_response = auth_client.post(
            f"/projects/{project}/milestones", json=payload
        )
        milestone_id = create_response.json["id"]

        # Get milestone
        response = auth_client.get(f"/milestones/{milestone_id}")
        assert response.status_code == 200
        assert response.json["id"] == milestone_id
        assert response.json["name"] == "Test Milestone"

    def test_get_milestone_not_found(self, auth_client):
        """Test GET /milestones/{id} with non-existent ID."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/milestones/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json["message"].lower()

    def test_get_milestone_invalid_uuid(self, auth_client):
        """Test GET /milestones/{id} with invalid UUID."""
        response = auth_client.get("/milestones/invalid-uuid")
        assert response.status_code == 400
        assert "UUID" in response.json["message"]

    def test_update_milestone_put(self, auth_client, project):
        """Test PUT /milestones/{id}."""
        # Create milestone
        create_response = auth_client.post(
            f"/projects/{project}/milestones", json={"name": "Original Name"}
        )
        milestone_id = create_response.json["id"]

        # Update milestone
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "status": "in_progress",
        }
        response = auth_client.put(
            f"/milestones/{milestone_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Updated Name"
        assert response.json["description"] == "Updated description"
        assert response.json["status"] == "in_progress"

    def test_update_milestone_patch(self, auth_client, project):
        """Test PATCH /milestones/{id}."""
        # Create milestone
        create_response = auth_client.post(
            f"/projects/{project}/milestones", json={"name": "Original Name"}
        )
        milestone_id = create_response.json["id"]

        # Partial update
        update_payload = {"status": "completed"}
        response = auth_client.patch(
            f"/milestones/{milestone_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Original Name"
        assert response.json["status"] == "completed"

    def test_delete_milestone(self, auth_client, project):
        """Test DELETE /milestones/{id}."""
        # Create milestone
        create_response = auth_client.post(
            f"/projects/{project}/milestones", json={"name": "To Delete"}
        )
        milestone_id = create_response.json["id"]

        # Delete milestone
        response = auth_client.delete(f"/milestones/{milestone_id}")
        assert response.status_code == 204

        # Verify milestone is soft-deleted
        get_response = auth_client.get(f"/milestones/{milestone_id}")
        assert get_response.status_code == 404

        # Verify it's not in the list
        list_response = auth_client.get(f"/projects/{project}/milestones")
        assert response.status_code == 204
        milestone_ids = [m["id"] for m in list_response.json]
        assert milestone_id not in milestone_ids

    def test_unauthorized_missing_jwt(self, client):
        """Test endpoints without JWT."""
        # Create a project first with auth
        company_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        token = create_jwt_token(company_id, user_id)
        client.set_cookie("access_token", token, domain="localhost")

        payload = {"name": "Test Project"}
        response = client.post("/projects", json=payload)
        project_id = response.json["id"]

        # Clear the cookie
        client.delete_cookie("access_token", domain="localhost")

        # Now test without JWT
        response = client.get(f"/projects/{project_id}/milestones")
        assert response.status_code == 401
