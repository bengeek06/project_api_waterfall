"""
Project metadata resource for lightweight project information retrieval.
"""

from flask import g
from flask_restful import Resource
from app.models import Project
from app.utils.auth import require_jwt_auth, check_access_required
from app.logger import logger


class ProjectMetadataResource(Resource):
    """
    Resource for retrieving lightweight project metadata.

    This endpoint provides essential project information without full details,
    optimized for list views and quick lookups.
    """

    @require_jwt_auth()
    @check_access_required("read")
    def get(self, project_id):
        """
        Get project metadata.

        Returns lightweight project information including:
        - id, name, status
        - company_id, customer_id

        Args:
            project_id: UUID of the project

        Returns:
            dict: Project metadata

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
                f"Project metadata not found: project_id={project_id}, "
                f"company_id={company_id}"
            )
            return {"error": "Project not found"}, 404

        # Return metadata (lightweight)
        metadata = {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "company_id": project.company_id,
            "customer_id": project.customer_id,
        }

        logger.info(
            f"Project metadata retrieved: project_id={project_id}, "
            f"company_id={company_id}"
        )

        return metadata, 200
