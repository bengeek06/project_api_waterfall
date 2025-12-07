# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
WBS (Work Breakdown Structure) resource for Task Service integration.
"""

from flask import g
from flask_restful import Resource

from app.logger import logger
from app.models.db import db
from app.models.project import (
    Deliverable,
    Milestone,
    Project,
    milestone_deliverable_association,
)
from app.schemas import DeliverableSchema, MilestoneSchema
from app.utils import check_access_required, require_jwt_auth

milestone_schema = MilestoneSchema()
deliverable_schema = DeliverableSchema()


class WBSStructureResource(Resource):
    """
    Resource for providing WBS structure to Task Service.

    Returns complete project structure including milestones, deliverables,
    and their associations for WBS generation.
    """

    @require_jwt_auth()
    @check_access_required("read")
    def get(self, project_id):
        """
        Get WBS structure for Task Service integration.

        Returns hierarchical project structure including:
        - Project metadata
        - All milestones
        - All deliverables
        - Milestone-deliverable associations

        Args:
            project_id: UUID of the project

        Returns:
            dict: Complete WBS structure

        Raises:
            404: Project not found
        """
        company_id = g.company_id

        # Fetch project
        project = Project.query.filter_by(
            id=project_id, company_id=company_id
        ).first()

        if not project:
            logger.warning(
                f"Project not found for WBS structure: project_id={project_id}, "
                f"company_id={company_id}"
            )
            return {"error": "Project not found"}, 404

        # Fetch milestones
        milestones = (
            Milestone.query.filter_by(project_id=project_id)
            .order_by(Milestone.due_date)
            .all()
        )

        # Fetch deliverables
        deliverables = Deliverable.query.filter_by(project_id=project_id).all()

        # Fetch associations
        associations = milestone_deliverable_association.select().where(
            milestone_deliverable_association.c.milestone_id.in_(
                [m.id for m in milestones]
            )
        )

        association_results = db.session.execute(associations).fetchall()

        # Build WBS structure
        wbs_structure = {
            "project": {
                "id": project.id,
                "name": project.name,
                "status": project.status,
                "company_id": project.company_id,
                "customer_id": project.customer_id,
            },
            "milestones": [milestone_schema.dump(m) for m in milestones],
            "deliverables": [deliverable_schema.dump(d) for d in deliverables],
            "associations": [
                {
                    "milestone_id": row.milestone_id,
                    "deliverable_id": row.deliverable_id,
                }
                for row in association_results
            ],
        }

        logger.info(
            f"WBS structure retrieved: project_id={project_id}, "
            f"milestones={len(milestones)}, deliverables={len(deliverables)}"
        )

        return wbs_structure, 200
