# Contributing to Project Service

Thank you for your interest in contributing to the **Project Service**!

> **Note**: This service is part of the larger [Waterfall](../../README.md) project. For the overall development workflow, branch strategy, and contribution guidelines, please refer to the [main CONTRIBUTING.md](../../CONTRIBUTING.md) in the root repository.

## Table of Contents

- [Service Overview](#service-overview)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [API Development](#api-development)
- [Common Tasks](#common-tasks)

## Service Overview

The **Project Service** manages projects, milestones, deliverables, and tasks for the Waterfall platform:

- **Technology Stack**: Python 3.13+, Flask 3.1+, SQLAlchemy, PostgreSQL
- **Port**: 5006 (containerized) / 5000 (standalone)
- **Responsibilities**:
  - Project lifecycle management (CRUD)
  - Milestone tracking
  - Deliverable management
  - Task assignment and tracking
  - Project team coordination
  - Integration with Guardian for permissions

**Key Dependencies:**
- Flask 3.1+ for REST API
- SQLAlchemy for ORM
- Marshmallow for serialization/validation
- PostgreSQL for data persistence
- Gunicorn for production WSGI server

## Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16+ (or use Docker)
- pip and virtualenv

### Local Setup

```bash
# Navigate to service directory
cd services/project_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment configuration
cp env.example .env.development
```

### Environment Configuration

```bash
# Flask environment
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://project_user:project_pass@localhost:5432/project_dev

# External services
GUARDIAN_SERVICE_URL=http://localhost:5003
IDENTITY_SERVICE_URL=http://localhost:5002
INTERNAL_AUTH_TOKEN=dev-internal-secret

# Security
JWT_SECRET=dev-jwt-secret
```

### Database Setup

```bash
# Create database
createdb project_dev

# Run migrations
flask db upgrade

# Or use Docker
docker run -d \
  --name project_db_dev \
  -e POSTGRES_USER=project_user \
  -e POSTGRES_PASSWORD=project_pass \
  -e POSTGRES_DB=project_dev \
  -p 5432:5432 \
  postgres:16-alpine
```

### Running the Service

```bash
# Development mode
python run.py

# Production-style
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

The service will be available at `http://localhost:5000`

## Coding Standards

### Python Style Guide

Follow **PEP 8** with Black formatting:

```bash
# Format code
black app/ tests/

# Check quality
pylint app/ tests/

# Sort imports
isort app/ tests/
```

### Project-Specific Conventions

**Status Enums:**
```python
# Use clear, descriptive status values
PROJECT_STATUS = [
    'planning',      # Initial planning phase
    'active',        # Currently in progress
    'on_hold',       # Temporarily paused
    'completed',     # Successfully finished
    'cancelled'      # Terminated before completion
]

MILESTONE_STATUS = [
    'pending',       # Not started
    'in_progress',   # Currently working
    'completed',     # Finished
    'overdue'        # Past deadline
]

TASK_STATUS = [
    'todo',          # Not started
    'in_progress',   # Currently working
    'review',        # Under review
    'done',          # Completed
    'blocked'        # Cannot proceed
]
```

**Date Handling:**
```python
from datetime import datetime, timezone

# Always use UTC for database storage
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Convert to user timezone in API responses
def to_dict(self):
    return {
        'created_at': self.created_at.isoformat(),
        'deadline': self.deadline.isoformat() if self.deadline else None
    }
```

### Type Hints and Documentation

```python
from typing import List, Optional, Dict
from datetime import datetime
from app.models import Project, Milestone

def get_project_milestones(
    project_id: int,
    status: Optional[str] = None,
    include_overdue: bool = True
) -> List[Milestone]:
    """Get milestones for a project with optional filtering.
    
    Args:
        project_id: The project's database ID
        status: Optional status filter ('pending', 'in_progress', 'completed')
        include_overdue: Whether to include overdue milestones
    
    Returns:
        List of Milestone objects matching criteria
    
    Raises:
        ValueError: If project_id is invalid
        
    Example:
        >>> milestones = get_project_milestones(1, status='in_progress')
        >>> len(milestones)
        3
    """
    query = Milestone.query.filter_by(project_id=project_id)
    
    if status:
        query = query.filter_by(status=status)
    
    return query.all()
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test module
pytest tests/test_projects.py -v
pytest tests/test_milestones.py -v
```

### Test Structure

```python
import pytest
from datetime import datetime, timedelta
from app.models import Project, Milestone, db

class TestProjectEndpoints:
    """Test suite for project management endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Setup test data."""
        # Create test project
        project = Project(
            name="Test Project",
            description="Test description",
            company_id=1,
            status='planning',
            start_date=datetime.now(),
            deadline=datetime.now() + timedelta(days=30)
        )
        db.session.add(project)
        db.session.commit()
        
        self.project_id = project.id
        
        yield
        
        # Cleanup
        db.session.query(Project).delete()
        db.session.commit()
    
    def test_create_project(self, client):
        """Test creating a new project."""
        response = client.post('/projects', json={
            'name': 'New Project',
            'description': 'Project description',
            'company_id': 1,
            'status': 'planning',
            'start_date': datetime.now().isoformat(),
            'deadline': (datetime.now() + timedelta(days=60)).isoformat()
        })
        
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'New Project'
        assert data['status'] == 'planning'
    
    def test_add_milestone_to_project(self, client):
        """Test adding a milestone to a project."""
        response = client.post(f'/projects/{self.project_id}/milestones', json={
            'name': 'Phase 1 Complete',
            'description': 'First phase milestone',
            'deadline': (datetime.now() + timedelta(days=15)).isoformat(),
            'status': 'pending'
        })
        
        assert response.status_code == 201
        data = response.json
        assert data['project_id'] == self.project_id
        assert data['name'] == 'Phase 1 Complete'
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Critical paths**: Project creation, milestone tracking, task assignment require 100% coverage
- **Focus areas**: Date validation, status transitions, permission checks

## API Development

### Adding a New Resource

1. **Create model** in `app/models/`:

```python
# app/models/task.py
from app.models import db
from datetime import datetime

class Task(db.Model):
    """Task model for project work items."""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.id'))
    assigned_to = db.Column(db.Integer)  # User ID from Identity Service
    status = db.Column(db.String(50), default='todo')
    priority = db.Column(db.String(20), default='medium')
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref='tasks')
    milestone = db.relationship('Milestone', backref='tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'milestone_id': self.milestone_id,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

2. **Create schema** and **resource**, then **add tests**

### Working with Project Hierarchy

```python
# Get project progress
def calculate_project_progress(project_id: int) -> float:
    """Calculate project completion percentage based on tasks."""
    project = Project.query.get(project_id)
    total_tasks = len(project.tasks)
    
    if total_tasks == 0:
        return 0.0
    
    completed_tasks = sum(1 for task in project.tasks if task.status == 'done')
    return (completed_tasks / total_tasks) * 100

# Check overdue milestones
def get_overdue_milestones(project_id: int) -> List[Milestone]:
    """Get all overdue milestones for a project."""
    now = datetime.now(timezone.utc)
    return Milestone.query.filter(
        Milestone.project_id == project_id,
        Milestone.deadline < now,
        Milestone.status != 'completed'
    ).all()
```

## Common Tasks

### Status Transitions

```python
# Valid status transitions
PROJECT_STATUS_TRANSITIONS = {
    'planning': ['active', 'cancelled'],
    'active': ['on_hold', 'completed', 'cancelled'],
    'on_hold': ['active', 'cancelled'],
    'completed': [],  # Terminal state
    'cancelled': []   # Terminal state
}

def transition_project_status(project: Project, new_status: str) -> bool:
    """Safely transition project to new status."""
    current_status = project.status
    
    if new_status not in PROJECT_STATUS_TRANSITIONS.get(current_status, []):
        raise ValueError(
            f"Invalid status transition: {current_status} -> {new_status}"
        )
    
    project.status = new_status
    project.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return True
```

### Integration with Other Services

```python
import requests
from flask import current_app

def get_project_team_members(project_id: int) -> List[Dict]:
    """Get team members from Identity Service."""
    project = Project.query.get(project_id)
    identity_url = current_app.config['IDENTITY_SERVICE_URL']
    
    response = requests.get(
        f"{identity_url}/users",
        params={'company_id': project.company_id},
        headers={'Authorization': f'Bearer {get_internal_token()}'}
    )
    
    response.raise_for_status()
    return response.json()

def check_project_permission(user_id: int, project_id: int, action: str) -> bool:
    """Check permission via Guardian Service."""
    guardian_url = current_app.config['GUARDIAN_SERVICE_URL']
    
    response = requests.post(
        f"{guardian_url}/check-access",
        json={
            'user_id': user_id,
            'resource': 'projects',
            'action': action
        },
        headers={'Authorization': f'Bearer {get_internal_token()}'}
    )
    
    response.raise_for_status()
    return response.json()['has_access']
```

## Service-Specific Guidelines

### Multi-tenancy

All projects belong to a company:

```python
@projects_bp.route('/projects', methods=['GET'])
@require_authentication
def get_projects():
    """Get projects scoped by user's company."""
    company_id = g.user_company_id  # From auth context
    projects = Project.query.filter_by(company_id=company_id).all()
    return jsonify([p.to_dict() for p in projects]), 200
```

### Date Validation

```python
from marshmallow import validates, ValidationError

class ProjectSchema(Schema):
    start_date = fields.DateTime(required=True)
    deadline = fields.DateTime(required=True)
    
    @validates('deadline')
    def validate_deadline(self, value):
        """Ensure deadline is after start date."""
        start_date = self.context.get('start_date')
        if start_date and value <= start_date:
            raise ValidationError("Deadline must be after start date")
```

## Getting Help

- **Main Project**: See [root CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Issues**: Use GitHub issues with `service:project` label
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Documentation**: [README.md](README.md)

---

**Remember**: Always refer to the [main CONTRIBUTING.md](../../CONTRIBUTING.md) for branch strategy, commit conventions, and pull request process!
