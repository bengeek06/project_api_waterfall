"""
app.models.project
------------------

This module defines the SQLAlchemy models for the Project Service.
All models follow the OpenAPI specification defined in specifications/SCHEMAS_SPECIFICATION.md

Models included:
- Project: Core project entity with lifecycle management
- ProjectMember: User membership in projects with roles
- Milestone: Project milestones tracking
- Deliverable: Project deliverables tracking
- MilestoneDeliverableAssociation: Many-to-many association
- ProjectRole: RBAC roles for projects
- ProjectPolicy: RBAC policies grouping permissions
- ProjectPermission: Granular permissions
- RolePolicyAssociation: Many-to-many association
- PolicyPermissionAssociation: Many-to-many association
- ProjectHistory: Audit trail for project changes
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index, CheckConstraint
from app.models.db import db


# ============================================================================
# ASSOCIATION TABLES (Many-to-Many)
# ============================================================================

milestone_deliverable_association = db.Table(
    "milestone_deliverable_association",
    db.Column(
        "milestone_id",
        UUID(as_uuid=True),
        db.ForeignKey("milestones.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "deliverable_id",
        UUID(as_uuid=True),
        db.ForeignKey("deliverables.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("created_at", db.DateTime, nullable=False, default=datetime.utcnow),
)

role_policy_association = db.Table(
    "role_policy_association",
    db.Column(
        "role_id",
        UUID(as_uuid=True),
        db.ForeignKey("project_roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "policy_id",
        UUID(as_uuid=True),
        db.ForeignKey("project_policies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("created_at", db.DateTime, nullable=False, default=datetime.utcnow),
)

policy_permission_association = db.Table(
    "policy_permission_association",
    db.Column(
        "policy_id",
        UUID(as_uuid=True),
        db.ForeignKey("project_policies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "permission_id",
        UUID(as_uuid=True),
        db.ForeignKey("project_permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column("created_at", db.DateTime, nullable=False, default=datetime.utcnow),
)


# ============================================================================
# PROJECT MODEL
# ============================================================================


class Project(db.Model):
    """
    Project model representing a project entity with complete lifecycle management.

    Lifecycle statuses:
    - created: Initial creation
    - initialized: Default roles/policies created
    - consultation: In bidding/consultation phase
    - lost: Lost the bid
    - active: Active execution
    - suspended: Temporarily suspended
    - completed: Execution completed
    - archived: Archived for long-term storage

    Multi-tenant: Isolated by company_id
    Soft delete: Uses removed_at for data recovery
    """

    __tablename__ = "projects"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core fields
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    # Multi-tenancy and ownership
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_id = db.Column(
        db.String(36), nullable=True
    )  # Reference to Identity Service (external UUID as string)
    created_by = db.Column(
        db.String(36), nullable=False
    )  # User who created (external UUID as string)

    # Lifecycle status
    status = db.Column(db.String(20), nullable=False, default="created", index=True)

    # Consultation phase dates
    consultation_date = db.Column(db.Date, nullable=True)
    submission_deadline = db.Column(db.Date, nullable=True)
    notification_date = db.Column(db.Date, nullable=True)

    # Execution phase dates
    contract_start_date = db.Column(db.Date, nullable=True)
    planned_start_date = db.Column(db.Date, nullable=True)
    actual_start_date = db.Column(db.Date, nullable=True)

    # Delivery phase dates
    contract_delivery_date = db.Column(db.Date, nullable=True)
    planned_delivery_date = db.Column(db.Date, nullable=True)
    actual_delivery_date = db.Column(db.Date, nullable=True)

    # Financial data
    contract_amount = db.Column(
        db.Numeric(12, 2), nullable=True
    )  # Decimal for precision
    budget_currency = db.Column(db.String(3), nullable=True, default="EUR")  # ISO 4217

    # Lifecycle timestamps
    suspended_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    archived_at = db.Column(db.DateTime, nullable=True)

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    removed_at = db.Column(db.DateTime, nullable=True)  # Soft delete

    # Relationships
    members = db.relationship(
        "ProjectMember",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    milestones = db.relationship(
        "Milestone",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    deliverables = db.relationship(
        "Deliverable",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    roles = db.relationship(
        "ProjectRole",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    policies = db.relationship(
        "ProjectPolicy",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    history = db.relationship(
        "ProjectHistory",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ProjectHistory.changed_at.desc()",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_projects_company_status", "company_id", "status"),
        Index("idx_projects_company_removed", "company_id", "removed_at"),
        Index("idx_projects_customer", "customer_id"),
        CheckConstraint(
            "status IN ('created', 'initialized', 'consultation', "
            "'lost', 'active', 'suspended', 'completed', 'archived')",
            name="check_project_status",
        ),
        CheckConstraint(
            "budget_currency IS NULL OR length(budget_currency) = 3",
            name="check_currency_code",
        ),
    )

    def __repr__(self):
        return f"<Project {self.name} ({self.status})>"

    def is_active(self):
        """Check if project is not soft-deleted."""
        return self.removed_at is None

    def can_transition_to(self, new_status):
        """
        Validate if status transition is allowed.

        Allowed transitions:
        - created -> initialized
        - initialized -> consultation
        - consultation -> active | lost
        - active -> suspended | completed
        - suspended -> active
        - completed -> archived
        """
        transitions = {
            "created": ["initialized"],
            "initialized": ["consultation"],
            "consultation": ["active", "lost"],
            "lost": [],  # Terminal state
            "active": ["suspended", "completed"],
            "suspended": ["active"],
            "completed": ["archived"],
            "archived": [],  # Terminal state
        }
        return new_status in transitions.get(self.status, [])

    def soft_delete(self):
        """Soft delete the project."""
        self.removed_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        """Restore a soft-deleted project."""
        self.removed_at = None
        db.session.commit()


# ============================================================================
# MILESTONE MODEL
# ============================================================================


class Milestone(db.Model):
    """
    Milestone model representing project milestones.

    Status values:
    - planned: Not started yet
    - in_progress: Currently being worked on
    - completed: Successfully completed
    - delayed: Behind schedule
    - cancelled: Cancelled
    """

    __tablename__ = "milestones"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(
        UUID(as_uuid=True), nullable=False, index=True
    )  # Denormalized for performance

    # Core fields
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    # Status and dates
    status = db.Column(db.String(20), nullable=False, default="planned")
    planned_date = db.Column(db.Date, nullable=True)
    actual_date = db.Column(db.Date, nullable=True)

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    removed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship("Project", back_populates="milestones")
    deliverables = db.relationship(
        "Deliverable",
        secondary=milestone_deliverable_association,
        back_populates="milestones",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("idx_milestones_project_status", "project_id", "status"),
        Index("idx_milestones_company", "company_id"),
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed', 'delayed', 'cancelled')",
            name="check_milestone_status",
        ),
    )

    def __repr__(self):
        return f"<Milestone {self.name} ({self.status})>"


# ============================================================================
# DELIVERABLE MODEL
# ============================================================================


class Deliverable(db.Model):
    """
    Deliverable model representing project deliverables.

    Status values: planned, in_progress, completed, delayed, cancelled
    Type values: document, software, hardware, service, other
    """

    __tablename__ = "deliverables"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Core fields
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    type = db.Column(db.String(20), nullable=False)

    # Status and dates
    status = db.Column(db.String(20), nullable=False, default="planned")
    planned_date = db.Column(db.Date, nullable=True)
    actual_date = db.Column(db.Date, nullable=True)

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    removed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship("Project", back_populates="deliverables")
    milestones = db.relationship(
        "Milestone",
        secondary=milestone_deliverable_association,
        back_populates="deliverables",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("idx_deliverables_project_status", "project_id", "status"),
        Index("idx_deliverables_company", "company_id"),
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed', 'delayed', 'cancelled')",
            name="check_deliverable_status",
        ),
        CheckConstraint(
            "type IN ('document', 'software', 'hardware', 'service', 'other')",
            name="check_deliverable_type",
        ),
    )

    def __repr__(self):
        return f"<Deliverable {self.name} ({self.type})>"


# ============================================================================
# PROJECT MEMBER MODEL
# ============================================================================


class ProjectMember(db.Model):
    """
    ProjectMember model representing user membership in projects.

    Associates users (from Identity Service) with projects and assigns roles.
    """

    __tablename__ = "project_members"

    # Composite primary key (project_id, user_id)
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = db.Column(
        UUID(as_uuid=True), primary_key=True
    )  # Reference to Identity Service

    # Denormalized for performance
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Role assignment
    role_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("project_roles.id"), nullable=False
    )

    # Audit trail
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    added_by = db.Column(
        UUID(as_uuid=True), nullable=False
    )  # User who added this member
    removed_at = db.Column(db.DateTime, nullable=True)  # Soft delete

    # Relationships
    project = db.relationship("Project", back_populates="members")
    role = db.relationship("ProjectRole")

    __table_args__ = (
        Index("idx_project_members_user", "user_id"),
        Index("idx_project_members_company", "company_id"),
        Index("idx_project_members_role", "role_id"),
    )

    def __repr__(self):
        return f"<ProjectMember user={self.user_id} project={self.project_id}>"


# ============================================================================
# RBAC: PROJECT ROLE MODEL
# ============================================================================


class ProjectRole(db.Model):
    """
    ProjectRole model representing roles in project RBAC system.

    Default roles (created automatically for each project):
    - owner: Full access
    - validator: Can validate files
    - contributor: Can read/write files
    - viewer: Read-only access

    Custom roles can be created with is_default=False.
    """

    __tablename__ = "project_roles"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Core fields
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    is_default = db.Column(
        db.Boolean, nullable=False, default=False
    )  # True for owner/validator/contributor/viewer

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    removed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship("Project", back_populates="roles")
    policies = db.relationship(
        "ProjectPolicy",
        secondary=role_policy_association,
        back_populates="roles",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("idx_project_roles_project_name", "project_id", "name"),
        Index("idx_project_roles_company", "company_id"),
        db.UniqueConstraint("project_id", "name", name="uq_project_role_name"),
    )

    def __repr__(self):
        return f"<ProjectRole {self.name}>"


# ============================================================================
# RBAC: PROJECT POLICY MODEL
# ============================================================================


class ProjectPolicy(db.Model):
    """
    ProjectPolicy model representing policy groups in RBAC system.

    Policies group related permissions together.
    Example: "File Management" policy groups read_files, write_files, delete_files.
    """

    __tablename__ = "project_policies"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Core fields
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    removed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship("Project", back_populates="policies")
    roles = db.relationship(
        "ProjectRole",
        secondary=role_policy_association,
        back_populates="policies",
        lazy="dynamic",
    )
    permissions = db.relationship(
        "ProjectPermission",
        secondary=policy_permission_association,
        back_populates="policies",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("idx_project_policies_project_name", "project_id", "name"),
        Index("idx_project_policies_company", "company_id"),
        db.UniqueConstraint("project_id", "name", name="uq_project_policy_name"),
    )

    def __repr__(self):
        return f"<ProjectPolicy {self.name}>"


# ============================================================================
# RBAC: PROJECT PERMISSION MODEL
# ============================================================================


class ProjectPermission(db.Model):
    """
    ProjectPermission model representing granular permissions.

    Predefined permissions:
    File operations (mapped to Storage Service):
    - read_files: Read files in Storage
    - write_files: Write/upload files in Storage
    - delete_files: Delete files in Storage
    - lock_files: Lock files in Storage
    - validate_files: Validate files in Storage

    Project operations:
    - update_project: Update project metadata
    - delete_project: Delete/archive project

    Member operations:
    - manage_members: Add/remove project members
    - manage_roles: Create/modify project roles
    - manage_policies: Create/modify project policies
    """

    __tablename__ = "project_permissions"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Core fields
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    category = db.Column(
        db.String(20), nullable=False
    )  # file_operations, project_operations, member_operations

    # Audit trail
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    removed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    policies = db.relationship(
        "ProjectPolicy",
        secondary=policy_permission_association,
        back_populates="permissions",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("idx_project_permissions_project_name", "project_id", "name"),
        Index("idx_project_permissions_company", "company_id"),
        Index("idx_project_permissions_category", "category"),
        db.UniqueConstraint("project_id", "name", name="uq_project_permission_name"),
        CheckConstraint(
            "category IN ('file_operations', 'project_operations', 'member_operations')",
            name="check_permission_category",
        ),
    )

    def __repr__(self):
        return f"<ProjectPermission {self.name} ({self.category})>"


# ============================================================================
# PROJECT HISTORY MODEL (Audit Trail)
# ============================================================================


class ProjectHistory(db.Model):
    """
    ProjectHistory model for audit trail of project changes.

    Tracks all significant changes to projects for compliance and debugging.
    """

    __tablename__ = "project_history"

    # Primary key
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)

    # Change tracking
    changed_by = db.Column(
        db.String(36), nullable=False
    )  # User who made the change (external UUID as string)
    changed_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # Change details
    action = db.Column(
        db.String(20), nullable=False
    )  # created, updated, status_changed, deleted, restored
    field_name = db.Column(
        db.String(50), nullable=True
    )  # Which field changed (for updates)
    old_value = db.Column(
        db.Text, nullable=True
    )  # Previous value (JSON for complex types)
    new_value = db.Column(db.Text, nullable=True)  # New value (JSON for complex types)
    comment = db.Column(db.String(500), nullable=True)  # Optional comment

    # Relationships
    project = db.relationship("Project", back_populates="history")

    __table_args__ = (
        Index("idx_project_history_project_date", "project_id", "changed_at"),
        Index("idx_project_history_company", "company_id"),
        Index("idx_project_history_action", "action"),
        CheckConstraint(
            "action IN ('created', 'updated', 'status_changed', "
            "'deleted', 'restored', 'member_added', 'member_removed', "
            "'role_assigned')",
            name="check_history_action",
        ),
    )

    def __repr__(self):
        return f"<ProjectHistory {self.action} at {self.changed_at}>"
