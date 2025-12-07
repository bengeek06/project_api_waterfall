# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
test_deliverable_resources.py
-----------------------------
Tests for Deliverable CRUD resources.
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
    payload = {"name": "Test Project", "description": "For deliverable tests"}
    response = auth_client.post("/projects", json=payload)
    assert response.status_code == 201
    return response.json["id"]


class TestDeliverableListResource:
    """Tests for DeliverableListResource."""

    def test_get_deliverables_empty(self, auth_client, project):
        """Test GET /projects/{id}/deliverables with no deliverables."""
        response = auth_client.get(f"/projects/{project}/deliverables")
        assert response.status_code == 200
        assert response.json == []

    def test_get_deliverables_project_not_found(self, auth_client):
        """Test GET /projects/{id}/deliverables with non-existent project."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/projects/{fake_id}/deliverables")
        assert response.status_code == 404
        assert "not found" in response.json["message"].lower()

    def test_create_deliverable(self, auth_client, project):
        """Test POST /projects/{id}/deliverables."""
        payload = {
            "name": "Deliverable 1",
            "description": "First deliverable",
            "type": "document",
            "status": "planned",
        }

        response = auth_client.post(
            f"/projects/{project}/deliverables", json=payload
        )
        if response.status_code != 201:
            print(f"Error response: {response.json}")
        assert response.status_code == 201
        assert response.json["name"] == "Deliverable 1"
        assert response.json["type"] == "document"
        assert response.json["status"] == "planned"
        assert "id" in response.json
        assert response.json["project_id"] == project

    def test_create_deliverable_missing_name(self, auth_client, project):
        """Test POST /projects/{id}/deliverables without name."""
        payload = {"description": "Missing name"}

        response = auth_client.post(
            f"/projects/{project}/deliverables", json=payload
        )
        assert response.status_code == 400
        assert "message" in response.json

    def test_create_deliverable_project_not_found(self, auth_client):
        """Test POST to non-existent project."""
        fake_id = str(uuid.uuid4())
        payload = {"name": "Deliverable 1"}

        response = auth_client.post(
            f"/projects/{fake_id}/deliverables", json=payload
        )
        assert response.status_code == 404

    def test_get_deliverables_after_create(self, auth_client, project):
        """Test GET /projects/{id}/deliverables after creating deliverables."""
        # Create two deliverables
        auth_client.post(
            f"/projects/{project}/deliverables", json={"name": "Deliverable 1"}
        )
        auth_client.post(
            f"/projects/{project}/deliverables", json={"name": "Deliverable 2"}
        )

        # Get deliverables
        response = auth_client.get(f"/projects/{project}/deliverables")
        assert response.status_code == 200
        assert len(response.json) == 2
        names = [d["name"] for d in response.json]
        assert "Deliverable 1" in names
        assert "Deliverable 2" in names


class TestDeliverableResource:
    """Tests for DeliverableResource."""

    def test_get_deliverable(self, auth_client, project):
        """Test GET /deliverables/{id}."""
        # Create deliverable
        payload = {"name": "Test Deliverable"}
        create_response = auth_client.post(
            f"/projects/{project}/deliverables", json=payload
        )
        deliverable_id = create_response.json["id"]

        # Get deliverable
        response = auth_client.get(f"/deliverables/{deliverable_id}")
        assert response.status_code == 200
        assert response.json["id"] == deliverable_id
        assert response.json["name"] == "Test Deliverable"

    def test_get_deliverable_not_found(self, auth_client):
        """Test GET /deliverables/{id} with non-existent ID."""
        fake_id = str(uuid.uuid4())
        response = auth_client.get(f"/deliverables/{fake_id}")
        assert response.status_code == 404

    def test_update_deliverable_put(self, auth_client, project):
        """Test PUT /deliverables/{id}."""
        # Create deliverable
        create_response = auth_client.post(
            f"/projects/{project}/deliverables", json={"name": "Original Name"}
        )
        deliverable_id = create_response.json["id"]

        # Update deliverable
        update_payload = {
            "name": "Updated Name",
            "description": "Updated description",
        }
        response = auth_client.put(
            f"/deliverables/{deliverable_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Updated Name"
        assert response.json["description"] == "Updated description"

    def test_update_deliverable_patch(self, auth_client, project):
        """Test PATCH /deliverables/{id}."""
        # Create deliverable
        create_response = auth_client.post(
            f"/projects/{project}/deliverables", json={"name": "Original Name"}
        )
        deliverable_id = create_response.json["id"]

        # Partial update
        update_payload = {"description": "Partial update"}
        response = auth_client.patch(
            f"/deliverables/{deliverable_id}", json=update_payload
        )
        assert response.status_code == 200
        assert response.json["name"] == "Original Name"  # Unchanged
        assert response.json["description"] == "Partial update"

    def test_delete_deliverable(self, auth_client, project):
        """Test DELETE /deliverables/{id}."""
        # Create deliverable
        create_response = auth_client.post(
            f"/projects/{project}/deliverables", json={"name": "To Delete"}
        )
        deliverable_id = create_response.json["id"]

        # Delete deliverable
        response = auth_client.delete(f"/deliverables/{deliverable_id}")
        assert response.status_code == 204

        # Verify deliverable is gone (soft delete)
        get_response = auth_client.get(f"/deliverables/{deliverable_id}")
        assert get_response.status_code == 404

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

        # Create deliverable with auth
        response = client.post(
            f"/projects/{project_id}/deliverables", json={"name": "Test"}
        )
        deliverable_id = response.json["id"]

        # Clear the cookie to remove auth
        client.delete_cookie("access_token", domain="localhost")

        # Now test endpoints without auth
        response = client.get(f"/projects/{project_id}/deliverables")
        assert response.status_code == 401

        response = client.post(
            f"/projects/{project_id}/deliverables", json={"name": "Test"}
        )
        assert response.status_code == 401

        response = client.get(f"/deliverables/{deliverable_id}")
        assert response.status_code == 401

        response = client.put(
            f"/deliverables/{deliverable_id}", json={"name": "Updated"}
        )
        assert response.status_code == 401

        response = client.delete(f"/deliverables/{deliverable_id}")
        assert response.status_code == 401
