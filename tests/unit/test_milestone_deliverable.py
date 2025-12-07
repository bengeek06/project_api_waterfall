# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
tests.unit.test_milestone_deliverable
--------------------------------------

Unit tests for Milestone-Deliverable association resources.

Tests cover:
- Listing associated deliverables (empty list, with associations)
- Creating associations (valid, duplicate, invalid IDs)
- Removing associations (success, not found, non-existent association)
- Cross-project validation (cannot associate deliverables from different projects)
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
    return response.get_json()


@pytest.fixture
def milestone(auth_client, project):
    """Create a test milestone."""
    payload = {"name": "Milestone 1", "description": "Test milestone"}
    response = auth_client.post(
        f"/projects/{project['id']}/milestones", json=payload
    )
    assert response.status_code == 201
    return response.get_json()


@pytest.fixture
def deliverable(auth_client, project):
    """Create a test deliverable."""
    payload = {"name": "Deliverable 1", "description": "Test deliverable"}
    response = auth_client.post(
        f"/projects/{project['id']}/deliverables", json=payload
    )
    assert response.status_code == 201
    return response.get_json()


class TestMilestoneDeliverableListResource:
    """Tests for MilestoneDeliverableListResource (GET, POST)"""

    def test_get_deliverables_empty(self, auth_client, project, milestone):
        """Test GET returns empty list when no deliverables are associated"""
        response = auth_client.get(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_add_deliverable_association(
        self, auth_client, project, milestone, deliverable
    ):
        """Test POST creates association between milestone and deliverable"""
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable["id"]},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["id"] == deliverable["id"]
        assert data["name"] == deliverable["name"]

    def test_get_deliverables_after_association(
        self, auth_client, project, milestone, deliverable
    ):
        """Test GET returns associated deliverables"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable["id"]},
        )

        # Get associated deliverables
        response = auth_client.get(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["id"] == deliverable["id"]

    def test_add_duplicate_association(
        self, auth_client, project, milestone, deliverable
    ):
        """Test POST returns 409 when trying to create duplicate association"""
        # Create first association
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable["id"]},
        )
        assert response.status_code == 201

        # Try to create duplicate
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable["id"]},
        )
        assert response.status_code == 409
        data = response.get_json()
        assert "already exists" in data["error"].lower()

    def test_add_deliverable_missing_id(self, auth_client, project, milestone):
        """Test POST returns 400 when deliverable_id is missing"""
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_add_deliverable_not_found(self, auth_client, project, milestone):
        """Test POST returns 404 when deliverable doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": fake_id},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_add_deliverable_from_different_project(
        self, auth_client, project, milestone
    ):
        """Test POST returns 404 when deliverable belongs to different project"""
        # Create another project
        other_project_response = auth_client.post(
            "/projects", json={"name": "Other Project"}
        )
        other_project = other_project_response.get_json()

        # Create deliverable in other project
        deliverable_response = auth_client.post(
            f"/projects/{other_project['id']}/deliverables",
            json={"name": "Other Deliverable"},
        )
        other_deliverable = deliverable_response.get_json()

        # Try to associate it with milestone from first project
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": other_deliverable["id"]},
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_milestone_not_found(self, auth_client, project):
        """Test GET/POST returns 404 when milestone doesn't exist"""
        fake_milestone_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{project['id']}/milestones/{fake_milestone_id}/deliverables"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{project['id']}/milestones/{fake_milestone_id}/deliverables",
            json={"deliverable_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_project_not_found(self, auth_client):
        """Test GET/POST returns 404 when project doesn't exist"""
        fake_project_id = str(uuid.uuid4())
        fake_milestone_id = str(uuid.uuid4())

        # Test GET
        response = auth_client.get(
            f"/projects/{fake_project_id}/milestones/{fake_milestone_id}/deliverables"
        )
        assert response.status_code == 404

        # Test POST
        response = auth_client.post(
            f"/projects/{fake_project_id}/milestones/{fake_milestone_id}/deliverables",
            json={"deliverable_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404

    def test_multiple_deliverables_association(
        self, auth_client, project, milestone
    ):
        """Test that a milestone can have multiple deliverables"""
        # Create two deliverables
        deliverable1_response = auth_client.post(
            f"/projects/{project['id']}/deliverables",
            json={"name": "Deliverable 1"},
        )
        deliverable1 = deliverable1_response.get_json()

        deliverable2_response = auth_client.post(
            f"/projects/{project['id']}/deliverables",
            json={"name": "Deliverable 2"},
        )
        deliverable2 = deliverable2_response.get_json()

        # Associate both with milestone
        auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable1["id"]},
        )
        auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable2["id"]},
        )

        # Get all associated deliverables
        response = auth_client.get(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables"
        )
        data = response.get_json()
        assert len(data) == 2
        deliverable_ids = [d["id"] for d in data]
        assert deliverable1["id"] in deliverable_ids
        assert deliverable2["id"] in deliverable_ids


class TestMilestoneDeliverableResource:
    """Tests for MilestoneDeliverableResource (DELETE)"""

    def test_remove_association(
        self, auth_client, project, milestone, deliverable
    ):
        """Test DELETE removes association between milestone and deliverable"""
        # Create association
        auth_client.post(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables",
            json={"deliverable_id": deliverable["id"]},
        )

        # Remove association
        response = auth_client.delete(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables/{deliverable['id']}"
        )
        assert response.status_code == 204

        # Verify association is removed
        get_response = auth_client.get(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables"
        )
        data = get_response.get_json()
        assert len(data) == 0

    def test_remove_non_existent_association(
        self, auth_client, project, milestone, deliverable
    ):
        """Test DELETE returns 404 when association doesn't exist"""
        # Don't create association, just try to delete
        response = auth_client.delete(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables/{deliverable['id']}"
        )
        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["error"].lower()

    def test_remove_association_deliverable_not_found(
        self, auth_client, project, milestone
    ):
        """Test DELETE returns 404 when deliverable doesn't exist"""
        fake_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/milestones/{milestone['id']}/deliverables/{fake_id}"
        )
        assert response.status_code == 404

    def test_remove_association_milestone_not_found(
        self, auth_client, project, deliverable
    ):
        """Test DELETE returns 404 when milestone doesn't exist"""
        fake_milestone_id = str(uuid.uuid4())
        response = auth_client.delete(
            f"/projects/{project['id']}/milestones/{fake_milestone_id}/deliverables/{deliverable['id']}"
        )
        assert response.status_code == 404

    def test_unauthorized_missing_jwt(self, client):
        """Test all endpoints require JWT authentication"""
        project_id = str(uuid.uuid4())
        milestone_id = str(uuid.uuid4())
        deliverable_id = str(uuid.uuid4())

        # GET list
        response = client.get(
            f"/projects/{project_id}/milestones/{milestone_id}/deliverables"
        )
        assert response.status_code == 401

        # POST create
        response = client.post(
            f"/projects/{project_id}/milestones/{milestone_id}/deliverables",
            json={"deliverable_id": deliverable_id},
        )
        assert response.status_code == 401

        # DELETE remove
        response = client.delete(
            f"/projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}"
        )
        assert response.status_code == 401
