# Spécification des Réponses HTTP - Project Service API

**Version**: 0.0.1  
**Date**: 2025-11-11  

---

## Table des matières

1. [Codes de statut HTTP](#codes-de-statut-http)
2. [Réponses par endpoint](#réponses-par-endpoint)
   - [Endpoints système](#endpoints-système)
   - [Endpoints projets](#endpoints-projets)
   - [Endpoints membres](#endpoints-membres)
   - [Endpoints milestones](#endpoints-milestones)
   - [Endpoints deliverables](#endpoints-deliverables)
   - [Endpoints rôles](#endpoints-rôles)
   - [Endpoints politiques](#endpoints-politiques)
   - [Endpoints permissions](#endpoints-permissions)
   - [Endpoints associations](#endpoints-associations)
   - [Endpoints contrôle d'accès](#endpoints-contrôle-daccès)
3. [Exemples de réponses](#exemples-de-réponses)

---

## Codes de statut HTTP

### Codes de succès (2xx)

| Code | Nom | Usage |
|------|-----|-------|
| 200 | OK | Requête réussie, données retournées (GET, PUT, PATCH) |
| 201 | Created | Ressource créée avec succès (POST) |
| 204 | No Content | Succès sans contenu à retourner (DELETE) |

### Codes d'erreur client (4xx)

| Code | Nom | Usage |
|------|-----|-------|
| 400 | Bad Request | Données invalides, champs manquants, format incorrect |
| 401 | Unauthorized | JWT manquant, invalide ou expiré |
| 403 | Forbidden | Authentifié mais permissions insuffisantes |
| 404 | Not Found | Ressource non trouvée |
| 409 | Conflict | Conflit (ressource existe déjà, contrainte violée) |

### Codes d'erreur serveur (5xx)

| Code | Nom | Usage |
|------|-----|-------|
| 500 | Internal Server Error | Erreur interne du serveur |
| 502 | Bad Gateway | Service dépendant (Identity, Guardian) injoignable |
| 503 | Service Unavailable | Service temporairement indisponible |
| 504 | Gateway Timeout | Timeout lors de l'appel à un service externe |

---

## Réponses par endpoint

### Endpoints système

#### GET /health

**200 OK** - Service opérationnel
```json
{
  "status": "healthy",
  "service": "project_service",
  "timestamp": "2025-11-11T12:00:00Z",
  "version": "0.0.1",
  "environment": "development",
  "checks": {
    "database": {
      "healthy": true,
      "message": "Database connection successful",
      "response_time_ms": 5.2
    }
  }
}
```

**503 Service Unavailable** - Service dégradé
```json
{
  "status": "unhealthy",
  "service": "project_service",
  "timestamp": "2025-11-11T12:00:00Z",
  "version": "0.0.1",
  "environment": "development",
  "checks": {
    "database": {
      "healthy": false,
      "message": "Cannot connect to database",
      "response_time_ms": 0
    }
  }
}
```

---

#### GET /version

**200 OK**
```json
{
  "version": "0.0.1"
}
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

---

#### GET /config

**200 OK**
```json
{
  "env": "development",
  "debug": true,
  "database_url": "postgresql://***:***@localhost:5432/project_db"
}
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

---

### Endpoints projets

#### GET /projects

**200 OK** - Liste paginée
```json
[
  {
    "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Projet Alpha",
    "description": "Développement module CRM",
    "company_id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
    "customer_id": "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b",
    "created_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
    "status": "active",
    "contract_amount": 250000.00,
    "budget_currency": "EUR",
    "created_at": "2025-01-10T14:20:00Z",
    "updated_at": "2025-11-11T11:30:00Z"
  }
]
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

**403 Forbidden** - Pas accès via Guardian
```json
{
  "message": "Access denied - insufficient permissions"
}
```

**500 Internal Server Error**
```json
{
  "message": "Internal server error"
}
```

---

#### POST /projects

**201 Created**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Projet Alpha",
  "description": "Développement module CRM",
  "company_id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
  "customer_id": null,
  "created_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
  "status": "created",
  "contract_amount": null,
  "budget_currency": null,
  "created_at": "2025-11-11T12:00:00Z",
  "updated_at": "2025-11-11T12:00:00Z"
}
```

**400 Bad Request** - Données invalides
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required",
    "budget_currency": "Invalid currency code, must be 3 uppercase letters"
  }
}
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

**403 Forbidden**
```json
{
  "message": "Access denied - insufficient permissions"
}
```

**409 Conflict** - Projet existe déjà
```json
{
  "message": "Project with this name already exists for this company"
}
```

**500 Internal Server Error**
```json
{
  "message": "Internal server error"
}
```

---

#### GET /projects/{project_id}

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Projet Alpha",
  "description": "Développement module CRM",
  "company_id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
  "customer_id": "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b",
  "created_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
  "status": "active",
  "consultation_date": "2025-01-15",
  "submission_deadline": "2025-02-15",
  "notification_date": "2025-03-01",
  "contract_start_date": "2025-03-15",
  "planned_start_date": "2025-03-20",
  "actual_start_date": "2025-03-22",
  "contract_delivery_date": "2025-12-31",
  "planned_delivery_date": "2025-12-15",
  "actual_delivery_date": null,
  "contract_amount": 250000.00,
  "budget_currency": "EUR",
  "suspended_at": null,
  "completed_at": null,
  "archived_at": null,
  "created_at": "2025-01-10T14:20:00Z",
  "updated_at": "2025-11-11T11:30:00Z"
}
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

**403 Forbidden**
```json
{
  "message": "Access denied - insufficient permissions"
}
```

**404 Not Found**
```json
{
  "message": "Project not found"
}
```

**500 Internal Server Error**
```json
{
  "message": "Internal server error"
}
```

---

#### PUT /projects/{project_id}

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Projet Alpha - Module CRM (Mise à jour)",
  "description": "Description mise à jour",
  "status": "active",
  ...
  "updated_at": "2025-11-11T12:30:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "status": "Invalid status transition from 'lost' to 'active'"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **409 Conflict** | **500 Internal Server Error**

(Mêmes formats que POST)

---

#### PATCH /projects/{project_id}

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "status": "completed",
  "completed_at": "2025-11-11T12:30:00Z",
  "updated_at": "2025-11-11T12:30:00Z",
  ...
}
```

**400 Bad Request** | **401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **409 Conflict** | **500 Internal Server Error**

(Mêmes formats que PUT)

---

#### DELETE /projects/{project_id}

**204 No Content** - Suppression réussie (pas de body)

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

**403 Forbidden**
```json
{
  "message": "Access denied - only project owner can delete project"
}
```

**404 Not Found**
```json
{
  "message": "Project not found"
}
```

**409 Conflict** - Contraintes
```json
{
  "message": "Cannot delete project with active members or milestones"
}
```

**500 Internal Server Error**
```json
{
  "message": "Internal server error"
}
```

---

#### GET /projects/{project_id}/metadata

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Projet Alpha",
  "status": "active",
  "company_id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
  "customer_id": "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/archive

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "status": "archived",
  "archived_at": "2025-11-11T12:45:00Z",
  "updated_at": "2025-11-11T12:45:00Z",
  ...
}
```

**400 Bad Request** - Déjà archivé
```json
{
  "message": "Project is already archived"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/restore

**200 OK**
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "status": "active",
  "archived_at": null,
  "updated_at": "2025-11-11T12:50:00Z",
  ...
}
```

**400 Bad Request** - Pas archivé
```json
{
  "message": "Project is not archived"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### GET /projects/{project_id}/history

**200 OK**
```json
[
  {
    "id": "h1i2j3k4-l5m6-4n7o-8p9q-0r1s2t3u4v5w",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "user_id": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
    "action": "status_changed",
    "entity_type": "project",
    "entity_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "changes": {
      "old_status": "consultation",
      "new_status": "active",
      "notification_date": "2025-03-01"
    },
    "created_at": "2025-03-01T14:30:00Z"
  },
  {
    "id": "h2i3j4k5-l6m7-4n8o-9p0q-1r2s3t4u5v6w",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "user_id": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
    "action": "member_added",
    "entity_type": "member",
    "entity_id": "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a",
    "changes": {
      "user_id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
      "role": "contributor"
    },
    "created_at": "2025-03-05T10:15:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### GET /projects/{project_id}/wbs-structure

**200 OK**
```json
{
  "project": {
    "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Projet Alpha",
    "status": "active",
    "company_id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f"
  },
  "milestones": [
    {
      "id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
      "name": "Livraison Phase 1",
      "description": "Module d'authentification",
      "due_date": "2025-06-30",
      "status": "in_progress",
      "order": 1
    }
  ],
  "deliverables": [
    {
      "id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
      "name": "Documentation technique API",
      "description": "Documentation complète",
      "type": "document",
      "due_date": "2025-06-15",
      "status": "in_progress",
      "order": 1
    }
  ],
  "associations": [
    {
      "milestone_id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
      "deliverable_id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f"
    }
  ]
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

### Endpoints membres

#### GET /projects/{project_id}/members

**200 OK**
```json
[
  {
    "id": "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "user_id": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
    "role_id": "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b",
    "added_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
    "added_at": "2025-01-10T14:20:00Z",
    "removed_at": null
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/members

**201 Created**
```json
{
  "id": "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "user_id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
  "role_id": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",
  "added_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
  "added_at": "2025-11-11T13:00:00Z",
  "removed_at": null
}
```

**400 Bad Request** - Données invalides
```json
{
  "message": "Invalid input data",
  "errors": {
    "user_id": "User ID must be a valid UUID",
    "role_id": "Role does not exist in this project"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict** - Membre existe déjà
```json
{
  "message": "User is already a member of this project"
}
```

**502 Bad Gateway** - Identity Service injoignable
```json
{
  "message": "Cannot verify user existence: Identity Service unavailable"
}
```

**500 Internal Server Error**

---

#### GET /projects/{project_id}/members/{user_id}

**200 OK**
```json
{
  "id": "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "user_id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
  "role_id": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",
  "added_by": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
  "added_at": "2025-03-05T10:15:00Z",
  "removed_at": null
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PUT /projects/{project_id}/members/{user_id}

**200 OK**
```json
{
  "id": "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a",
  "role_id": "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d",
  "updated_at": "2025-11-11T13:15:00Z",
  ...
}
```

**400 Bad Request** | **401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PATCH /projects/{project_id}/members/{user_id}

(Mêmes réponses que PUT)

---

#### DELETE /projects/{project_id}/members/{user_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden**

**404 Not Found**
```json
{
  "message": "Member not found in this project"
}
```

**409 Conflict** - Dernier owner
```json
{
  "message": "Cannot remove the last owner of the project"
}
```

**500 Internal Server Error**

---

### Endpoints milestones

#### GET /projects/{project_id}/milestones

**200 OK**
```json
[
  {
    "id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Livraison Phase 1",
    "description": "Module d'authentification et interface de base",
    "due_date": "2025-06-30",
    "status": "in_progress",
    "order": 1,
    "created_at": "2025-02-01T10:00:00Z",
    "updated_at": "2025-03-15T14:30:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/milestones

**201 Created**
```json
{
  "id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Livraison Phase 1",
  "description": "Module d'authentification",
  "due_date": "2025-06-30",
  "status": "planned",
  "order": 1,
  "created_at": "2025-11-11T13:30:00Z",
  "updated_at": "2025-11-11T13:30:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required",
    "due_date": "Invalid date format, expected YYYY-MM-DD"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** (project) | **500 Internal Server Error**

---

#### GET /projects/{project_id}/milestones/{milestone_id}

**200 OK** (format identique à POST 201)

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PUT /projects/{project_id}/milestones/{milestone_id}

**200 OK** (format identique à GET)

**400 Bad Request** | **401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PATCH /projects/{project_id}/milestones/{milestone_id}

(Mêmes réponses que PUT)

---

#### DELETE /projects/{project_id}/milestones/{milestone_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict**
```json
{
  "message": "Cannot delete milestone with associated deliverables"
}
```

**500 Internal Server Error**

---

#### GET /projects/{project_id}/milestones/{milestone_id}/deliverables

**200 OK**
```json
[
  {
    "id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Documentation technique API",
    "type": "document",
    "status": "in_progress",
    ...
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/milestones/{milestone_id}/deliverables

**201 Created**
```json
{
  "milestone_id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
  "deliverable_id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
  "created_at": "2025-11-11T14:00:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "deliverable_id": "Deliverable ID must be a valid UUID"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict**
```json
{
  "message": "Deliverable is already associated with this milestone"
}
```

**500 Internal Server Error**

---

#### GET /projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}

**200 OK**
```json
{
  "milestone_id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
  "deliverable_id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
  "created_at": "2025-11-11T14:00:00Z"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### DELETE /projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

### Endpoints deliverables

#### GET /projects/{project_id}/deliverables

**200 OK**
```json
[
  {
    "id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Documentation technique API",
    "description": "Documentation complète de l'API REST",
    "type": "document",
    "due_date": "2025-06-15",
    "status": "in_progress",
    "order": 1,
    "created_at": "2025-02-01T10:00:00Z",
    "updated_at": "2025-03-15T14:30:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/deliverables

**201 Created**
```json
{
  "id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Documentation technique API",
  "description": "Documentation complète",
  "type": "document",
  "due_date": "2025-06-15",
  "status": "planned",
  "order": 1,
  "created_at": "2025-11-11T14:15:00Z",
  "updated_at": "2025-11-11T14:15:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required",
    "type": "Invalid type, must be one of: document, software, hardware, service, other"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** (project) | **500 Internal Server Error**

---

#### GET /projects/{project_id}/deliverables/{deliverable_id}

**200 OK** (format identique à POST 201)

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PUT /projects/{project_id}/deliverables/{deliverable_id}

**200 OK** (format identique à GET)

**400 Bad Request** | **401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PATCH /projects/{project_id}/deliverables/{deliverable_id}

(Mêmes réponses que PUT)

---

#### DELETE /projects/{project_id}/deliverables/{deliverable_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

### Endpoints rôles

#### GET /projects/{project_id}/roles

**200 OK**
```json
[
  {
    "id": "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "owner",
    "description": "Créateur du projet avec tous les droits",
    "is_default": true,
    "created_at": "2025-01-10T14:20:00Z",
    "updated_at": "2025-01-10T14:20:00Z"
  },
  {
    "id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Chef de chantier",
    "description": "Responsable supervision chantier",
    "is_default": false,
    "created_at": "2025-03-01T10:00:00Z",
    "updated_at": "2025-03-01T10:00:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/roles

**201 Created**
```json
{
  "id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Chef de chantier",
  "description": "Responsable supervision chantier",
  "is_default": false,
  "created_at": "2025-11-11T14:30:00Z",
  "updated_at": "2025-11-11T14:30:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required and must be max 50 characters"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** (project)

**409 Conflict**
```json
{
  "message": "Role with this name already exists in this project"
}
```

**500 Internal Server Error**

---

#### GET /projects/{project_id}/roles/{role_id}

**200 OK** (format identique à POST 201)

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PUT /projects/{project_id}/roles/{role_id}

**200 OK** (format identique à GET)

**400 Bad Request**

**403 Forbidden** - Rôle par défaut
```json
{
  "message": "Cannot modify default roles"
}
```

**401 Unauthorized** | **404 Not Found** | **409 Conflict** | **500 Internal Server Error**

---

#### PATCH /projects/{project_id}/roles/{role_id}

(Mêmes réponses que PUT)

---

#### DELETE /projects/{project_id}/roles/{role_id}

**204 No Content**

**401 Unauthorized**

**403 Forbidden** - Rôle par défaut
```json
{
  "message": "Cannot delete default roles"
}
```

**404 Not Found**

**409 Conflict** - Rôle utilisé
```json
{
  "message": "Cannot delete role: members are currently assigned to this role"
}
```

**500 Internal Server Error**

---

### Endpoints politiques

#### GET /projects/{project_id}/policies

**200 OK**
```json
[
  {
    "id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Gestion des fichiers techniques",
    "description": "Autorise lecture, écriture et validation fichiers",
    "created_at": "2025-03-01T10:00:00Z",
    "updated_at": "2025-03-15T14:30:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/policies

**201 Created**
```json
{
  "id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "name": "Gestion des fichiers techniques",
  "description": "Autorise lecture, écriture et validation fichiers",
  "created_at": "2025-11-11T14:45:00Z",
  "updated_at": "2025-11-11T14:45:00Z"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required and must be max 100 characters"
  }
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** (project)

**409 Conflict**
```json
{
  "message": "Policy with this name already exists in this project"
}
```

**500 Internal Server Error**

---

#### GET /projects/{project_id}/policies/{policy_id}

**200 OK** (format identique à POST 201)

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### PUT /projects/{project_id}/policies/{policy_id}

**200 OK** (format identique à GET)

**400 Bad Request** | **401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **409 Conflict** | **500 Internal Server Error**

---

#### PATCH /projects/{project_id}/policies/{policy_id}

(Mêmes réponses que PUT)

---

#### DELETE /projects/{project_id}/policies/{policy_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict**
```json
{
  "message": "Cannot delete policy: currently assigned to one or more roles"
}
```

**500 Internal Server Error**

---

### Endpoints permissions

#### GET /projects/{project_id}/permissions

**200 OK**
```json
[
  {
    "id": "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d",
    "name": "read_files",
    "description": "Permet de lire et télécharger les fichiers du projet",
    "category": "files"
  },
  {
    "id": "b9c0d1e2-f3a4-4b5c-6d7e-8f9a0b1c2d3e",
    "name": "write_files",
    "description": "Permet de créer et modifier les fichiers du projet",
    "category": "files"
  },
  {
    "id": "c0d1e2f3-a4b5-4c6d-7e8f-9a0b1c2d3e4f",
    "name": "delete_files",
    "description": "Permet de supprimer les fichiers du projet",
    "category": "files"
  },
  {
    "id": "d1e2f3a4-b5c6-4d7e-8f9a-0b1c2d3e4f5a",
    "name": "lock_files",
    "description": "Permet de verrouiller et déverrouiller les fichiers",
    "category": "files"
  },
  {
    "id": "e2f3a4b5-c6d7-4e8f-9a0b-1c2d3e4f5a6b",
    "name": "validate_files",
    "description": "Permet d'approuver ou rejeter les versions de fichiers",
    "category": "files"
  },
  {
    "id": "f3a4b5c6-d7e8-4f9a-0b1c-2d3e4f5a6b7c",
    "name": "update_project",
    "description": "Permet de modifier les informations du projet",
    "category": "project"
  },
  {
    "id": "a4b5c6d7-e8f9-4a0b-1c2d-3e4f5a6b7c8d",
    "name": "delete_project",
    "description": "Permet de supprimer le projet",
    "category": "project"
  },
  {
    "id": "b5c6d7e8-f9a0-4b1c-2d3e-4f5a6b7c8d9e",
    "name": "manage_members",
    "description": "Permet de gérer les membres du projet",
    "category": "members"
  },
  {
    "id": "c6d7e8f9-a0b1-4c2d-3e4f-5a6b7c8d9e0f",
    "name": "manage_roles",
    "description": "Permet de créer et modifier les rôles du projet",
    "category": "rbac"
  },
  {
    "id": "d7e8f9a0-b1c2-4d3e-4f5a-6b7c8d9e0f1a",
    "name": "manage_policies",
    "description": "Permet de créer et modifier les politiques du projet",
    "category": "rbac"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** (project) | **500 Internal Server Error**

---

### Endpoints associations

#### GET /projects/{project_id}/roles/{role_id}/policies

**200 OK**
```json
[
  {
    "id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
    "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "Gestion des fichiers techniques",
    "description": "Autorise lecture, écriture et validation fichiers",
    "created_at": "2025-03-01T10:00:00Z",
    "updated_at": "2025-03-15T14:30:00Z"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### GET /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**200 OK**
```json
{
  "role_id": "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b",
  "policy_id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "associated": true,
  "created_at": "2025-03-01T10:30:00Z"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**201 Created**
```json
{
  "role_id": "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b",
  "policy_id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "message": "Policy successfully associated with role",
  "created_at": "2025-11-11T15:00:00Z"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict**
```json
{
  "message": "Policy is already associated with this role"
}
```

**500 Internal Server Error**

---

#### DELETE /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### GET /projects/{project_id}/policies/{policy_id}/permissions

**200 OK**
```json
[
  {
    "id": "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d",
    "name": "read_files",
    "description": "Permet de lire et télécharger les fichiers du projet",
    "category": "files"
  },
  {
    "id": "b9c0d1e2-f3a4-4b5c-6d7e-8f9a0b1c2d3e",
    "name": "write_files",
    "description": "Permet de créer et modifier les fichiers du projet",
    "category": "files"
  }
]
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### GET /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**200 OK**
```json
{
  "policy_id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "permission_id": "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d",
  "associated": true,
  "created_at": "2025-03-01T10:45:00Z"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**201 Created**
```json
{
  "policy_id": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "permission_id": "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d",
  "message": "Permission successfully associated with policy",
  "created_at": "2025-11-11T15:15:00Z"
}
```

**401 Unauthorized** | **403 Forbidden** | **404 Not Found**

**409 Conflict**
```json
{
  "message": "Permission is already associated with this policy"
}
```

**500 Internal Server Error**

---

#### DELETE /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**204 No Content**

**401 Unauthorized** | **403 Forbidden** | **404 Not Found** | **500 Internal Server Error**

---

### Endpoints contrôle d'accès

#### POST /check-file-access

**200 OK** - Accès autorisé
```json
{
  "allowed": true,
  "role": "contributor",
  "reason": "User has permission write_files"
}
```

**200 OK** - Accès refusé (pas membre)
```json
{
  "allowed": false,
  "reason": "User is not a member of this project"
}
```

**200 OK** - Accès refusé (permission manquante)
```json
{
  "allowed": false,
  "role": "viewer",
  "reason": "User does not have permission write_files"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "project_id": "Project ID must be a valid UUID",
    "action": "Invalid action, must be one of: read, write, delete, lock, validate"
  }
}
```

**401 Unauthorized**
```json
{
  "message": "Missing or invalid JWT token"
}
```

**404 Not Found**
```json
{
  "message": "Project not found"
}
```

**500 Internal Server Error**
```json
{
  "message": "Internal server error"
}
```

---

#### POST /check-file-access-batch

**200 OK**
```json
{
  "results": [
    {
      "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
      "action": "read",
      "allowed": true,
      "role": "viewer"
    },
    {
      "project_id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
      "action": "write",
      "allowed": false,
      "reason": "User is not a member of this project"
    },
    {
      "project_id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
      "action": "validate",
      "allowed": false,
      "role": "contributor",
      "reason": "User does not have permission validate_files"
    }
  ]
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "checks": "At least one check is required"
  }
}
```

**401 Unauthorized** | **500 Internal Server Error**

---

#### POST /check-project-access

**200 OK** - Accès autorisé
```json
{
  "allowed": true,
  "role": "admin",
  "project_status": "active",
  "reason": "User is a member with read access"
}
```

**200 OK** - Accès refusé
```json
{
  "allowed": false,
  "reason": "User is not a member of this project"
}
```

**200 OK** - Accès refusé (permission insuffisante)
```json
{
  "allowed": false,
  "role": "viewer",
  "project_status": "active",
  "reason": "User does not have permission update_project"
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "project_id": "Project ID must be a valid UUID",
    "action": "Invalid action, must be one of: read, write, manage"
  }
}
```

**401 Unauthorized** | **404 Not Found** | **500 Internal Server Error**

---

#### POST /check-project-access-batch

**200 OK**
```json
{
  "results": [
    {
      "project_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
      "action": "read",
      "allowed": true,
      "role": "contributor",
      "project_status": "active"
    },
    {
      "project_id": "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e",
      "action": "write",
      "allowed": false,
      "reason": "Insufficient permissions"
    },
    {
      "project_id": "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f",
      "action": "manage",
      "allowed": true,
      "role": "admin",
      "project_status": "active"
    }
  ]
}
```

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "checks": "At least one check is required"
  }
}
```

**401 Unauthorized** | **500 Internal Server Error**

---

## Exemples de réponses

### Exemple d'erreur de validation complète

**POST /projects** avec données invalides

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "name": "Name is required",
    "budget_currency": "Invalid currency code, must be 3 uppercase letters (e.g., EUR, USD)",
    "contract_amount": "Contract amount must be a positive number",
    "consultation_date": "Invalid date format, expected YYYY-MM-DD"
  }
}
```

---

### Exemple d'erreur Guardian (RBAC endpoint-level)

**GET /projects** sans permission Guardian

**403 Forbidden**
```json
{
  "message": "Access denied - insufficient permissions"
}
```

---

### Exemple d'erreur Identity Service indisponible

**POST /projects/{project_id}/members** - Identity Service down

**502 Bad Gateway**
```json
{
  "message": "Cannot verify user existence: Identity Service unavailable"
}
```

---

### Exemple de contrainte violée

**DELETE /projects/{project_id}/members/{user_id}** - Dernier owner

**409 Conflict**
```json
{
  "message": "Cannot remove the last owner of the project"
}
```

---

### Exemple de transition de statut invalide

**PATCH /projects/{project_id}** - Transition impossible

**400 Bad Request**
```json
{
  "message": "Invalid input data",
  "errors": {
    "status": "Invalid status transition from 'lost' to 'active'. Lost projects cannot be reactivated."
  }
}
```

---

## Résumé des codes de statut par catégorie d'endpoint

### Endpoints CRUD standards (projects, milestones, deliverables, roles, policies)

| Méthode | Succès | Erreurs possibles |
|---------|--------|-------------------|
| GET (liste) | 200 | 401, 403, 500 |
| POST (create) | 201 | 400, 401, 403, 404 (parent), 409, 500, 502 (services externes) |
| GET (item) | 200 | 401, 403, 404, 500 |
| PUT (update) | 200 | 400, 401, 403, 404, 409, 500 |
| PATCH (update) | 200 | 400, 401, 403, 404, 409, 500 |
| DELETE | 204 | 401, 403, 404, 409, 500 |

### Endpoints spéciaux

| Endpoint | Succès | Erreurs possibles |
|----------|--------|-------------------|
| /health | 200, 503 | - |
| /version | 200 | 401 |
| /config | 200 | 401 |
| /archive | 200 | 400, 401, 403, 404, 500 |
| /restore | 200 | 400, 401, 403, 404, 500 |
| /history | 200 | 401, 403, 404, 500 |
| /wbs-structure | 200 | 401, 403, 404, 500 |
| /check-file-access | 200 | 400, 401, 404, 500 |
| /check-project-access | 200 | 400, 401, 404, 500 |

### Endpoints associations

| Endpoint | Méthode | Succès | Erreurs possibles |
|----------|---------|--------|-------------------|
| /roles/{role_id}/policies | GET | 200 | 401, 403, 404, 500 |
| /roles/{role_id}/policies/{policy_id} | GET | 200 | 401, 403, 404, 500 |
| /roles/{role_id}/policies/{policy_id} | POST | 201 | 401, 403, 404, 409, 500 |
| /roles/{role_id}/policies/{policy_id} | DELETE | 204 | 401, 403, 404, 500 |
| /policies/{policy_id}/permissions | GET | 200 | 401, 403, 404, 500 |
| /policies/{policy_id}/permissions/{permission_id} | GET | 200 | 401, 403, 404, 500 |
| /policies/{policy_id}/permissions/{permission_id} | POST | 201 | 401, 403, 404, 409, 500 |
| /policies/{policy_id}/permissions/{permission_id} | DELETE | 204 | 401, 403, 404, 500 |


---

**Dernière mise à jour** : 2025-11-11  
**Auteur** : bengeek06
