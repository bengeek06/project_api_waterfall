"""
__init__.py
-----------
Resource exports for the Project Service API.
"""

from app.resources.project import ProjectListResource, ProjectResource

__all__ = ["ProjectListResource", "ProjectResource"]
