"""
routes.py
-----------
Routes for the Flask application.
# This module is responsible for registering the routes of the REST API
# and linking them to the corresponding resources.
"""

from flask_restful import Api
from app.logger import logger
from app.resources.version import VersionResource
from app.resources.config import ConfigResource
from app.resources.health import HealthResource
from app.resources.project import ProjectListResource, ProjectResource
from app.resources.milestone import (
    MilestoneListResource,
    MilestoneResource,
)
from app.resources.deliverable import (
    DeliverableListResource,
    DeliverableResource,
)
from app.resources.member import (
    MemberListResource,
    MemberResource,
)
from app.resources.role import (
    RoleListResource,
    RoleResource,
)
from app.resources.policy import (
    PolicyListResource,
    PolicyResource,
)
from app.resources.permission import (
    PermissionListResource,
)
from app.resources.milestone_deliverable import (
    MilestoneDeliverableListResource,
    MilestoneDeliverableResource,
)
from app.resources.role_policy import (
    RolePolicyListResource,
    RolePolicyResource,
)
from app.resources.policy_permission import (
    PolicyPermissionListResource,
    PolicyPermissionResource,
)
from app.resources.access_control import (
    CheckFileAccessResource,
    CheckProjectAccessResource,
)


def register_routes(app):
    """
    Register the REST API routes on the Flask application.

    Args:
        app (Flask): The Flask application instance.

    This function creates a Flask-RESTful Api instance and adds all resource
    endpoints for the Project Service API.
    """
    api = Api(app)

    # System endpoints
    api.add_resource(HealthResource, "/health")
    api.add_resource(VersionResource, "/version")
    api.add_resource(ConfigResource, "/config")

    # Project endpoints
    api.add_resource(ProjectListResource, "/projects")
    api.add_resource(ProjectResource, "/projects/<string:project_id>")

    # Milestone endpoints
    api.add_resource(
        MilestoneListResource,
        "/projects/<string:project_id>/milestones",
    )
    api.add_resource(MilestoneResource, "/milestones/<string:milestone_id>")

    # Deliverable endpoints
    api.add_resource(
        DeliverableListResource,
        "/projects/<string:project_id>/deliverables",
    )
    api.add_resource(
        DeliverableResource, "/deliverables/<string:deliverable_id>"
    )

    # Member endpoints
    api.add_resource(
        MemberListResource,
        "/projects/<string:project_id>/members",
    )
    api.add_resource(
        MemberResource,
        "/projects/<string:project_id>/members/<string:user_id>",
    )

    # Role endpoints
    api.add_resource(
        RoleListResource,
        "/projects/<string:project_id>/roles",
    )
    api.add_resource(
        RoleResource,
        "/projects/<string:project_id>/roles/<string:role_id>",
    )

    # Policy endpoints
    api.add_resource(
        PolicyListResource,
        "/projects/<string:project_id>/policies",
    )
    api.add_resource(
        PolicyResource,
        "/projects/<string:project_id>/policies/<string:policy_id>",
    )

    # Permission endpoints (read-only)
    api.add_resource(
        PermissionListResource,
        "/projects/<string:project_id>/permissions",
    )

    # Milestone-Deliverable association endpoints
    api.add_resource(
        MilestoneDeliverableListResource,
        "/projects/<string:project_id>/milestones/<string:milestone_id>/deliverables",
    )
    api.add_resource(
        MilestoneDeliverableResource,
        "/projects/<string:project_id>/milestones/<string:milestone_id>"
        "/deliverables/<string:deliverable_id>",
    )

    # Role-Policy association endpoints
    api.add_resource(
        RolePolicyListResource,
        "/projects/<string:project_id>/roles/<string:role_id>/policies",
    )
    api.add_resource(
        RolePolicyResource,
        "/projects/<string:project_id>/roles/<string:role_id>/policies/<string:policy_id>",
    )

    # Policy-Permission association endpoints
    api.add_resource(
        PolicyPermissionListResource,
        "/projects/<string:project_id>/policies/<string:policy_id>/permissions",
    )
    api.add_resource(
        PolicyPermissionResource,
        "/projects/<string:project_id>/policies/<string:policy_id>"
        "/permissions/<string:permission_id>",
    )

    # Access Control endpoints
    api.add_resource(CheckFileAccessResource, "/check-file-access")
    api.add_resource(CheckProjectAccessResource, "/check-project-access")

    logger.info("Routes registered successfully.")
