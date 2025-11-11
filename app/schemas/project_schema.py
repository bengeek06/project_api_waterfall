"""
app.schemas.project_schema
---------------------------

Marshmallow schemas for Project Service models.
Handles serialization, deserialization, and validation.
"""

from marshmallow import ValidationError, fields, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

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
# PROJECT SCHEMAS
# ============================================================================


class ProjectSchema(SQLAlchemyAutoSchema):
    """
    Schema for Project model.

    Handles serialization/deserialization with validation for:
    - Required fields
    - Status transitions
    - Date field consistency
    - Currency code format
    """

    class Meta:
        """Meta configuration for ProjectSchema."""

        model = Project
        load_instance = True
        include_fk = True
        dump_only = (
            "id",
            "created_at",
            "updated_at",
            "removed_at",
            "suspended_at",
            "completed_at",
            "archived_at",
        )

    @validates("status")
    def validate_status(self, value):
        """Validate project status is in allowed values."""
        allowed_statuses = [
            "created",
            "initialized",
            "consultation",
            "lost",
            "active",
            "suspended",
            "completed",
            "archived",
        ]
        if value not in allowed_statuses:
            raise ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value

    @validates("budget_currency")
    def validate_currency(self, value):
        """Validate currency code is 3 uppercase letters (ISO 4217)."""
        if value and (len(value) != 3 or not value.isupper()):
            raise ValidationError(
                "Currency code must be 3 uppercase letters (e.g., EUR, USD)"
            )
        return value

    @validates("name")
    def validate_name(self, value):
        """Validate project name is not empty."""
        if not value or not value.strip():
            raise ValidationError("Project name cannot be empty")
        return value


class ProjectCreateSchema(SQLAlchemyAutoSchema):
    """
    Schema for creating a new project.
    Only includes fields needed at creation time.
    """

    class Meta:
        """Meta configuration for ProjectCreateSchema."""

        model = Project
        load_instance = False  # Don't try to load instance, just validate data
        include_fk = True
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "removed_at",
            "suspended_at",
            "completed_at",
            "archived_at",
        )


class ProjectUpdateSchema(SQLAlchemyAutoSchema):
    """
    Schema for updating an existing project.
    All fields are optional for partial updates.
    """

    class Meta:
        """Meta configuration for ProjectUpdateSchema."""

        model = Project
        load_instance = False
        include_fk = True
        exclude = (
            "id",
            "company_id",
            "created_by",
            "created_at",
            "updated_at",
            "removed_at",
        )
        # Make all fields optional for PATCH
        partial = True


# ============================================================================
# MILESTONE SCHEMAS
# ============================================================================


class MilestoneSchema(SQLAlchemyAutoSchema):
    """Schema for Milestone model."""

    class Meta:
        """Meta configuration for MilestoneSchema."""

        model = Milestone
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at", "removed_at")

    @validates("status")
    def validate_status(self, value):
        """Validate milestone status."""
        allowed_statuses = [
            "planned",
            "in_progress",
            "completed",
            "delayed",
            "cancelled",
        ]
        if value not in allowed_statuses:
            raise ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value


class MilestoneCreateSchema(SQLAlchemyAutoSchema):
    """Schema for creating a new milestone."""

    class Meta:
        """Meta configuration for MilestoneCreateSchema."""

        model = Milestone
        load_instance = False  # Don't try to load instance
        include_fk = True
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "removed_at",
        )


class MilestoneUpdateSchema(SQLAlchemyAutoSchema):
    """Schema for updating a milestone."""

    class Meta:
        """Meta configuration for MilestoneUpdateSchema."""

        model = Milestone
        load_instance = False
        include_fk = True
        exclude = (
            "id",
            "project_id",
            "company_id",
            "created_at",
            "updated_at",
            "removed_at",
        )
        partial = True


# ============================================================================
# DELIVERABLE SCHEMAS
# ============================================================================


class DeliverableSchema(SQLAlchemyAutoSchema):
    """Schema for Deliverable model."""

    class Meta:
        """Meta configuration for DeliverableSchema."""

        model = Deliverable
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at", "removed_at")

    @validates("status")
    def validate_status(self, value):
        """Validate deliverable status."""
        allowed_statuses = [
            "planned",
            "in_progress",
            "completed",
            "delayed",
            "cancelled",
        ]
        if value not in allowed_statuses:
            raise ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value

    @validates("type")
    def validate_type(self, value):
        """Validate deliverable type."""
        allowed_types = [
            "document",
            "software",
            "hardware",
            "service",
            "other",
        ]
        if value not in allowed_types:
            raise ValidationError(f"Type must be one of: {', '.join(allowed_types)}")
        return value


class DeliverableCreateSchema(SQLAlchemyAutoSchema):
    """Schema for creating a new deliverable."""

    class Meta:
        """Meta configuration for DeliverableCreateSchema."""

        model = Deliverable
        load_instance = False  # Don't try to load instance
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "removed_at")


class DeliverableUpdateSchema(SQLAlchemyAutoSchema):
    """Schema for updating a deliverable."""

    class Meta:
        """Meta configuration for DeliverableUpdateSchema."""

        model = Deliverable
        load_instance = False
        include_fk = True
        exclude = (
            "id",
            "project_id",
            "company_id",
            "created_at",
            "updated_at",
            "removed_at",
        )
        partial = True


# ============================================================================
# RBAC SCHEMAS
# ============================================================================


