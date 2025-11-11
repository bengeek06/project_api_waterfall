"""
tests.unit.test_access_control
-------------------------------

Unit tests for Access Control resources.

Tests cover:
- File access checks (batch validation)
- Project access checks (batch validation)
- Complete RBAC chain evaluation (User → Member → Role → Policy → Permission)
- Permission validation for various actions
- Invalid request handling
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
def project_with_permissions(auth_client):
    """Create a project, initialize it, and set up RBAC chain."""
    # Create project
    project_response = auth_client.post(
        "/projects",
        json={"name": "Test Project", "description": "For access tests"},
    )
    project = project_response.get_json()

    # Initialize project to seed permissions
    auth_client.patch(
        f"/projects/{project['id']}", json={"status": "initialized"}
    )

    # Create a role
    role_response = auth_client.post(
        f"/projects/{project['id']}/roles",
        json={"name": "Test Role", "description": "Test role"},
    )
    role = role_response.get_json()

    # Create a member (the authenticated user)
    member_response = auth_client.post(
        f"/projects/{project['id']}/members",
        json={
            "user_id": auth_client.user_id,
            "role_id": role["id"],
        },
    )
    member = member_response.get_json()

    # Create a policy
    policy_response = auth_client.post(
        f"/projects/{project['id']}/policies",
        json={"name": "Test Policy", "description": "Test policy"},
    )
    policy = policy_response.get_json()

    # Get some permissions
    permissions_response = auth_client.get(
        f"/projects/{project['id']}/permissions"
    )
    permissions = permissions_response.get_json()

    # Assign permissions to policy
    read_files_perm = next(p for p in permissions if p["name"] == "read_files")
    write_files_perm = next(
        p for p in permissions if p["name"] == "write_files"
    )
    update_project_perm = next(
        p for p in permissions if p["name"] == "update_project"
    )

    auth_client.post(
        f"/projects/{project['id']}/policies/{policy['id']}/permissions",
        json={"permission_id": read_files_perm["id"]},
    )
    auth_client.post(
        f"/projects/{project['id']}/policies/{policy['id']}/permissions",
        json={"permission_id": write_files_perm["id"]},
    )
    auth_client.post(
        f"/projects/{project['id']}/policies/{policy['id']}/permissions",
        json={"permission_id": update_project_perm["id"]},
    )

    # Assign policy to role
    auth_client.post(
        f"/projects/{project['id']}/roles/{role['id']}/policies",
        json={"policy_id": policy["id"]},
    )

    return {
        "project": project,
        "member": member,
        "role": role,
        "policy": policy,
        "permissions": {
            "read_files": read_files_perm,
            "write_files": write_files_perm,
            "update_project": update_project_perm,
        },
    }


class TestCheckFileAccessResource:
    """Tests for CheckFileAccessResource (POST /check-file-access)"""

    def test_check_file_access_allowed(
        self, auth_client, project_with_permissions
    ):
        """Test file access check returns allowed=true when user has permission"""
        project = project_with_permissions["project"]
        file_id = str(uuid.uuid4())

        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": file_id,
                        "project_id": project["id"],
                        "action": "read_files",
                    }
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["file_id"] == file_id
        assert result["project_id"] == project["id"]
        assert result["action"] == "read_files"
        assert result["allowed"] is True

    def test_check_file_access_denied(
        self, auth_client, project_with_permissions
    ):
        """Test file access check returns allowed=false when user lacks permission"""
        project = project_with_permissions["project"]
        file_id = str(uuid.uuid4())

        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": file_id,
                        "project_id": project["id"],
                        "action": "delete_files",  # Not assigned to policy
                    }
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["allowed"] is False

    def test_check_file_access_batch(
        self, auth_client, project_with_permissions
    ):
        """Test batch file access checks"""
        project = project_with_permissions["project"]
        file1_id = str(uuid.uuid4())
        file2_id = str(uuid.uuid4())
        file3_id = str(uuid.uuid4())

        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": file1_id,
                        "project_id": project["id"],
                        "action": "read_files",
                    },
                    {
                        "file_id": file2_id,
                        "project_id": project["id"],
                        "action": "write_files",
                    },
                    {
                        "file_id": file3_id,
                        "project_id": project["id"],
                        "action": "delete_files",
                    },
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 3
        assert data["results"][0]["allowed"] is True  # read_files
        assert data["results"][1]["allowed"] is True  # write_files
        assert data["results"][2]["allowed"] is False  # delete_files

    def test_check_file_access_non_member(self, auth_client):
        """Test file access denied when user is not a project member"""
        # Create another client with different user
        other_user_id = str(uuid.uuid4())
        other_token = create_jwt_token(auth_client.company_id, other_user_id)
        auth_client.set_cookie("access_token", other_token, domain="localhost")

        # Create a project but don't add the user as member
        project_response = auth_client.post(
            "/projects", json={"name": "Other Project"}
        )
        project = project_response.get_json()

        file_id = str(uuid.uuid4())

        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": file_id,
                        "project_id": project["id"],
                        "action": "read_files",
                    }
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["results"][0]["allowed"] is False

    def test_check_file_access_invalid_request(self, auth_client):
        """Test file access check with invalid request"""
        # Missing file_checks
        response = auth_client.post("/check-file-access", json={})
        assert response.status_code == 400

        # file_checks not an array
        response = auth_client.post(
            "/check-file-access", json={"file_checks": "not-an-array"}
        )
        assert response.status_code == 400

    def test_check_file_access_invalid_check_format(self, auth_client):
        """Test file access check with invalid check format"""
        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": str(uuid.uuid4())
                    }  # Missing project_id and action
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        result = data["results"][0]
        assert result["allowed"] is False
        assert "reason" in result

    def test_check_file_access_project_not_found(self, auth_client):
        """Test file access check with non-existent project"""
        response = auth_client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": str(uuid.uuid4()),
                        "project_id": str(uuid.uuid4()),
                        "action": "read_files",
                    }
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["results"][0]["allowed"] is False

    def test_check_file_access_unauthorized(self, client):
        """Test file access check requires authentication"""
        response = client.post(
            "/check-file-access",
            json={
                "file_checks": [
                    {
                        "file_id": str(uuid.uuid4()),
                        "project_id": str(uuid.uuid4()),
                        "action": "read_files",
                    }
                ]
            },
        )
        assert response.status_code == 401


class TestCheckProjectAccessResource:
    """Tests for CheckProjectAccessResource (POST /check-project-access)"""

    def test_check_project_access_allowed(
        self, auth_client, project_with_permissions
    ):
        """Test project access check returns allowed=true when user has permission"""
        project = project_with_permissions["project"]

        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {"project_id": project["id"], "action": "update_project"}
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["project_id"] == project["id"]
        assert result["action"] == "update_project"
        assert result["allowed"] is True

    def test_check_project_access_denied(
        self, auth_client, project_with_permissions
    ):
        """Test project access check returns allowed=false when user lacks permission"""
        project = project_with_permissions["project"]

        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {"project_id": project["id"], "action": "delete_project"}
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["allowed"] is False

    def test_check_project_access_batch(
        self, auth_client, project_with_permissions
    ):
        """Test batch project access checks"""
        project = project_with_permissions["project"]

        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {"project_id": project["id"], "action": "update_project"},
                    {"project_id": project["id"], "action": "delete_project"},
                    {"project_id": project["id"], "action": "manage_members"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["results"]) == 3
        assert data["results"][0]["allowed"] is True  # update_project
        assert data["results"][1]["allowed"] is False  # delete_project
        assert data["results"][2]["allowed"] is False  # manage_members

    def test_check_project_access_non_member(self, auth_client):
        """Test project access denied when user is not a project member"""
        # Create another client with different user
        other_user_id = str(uuid.uuid4())
        other_token = create_jwt_token(auth_client.company_id, other_user_id)
        auth_client.set_cookie("access_token", other_token, domain="localhost")

        # Create a project but don't add the user as member
        project_response = auth_client.post(
            "/projects", json={"name": "Other Project"}
        )
        project = project_response.get_json()

        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {"project_id": project["id"], "action": "update_project"}
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["results"][0]["allowed"] is False

    def test_check_project_access_invalid_request(self, auth_client):
        """Test project access check with invalid request"""
        # Missing project_checks
        response = auth_client.post("/check-project-access", json={})
        assert response.status_code == 400

        # project_checks not an array
        response = auth_client.post(
            "/check-project-access", json={"project_checks": "not-an-array"}
        )
        assert response.status_code == 400

    def test_check_project_access_invalid_check_format(self, auth_client):
        """Test project access check with invalid check format"""
        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [{"project_id": str(uuid.uuid4())}]
            },  # Missing action
        )

        assert response.status_code == 200
        data = response.get_json()
        result = data["results"][0]
        assert result["allowed"] is False
        assert "reason" in result

    def test_check_project_access_project_not_found(self, auth_client):
        """Test project access check with non-existent project"""
        response = auth_client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {
                        "project_id": str(uuid.uuid4()),
                        "action": "update_project",
                    }
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["results"][0]["allowed"] is False

    def test_check_project_access_unauthorized(self, client):
        """Test project access check requires authentication"""
        response = client.post(
            "/check-project-access",
            json={
                "project_checks": [
                    {
                        "project_id": str(uuid.uuid4()),
                        "action": "update_project",
                    }
                ]
            },
        )
        assert response.status_code == 401
