# Waterfall Project Service API

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-%3E=2.0-green.svg)
![License](https://img.shields.io/badge/license-AGPLv3%2FCommercial-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green.svg)

**Project Service** is a core microservice in the Waterfall platform ecosystem, managing the complete lifecycle of projects from initial consultation through delivery and archival.

This service handles project structure (milestones, deliverables), team membership, role-based access control (RBAC), and provides integration endpoints for the Storage and Task services.

---

## Features

### Project Lifecycle Management
- **8 lifecycle statuses**: created, initialized, consultation, lost, active, suspended, completed, archived
- **Comprehensive date tracking**: Consultation phase, execution phase, delivery phase
- **Status transitions**: Automated workflow enforcement
- **History tracking**: Complete audit trail of all changes

### Project Components
- **Projects**: Main entities with contractual and timeline information
- **Milestones**: Key project checkpoints with delivery dates
- **Deliverables**: Specific outputs (documents, software, hardware, services)
- **Members**: Team members with role-based permissions
- **WBS Structure**: Work Breakdown Structure for Task Service integration

### Role-Based Access Control (RBAC)
- **Two-tier RBAC**: Guardian (endpoint-level) + Project Service (context-level)
- **Default roles**: owner, validator, contributor, viewer (auto-created)
- **Custom roles**: User-defined roles with configurable permissions
- **Policies**: Organized groups of permissions
- **10 predefined permissions**: read_files, write_files, delete_files, lock_files, validate_files, update_project, delete_project, manage_members, manage_roles, manage_policies

### Integration with Waterfall Ecosystem
- **Storage Service**: File access validation via `/check-file-access` endpoints
- **Task Service**: WBS structure provisioning via `/projects/{id}/wbs-structure`
- **Identity Service**: User and customer management integration
- **Guardian Service**: Endpoint-level RBAC enforcement
- **Auth Service**: JWT-based authentication

### Technical Features
- **Multi-tenancy**: Company-level isolation (automatic `company_id` extraction)
- **RESTful API**: 40+ endpoints following REST principles
- **OpenAPI 3.0.3**: Complete specification in [`openapi.yml`](openapi.yml)
- **Database migrations**: Managed with Alembic/Flask-Migrate
- **Docker-ready**: Production containerization
- **Testing**: Pytest-based test suite
- **Logging**: Structured logging for monitoring

---

## Architecture

### Project Lifecycle Workflow

```
created → initialized → consultation → [active | lost]
                                          ↓
                                      suspended ↔ completed → archived
```

**Status Descriptions:**
- `created`: Initial project creation
- `initialized`: Project setup with basic information
- `consultation`: Proposal/tender phase
- `lost`: Consultation lost (terminal state)
- `active`: Project won and in execution
- `suspended`: Temporarily paused
- `completed`: Work finished
- `archived`: Long-term storage

### RBAC Architecture

#### Two-Tier Access Control

1. **Guardian Service (Endpoint-level)**
   - Controls WHO can call WHICH endpoints
   - User → Guardian Roles → Guardian Policies → Guardian Permissions
   - Enforced before request reaches Project Service

2. **Project Service (Context-level)**
   - Controls WHO can access WHICH project resources
   - User → Project Roles → Project Policies → Project Permissions
   - Enforced within Project Service logic

#### Default Roles

| Role | Description | Typical Permissions |
|------|-------------|---------------------|
| `owner` | Project creator | All permissions |
| `validator` | Quality control | read_files, validate_files |
| `contributor` | Team member | read_files, write_files |
| `viewer` | Read-only access | read_files |

#### Permission Categories

**Files** (integrated with Storage Service):
- `read_files` → Storage: read action
- `write_files` → Storage: write action
- `delete_files` → Storage: delete action
- `lock_files` → Storage: lock action
- `validate_files` → Storage: validate action

**Project**:
- `update_project`: Modify project information
- `delete_project`: Delete the project

**Members**:
- `manage_members`: Add/remove team members

**RBAC**:
- `manage_roles`: Create/modify custom roles
- `manage_policies`: Create/modify policies

### Date Tracking

#### Consultation Phase
- `consultation_date`: When consultation begins
- `submission_deadline`: Proposal submission deadline
- `notification_date`: Decision notification date (won/lost)

#### Execution Phase
- `contract_start_date`: Official contract start
- `planned_start_date`: Internally planned start
- `actual_start_date`: Real start date

#### Delivery Phase
- `contract_delivery_date`: Contractual delivery date
- `planned_delivery_date`: Internally planned delivery
- `actual_delivery_date`: Actual delivery date

---

## API Endpoints

### System Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (public) |
| GET | `/version` | API version |
| GET | `/config` | Configuration info |

### Project Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects` | List all projects |
| POST | `/projects` | Create new project |
| GET | `/projects/{id}` | Get project details |
| PUT | `/projects/{id}` | Update project (full) |
| PATCH | `/projects/{id}` | Update project (partial) |
| DELETE | `/projects/{id}` | Delete project (soft delete) |
| GET | `/projects/{id}/metadata` | Get lightweight metadata |
| POST | `/projects/{id}/archive` | Archive completed project |
| POST | `/projects/{id}/restore` | Restore archived project |
| GET | `/projects/{id}/history` | Get project change history |

### Members

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/members` | List project members |
| POST | `/projects/{id}/members` | Add member to project |
| GET | `/projects/{id}/members/{user_id}` | Get member details |
| PUT | `/projects/{id}/members/{user_id}` | Update member role |
| PATCH | `/projects/{id}/members/{user_id}` | Update member role (partial) |
| DELETE | `/projects/{id}/members/{user_id}` | Remove member |

### Milestones

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/milestones` | List milestones |
| POST | `/projects/{id}/milestones` | Create milestone |
| GET | `/projects/{id}/milestones/{milestone_id}` | Get milestone details |
| PUT | `/projects/{id}/milestones/{milestone_id}` | Update milestone |
| PATCH | `/projects/{id}/milestones/{milestone_id}` | Update milestone (partial) |
| DELETE | `/projects/{id}/milestones/{milestone_id}` | Delete milestone |
| GET | `/projects/{id}/milestones/{milestone_id}/deliverables` | List milestone deliverables |
| POST | `/projects/{id}/milestones/{milestone_id}/deliverables` | Associate deliverable |
| DELETE | `/projects/{id}/milestones/{milestone_id}/deliverables/{deliverable_id}` | Remove association |

### Deliverables

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/deliverables` | List deliverables |
| POST | `/projects/{id}/deliverables` | Create deliverable |
| GET | `/projects/{id}/deliverables/{deliverable_id}` | Get deliverable details |
| PUT | `/projects/{id}/deliverables/{deliverable_id}` | Update deliverable |
| PATCH | `/projects/{id}/deliverables/{deliverable_id}` | Update deliverable (partial) |
| DELETE | `/projects/{id}/deliverables/{deliverable_id}` | Delete deliverable |

### RBAC - Roles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/roles` | List roles |
| POST | `/projects/{id}/roles` | Create custom role |
| GET | `/projects/{id}/roles/{role_id}` | Get role details |
| PUT | `/projects/{id}/roles/{role_id}` | Update custom role |
| DELETE | `/projects/{id}/roles/{role_id}` | Delete custom role |

### RBAC - Policies

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/policies` | List policies |
| POST | `/projects/{id}/policies` | Create policy |
| GET | `/projects/{id}/policies/{policy_id}` | Get policy details |
| PUT | `/projects/{id}/policies/{policy_id}` | Update policy |
| DELETE | `/projects/{id}/policies/{policy_id}` | Delete policy |

### RBAC - Permissions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/permissions` | List all permissions |

### RBAC - Associations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/roles/{role_id}/policies` | List role policies |
| POST | `/projects/{id}/roles/{role_id}/policies/{policy_id}` | Associate policy to role |
| DELETE | `/projects/{id}/roles/{role_id}/policies/{policy_id}` | Remove policy from role |
| GET | `/projects/{id}/policies/{policy_id}/permissions` | List policy permissions |
| POST | `/projects/{id}/policies/{policy_id}/permissions/{perm_id}` | Associate permission |
| DELETE | `/projects/{id}/policies/{policy_id}/permissions/{perm_id}` | Remove permission |

### Integration Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{id}/wbs-structure` | Get WBS for Task Service |
| POST | `/check-file-access` | Validate file access (Storage calls) |
| POST | `/check-file-access-batch` | Batch file access validation |
| POST | `/check-project-access` | Validate project access |
| POST | `/check-project-access-batch` | Batch project access validation |

For detailed schemas and examples, see [`openapi.yml`](openapi.yml) or the [`specifications/`](specifications/) directory.

---

## Environments

The application behavior is controlled by the `FLASK_ENV` environment variable:

| Environment | Config Class | Debug | Description |
|-------------|--------------|-------|-------------|
| `development` (default) | `DevelopmentConfig` | ✅ | Local development |
| `testing` | `TestingConfig` | ✅ | Unit/integration tests |
| `staging` | `StagingConfig` | ✅ | Pre-production |
| `production` | `ProductionConfig` | ❌ | Production |

Each environment loads its corresponding `.env.<environment>` file.  
Use `env.example` as a template for your environment files.

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/project_db

# JWT Configuration (shared across Waterfall services)
JWT_SECRET_KEY=your-secret-key-here

# Service URLs (for integration)
IDENTITY_SERVICE_URL=http://localhost:5001
GUARDIAN_SERVICE_URL=http://localhost:5003
STORAGE_SERVICE_URL=http://localhost:5004
TASK_SERVICE_URL=http://localhost:5005

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-flask-secret-key
```

---

## Documentation

### Specifications

Complete API specifications are available in the [`specifications/`](specifications/) directory:

- **[specifications/README.md](specifications/README.md)**: Overview and architecture
- **[specifications/ENDPOINTS_SPECIFICATION.md](specifications/ENDPOINTS_SPECIFICATION.md)**: All endpoints with detailed descriptions
- **[specifications/SCHEMAS_SPECIFICATION.md](specifications/SCHEMAS_SPECIFICATION.md)**: Data schemas with validation rules
- **[specifications/RESPONSES_SPECIFICATION.md](specifications/RESPONSES_SPECIFICATION.md)**: HTTP status codes and response formats

### OpenAPI

The complete OpenAPI 3.0.3 specification is available in [`openapi.yml`](openapi.yml).

You can visualize it using:
- [Swagger Editor](https://editor.swagger.io/) - Paste the YAML content
- [Redoc](https://redocly.github.io/redoc/) - Generate beautiful documentation
- VSCode extensions: OpenAPI Editor, Swagger Viewer

---

## Project Structure

```
project_service/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Environment configurations
│   ├── logger.py                # Logging configuration
│   ├── routes.py                # Route registration
│   ├── utils.py                 # Utility functions
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── db.py                # Database instance
│   │   ├── project.py           # Project model
│   │   ├── milestone.py         # Milestone model
│   │   ├── deliverable.py       # Deliverable model
│   │   ├── member.py            # Member model
│   │   ├── role.py              # Role model
│   │   ├── policy.py            # Policy model
│   │   └── permission.py        # Permission model
│   ├── resources/               # API endpoints (controllers)
│   │   ├── __init__.py
│   │   ├── health.py            # Health check
│   │   ├── version.py           # Version endpoint
│   │   ├── config.py            # Config endpoint
│   │   ├── projects.py          # Project CRUD
│   │   ├── members.py           # Member management
│   │   ├── milestones.py        # Milestone management
│   │   ├── deliverables.py      # Deliverable management
│   │   ├── roles.py             # Role management
│   │   ├── policies.py          # Policy management
│   │   ├── permissions.py       # Permission listing
│   │   └── access_control.py    # Access validation
│   └── schemas/                 # Marshmallow schemas
│       ├── __init__.py
│       ├── project_schema.py
│       ├── milestone_schema.py
│       ├── deliverable_schema.py
│       ├── member_schema.py
│       ├── role_schema.py
│       ├── policy_schema.py
│       └── permission_schema.py
├── migrations/                  # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── specifications/              # API specifications
│   ├── README.md
│   ├── ENDPOINTS_SPECIFICATION.md
│   ├── SCHEMAS_SPECIFICATION.md
│   └── RESPONSES_SPECIFICATION.md
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api.py
│   ├── test_projects.py
│   ├── test_members.py
│   ├── test_milestones.py
│   ├── test_deliverables.py
│   ├── test_rbac.py
│   └── test_access_control.py
├── openapi.yml                  # OpenAPI 3.0.3 specification
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                   # Pytest configuration
├── Dockerfile                   # Container image
├── docker-entrypoint.sh         # Container startup script
├── wait-for-it.sh               # Service dependency wait script
├── run.py                       # Development server
├── wsgi.py                      # Production WSGI entry point
├── env.example                  # Environment variables template
├── README.md                    # This file
├── LICENSE                      # AGPL v3 License
├── LICENSE.md                   # License details
├── COMMERCIAL-LICENSE.txt       # Commercial licensing
└── CODE_OF_CONDUCT.md           # Community guidelines
```

---

## Usage

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bengeek06/project_api_waterfall.git
   cd project_api_waterfall
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env.development
   # Edit .env.development with your settings
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the development server**
   ```bash
   FLASK_ENV=development python run.py
   ```

   The API will be available at `http://localhost:5000`

### Docker

1. **Build the image**
   ```bash
   docker build -t waterfall/project-service:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name project-service \
     --env-file .env.production \
     -p 5000:5000 \
     waterfall/project-service:latest
   ```

### Docker Compose (recommended for Waterfall ecosystem)

```yaml
version: '3.8'

services:
  project-service:
    image: waterfall/project-service:latest
    ports:
      - "5002:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/project_db
      - IDENTITY_SERVICE_URL=http://identity-service:5000
      - GUARDIAN_SERVICE_URL=http://guardian-service:5000
      - STORAGE_SERVICE_URL=http://storage-service:5000
    depends_on:
      - db
      - identity-service
      - guardian-service
    networks:
      - waterfall-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=project_db
      - POSTGRES_PASSWORD=password
    volumes:
      - project-db-data:/var/lib/postgresql/data
    networks:
      - waterfall-network

volumes:
  project-db-data:

networks:
  waterfall-network:
    external: true
```

### Testing

Run the complete test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_projects.py
```

Run tests matching a pattern:
```bash
pytest -k "test_create_project"
```

---

## Integration Examples

### Storage Service Integration

When a user attempts to access a file in Storage Service, Storage calls Project Service to validate permissions:

```python
# Storage Service code
import requests

def check_file_permission(project_id, user_id, action):
    """Check if user can perform action on project files"""
    response = requests.post(
        'http://project-service:5000/check-file-access',
        json={
            'project_id': project_id,
            'action': action  # 'read', 'write', 'delete', 'lock', 'validate'
        },
        headers={'Authorization': f'Bearer {jwt_token}'}
    )
    
    result = response.json()
    return result['allowed']
```

### Task Service Integration

Task Service pulls project structure to generate WBS:

```python
# Task Service code
import requests

def get_project_wbs(project_id):
    """Retrieve project structure for WBS generation"""
    response = requests.get(
        f'http://project-service:5000/projects/{project_id}/wbs-structure',
        headers={'Authorization': f'Bearer {jwt_token}'}
    )
    
    data = response.json()
    # data contains: project metadata, milestones, deliverables, associations
    return data
```

---

## Database Schema

### Core Tables

- `projects`: Main project entities
- `project_members`: User-project associations with roles
- `milestones`: Project milestones
- `deliverables`: Project deliverables
- `milestone_deliverables`: Many-to-many milestone-deliverable associations

### RBAC Tables

- `project_roles`: Roles within projects (default + custom)
- `project_policies`: Groups of permissions
- `project_permissions`: Predefined permissions (seeded at startup)
- `role_policies`: Many-to-many role-policy associations
- `policy_permissions`: Many-to-many policy-permission associations

### Audit Tables

- `project_history`: Complete audit trail of all changes

All tables include:
- `company_id`: Multi-tenant isolation
- `created_at`, `updated_at`: Timestamps
- `removed_at`: Soft delete support (where applicable)

---

## Authentication & Authorization

### Authentication Flow

1. User authenticates via Auth Service → receives JWT token
2. JWT token stored in HTTP-only cookie
3. Every request includes JWT cookie
4. Project Service validates JWT and extracts `user_id` and `company_id`

### Authorization Flow

1. **Guardian Check** (Endpoint-level)
   - Guardian Service validates if user's Guardian role has permission to call this endpoint
   - If denied → 403 Forbidden

2. **Project Service Check** (Context-level)
   - Project Service validates if user is project member
   - Checks user's project role permissions for the specific action
   - If denied → 403 Forbidden

### Example: File Write Permission

```
User → Guardian → Project Service → Storage Service
  ↓        ↓            ↓                  ↓
JWT    Can call    Is member?      Execute write
       endpoint?   Has write_files?
```

---

---

## Development

### Adding a New Endpoint

1. **Define the route** in `app/routes.py`
2. **Create the resource** in `app/resources/`
3. **Add database model** (if needed) in `app/models/`
4. **Create schema** for validation in `app/schemas/`
5. **Update OpenAPI** specification in `openapi.yml`
6. **Write tests** in `tests/`
7. **Create migration** (if model changed): `flask db migrate -m "description"`

### Code Style

This project follows:
- **PEP 8** for Python code style
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **Flake8** for linting
- **mypy** for type checking (optional)

Run formatters:
```bash
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-endpoint

# Make changes and commit
git add .
git commit -m "feat: add new endpoint for X"

# Push and create PR
git push origin feature/new-endpoint
```

Commit message format: `type: description`
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify DATABASE_URL in .env file
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL
```

### JWT Token Issues

```bash
# Verify JWT_SECRET_KEY matches across all Waterfall services
# Check token expiration
# Ensure HTTP-only cookies are enabled
```

### Service Integration Issues

```bash
# Verify service URLs in .env
# Check services are running:
curl http://localhost:5001/health  # Identity Service
curl http://localhost:5003/health  # Guardian Service
curl http://localhost:5004/health  # Storage Service

# Check network connectivity in Docker
docker network inspect waterfall-network
```

### Migration Issues

```bash
# Reset migrations (CAUTION: destroys data)
flask db downgrade base
flask db upgrade

# View migration history
flask db history

# Create manual migration
flask db revision -m "manual migration"
```

---

## Performance Considerations

### Database

- **Indexes**: All foreign keys and frequently queried fields are indexed
- **Connection pooling**: Configured via SQLAlchemy
- **Query optimization**: Use `.options()` for eager loading related entities

### Caching

Consider implementing:
- Redis for session caching
- Response caching for frequently accessed projects
- Permission caching to reduce RBAC query overhead

### Batch Operations

Use batch endpoints when checking multiple permissions:
- `/check-file-access-batch`
- `/check-project-access-batch`

These endpoints process multiple checks in a single database transaction.

---

## Security

### Best Practices Implemented

- ✅ **JWT Authentication**: Secure token-based auth
- ✅ **HTTP-only Cookies**: Prevents XSS attacks
- ✅ **Multi-tenant Isolation**: Company-level data segregation
- ✅ **Role-Based Access Control**: Granular permissions
- ✅ **SQL Injection Protection**: SQLAlchemy ORM
- ✅ **Input Validation**: Marshmallow schemas
- ✅ **Audit Trail**: Complete history tracking
- ✅ **Soft Deletes**: Data recovery capability

### Security Checklist

- [ ] Rotate JWT_SECRET_KEY regularly
- [ ] Use HTTPS in production
- [ ] Configure CORS properly
- [ ] Enable rate limiting (e.g., Flask-Limiter)
- [ ] Set up security headers (e.g., Flask-Talisman)
- [ ] Regular dependency updates
- [ ] Database backups
- [ ] Monitor and log security events

---

## Monitoring & Logging

### Health Check

```bash
curl http://localhost:5000/health
```

Response includes:
- Service status
- Database connectivity
- Response times
- Version information

### Logging

Logs are structured for easy parsing:
```json
{
  "timestamp": "2025-11-11T12:30:00Z",
  "level": "INFO",
  "service": "project_service",
  "message": "Project created",
  "project_id": "a1b2c3d4-...",
  "user_id": "f8a9b0c1-...",
  "company_id": "c5d6e7f8-..."
}
```

### Metrics to Monitor

- Request rate and latency
- Error rate by endpoint
- Database query performance
- JWT validation failures
- Permission check failures
- Project lifecycle status distribution

---

## Roadmap

### Version 0.0.1 (Current)
- ✅ Core project lifecycle management
- ✅ RBAC implementation
- ✅ Storage Service integration
- ✅ Task Service integration
- ✅ Complete OpenAPI specification

### Version 0.1.0 (Planned)
- [ ] Project templates
- [ ] Bulk import/export
- [ ] Project duplication
- [ ] Advanced search and filtering
- [ ] Project tags and categories
- [ ] Custom fields

### Version 0.2.0 (Future)
- [ ] Project budget tracking integration
- [ ] Gantt chart data endpoints
- [ ] Resource allocation
- [ ] Project analytics dashboard
- [ ] Webhooks for project events
- [ ] GraphQL API

---

## Contributing

We welcome contributions! Please see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Pull Request Guidelines

- Update documentation (README, OpenAPI, specifications)
- Add tests for new features
- Follow existing code style
- Keep PRs focused on a single feature/fix
- Update CHANGELOG.md

---

## License

This project is dual-licensed:

### Open Source License
GNU Affero General Public License v3.0 (AGPL-3.0)  
See [LICENSE](LICENSE) for details.

**AGPL-3.0 requires:**
- Source code disclosure for network use
- Same license for derivative works
- Attribution to original authors

### Commercial License
Commercial licensing available for organizations that cannot comply with AGPL-3.0.  
See [COMMERCIAL-LICENSE.txt](COMMERCIAL-LICENSE.txt) for details.

Contact: contact@waterfall-project.pro

---

## Support

- **Documentation**: [specifications/](specifications/)
- **Issues**: [GitHub Issues](https://github.com/bengeek06/project_api_waterfall/issues)
- **Email**: contact@waterfall-project.pro
- **Waterfall Platform**: Part of the complete Waterfall project management ecosystem

---

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Database: [PostgreSQL](https://www.postgresql.org/)
- ORM: [SQLAlchemy](https://www.sqlalchemy.org/)
- Validation: [Marshmallow](https://marshmallow.readthedocs.io/)
- Testing: [Pytest](https://pytest.org/)
- API Spec: [OpenAPI 3.0.3](https://swagger.io/specification/)

Part of the **Waterfall Platform** - Open source project management suite.

---

**Version**: 0.0.1  
**Last Updated**: 2025-11-11  
**Maintainer**: bengeek06
