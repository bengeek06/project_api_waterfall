"""
app.schemas
-----------

This module exports Marshmallow schemas for the Project Service.
"""

from app.schemas.dummy_schema import DummySchema
from app.schemas.project_schema import (
    DeliverableCreateSchema,
    DeliverableSchema,
    DeliverableUpdateSchema,
    MilestoneCreateSchema,
    MilestoneDeliverableAssociationSchema,
    MilestoneSchema,
    MilestoneUpdateSchema,
    PolicyPermissionAssociationSchema,
    ProjectCreateSchema,
    ProjectHistorySchema,
    ProjectMemberCreateSchema,
    ProjectMemberSchema,
    ProjectPermissionCreateSchema,
    ProjectPermissionSchema,
    ProjectPolicyCreateSchema,
    ProjectPolicySchema,
    ProjectPolicyUpdateSchema,
    ProjectRoleCreateSchema,
    ProjectRoleSchema,
    ProjectRoleUpdateSchema,
    ProjectSchema,
    ProjectUpdateSchema,
    RolePolicyAssociationSchema,
)

__all__ = [
    "DummySchema",
    "ProjectSchema",
    "ProjectCreateSchema",
    "ProjectUpdateSchema",
    "MilestoneSchema",
    "MilestoneCreateSchema",
    "MilestoneUpdateSchema",
    "DeliverableSchema",
    "DeliverableCreateSchema",
    "DeliverableUpdateSchema",
    "ProjectRoleSchema",
    "ProjectRoleCreateSchema",
    "ProjectRoleUpdateSchema",
    "ProjectPolicySchema",
    "ProjectPolicyCreateSchema",
    "ProjectPolicyUpdateSchema",
    "ProjectPermissionSchema",
    "ProjectPermissionCreateSchema",
    "ProjectMemberSchema",
    "ProjectMemberCreateSchema",
    "ProjectHistorySchema",
    "MilestoneDeliverableAssociationSchema",
    "RolePolicyAssociationSchema",
    "PolicyPermissionAssociationSchema",
]
