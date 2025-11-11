"""
__init__.py
-----------
Resource exports for the Project Service API.
"""

from app.resources.project import ProjectListResource, ProjectResource
from app.resources.milestone import MilestoneListResource, MilestoneResource

__all__ = [
    "ProjectListResource",
    "ProjectResource",
    "MilestoneListResource",
    "MilestoneResource",
]
