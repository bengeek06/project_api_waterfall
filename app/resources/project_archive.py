# Copyright (c) 2025 Waterfall
#
# This source code is dual-licensed under:
# - GNU Affero General Public License v3.0 (AGPLv3) for open source use
# - Commercial License for proprietary use
#
# See LICENSE and LICENSE.md files in the root directory for full license text.
# For commercial licensing inquiries, contact: benjamin@waterfall-project.pro
"""
Project archive and restore operations.
"""

from datetime import datetime, timezone

from flask import g
from flask_restful import Resource

from app.logger import logger
from app.models.db import db
from app.models.project import Project
from app.schemas import ProjectSchema
from app.utils import check_access_required, require_jwt_auth

project_schema = ProjectSchema()


class ProjectArchiveResource(Resource):
    """
    Resource for archiving a completed project.
    """

    @require_jwt_auth()
    @check_access_required("CREATE")
    def post(self, project_id):
        """
        Archive a completed project.

        Transitions a completed project to archived status.

        Args:
            project_id: UUID of the project

        Returns:
            dict: Updated project with archived status

        Raises:
            400: Project is not in completed status
            404: Project not found
        """
        company_id = g.company_id

        # Fetch project
        project = Project.query.filter_by(
            id=project_id, company_id=company_id
        ).first()

        if not project:
            logger.warning(
                f"Project not found for archiving: project_id={project_id}, "
                f"company_id={company_id}"
            )
            return {"error": "Project not found"}, 404

        # Validate status (only completed projects can be archived)
        if project.status != "completed":
            logger.warning(
                f"Cannot archive project with status {project.status}: "
                f"project_id={project_id}"
            )
            return {"error": "Only completed projects can be archived"}, 400

        # Update status and dates
        project.status = "archived"
        project.archived_at = datetime.now(timezone.utc)
        project.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        logger.info(
            f"Project archived: project_id={project_id}, "
            f"company_id={company_id}"
        )

        return project_schema.dump(project), 200


class ProjectRestoreResource(Resource):
    """
    Resource for restoring an archived project.
    """

    @require_jwt_auth()
    @check_access_required("update")
    def post(self, project_id):
        """
        Restore an archived project to active status.

        Args:
            project_id: UUID of the project

        Returns:
            dict: Updated project with active status

        Raises:
            400: Project is not archived
            404: Project not found
        """
        company_id = g.company_id

        # Fetch project
        project = Project.query.filter_by(
            id=project_id, company_id=company_id
        ).first()

        if not project:
            logger.warning(
                f"Project not found for restoring: project_id={project_id}, "
                f"company_id={company_id}"
            )
            return {"error": "Project not found"}, 404

        # Validate status (only archived projects can be restored)
        if project.status != "archived":
            logger.warning(
                f"Cannot restore project with status {project.status}: "
                f"project_id={project_id}"
            )
            return {"error": "Only archived projects can be restored"}, 400

        # Update status
        project.status = "active"
        project.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        logger.info(
            f"Project restored: project_id={project_id}, "
            f"company_id={company_id}"
        )

        return project_schema.dump(project), 200
