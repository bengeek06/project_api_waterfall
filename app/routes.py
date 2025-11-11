"""
routes.py
-----------
Routes for the Flask application.
# This module is responsible for registering the routes of the REST API
# and linking them to the corresponding resources.
"""

from flask_restful import Api
from app.logger import logger
from app.resources.dummy import DummyResource, DummyListResource
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


def register_routes(app):
    """
    Register the REST API routes on the Flask application.

    Args:
        app (Flask): The Flask application instance.

    This function creates a Flask-RESTful Api instance, adds the resource
    endpoints for managing dummy items, and logs the successful registration
    of routes.
    """
    api = Api(app)

    # System endpoints
    api.add_resource(HealthResource, "/health")
    api.add_resource(VersionResource, "/version")
    api.add_resource(ConfigResource, "/config")

    # Legacy dummy endpoints (to be removed)
    api.add_resource(DummyListResource, "/dummies")
    api.add_resource(DummyResource, "/dummies/<int:dummy_id>")

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
    api.add_resource(DeliverableResource, "/deliverables/<string:deliverable_id>")

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

    logger.info("Routes registered successfully.")
