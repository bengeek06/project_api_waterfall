# Schémas de Données - Project Service API

**Version**: 0.0.1  
**Date**: 2025-11-11  

---

## Table des matières

1. [Schémas Project](#schémas-project)
2. [Schémas Milestone](#schémas-milestone)
3. [Schémas Deliverable](#schémas-deliverable)
4. [Schémas Member](#schémas-member)
5. [Schémas Role](#schémas-role)
6. [Schémas Policy](#schémas-policy)
7. [Schémas Permission](#schémas-permission)
8. [Schémas Associations](#schémas-associations)
9. [Schémas Contrôle d'accès](#schémas-contrôle-daccès)
10. [Schémas Réponses communes](#schémas-réponses-communes)

---

## Schémas Project

### Project (Complet)

Représentation complète d'un projet (retourné par GET).

```yaml
Project:
  type: object
  required:
    - id
    - name
    - company_id
    - created_by
    - status
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      maxLength: 100
      description: Nom du projet
      example: "Projet Alpha - Développement Module CRM"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description détaillée du projet
      example: "Développement d'un nouveau module CRM pour gérer les contacts clients"
    
    company_id:
      type: string
      format: uuid
      description: Identifiant de l'entreprise propriétaire (multi-tenant)
      example: "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f"
    
    customer_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant du client (référence vers Identity Service)
      example: "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"
    
    created_by:
      type: string
      format: uuid
      readOnly: true
      description: User créateur du projet (devient automatiquement owner)
      example: "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c"
    
    status:
      type: string
      enum:
        - created
        - initialized
        - consultation
        - lost
        - active
        - suspended
        - completed
        - archived
      description: Statut actuel du projet
      example: "active"
    
    # Dates phase consultation
    consultation_date:
      type: string
      format: date
      nullable: true
      description: Date de publication de la consultation/appel d'offres
      example: "2025-01-15"
    
    submission_deadline:
      type: string
      format: date
      nullable: true
      description: Date limite de soumission de l'offre
      example: "2025-02-15"
    
    notification_date:
      type: string
      format: date
      nullable: true
      description: Date de notification du résultat (gagné/perdu)
      example: "2025-03-01"
    
    # Dates phase exécution
    contract_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage contractuel du projet
      example: "2025-03-15"
    
    planned_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage prévue (peut différer du contractuel)
      example: "2025-03-20"
    
    actual_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage réel du projet
      example: "2025-03-22"
    
    # Dates phase livraison
    contract_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison contractuelle
      example: "2025-12-31"
    
    planned_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison prévue
      example: "2025-12-15"
    
    actual_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison réelle
      example: "2025-12-10"
    
    # Données financières
    contract_amount:
      type: number
      format: decimal
      nullable: true
      description: Montant contractuel du projet
      example: 250000.00
      minimum: 0
    
    budget_currency:
      type: string
      maxLength: 3
      nullable: true
      description: Code devise ISO 4217 (EUR, USD, GBP, etc.)
      example: "EUR"
      pattern: "^[A-Z]{3}$"
    
    # Dates de gestion du cycle de vie
    suspended_at:
      type: string
      format: date-time
      nullable: true
      readOnly: true
      description: Date de suspension du projet
      example: "2025-06-15T10:30:00Z"
    
    completed_at:
      type: string
      format: date-time
      nullable: true
      readOnly: true
      description: Date de complétion du projet
      example: "2025-12-10T16:45:00Z"
    
    archived_at:
      type: string
      format: date-time
      nullable: true
      readOnly: true
      description: Date d'archivage du projet
      example: "2026-01-15T09:00:00Z"
    
    # Métadonnées
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de création du projet
      example: "2025-01-10T14:20:00Z"
    
    updated_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de dernière modification
      example: "2025-11-11T11:30:00Z"
```

---

### ProjectCreate

Schéma pour créer un nouveau projet (POST /projects).

```yaml
ProjectCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du projet
      example: "Projet Alpha - Développement Module CRM"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description détaillée du projet
      example: "Développement d'un nouveau module CRM pour gérer les contacts clients"
    
    customer_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant du client (référence vers Identity Service)
      example: "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"
    
    consultation_date:
      type: string
      format: date
      nullable: true
      description: Date de publication de la consultation
      example: "2025-01-15"
    
    submission_deadline:
      type: string
      format: date
      nullable: true
      description: Date limite de soumission de l'offre
      example: "2025-02-15"
    
    contract_amount:
      type: number
      format: decimal
      nullable: true
      description: Montant contractuel estimé
      example: 250000.00
      minimum: 0
    
    budget_currency:
      type: string
      maxLength: 3
      nullable: true
      description: Code devise ISO 4217
      example: "EUR"
      pattern: "^[A-Z]{3}$"

# Notes:
# - company_id est extrait du JWT (g.company_id)
# - created_by est extrait du JWT (g.user_id)
# - status est défini automatiquement à 'created'
# - Le créateur devient automatiquement membre avec role 'owner'
```

---

### ProjectUpdate

Schéma pour mettre à jour un projet (PUT/PATCH /projects/{project_id}).

```yaml
ProjectUpdate:
  type: object
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du projet
      example: "Projet Alpha - Module CRM (Mise à jour)"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description du projet
      example: "Description mise à jour"
    
    customer_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant du client
      example: "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"
    
    status:
      type: string
      enum:
        - created
        - initialized
        - consultation
        - lost
        - active
        - suspended
        - completed
        - archived
      description: Nouveau statut du projet
      example: "active"
    
    # Dates phase consultation
    consultation_date:
      type: string
      format: date
      nullable: true
      description: Date de publication de la consultation
      example: "2025-01-15"
    
    submission_deadline:
      type: string
      format: date
      nullable: true
      description: Date limite de soumission
      example: "2025-02-15"
    
    notification_date:
      type: string
      format: date
      nullable: true
      description: Date de notification du résultat
      example: "2025-03-01"
    
    # Dates phase exécution
    contract_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage contractuel
      example: "2025-03-15"
    
    planned_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage prévue
      example: "2025-03-20"
    
    actual_start_date:
      type: string
      format: date
      nullable: true
      description: Date de démarrage réel
      example: "2025-03-22"
    
    # Dates phase livraison
    contract_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison contractuelle
      example: "2025-12-31"
    
    planned_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison prévue
      example: "2025-12-15"
    
    actual_delivery_date:
      type: string
      format: date
      nullable: true
      description: Date de livraison réelle
      example: "2025-12-10"
    
    # Données financières
    contract_amount:
      type: number
      format: decimal
      nullable: true
      description: Montant contractuel
      example: 250000.00
      minimum: 0
    
    budget_currency:
      type: string
      maxLength: 3
      nullable: true
      description: Code devise ISO 4217
      example: "EUR"
      pattern: "^[A-Z]{3}$"

# Notes:
# - Tous les champs sont optionnels pour PATCH
# - Tous les champs sont requis pour PUT (sauf les readOnly)
# - company_id et created_by ne peuvent pas être modifiés
# - Les changements de statut créent une entrée d'historique
```

---

### ProjectMetadata

Schéma pour les métadonnées minimales (GET /projects/{project_id}/metadata).

```yaml
ProjectMetadata:
  type: object
  required:
    - id
    - name
    - status
    - company_id
  properties:
    id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      description: Nom du projet
      example: "Projet Alpha"
    
    status:
      type: string
      enum:
        - created
        - initialized
        - consultation
        - lost
        - active
        - suspended
        - completed
        - archived
      description: Statut actuel
      example: "active"
    
    company_id:
      type: string
      format: uuid
      description: Identifiant de l'entreprise
      example: "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f"
    
    customer_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant du client
      example: "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"
```

---

### WBSStructure

Schéma pour la structure WBS (GET /projects/{project_id}/wbs-structure).

```yaml
WBSStructure:
  type: object
  required:
    - project
    - milestones
    - deliverables
    - associations
  properties:
    project:
      type: object
      description: Métadonnées du projet
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        status:
          type: string
        company_id:
          type: string
          format: uuid
    
    milestones:
      type: array
      description: Liste des jalons du projet
      items:
        type: object
        properties:
          id:
            type: string
            format: uuid
          name:
            type: string
          description:
            type: string
            nullable: true
          due_date:
            type: string
            format: date
            nullable: true
          status:
            type: string
          order:
            type: integer
    
    deliverables:
      type: array
      description: Liste des livrables du projet
      items:
        type: object
        properties:
          id:
            type: string
            format: uuid
          name:
            type: string
          description:
            type: string
            nullable: true
          type:
            type: string
          due_date:
            type: string
            format: date
            nullable: true
          status:
            type: string
          order:
            type: integer
    
    associations:
      type: array
      description: Associations milestone-deliverable
      items:
        type: object
        properties:
          milestone_id:
            type: string
            format: uuid
          deliverable_id:
            type: string
            format: uuid
```

---

## Schémas Milestone

### Milestone (Complet)

```yaml
Milestone:
  type: object
  required:
    - id
    - project_id
    - name
    - status
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique du jalon
      example: "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet parent
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      maxLength: 100
      description: Nom du jalon
      example: "Livraison Phase 1"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description détaillée du jalon
      example: "Livraison du module d'authentification et interface utilisateur de base"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance du jalon
      example: "2025-06-30"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - cancelled
      description: Statut du jalon
      example: "in_progress"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage/séquence
      example: 1
      minimum: 0
    
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de création
      example: "2025-02-01T10:00:00Z"
    
    updated_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de dernière modification
      example: "2025-03-15T14:30:00Z"
```

---

### MilestoneCreate

```yaml
MilestoneCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du jalon
      example: "Livraison Phase 1"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description du jalon
      example: "Livraison du module d'authentification"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance
      example: "2025-06-30"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - cancelled
      default: planned
      description: Statut initial du jalon
      example: "planned"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage
      example: 1
      minimum: 0

# Note: project_id est extrait du path parameter
```

---

### MilestoneUpdate

```yaml
MilestoneUpdate:
  type: object
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du jalon
      example: "Livraison Phase 1 (mise à jour)"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description du jalon
      example: "Description mise à jour"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance
      example: "2025-07-15"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - cancelled
      description: Statut du jalon
      example: "in_progress"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage
      example: 2
      minimum: 0
```

---

## Schémas Deliverable

### Deliverable (Complet)

```yaml
Deliverable:
  type: object
  required:
    - id
    - project_id
    - name
    - status
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique du livrable
      example: "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet parent
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      maxLength: 100
      description: Nom du livrable
      example: "Documentation technique API"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description détaillée du livrable
      example: "Documentation complète de l'API REST incluant tous les endpoints et exemples"
    
    type:
      type: string
      enum:
        - document
        - software
        - hardware
        - service
        - other
      nullable: true
      description: Type de livrable
      example: "document"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance du livrable
      example: "2025-06-15"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - delivered
        - accepted
      description: Statut du livrable
      example: "in_progress"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage/séquence
      example: 1
      minimum: 0
    
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de création
      example: "2025-02-01T10:00:00Z"
    
    updated_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de dernière modification
      example: "2025-03-15T14:30:00Z"
```

---

### DeliverableCreate

```yaml
DeliverableCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du livrable
      example: "Documentation technique API"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description du livrable
      example: "Documentation complète de l'API REST"
    
    type:
      type: string
      enum:
        - document
        - software
        - hardware
        - service
        - other
      nullable: true
      default: document
      description: Type de livrable
      example: "document"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance
      example: "2025-06-15"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - delivered
        - accepted
      default: planned
      description: Statut initial
      example: "planned"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage
      example: 1
      minimum: 0

# Note: project_id est extrait du path parameter
```

---

### DeliverableUpdate

```yaml
DeliverableUpdate:
  type: object
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom du livrable
      example: "Documentation API (v2)"
    
    description:
      type: string
      maxLength: 500
      nullable: true
      description: Description du livrable
      example: "Description mise à jour"
    
    type:
      type: string
      enum:
        - document
        - software
        - hardware
        - service
        - other
      nullable: true
      description: Type de livrable
      example: "document"
    
    due_date:
      type: string
      format: date
      nullable: true
      description: Date d'échéance
      example: "2025-06-30"
    
    status:
      type: string
      enum:
        - planned
        - in_progress
        - completed
        - delivered
        - accepted
      description: Statut du livrable
      example: "delivered"
    
    order:
      type: integer
      nullable: true
      description: Ordre d'affichage
      example: 2
      minimum: 0
```

---

## Schémas Member

### ProjectMember (Complet)

```yaml
ProjectMember:
  type: object
  required:
    - id
    - project_id
    - user_id
    - role_id
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique du membre
      example: "d4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    user_id:
      type: string
      format: uuid
      description: Identifiant du user (référence Identity Service)
      example: "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"
    
    role_id:
      type: string
      format: uuid
      description: Identifiant du rôle projet assigné
      example: "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c"
    
    added_by:
      type: string
      format: uuid
      readOnly: true
      description: User qui a ajouté ce membre
      example: "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d"
    
    added_at:
      type: string
      format: date-time
      readOnly: true
      description: Date d'ajout au projet
      example: "2025-03-01T09:00:00Z"
    
    removed_at:
      type: string
      format: date-time
      nullable: true
      readOnly: true
      description: Date de retrait du projet (null si membre actif)
      example: null
```

---

### ProjectMemberCreate

```yaml
ProjectMemberCreate:
  type: object
  required:
    - user_id
    - role_id
  properties:
    user_id:
      type: string
      format: uuid
      description: Identifiant du user à ajouter au projet
      example: "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"
    
    role_id:
      type: string
      format: uuid
      description: Identifiant du rôle à assigner
      example: "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c"

# Notes:
# - project_id est extrait du path parameter
# - added_by est extrait du JWT (g.user_id)
# - Vérifier que user_id existe dans Identity Service
# - Vérifier que role_id existe dans ce projet
```

---

### ProjectMemberUpdate

```yaml
ProjectMemberUpdate:
  type: object
  properties:
    role_id:
      type: string
      format: uuid
      description: Nouveau rôle à assigner au membre
      example: "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d"

# Note: Seul le rôle peut être modifié
```

---

## Schémas Role

### ProjectRole (Complet)

```yaml
ProjectRole:
  type: object
  required:
    - id
    - project_id
    - name
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique du rôle
      example: "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      maxLength: 50
      description: Nom du rôle
      example: "Chef de chantier"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description du rôle
      example: "Responsable de la supervision du chantier et coordination des équipes"
    
    is_default:
      type: boolean
      readOnly: true
      description: Indique si c'est un rôle par défaut (créé automatiquement)
      example: false
    
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de création
      example: "2025-03-01T10:00:00Z"
    
    updated_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de dernière modification
      example: "2025-03-15T14:30:00Z"
```

---

### ProjectRoleCreate

```yaml
ProjectRoleCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      maxLength: 50
      description: Nom du rôle
      example: "Chef de chantier"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description du rôle
      example: "Responsable de la supervision du chantier"

# Notes:
# - project_id est extrait du path parameter
# - is_default est défini automatiquement à false
```

---

### ProjectRoleUpdate

```yaml
ProjectRoleUpdate:
  type: object
  properties:
    name:
      type: string
      maxLength: 50
      description: Nom du rôle
      example: "Chef de chantier senior"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description du rôle
      example: "Description mise à jour"

# Note: Les rôles par défaut (is_default=true) ne peuvent pas être modifiés
```

---

## Schémas Policy

### ProjectPolicy (Complet)

```yaml
ProjectPolicy:
  type: object
  required:
    - id
    - project_id
    - name
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique de la politique
      example: "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    name:
      type: string
      maxLength: 100
      description: Nom de la politique
      example: "Gestion des fichiers techniques"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description de la politique
      example: "Autorise la lecture, écriture et validation des fichiers techniques du projet"
    
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de création
      example: "2025-03-01T10:00:00Z"
    
    updated_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de dernière modification
      example: "2025-03-15T14:30:00Z"
```

---

### ProjectPolicyCreate

```yaml
ProjectPolicyCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom de la politique
      example: "Gestion des fichiers techniques"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description de la politique
      example: "Autorise la lecture, écriture et validation des fichiers"

# Note: project_id est extrait du path parameter
```

---

### ProjectPolicyUpdate

```yaml
ProjectPolicyUpdate:
  type: object
  properties:
    name:
      type: string
      maxLength: 100
      description: Nom de la politique
      example: "Gestion fichiers (mise à jour)"
    
    description:
      type: string
      maxLength: 255
      nullable: true
      description: Description de la politique
      example: "Description mise à jour"
```

---

## Schémas Permission

### ProjectPermission (Read-only)

```yaml
ProjectPermission:
  type: object
  required:
    - id
    - name
    - category
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique de la permission
      example: "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d"
    
    name:
      type: string
      maxLength: 50
      description: Nom de la permission
      example: "read_files"
    
    description:
      type: string
      maxLength: 255
      description: Description de la permission
      example: "Permet de lire et télécharger les fichiers du projet"
    
    category:
      type: string
      enum:
        - files
        - project
        - members
        - rbac
      description: Catégorie de la permission
      example: "files"

# Note: Les permissions sont prédéfinies et en lecture seule
# Liste complète des permissions:
# 
# Catégorie 'files':
# - read_files: Lire/télécharger fichiers
# - write_files: Créer/modifier fichiers
# - delete_files: Supprimer fichiers
# - lock_files: Verrouiller/déverrouiller fichiers
# - validate_files: Approuver/rejeter versions
#
# Catégorie 'project':
# - update_project: Modifier les informations du projet
# - delete_project: Supprimer le projet
#
# Catégorie 'members':
# - manage_members: Gérer les membres du projet
#
# Catégorie 'rbac':
# - manage_roles: Créer/modifier les rôles projet
# - manage_policies: Créer/modifier les politiques projet
```

---

## Schémas Associations

### MilestoneDeliverableAssociation

```yaml
MilestoneDeliverableAssociation:
  type: object
  required:
    - deliverable_id
  properties:
    deliverable_id:
      type: string
      format: uuid
      description: Identifiant du livrable à associer au jalon
      example: "c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f"

# Note: milestone_id est extrait du path parameter
```

---

### RolePolicyAssociation

```yaml
RolePolicyAssociation:
  type: object
  required:
    - policy_id
  properties:
    policy_id:
      type: string
      format: uuid
      description: Identifiant de la politique à associer au rôle
      example: "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c"

# Note: role_id est extrait du path parameter
# Alternative: envoyer dans le body pour POST /roles/{role_id}/policies
```

---

### PolicyPermissionAssociation

```yaml
PolicyPermissionAssociation:
  type: object
  required:
    - permission_id
  properties:
    permission_id:
      type: string
      format: uuid
      description: Identifiant de la permission à associer à la politique
      example: "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d"

# Note: policy_id est extrait du path parameter
```

---

## Schémas Contrôle d'accès

### CheckFileAccessRequest

```yaml
CheckFileAccessRequest:
  type: object
  required:
    - project_id
    - action
  properties:
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet contenant le fichier
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    action:
      type: string
      enum:
        - read
        - write
        - delete
        - lock
        - validate
      description: Action à effectuer sur le fichier
      example: "write"
    
    file_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant du fichier (optionnel, pour audit)
      example: "b9c0d1e2-f3a4-4b5c-6d7e-8f9a0b1c2d3e"

# Note: user_id est extrait du JWT automatiquement (g.user_id)
```

---

### CheckFileAccessResponse

```yaml
CheckFileAccessResponse:
  type: object
  required:
    - allowed
  properties:
    allowed:
      type: boolean
      description: Indique si l'accès est autorisé
      example: true
    
    role:
      type: string
      nullable: true
      description: Rôle de l'utilisateur dans le projet (si membre)
      example: "contributor"
    
    reason:
      type: string
      nullable: true
      description: Raison de l'autorisation ou du refus
      example: "User has permission write_files"

# Exemples de réponses:
# 
# Accès autorisé:
# {
#   "allowed": true,
#   "role": "contributor",
#   "reason": "User has permission write_files"
# }
#
# Accès refusé - pas membre:
# {
#   "allowed": false,
#   "reason": "User is not a member of this project"
# }
#
# Accès refusé - permission manquante:
# {
#   "allowed": false,
#   "role": "viewer",
#   "reason": "User does not have permission write_files"
# }
```

---

### CheckFileAccessBatchRequest

```yaml
CheckFileAccessBatchRequest:
  type: object
  required:
    - checks
  properties:
    checks:
      type: array
      description: Liste des vérifications à effectuer
      items:
        type: object
        required:
          - project_id
          - action
        properties:
          project_id:
            type: string
            format: uuid
            description: Identifiant du projet
          action:
            type: string
            enum: [read, write, delete, lock, validate]
            description: Action à vérifier
          file_id:
            type: string
            format: uuid
            nullable: true
            description: Identifiant du fichier (optionnel)
      example:
        - project_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
          action: "read"
          file_id: "file-uuid-1"
        - project_id: "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e"
          action: "write"
          file_id: "file-uuid-2"
```

---

### CheckFileAccessBatchResponse

```yaml
CheckFileAccessBatchResponse:
  type: object
  required:
    - results
  properties:
    results:
      type: array
      description: Résultats des vérifications
      items:
        type: object
        properties:
          project_id:
            type: string
            format: uuid
          action:
            type: string
          allowed:
            type: boolean
          role:
            type: string
            nullable: true
          reason:
            type: string
            nullable: true
      example:
        - project_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
          action: "read"
          allowed: true
          role: "viewer"
        - project_id: "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e"
          action: "write"
          allowed: false
          reason: "User is not a member of this project"
```

---

### CheckProjectAccessRequest

```yaml
CheckProjectAccessRequest:
  type: object
  required:
    - project_id
    - action
  properties:
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    action:
      type: string
      enum:
        - read
        - write
        - manage
      description: Action à effectuer sur le projet
      example: "read"

# Mapping action → vérification:
# - read: User doit être membre du projet (n'importe quel rôle)
# - write: User doit avoir la permission 'update_project'
# - manage: User doit avoir 'manage_members' ou 'manage_roles' ou 'manage_policies'
```

---

### CheckProjectAccessResponse

```yaml
CheckProjectAccessResponse:
  type: object
  required:
    - allowed
  properties:
    allowed:
      type: boolean
      description: Indique si l'accès est autorisé
      example: true
    
    role:
      type: string
      nullable: true
      description: Rôle de l'utilisateur dans le projet
      example: "admin"
    
    project_status:
      type: string
      nullable: true
      description: Statut actuel du projet
      example: "active"
    
    reason:
      type: string
      nullable: true
      description: Raison de l'autorisation ou du refus
      example: "User is a member with read access"
```

---

### CheckProjectAccessBatchRequest

```yaml
CheckProjectAccessBatchRequest:
  type: object
  required:
    - checks
  properties:
    checks:
      type: array
      description: Liste des vérifications à effectuer
      items:
        type: object
        required:
          - project_id
          - action
        properties:
          project_id:
            type: string
            format: uuid
          action:
            type: string
            enum: [read, write, manage]
      example:
        - project_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
          action: "read"
        - project_id: "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e"
          action: "write"
```

---

### CheckProjectAccessBatchResponse

```yaml
CheckProjectAccessBatchResponse:
  type: object
  required:
    - results
  properties:
    results:
      type: array
      description: Résultats des vérifications
      items:
        type: object
        properties:
          project_id:
            type: string
            format: uuid
          action:
            type: string
          allowed:
            type: boolean
          role:
            type: string
            nullable: true
          project_status:
            type: string
            nullable: true
          reason:
            type: string
            nullable: true
      example:
        - project_id: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
          action: "read"
          allowed: true
          role: "contributor"
          project_status: "active"
        - project_id: "b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e"
          action: "write"
          allowed: false
          reason: "Insufficient permissions"
```

---

## Schémas Réponses communes

### ErrorResponse

```yaml
ErrorResponse:
  type: object
  required:
    - message
  properties:
    message:
      type: string
      description: Message d'erreur principal
      example: "Invalid input data"
    
    errors:
      type: object
      nullable: true
      description: Détails des erreurs de validation
      additionalProperties: true
      example:
        name: "Name is required"
        due_date: "Invalid date format"

# Utilisé pour les codes 400, 404, 409, 500, etc.
```

---

### SuccessResponse

```yaml
SuccessResponse:
  type: object
  required:
    - message
  properties:
    message:
      type: string
      description: Message de confirmation
      example: "Project archived successfully"

# Utilisé pour les opérations qui ne retournent pas de données (archive, restore, delete)
```

---

### HealthResponse

```yaml
HealthResponse:
  type: object
  required:
    - status
    - service
  properties:
    status:
      type: string
      enum:
        - healthy
        - unhealthy
      description: Statut de santé du service
      example: "healthy"
    
    service:
      type: string
      description: Nom du service
      example: "project_service"
    
    timestamp:
      type: string
      format: date-time
      description: Horodatage de la vérification
      example: "2025-11-11T12:00:00Z"
    
    version:
      type: string
      description: Version du service
      example: "0.0.1"
    
    environment:
      type: string
      enum:
        - development
        - testing
        - staging
        - production
      description: Environnement d'exécution
      example: "development"
    
    checks:
      type: object
      description: Résultats des vérifications de santé
      properties:
        database:
          type: object
          properties:
            healthy:
              type: boolean
              example: true
            message:
              type: string
              example: "Database connection successful"
            response_time_ms:
              type: number
              format: float
              example: 5.2
```

---

### VersionResponse

```yaml
VersionResponse:
  type: object
  required:
    - version
  properties:
    version:
      type: string
      description: Numéro de version de l'API
      example: "0.0.1"
```

---

### ConfigResponse

```yaml
ConfigResponse:
  type: object
  properties:
    env:
      type: string
      enum:
        - development
        - testing
        - staging
        - production
      description: Environnement actuel
      example: "development"
    
    debug:
      type: boolean
      description: Mode debug activé
      example: true
    
    database_url:
      type: string
      description: URL de connexion à la base (info sensible masquée)
      example: "postgresql://***:***@localhost:5432/project_db"
```

---

### ProjectHistory

```yaml
ProjectHistory:
  type: object
  required:
    - id
    - project_id
    - user_id
    - action
    - entity_type
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
      description: Identifiant unique de l'entrée d'historique
      example: "h1i2j3k4-l5m6-4n7o-8p9q-0r1s2t3u4v5w"
    
    project_id:
      type: string
      format: uuid
      description: Identifiant du projet
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    user_id:
      type: string
      format: uuid
      description: User ayant effectué le changement
      example: "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"
    
    action:
      type: string
      maxLength: 50
      description: Type d'action effectuée
      example: "status_changed"
    
    entity_type:
      type: string
      maxLength: 50
      description: Type d'entité modifiée
      example: "project"
    
    entity_id:
      type: string
      format: uuid
      nullable: true
      description: Identifiant de l'entité modifiée
      example: "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    
    changes:
      type: object
      description: Détails des changements effectués (format JSON)
      additionalProperties: true
      example:
        old_status: "consultation"
        new_status: "active"
        notification_date: "2025-03-01"
    
    created_at:
      type: string
      format: date-time
      readOnly: true
      description: Date de l'événement
      example: "2025-03-01T14:30:00Z"

# Types d'actions courantes:
# - project_created
# - status_changed
# - member_added
# - member_removed
# - role_changed
# - milestone_created
# - deliverable_created
# - etc.
```

---

**Dernière mise à jour** : 2025-11-11  
**Auteur** : bengeek06
