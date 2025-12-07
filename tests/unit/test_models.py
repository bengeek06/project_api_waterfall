# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
tests.test_models
-----------------

Unit tests for Project Service models.
Tests model validation, relationships, soft deletes, and business logic.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.project import (
    Deliverable,
    Milestone,
    Project,
    ProjectHistory,
    ProjectMember,
    ProjectPermission,
    ProjectPolicy,
    ProjectRole,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def company_id():
    """Fixture for company UUID (as string for SQLite compatibility)."""
    return str(uuid4())


@pytest.fixture
def user_id():
    """Fixture for user UUID (as string for SQLite compatibility)."""
    return str(uuid4())


@pytest.fixture
def customer_id():
    """Fixture for customer UUID (as string for SQLite compatibility)."""
    return str(uuid4())


@pytest.fixture
def sample_project(session, company_id, user_id):
    """Create a sample project for testing."""
    project = Project(
        name="Test Project",
        description="A test project",
        company_id=company_id,
        created_by=user_id,
        status="created",
    )
    session.add(project)
    session.commit()
    return project


@pytest.fixture
def sample_role(session, sample_project, company_id):
    """Create a sample role for testing."""
    role = ProjectRole(
        project_id=sample_project.id,
        company_id=company_id,
        name="owner",
        description="Project owner",
        is_default=True,
    )
    session.add(role)
    session.commit()
    return role


# ============================================================================
# PROJECT MODEL TESTS
# ============================================================================


class TestProjectModel:
    """Tests for the Project model."""

    def test_create_project_minimal(self, session, company_id, user_id):
        """Test creating a project with minimal required fields."""
        project = Project(
            name="Minimal Project",
            company_id=company_id,
            created_by=user_id,
        )
        session.add(project)
        session.commit()

        assert project.id is not None
        assert project.name == "Minimal Project"
        assert project.company_id == company_id
        assert project.created_by == user_id
        assert project.status == "created"  # Default status
        assert project.is_active() is True
        assert project.removed_at is None

    def test_create_project_full(
        self, session, company_id, user_id, customer_id
    ):
        """Test creating a project with all fields."""
        project = Project(
            name="Full Project",
            description="A complete project",
            company_id=company_id,
            customer_id=customer_id,
            created_by=user_id,
            status="active",
            consultation_date=date(2025, 1, 15),
            submission_deadline=date(2025, 2, 15),
            notification_date=date(2025, 3, 1),
            contract_start_date=date(2025, 3, 15),
            planned_start_date=date(2025, 3, 20),
            actual_start_date=date(2025, 3, 22),
            contract_delivery_date=date(2025, 12, 31),
            planned_delivery_date=date(2025, 12, 15),
            actual_delivery_date=date(2025, 12, 10),
            contract_amount=Decimal("250000.00"),
            budget_currency="EUR",
        )
        session.add(project)
        session.commit()

        assert project.id is not None
        assert project.name == "Full Project"
        assert project.customer_id == customer_id
        assert project.status == "active"
        assert project.contract_amount == Decimal("250000.00")
        assert project.budget_currency == "EUR"
        assert project.consultation_date == date(2025, 1, 15)

    def test_project_status_transition_valid(self, session, sample_project):
        """Test valid status transitions."""
        # created -> initialized
        assert sample_project.can_transition_to("initialized") is True
        sample_project.status = "initialized"

        # initialized -> consultation
        assert sample_project.can_transition_to("consultation") is True
        sample_project.status = "consultation"

        # consultation -> active
        assert sample_project.can_transition_to("active") is True
        sample_project.status = "active"

        # active -> suspended
        assert sample_project.can_transition_to("suspended") is True
        sample_project.status = "suspended"

        # suspended -> active (can resume)
        assert sample_project.can_transition_to("active") is True
        sample_project.status = "active"

        # active -> completed
        assert sample_project.can_transition_to("completed") is True
        sample_project.status = "completed"

        # completed -> archived
        assert sample_project.can_transition_to("archived") is True

    def test_project_status_transition_invalid(self, session, sample_project):
        """Test invalid status transitions."""
        # created -> active (should go through initialized and consultation)
        assert sample_project.can_transition_to("active") is False

        # created -> completed (can't complete without starting)
        assert sample_project.can_transition_to("completed") is False

        sample_project.status = "consultation"
        # consultation -> lost
        sample_project.status = "lost"

        # lost is terminal state
        assert sample_project.can_transition_to("active") is False
        assert sample_project.can_transition_to("completed") is False

    def test_project_soft_delete(self, session, sample_project):
        """Test soft delete functionality."""
        assert sample_project.is_active() is True
        assert sample_project.removed_at is None

        sample_project.soft_delete()

        assert sample_project.is_active() is False
        assert sample_project.removed_at is not None
        assert isinstance(sample_project.removed_at, datetime)

    def test_project_restore(self, session, sample_project):
        """Test restoring a soft-deleted project."""
        sample_project.soft_delete()
        assert sample_project.is_active() is False

        sample_project.restore()

        assert sample_project.is_active() is True
        assert sample_project.removed_at is None

    def test_project_repr(self, session, sample_project):
        """Test string representation."""
        assert "Test Project" in repr(sample_project)
        assert "created" in repr(sample_project)


# ============================================================================
# MILESTONE MODEL TESTS
# ============================================================================


class TestMilestoneModel:
    """Tests for the Milestone model."""

    def test_create_milestone(self, session, sample_project, company_id):
        """Test creating a milestone."""
        milestone = Milestone(
            project_id=sample_project.id,
            company_id=company_id,
            name="Phase 1 Completion",
            description="Complete phase 1 deliverables",
            status="planned",
            planned_date=date(2025, 6, 30),
        )
        session.add(milestone)
        session.commit()

        assert milestone.id is not None
        assert milestone.name == "Phase 1 Completion"
        assert milestone.status == "planned"
        assert milestone.planned_date == date(2025, 6, 30)
        assert milestone.project_id == sample_project.id

    def test_milestone_project_relationship(
        self, session, sample_project, company_id
    ):
        """Test milestone-project relationship."""
        milestone = Milestone(
            project_id=sample_project.id,
            company_id=company_id,
            name="Test Milestone",
            status="planned",
        )
        session.add(milestone)
        session.commit()

        # Access from milestone side
        assert milestone.project.id == sample_project.id

        # Access from project side
        milestones = sample_project.milestones.all()
        assert len(milestones) == 1
        assert milestones[0].id == milestone.id


# ============================================================================
# DELIVERABLE MODEL TESTS
# ============================================================================


class TestDeliverableModel:
    """Tests for the Deliverable model."""

    def test_create_deliverable(self, session, sample_project, company_id):
        """Test creating a deliverable."""
        deliverable = Deliverable(
            project_id=sample_project.id,
            company_id=company_id,
            name="Requirements Document",
            description="Project requirements specification",
            type="document",
            status="planned",
            planned_date=date(2025, 4, 30),
        )
        session.add(deliverable)
        session.commit()

        assert deliverable.id is not None
        assert deliverable.name == "Requirements Document"
        assert deliverable.type == "document"
        assert deliverable.status == "planned"

    def test_deliverable_types(self, session, sample_project, company_id):
        """Test different deliverable types."""
        types = ["document", "software", "hardware", "service", "other"]

        for dtype in types:
            deliverable = Deliverable(
                project_id=sample_project.id,
                company_id=company_id,
                name=f"Test {dtype}",
                type=dtype,
                status="planned",
            )
            session.add(deliverable)

        session.commit()

        deliverables = sample_project.deliverables.all()
        assert len(deliverables) == len(types)

    def test_milestone_deliverable_association(
        self, session, sample_project, company_id
    ):
        """Test many-to-many association between milestones and deliverables."""
        milestone = Milestone(
            project_id=sample_project.id,
            company_id=company_id,
            name="Phase 1",
            status="planned",
        )

        deliverable1 = Deliverable(
            project_id=sample_project.id,
            company_id=company_id,
            name="Doc 1",
            type="document",
            status="planned",
        )

        deliverable2 = Deliverable(
            project_id=sample_project.id,
            company_id=company_id,
            name="Doc 2",
            type="document",
            status="planned",
        )

        session.add_all([milestone, deliverable1, deliverable2])
        session.commit()

        # Associate deliverables with milestone
        milestone.deliverables.append(deliverable1)
        milestone.deliverables.append(deliverable2)
        session.commit()

        # Verify association from milestone side
        assert milestone.deliverables.count() == 2

        # Verify association from deliverable side
        assert deliverable1.milestones.count() == 1
        assert deliverable1.milestones.first().id == milestone.id


# ============================================================================
# RBAC MODEL TESTS
# ============================================================================


class TestProjectRoleModel:
    """Tests for the ProjectRole model."""

    def test_create_default_role(self, session, sample_project, company_id):
        """Test creating a default role."""
        role = ProjectRole(
            project_id=sample_project.id,
            company_id=company_id,
            name="owner",
            description="Project owner with full access",
            is_default=True,
        )
        session.add(role)
        session.commit()

        assert role.id is not None
        assert role.name == "owner"
        assert role.is_default is True

    def test_create_custom_role(self, session, sample_project, company_id):
        """Test creating a custom role."""
        role = ProjectRole(
            project_id=sample_project.id,
            company_id=company_id,
            name="custom_role",
            description="Custom role for special users",
            is_default=False,
        )
        session.add(role)
        session.commit()

        assert role.id is not None
        assert role.name == "custom_role"
        assert role.is_default is False

    def test_role_unique_constraint(self, session, sample_project, company_id):
        """Test that role names must be unique within a project."""
        role1 = ProjectRole(
            project_id=sample_project.id,
            company_id=company_id,
            name="owner",
            is_default=True,
        )
        session.add(role1)
        session.commit()

        # Try to create another role with same name in same project
        role2 = ProjectRole(
            project_id=sample_project.id,
            company_id=company_id,
            name="owner",  # Duplicate name
            is_default=False,
        )
        session.add(role2)

        with pytest.raises(Exception):  # IntegrityError
            session.commit()
        session.rollback()


class TestProjectPolicyModel:
    """Tests for the ProjectPolicy model."""

    def test_create_policy(self, session, sample_project, company_id):
        """Test creating a policy."""
        policy = ProjectPolicy(
            project_id=sample_project.id,
            company_id=company_id,
            name="File Management",
            description="Permissions for file operations",
        )
        session.add(policy)
        session.commit()

        assert policy.id is not None
        assert policy.name == "File Management"


class TestProjectPermissionModel:
    """Tests for the ProjectPermission model."""

    def test_create_permission(self, session, sample_project, company_id):
        """Test creating a permission."""
        permission = ProjectPermission(
            project_id=sample_project.id,
            company_id=company_id,
            name="read_files",
            description="Read files in Storage",
            category="file_operations",
        )
        session.add(permission)
        session.commit()

        assert permission.id is not None
        assert permission.name == "read_files"
        assert permission.category == "file_operations"

    def test_permission_categories(self, session, sample_project, company_id):
        """Test different permission categories."""
        categories = [
            ("read_files", "file_operations"),
            ("update_project", "project_operations"),
            ("manage_members", "member_operations"),
        ]

        for name, category in categories:
            permission = ProjectPermission(
                project_id=sample_project.id,
                company_id=company_id,
                name=name,
                category=category,
            )
            session.add(permission)

        session.commit()

        permissions = ProjectPermission.query.filter_by(
            project_id=sample_project.id
        ).all()
        assert len(permissions) == len(categories)


class TestRBACAssociations:
    """Tests for RBAC association tables."""

    def test_role_policy_association(
        self, session, sample_project, company_id
    ):
        """Test associating policies with roles."""
        role = ProjectRole(
            project_id=sample_project.id,
            company_id=company_id,
            name="owner",
            is_default=True,
        )

        policy1 = ProjectPolicy(
            project_id=sample_project.id,
            company_id=company_id,
            name="File Access",
        )

        policy2 = ProjectPolicy(
            project_id=sample_project.id,
            company_id=company_id,
            name="Project Management",
        )

        session.add_all([role, policy1, policy2])
        session.commit()

        # Associate policies with role
        role.policies.append(policy1)
        role.policies.append(policy2)
        session.commit()

        # Verify association
        assert role.policies.count() == 2
        assert policy1.roles.count() == 1

    def test_policy_permission_association(
        self, session, sample_project, company_id
    ):
        """Test associating permissions with policies."""
        policy = ProjectPolicy(
            project_id=sample_project.id,
            company_id=company_id,
            name="File Operations",
        )

        perm1 = ProjectPermission(
            project_id=sample_project.id,
            company_id=company_id,
            name="read_files",
            category="file_operations",
        )

        perm2 = ProjectPermission(
            project_id=sample_project.id,
            company_id=company_id,
            name="write_files",
            category="file_operations",
        )

        session.add_all([policy, perm1, perm2])
        session.commit()

        # Associate permissions with policy
        policy.permissions.append(perm1)
        policy.permissions.append(perm2)
        session.commit()

        # Verify association
        assert policy.permissions.count() == 2
        assert perm1.policies.count() == 1


# ============================================================================
# PROJECT MEMBER TESTS
# ============================================================================


class TestProjectMemberModel:
    """Tests for the ProjectMember model."""

    def test_create_project_member(
        self, session, sample_project, sample_role, company_id, user_id
    ):
        """Test adding a member to a project."""
        member = ProjectMember(
            project_id=sample_project.id,
            user_id=user_id,
            company_id=company_id,
            role_id=sample_role.id,
            added_by=user_id,
        )
        session.add(member)
        session.commit()

        assert member.project_id == sample_project.id
        assert member.user_id == user_id
        assert member.role_id == sample_role.id
        assert member.removed_at is None

    def test_project_member_relationship(
        self, session, sample_project, sample_role, company_id, user_id
    ):
        """Test project-member relationship."""
        member = ProjectMember(
            project_id=sample_project.id,
            user_id=user_id,
            company_id=company_id,
            role_id=sample_role.id,
            added_by=user_id,
        )
        session.add(member)
        session.commit()

        # Access from project side
        members = sample_project.members.all()
        assert len(members) == 1
        assert members[0].user_id == user_id

        # Access role
        assert member.role.id == sample_role.id


# ============================================================================
# PROJECT HISTORY TESTS
# ============================================================================


class TestProjectHistoryModel:
    """Tests for the ProjectHistory model."""

    def test_create_history_entry(
        self, session, sample_project, company_id, user_id
    ):
        """Test creating a history entry."""
        history = ProjectHistory(
            project_id=sample_project.id,
            company_id=company_id,
            changed_by=user_id,
            action="created",
            comment="Project created",
        )
        session.add(history)
        session.commit()

        assert history.id is not None
        assert history.action == "created"
        assert history.changed_by == user_id

    def test_history_field_change(
        self, session, sample_project, company_id, user_id
    ):
        """Test tracking field changes."""
        history = ProjectHistory(
            project_id=sample_project.id,
            company_id=company_id,
            changed_by=user_id,
            action="updated",
            field_name="status",
            old_value="created",
            new_value="initialized",
            comment="Project initialized with default roles",
        )
        session.add(history)
        session.commit()

        assert history.field_name == "status"
        assert history.old_value == "created"
        assert history.new_value == "initialized"

    def test_project_history_relationship(
        self, session, sample_project, company_id, user_id
    ):
        """Test project-history relationship."""
        history1 = ProjectHistory(
            project_id=sample_project.id,
            company_id=company_id,
            changed_by=user_id,
            action="created",
        )

        history2 = ProjectHistory(
            project_id=sample_project.id,
            company_id=company_id,
            changed_by=user_id,
            action="updated",
        )

        session.add_all([history1, history2])
        session.commit()

        # Access from project side (ordered by changed_at desc)
        history_entries = sample_project.history.all()
        assert len(history_entries) == 2


# ============================================================================
# CASCADE DELETE TESTS
# ============================================================================


class TestCascadeDeletes:
    """Tests for cascade delete behavior."""

    def test_project_delete_cascades_to_milestones(
        self, session, sample_project, company_id
    ):
        """Test that deleting a project deletes its milestones."""
        milestone = Milestone(
            project_id=sample_project.id,
            company_id=company_id,
            name="Test Milestone",
            status="planned",
        )
        session.add(milestone)
        session.commit()

        milestone_id = milestone.id
        project_id = sample_project.id

        # Delete project
        session.delete(sample_project)
        session.commit()

        # Verify milestone is also deleted
        assert session.get(Milestone, milestone_id) is None
        assert session.get(Project, project_id) is None

    def test_project_delete_cascades_to_roles(
        self, session, sample_project, sample_role
    ):
        """Test that deleting a project deletes its roles."""
        role_id = sample_role.id

        # Delete project
        session.delete(sample_project)
        session.commit()

        # Verify role is also deleted
        assert session.get(ProjectRole, role_id) is None
