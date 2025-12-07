# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
app.schemas
-----------

This module exports Marshmallow schemas for the Project Service.
"""

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
