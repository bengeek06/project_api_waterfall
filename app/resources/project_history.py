# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
Project history tracking resource.
"""

from flask import g
from flask_restful import Resource

from app.logger import logger
from app.models import Project, ProjectHistory
from app.utils import check_access_required, require_jwt_auth


class ProjectHistoryResource(Resource):
    """
    Resource for retrieving project change history.

    Returns chronological history of all changes made to a project,
    including status changes, member additions, and other modifications.
    """

    @require_jwt_auth()
    @check_access_required("READ")
    def get(self, project_id):
        """
        Get project history.

        Returns all history entries for the project in chronological order.

        Args:
            project_id: UUID of the project

        Returns:
            list: History entries

        Raises:
            404: Project not found
        """
        company_id = g.company_id

        # Verify project exists and belongs to company
        project = Project.query.filter_by(
            id=project_id, company_id=company_id
        ).first()

        if not project:
            logger.warning(
                f"Project not found for history: project_id={project_id}, "
                f"company_id={company_id}"
            )
            return {"error": "Project not found"}, 404

        # Fetch history entries
        history_entries = (
            ProjectHistory.query.filter_by(
                project_id=project_id, company_id=company_id
            )
            .order_by(ProjectHistory.changed_at.desc())
            .all()
        )

        # Serialize history entries (adapting to ProjectHistory model structure)
        history_data = [
            {
                "id": entry.id,
                "project_id": entry.project_id,
                "user_id": entry.changed_by,
                "action": entry.action,
                "entity_type": "project",  # ProjectHistory tracks project changes
                "entity_id": entry.project_id,
                "changes": (
                    {
                        "field_name": entry.field_name,
                        "old_value": entry.old_value,
                        "new_value": entry.new_value,
                        "comment": entry.comment,
                    }
                    if entry.field_name
                    else {}
                ),
                "created_at": entry.changed_at.isoformat(),
            }
            for entry in history_entries
        ]

        logger.info(
            f"Project history retrieved: project_id={project_id}, "
            f"entries={len(history_data)}"
        )

        return history_data, 200
