"""
app.resources.milestone_deliverable
------------------------------------

This module implements the Milestone-Deliverable association resources.
Manages the many-to-many relationship between milestones and deliverables.

A milestone can have multiple deliverables associated with it, and a deliverable
can be associated with multiple milestones. This allows tracking which deliverables
must be completed for each milestone.

Resources:
- MilestoneDeliverableListResource: GET (list), POST (add association)
- MilestoneDeliverableResource: DELETE (remove association)
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from app.models.db import db
from app.models.project import Project, Milestone, Deliverable
from app.schemas.project_schema import DeliverableSchema
from app.utils import require_jwt_auth, check_access_required


class MilestoneDeliverableListResource(Resource):
    """
    Resource for managing milestone-deliverable associations.

    GET /projects/{project_id}/milestones/{milestone_id}/deliverables
    - Returns list of all deliverables associated with a milestone
    - Requires JWT authentication and RBAC authorization

    POST /projects/{project_id}/milestones/{milestone_id}/deliverables
    - Associates a deliverable with a milestone
    - Request body: {"deliverable_id": "uuid"}
    - Prevents duplicate associations
    - Validates both milestone and deliverable exist and belong to same project
    - Requires JWT authentication and RBAC authorization
    """

    @require_jwt_auth()
    @check_access_required("update_project")
    def get(self, project_id, milestone_id):
        """
        List all deliverables associated with a milestone.

        Returns:
            200: List of deliverables
            404: Project or milestone not found
        """
        try:
            company_id = g.company_id

            # Verify project exists
            project = Project.query.filter_by(
                id=project_id, company_id=company_id, removed_at=None
            ).first()
            if not project:
                return {"error": "Project not found"}, 404

            # Verify milestone exists and belongs to project
            milestone = Milestone.query.filter_by(
                id=milestone_id,
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()
            if not milestone:
                return {"error": "Milestone not found"}, 404

            # Get all deliverables associated with this milestone
            deliverables = milestone.deliverables.filter(
                Deliverable.removed_at.is_(None)
            ).all()

            schema = DeliverableSchema(many=True)
            return schema.dump(deliverables), 200

        except Exception as e:
            return {
                "error": "Failed to retrieve milestone deliverables",
                "detail": str(e),
            }, 500

    @require_jwt_auth()
    @check_access_required("update_project")
    def post(self, project_id, milestone_id):
        """
        Associate a deliverable with a milestone.

        Request body:
        - deliverable_id: UUID of the deliverable to associate

        Returns:
            201: Association created successfully
            400: Invalid input or duplicate association
            404: Project, milestone, or deliverable not found
        """
        try:
            company_id = g.company_id

            # Verify project exists
            project = Project.query.filter_by(
                id=project_id, company_id=company_id, removed_at=None
            ).first()
            if not project:
                return {"error": "Project not found"}, 404

            # Verify milestone exists and belongs to project
            milestone = Milestone.query.filter_by(
                id=milestone_id,
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()
            if not milestone:
                return {"error": "Milestone not found"}, 404

            # Get deliverable_id from request
            data = request.get_json()
            if not data or "deliverable_id" not in data:
                return {
                    "error": "Invalid input data",
                    "detail": "deliverable_id is required",
                }, 400

            deliverable_id = data["deliverable_id"]

            # Verify deliverable exists and belongs to same project
            deliverable = Deliverable.query.filter_by(
                id=deliverable_id,
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()
            if not deliverable:
                return {
                    "error": "Deliverable not found",
                    "detail": "Deliverable not found or does not belong to this project",
                }, 404

            # Check if association already exists
            existing = milestone.deliverables.filter_by(
                id=deliverable_id
            ).first()
            if existing:
                return {
                    "error": "Association already exists",
                    "detail": "This deliverable is already associated with this milestone",
                }, 409

            # Create association
            milestone.deliverables.append(deliverable)
            db.session.commit()

            # Return the associated deliverable
            schema = DeliverableSchema()
            return schema.dump(deliverable), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "detail": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {
                "error": "Failed to create association",
                "detail": str(e),
            }, 500


class MilestoneDeliverableResource(Resource):
    """
    Resource for removing milestone-deliverable associations.

    DELETE /projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}
    - Removes the association between a milestone and a deliverable
    - Does not delete the deliverable itself, only the association
    - Requires JWT authentication and RBAC authorization
    """

    @require_jwt_auth()
    @check_access_required("update_project")
    def delete(self, project_id, milestone_id, deliverable_id):
        """
        Remove association between a milestone and a deliverable.

        Returns:
            204: Association removed successfully
            404: Project, milestone, deliverable, or association not found
        """
        try:
            company_id = g.company_id

            # Verify project exists
            project = Project.query.filter_by(
                id=project_id, company_id=company_id, removed_at=None
            ).first()
            if not project:
                return {"error": "Project not found"}, 404

            # Verify milestone exists and belongs to project
            milestone = Milestone.query.filter_by(
                id=milestone_id,
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()
            if not milestone:
                return {"error": "Milestone not found"}, 404

            # Verify deliverable exists and belongs to same project
            deliverable = Deliverable.query.filter_by(
                id=deliverable_id,
                project_id=project_id,
                company_id=company_id,
                removed_at=None,
            ).first()
            if not deliverable:
                return {"error": "Deliverable not found"}, 404

            # Check if association exists
            existing = milestone.deliverables.filter_by(
                id=deliverable_id
            ).first()
            if not existing:
                return {
                    "error": "Association not found",
                    "detail": "This deliverable is not associated with this milestone",
                }, 404

            # Remove association
            milestone.deliverables.remove(deliverable)
            db.session.commit()

            return "", 204

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error", "detail": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {
                "error": "Failed to remove association",
                "detail": str(e),
            }, 500