class ProjectRoleSchema(SQLAlchemyAutoSchema):
    """Schema for ProjectRole model."""

    class Meta:
        """Meta configuration for ProjectRoleSchema."""

        model = ProjectRole
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at", "removed_at")


class ProjectRoleCreateSchema(SQLAlchemyAutoSchema):
    """Schema for creating a new role."""

    class Meta:
        """Meta configuration for ProjectRoleCreateSchema."""

        model = ProjectRole
        load_instance = True
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "removed_at")


class ProjectRoleUpdateSchema(SQLAlchemyAutoSchema):
    """Schema for updating a role."""

    class Meta:
        """Meta configuration for ProjectRoleUpdateSchema."""

        model = ProjectRole
        load_instance = False
        include_fk = True
        exclude = (
            "id",
            "project_id",
            "company_id",
            "is_default",
            "created_at",
            "updated_at",
            "removed_at",
        )
        partial = True


class ProjectPolicySchema(SQLAlchemyAutoSchema):
    """Schema for ProjectPolicy model."""

    class Meta:
        """Meta configuration for ProjectPolicySchema."""

        model = ProjectPolicy
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at", "removed_at")


class ProjectPolicyCreateSchema(SQLAlchemyAutoSchema):
    """Schema for creating a new policy."""

    class Meta:
        """Meta configuration for ProjectPolicyCreateSchema."""

        model = ProjectPolicy
        load_instance = True
        include_fk = True
        exclude = ("id", "created_at", "updated_at", "removed_at")


class ProjectPolicyUpdateSchema(SQLAlchemyAutoSchema):
    """Schema for updating a policy."""

    class Meta:
        """Meta configuration for ProjectPolicyUpdateSchema."""

        model = ProjectPolicy
        load_instance = False
        include_fk = True
        exclude = (
            "id",
            "project_id",
            "company_id",
            "created_at",
            "updated_at",
            "removed_at",
        )
        partial = True


class ProjectPermissionSchema(SQLAlchemyAutoSchema):
    """Schema for ProjectPermission model."""

    class Meta:
        """Meta configuration for ProjectPermissionSchema."""

        model = ProjectPermission
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "removed_at")

    @validates("category")
    def validate_category(self, value):
        """Validate permission category."""
        allowed_categories = [
            "file_operations",
            "project_operations",
            "member_operations",
        ]
        if value not in allowed_categories:
            raise ValidationError(
                f"Category must be one of: {', '.join(allowed_categories)}"
            )
        return value


class ProjectPermissionCreateSchema(SQLAlchemyAutoSchema):
    """Schema for creating a new permission."""

    class Meta:
        """Meta configuration for ProjectPermissionCreateSchema."""

        model = ProjectPermission
        load_instance = True
        include_fk = True
        exclude = ("id", "created_at", "removed_at")


# ============================================================================
# MEMBER SCHEMAS
# ============================================================================


class ProjectMemberSchema(SQLAlchemyAutoSchema):
    """Schema for ProjectMember model."""

    class Meta:
        """Meta configuration for ProjectMemberSchema."""

        model = ProjectMember
        load_instance = True
        include_fk = True
        dump_only = ("added_at", "removed_at")


class ProjectMemberCreateSchema(SQLAlchemyAutoSchema):
    """Schema for adding a member to a project."""

    class Meta:
        """Meta configuration for ProjectMemberCreateSchema."""

        model = ProjectMember
        load_instance = False
        include_fk = True
        exclude = ("added_at", "removed_at")


class ProjectMemberUpdateSchema(SQLAlchemyAutoSchema):
    """Schema for updating a project member."""

    class Meta:
        """Meta configuration for ProjectMemberUpdateSchema."""

        model = ProjectMember
        load_instance = False
        include_fk = True
        exclude = (
            "project_id",
            "user_id",
            "company_id",
            "added_at",
            "added_by",
            "removed_at",
        )
        partial = True


# ============================================================================
# HISTORY SCHEMAS
# ============================================================================


class ProjectHistorySchema(SQLAlchemyAutoSchema):
    """Schema for ProjectHistory model."""

    class Meta:
        """Meta configuration for ProjectHistorySchema."""

        model = ProjectHistory
        load_instance = True
        include_fk = True
        dump_only = ("id", "changed_at")

    @validates("action")
    def validate_action(self, value):
        """Validate history action."""
        allowed_actions = [
            "created",
            "updated",
            "status_changed",
            "deleted",
            "restored",
            "member_added",
            "member_removed",
            "role_assigned",
        ]
        if value not in allowed_actions:
            raise ValidationError(
                f"Action must be one of: {', '.join(allowed_actions)}"
            )
        return value


# ============================================================================
# ASSOCIATION SCHEMAS (for requests)
# ============================================================================


class MilestoneDeliverableAssociationSchema(SQLAlchemyAutoSchema):
    """Schema for associating milestones with deliverables."""

    milestone_id = fields.UUID(required=True)
    deliverable_id = fields.UUID(required=True)


class RolePolicyAssociationSchema(SQLAlchemyAutoSchema):
    """Schema for associating roles with policies."""

    role_id = fields.UUID(required=True)
    policy_id = fields.UUID(required=True)


class PolicyPermissionAssociationSchema(SQLAlchemyAutoSchema):
    """Schema for associating policies with permissions."""

    policy_id = fields.UUID(required=True)
    permission_id = fields.UUID(required=True)
