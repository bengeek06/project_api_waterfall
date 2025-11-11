# Spécification des Endpoints - Project Service API

**Version**: 0.0.1  
**Date**: 2025-11-11  

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Modèles de données](#modèles-de-données)
4. [Endpoints système](#endpoints-système)
5. [Endpoints projets](#endpoints-projets)
6. [Endpoints membres](#endpoints-membres)
7. [Endpoints milestones](#endpoints-milestones)
8. [Endpoints deliverables](#endpoints-deliverables)
9. [Endpoints rôles projet](#endpoints-rôles-projet)
10. [Endpoints politiques projet](#endpoints-politiques-projet)
11. [Endpoints permissions projet](#endpoints-permissions-projet)
12. [Endpoints associations](#endpoints-associations)
13. [Endpoints contrôle d'accès](#endpoints-contrôle-daccès)

---

## Vue d'ensemble

Le **Project Service** gère le cycle de vie complet des projets de la consultation à la livraison finale, incluant :

- **Gestion des projets** : CRUD, statuts, dates contractuelles, métadonnées
- **Gestion des membres** : Association users avec rôles projet
- **Gestion des jalons (milestones)** : Points clés du projet
- **Gestion des livrables (deliverables)** : Produits/services à livrer
- **Système RBAC projet** : Rôles, politiques, permissions au niveau projet
- **Contrôle d'accès** : Vérification des permissions pour Storage et autres services
- **Historique** : Traçabilité complète des changements

---

## Architecture

### Intégration avec les autres services Waterfall

```
┌─────────────────────────────────────────────────────────┐
│                    Client (JWT Cookie)                   │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │  Auth   │   │ Guardian │   │ Identity │
    │ Service │   │ Service  │   │ Service  │
    └─────────┘   └──────────┘   └──────────┘
         │               │               │
         │ JWT           │ RBAC          │ Users/Companies/Customers
         │               │ (endpoints)   │
         └───────────────┼───────────────┘
                         ▼
                ┌─────────────────┐
                │     PROJECT     │◄────────┐
                │     SERVICE     │         │
                └────────┬────────┘         │
                         │                  │
         ┌───────────────┼──────────────────┼────────┐
         ▼               ▼                  ▼        ▼
    ┌─────────┐   ┌──────────┐      ┌──────────┐  ┌──────────┐
    │ Storage │   │   Task   │      │ Systems  │  │Requirements│
    │ Service │   │ Service  │      │ Service  │  │  Service   │
    └─────────┘   └──────────┘      └──────────┘  └──────────┘
         │               │                  │            │
         │ check-file-   │ WBS generation   │ PBS       │ Traçabilité
         │ access        │ (milestones/     │ reference │ exigences
         │               │  deliverables)   │           │
```

### Responsabilités

**Project Service** :
- Données contractuelles du projet
- Milestones et deliverables
- Membres et leurs rôles projet
- RBAC contextualisé (permissions par projet)
- Contrôle d'accès pour fichiers projet

**Task Service** (futur) :
- WBS (Work Breakdown Structure)
- Chiffrage et budget détaillé
- Pointages et suivi charges

**Systems Service** (futur) :
- PBS (Product Breakdown Structure)

**Requirements Service** (futur) :
- Gestion des exigences

---

## Modèles de données

### Project

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `name` | String(100) | Nom du projet | Oui |
| `description` | String(500) | Description du projet | Non |
| `company_id` | UUID | Entreprise propriétaire (multi-tenant) | Oui |
| `customer_id` | UUID | Client (référence Identity Service) | Non |
| `created_by` | UUID | User créateur (devient owner) | Auto |
| `status` | Enum | Statut du projet | Oui |
| `consultation_date` | Date | Date publication consultation | Non |
| `submission_deadline` | Date | Date limite soumission offre | Non |
| `notification_date` | Date | Date notification résultat | Non |
| `contract_start_date` | Date | Date démarrage contractuel | Non |
| `planned_start_date` | Date | Date démarrage prévue | Non |
| `actual_start_date` | Date | Date démarrage réel | Non |
| `contract_delivery_date` | Date | Date livraison contractuelle | Non |
| `planned_delivery_date` | Date | Date livraison prévue | Non |
| `actual_delivery_date` | Date | Date livraison réelle | Non |
| `contract_amount` | Decimal | Montant contractuel | Non |
| `budget_currency` | String(3) | Devise (EUR, USD, etc.) | Non |
| `suspended_at` | DateTime | Date de suspension | Non |
| `completed_at` | DateTime | Date de complétion | Non |
| `archived_at` | DateTime | Date d'archivage | Non |
| `created_at` | DateTime | Date de création | Auto |
| `updated_at` | DateTime | Date de dernière MAJ | Auto |

**Statuts possibles** :
- `created` - Projet créé
- `initialized` - Projet initialisé et prêt
- `consultation` - En phase consultation/appel d'offres
- `lost` - Consultation perdue
- `active` - Projet actif (consultation gagnée)
- `suspended` - Projet en pause
- `completed` - Projet terminé
- `archived` - Projet archivé

**Transitions de statut** :
```
created → initialized → consultation → active → [suspended ↔] → completed → archived
                                    ↘ lost → archived
```

### Milestone (Jalon)

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `project_id` | UUID | Projet parent | Oui |
| `name` | String(100) | Nom du jalon | Oui |
| `description` | String(500) | Description | Non |
| `due_date` | Date | Date d'échéance | Non |
| `status` | Enum | Statut (planned, in_progress, completed, cancelled) | Oui |
| `order` | Integer | Ordre d'affichage | Non |
| `created_at` | DateTime | Date de création | Auto |
| `updated_at` | DateTime | Date de dernière MAJ | Auto |

### Deliverable (Livrable)

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `project_id` | UUID | Projet parent | Oui |
| `name` | String(100) | Nom du livrable | Oui |
| `description` | String(500) | Description | Non |
| `type` | Enum | Type (document, software, hardware, service, other) | Non |
| `due_date` | Date | Date d'échéance | Non |
| `status` | Enum | Statut (planned, in_progress, completed, delivered, accepted) | Oui |
| `order` | Integer | Ordre d'affichage | Non |
| `created_at` | DateTime | Date de création | Auto |
| `updated_at` | DateTime | Date de dernière MAJ | Auto |

### ProjectMember (Membre du projet)

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `project_id` | UUID | Projet | Oui |
| `user_id` | UUID | User (référence Identity Service) | Oui |
| `role_id` | UUID | Rôle projet assigné | Oui |
| `added_by` | UUID | User qui a ajouté ce membre | Auto |
| `added_at` | DateTime | Date d'ajout | Auto |
| `removed_at` | DateTime | Date de retrait (null si actif) | Non |

### ProjectRole (Rôle projet)

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `project_id` | UUID | Projet | Oui |
| `name` | String(50) | Nom du rôle | Oui |
| `description` | String(255) | Description | Non |
| `is_default` | Boolean | Rôle par défaut (créé auto) | Auto |
| `created_at` | DateTime | Date de création | Auto |
| `updated_at` | DateTime | Date de dernière MAJ | Auto |

**Rôles par défaut** (créés automatiquement à l'initialisation du projet) :
- `owner` - Créateur du projet, tous les droits
- `validator` - Peut valider/approuver les fichiers
- `contributor` - Peut lire/écrire des fichiers
- `viewer` - Lecture seule

### ProjectPolicy (Politique projet)

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `id` | UUID | Identifiant unique | Auto |
| `project_id` | UUID | Projet | Oui |
| `name` | String(100) | Nom de la politique | Oui |
| `description` | String(255) | Description | Non |
| `created_at` | DateTime | Date de création | Auto |
| `updated_at` | DateTime | Date de dernière MAJ | Auto |

### ProjectPermission (Permission projet)

**Permissions prédéfinies** (read-only, gérées par le service) :

| Nom | Description | Actions Storage |
|-----|-------------|----------------|
| `read_files` | Lire/télécharger fichiers | read |
| `write_files` | Créer/modifier fichiers | write |
| `delete_files` | Supprimer fichiers | delete |
| `lock_files` | Verrouiller/déverrouiller | lock |
| `validate_files` | Approuver/rejeter versions | validate |
| `manage_members` | Gérer membres projet | - |
| `manage_roles` | Gérer rôles projet | - |
| `manage_policies` | Gérer politiques projet | - |
| `update_project` | Modifier projet | - |
| `delete_project` | Supprimer projet | - |

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique |
| `name` | String(50) | Nom de la permission |
| `description` | String(255) | Description |
| `category` | Enum | Catégorie (files, project, members, rbac) |

### MilestoneDeliverable (Association)

| Champ | Type | Description |
|-------|------|-------------|
| `milestone_id` | UUID | Jalon |
| `deliverable_id` | UUID | Livrable |
| `created_at` | DateTime | Date d'association |

### RolePolicy (Association)

| Champ | Type | Description |
|-------|------|-------------|
| `role_id` | UUID | Rôle projet |
| `policy_id` | UUID | Politique projet |
| `created_at` | DateTime | Date d'association |

### PolicyPermission (Association)

| Champ | Type | Description |
|-------|------|-------------|
| `policy_id` | UUID | Politique projet |
| `permission_id` | UUID | Permission |
| `created_at` | DateTime | Date d'association |

### ProjectHistory (Historique)

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique |
| `project_id` | UUID | Projet |
| `user_id` | UUID | User ayant effectué le changement |
| `action` | String(50) | Type d'action |
| `entity_type` | String(50) | Type d'entité modifiée |
| `entity_id` | UUID | ID de l'entité modifiée |
| `changes` | JSON | Détails des changements |
| `created_at` | DateTime | Date du changement |

---

## Endpoints système

### GET /health

**Description** : Vérification de santé du service

**Authentification** : Non requise

**Réponse** : Statut du service et connectivité DB

---

### GET /version

**Description** : Version de l'API

**Authentification** : Requise (JWT)

**Réponse** : Numéro de version

---

### GET /config

**Description** : Configuration de l'application

**Authentification** : Requise (JWT)

**Réponse** : Configuration actuelle (données non sensibles)

---

## Endpoints projets

### GET /projects

**Description** : Liste tous les projets de la company de l'utilisateur authentifié

**Authentification** : Requise (JWT)

**Query Parameters** :
- `status` (optional) : Filtrer par statut
- `page` (optional, default: 1) : Numéro de page
- `limit` (optional, default: 50) : Nombre de résultats par page

**Réponse** : Liste de projets

---

### POST /projects

**Description** : Créer un nouveau projet

**Authentification** : Requise (JWT)

**Body** : Données du projet (ProjectCreate schema)

**Logique** :
1. Créer le projet avec status = `created`
2. Définir `created_by` = user_id du JWT
3. Créer automatiquement le membre owner (user_id, role = owner)

**Réponse** : Projet créé

---

### GET /projects/{project_id}

**Description** : Obtenir les détails d'un projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Réponse** : Détails complets du projet

---

### PUT /projects/{project_id}

**Description** : Remplacer complètement un projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** : Toutes les données du projet (ProjectUpdate schema)

**Réponse** : Projet mis à jour

---

### PATCH /projects/{project_id}

**Description** : Mise à jour partielle d'un projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** : Champs à modifier (ProjectUpdate schema, tous optionnels)

**Logique** :
- Si changement de status : créer une entrée d'historique
- Si modification de dates : créer une entrée d'historique

**Réponse** : Projet mis à jour

---

### DELETE /projects/{project_id}

**Description** : Supprimer un projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Logique** : Suppression en cascade (members, milestones, deliverables, roles, etc.)

**Réponse** : Message de confirmation

---

### GET /projects/{project_id}/metadata

**Description** : Obtenir les métadonnées minimales du projet (pour autres services)

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Réponse** : Métadonnées (id, name, status, company_id, customer_id)

---

### POST /projects/{project_id}/archive

**Description** : Archiver un projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Logique** :
- Changer status → `archived`
- Définir `archived_at` = now
- Créer entrée historique

**Réponse** : Projet archivé

---

### POST /projects/{project_id}/restore

**Description** : Restaurer un projet archivé

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Logique** :
- Changer status → statut précédent ou `active`
- Vider `archived_at`
- Créer entrée historique

**Réponse** : Projet restauré

---

### GET /projects/{project_id}/history

**Description** : Obtenir l'historique complet des changements du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Query Parameters** :
- `entity_type` (optional) : Filtrer par type d'entité
- `page` (optional, default: 1)
- `limit` (optional, default: 50)

**Réponse** : Liste des événements historiques

---

### GET /projects/{project_id}/wbs-structure

**Description** : Obtenir la structure complète pour génération WBS (utilisé par Task Service)

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Réponse** : JSON avec milestones, deliverables, associations, métadonnées projet

**Format de réponse** :
```json
{
  "project": {
    "id": "uuid",
    "name": "Project Name",
    "status": "active"
  },
  "milestones": [
    {
      "id": "uuid",
      "name": "Milestone 1",
      "due_date": "2025-12-31",
      "order": 1
    }
  ],
  "deliverables": [
    {
      "id": "uuid",
      "name": "Deliverable 1",
      "type": "document",
      "due_date": "2025-12-31",
      "order": 1
    }
  ],
  "associations": [
    {
      "milestone_id": "uuid",
      "deliverable_id": "uuid"
    }
  ]
}
```

---

## Endpoints membres

### GET /projects/{project_id}/members

**Description** : Liste tous les membres du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Query Parameters** :
- `include_removed` (optional, default: false) : Inclure membres retirés

**Réponse** : Liste des membres avec leurs rôles

---

### POST /projects/{project_id}/members

**Description** : Ajouter un membre au projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** :
```json
{
  "user_id": "uuid",
  "role_id": "uuid"
}
```

**Logique** :
- Vérifier que user_id existe dans Identity Service
- Définir `added_by` = user_id du JWT
- Créer le membre

**Réponse** : Membre créé

---

### GET /projects/{project_id}/members/{user_id}

**Description** : Obtenir les détails d'un membre

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `user_id` (UUID) : ID du user

**Réponse** : Détails du membre

---

### PUT /projects/{project_id}/members/{user_id}

**Description** : Remplacer complètement un membre (changer son rôle)

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `user_id` (UUID) : ID du user

**Body** :
```json
{
  "role_id": "uuid"
}
```

**Réponse** : Membre mis à jour

---

### PATCH /projects/{project_id}/members/{user_id}

**Description** : Mise à jour partielle d'un membre

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `user_id` (UUID) : ID du user

**Body** :
```json
{
  "role_id": "uuid"  // optionnel
}
```

**Réponse** : Membre mis à jour

---

### DELETE /projects/{project_id}/members/{user_id}

**Description** : Retirer un membre du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `user_id` (UUID) : ID du user

**Logique** :
- Définir `removed_at` = now (soft delete)
- Créer entrée historique

**Réponse** : Message de confirmation

---

## Endpoints milestones

### GET /projects/{project_id}/milestones

**Description** : Liste tous les jalons du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Query Parameters** :
- `status` (optional) : Filtrer par statut

**Réponse** : Liste des milestones

---

### POST /projects/{project_id}/milestones

**Description** : Créer un nouveau jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** : Données du milestone (MilestoneCreate schema)

**Réponse** : Milestone créé

---

### GET /projects/{project_id}/milestones/{milestone_id}

**Description** : Obtenir les détails d'un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Réponse** : Détails du milestone

---

### PUT /projects/{project_id}/milestones/{milestone_id}

**Description** : Remplacer complètement un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Body** : Toutes les données du milestone

**Réponse** : Milestone mis à jour

---

### PATCH /projects/{project_id}/milestones/{milestone_id}

**Description** : Mise à jour partielle d'un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Body** : Champs à modifier

**Réponse** : Milestone mis à jour

---

### DELETE /projects/{project_id}/milestones/{milestone_id}

**Description** : Supprimer un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Logique** : Supprime aussi les associations milestone-deliverable

**Réponse** : Message de confirmation

---

### GET /projects/{project_id}/milestones/{milestone_id}/deliverables

**Description** : Liste les livrables associés à un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Réponse** : Liste des deliverables associés

---

### POST /projects/{project_id}/milestones/{milestone_id}/deliverables

**Description** : Associer un livrable existant à un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone

**Body** :
```json
{
  "deliverable_id": "uuid"
}
```

**Réponse** : Association créée

---

### GET /projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}

**Description** : Vérifier si un livrable est associé à un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone
- `deliverable_id` (UUID) : ID du deliverable

**Réponse** : Détails de l'association ou 404

---

### DELETE /projects/{project_id}/milestones/{milestone_id}/deliverables/{deliverable_id}

**Description** : Retirer l'association entre un livrable et un jalon

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `milestone_id` (UUID) : ID du milestone
- `deliverable_id` (UUID) : ID du deliverable

**Réponse** : Message de confirmation

---

## Endpoints deliverables

### GET /projects/{project_id}/deliverables

**Description** : Liste tous les livrables du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Query Parameters** :
- `status` (optional) : Filtrer par statut
- `type` (optional) : Filtrer par type

**Réponse** : Liste des deliverables

---

### POST /projects/{project_id}/deliverables

**Description** : Créer un nouveau livrable

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** : Données du deliverable (DeliverableCreate schema)

**Réponse** : Deliverable créé

---

### GET /projects/{project_id}/deliverables/{deliverable_id}

**Description** : Obtenir les détails d'un livrable

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `deliverable_id` (UUID) : ID du deliverable

**Réponse** : Détails du deliverable

---

### PUT /projects/{project_id}/deliverables/{deliverable_id}

**Description** : Remplacer complètement un livrable

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `deliverable_id` (UUID) : ID du deliverable

**Body** : Toutes les données du deliverable

**Réponse** : Deliverable mis à jour

---

### PATCH /projects/{project_id}/deliverables/{deliverable_id}

**Description** : Mise à jour partielle d'un livrable

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `deliverable_id` (UUID) : ID du deliverable

**Body** : Champs à modifier

**Réponse** : Deliverable mis à jour

---

### DELETE /projects/{project_id}/deliverables/{deliverable_id}

**Description** : Supprimer un livrable

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `deliverable_id` (UUID) : ID du deliverable

**Logique** : Supprime aussi les associations milestone-deliverable

**Réponse** : Message de confirmation

---

## Endpoints rôles projet

### GET /projects/{project_id}/roles

**Description** : Liste tous les rôles du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Réponse** : Liste des rôles (incluant rôles par défaut)

---

### POST /projects/{project_id}/roles

**Description** : Créer un nouveau rôle personnalisé

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** :
```json
{
  "name": "Chef de chantier",
  "description": "Responsable du chantier"
}
```

**Réponse** : Rôle créé

---

### GET /projects/{project_id}/roles/{role_id}

**Description** : Obtenir les détails d'un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle

**Réponse** : Détails du rôle

---

### PUT /projects/{project_id}/roles/{role_id}

**Description** : Remplacer complètement un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle

**Body** : Toutes les données du rôle

**Logique** : Ne peut pas modifier les rôles par défaut (is_default = true)

**Réponse** : Rôle mis à jour

---

### PATCH /projects/{project_id}/roles/{role_id}

**Description** : Mise à jour partielle d'un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle

**Body** : Champs à modifier

**Logique** : Ne peut pas modifier les rôles par défaut

**Réponse** : Rôle mis à jour

---

### DELETE /projects/{project_id}/roles/{role_id}

**Description** : Supprimer un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle

**Logique** :
- Ne peut pas supprimer les rôles par défaut
- Ne peut pas supprimer si des membres l'utilisent

**Réponse** : Message de confirmation

---

## Endpoints politiques projet

### GET /projects/{project_id}/policies

**Description** : Liste toutes les politiques du projet

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Réponse** : Liste des politiques

---

### POST /projects/{project_id}/policies

**Description** : Créer une nouvelle politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Body** :
```json
{
  "name": "Politique gestion fichiers",
  "description": "Permet lecture/écriture fichiers"
}
```

**Réponse** : Politique créée

---

### GET /projects/{project_id}/policies/{policy_id}

**Description** : Obtenir les détails d'une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique

**Réponse** : Détails de la politique

---

### PUT /projects/{project_id}/policies/{policy_id}

**Description** : Remplacer complètement une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique

**Body** : Toutes les données de la politique

**Réponse** : Politique mise à jour

---

### PATCH /projects/{project_id}/policies/{policy_id}

**Description** : Mise à jour partielle d'une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique

**Body** : Champs à modifier

**Réponse** : Politique mise à jour

---

### DELETE /projects/{project_id}/policies/{policy_id}

**Description** : Supprimer une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique

**Logique** : Ne peut pas supprimer si des rôles l'utilisent

**Réponse** : Message de confirmation

---

## Endpoints permissions projet

### GET /projects/{project_id}/permissions

**Description** : Liste toutes les permissions disponibles (prédéfinies)

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet

**Query Parameters** :
- `category` (optional) : Filtrer par catégorie (files, project, members, rbac)

**Réponse** : Liste des permissions

**Note** : Les permissions sont en lecture seule, elles ne peuvent pas être créées/modifiées/supprimées par les utilisateurs.

---

## Endpoints associations

### GET /projects/{project_id}/roles/{role_id}/policies

**Description** : Liste toutes les politiques associées à un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle

**Réponse** : Liste des politiques

---

### GET /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**Description** : Vérifier si une politique est associée à un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle
- `policy_id` (UUID) : ID de la politique

**Réponse** : Détails de l'association ou 404

---

### POST /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**Description** : Associer une politique à un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle
- `policy_id` (UUID) : ID de la politique

**Réponse** : Association créée

---

### DELETE /projects/{project_id}/roles/{role_id}/policies/{policy_id}

**Description** : Retirer une politique d'un rôle

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `role_id` (UUID) : ID du rôle
- `policy_id` (UUID) : ID de la politique

**Réponse** : Message de confirmation

---

### GET /projects/{project_id}/policies/{policy_id}/permissions

**Description** : Liste toutes les permissions associées à une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique

**Réponse** : Liste des permissions

---

### GET /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**Description** : Vérifier si une permission est associée à une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique
- `permission_id` (UUID) : ID de la permission

**Réponse** : Détails de l'association ou 404

---

### POST /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**Description** : Associer une permission à une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique
- `permission_id` (UUID) : ID de la permission

**Réponse** : Association créée

---

### DELETE /projects/{project_id}/policies/{policy_id}/permissions/{permission_id}

**Description** : Retirer une permission d'une politique

**Authentification** : Requise (JWT)

**Path Parameters** :
- `project_id` (UUID) : ID du projet
- `policy_id` (UUID) : ID de la politique
- `permission_id` (UUID) : ID de la permission

**Réponse** : Message de confirmation

---

## Endpoints contrôle d'accès

### POST /check-file-access

**Description** : Vérifier si l'utilisateur authentifié peut effectuer une action sur un fichier du projet (appelé par Storage Service)

**Authentification** : Requise (JWT - user_id extrait du token)

**Body** :
```json
{
  "project_id": "uuid",
  "action": "read|write|delete|lock|validate",
  "file_id": "uuid"  // optionnel, pour audit
}
```

**Logique** :
1. Extraire `user_id` du JWT
2. Vérifier que le user est membre du projet
3. Récupérer le rôle du membre
4. Récupérer les politiques du rôle
5. Récupérer les permissions des politiques
6. Vérifier si la permission correspondante à `action` existe

**Mapping action → permission** :
- `read` → `read_files`
- `write` → `write_files`
- `delete` → `delete_files`
- `lock` → `lock_files`
- `validate` → `validate_files`

**Réponse** :
```json
{
  "allowed": true,
  "role": "contributor",
  "reason": "User has permission read_files"
}
```

ou

```json
{
  "allowed": false,
  "reason": "User is not a member of this project"
}
```

**Codes de retour** :
- `200` - Vérification effectuée (allowed peut être true ou false)
- `400` - Requête invalide
- `404` - Projet non trouvé
- `500` - Erreur serveur

---

### POST /check-file-access-batch

**Description** : Vérifier l'accès à plusieurs fichiers/projets en une seule requête (optimisation)

**Authentification** : Requise (JWT)

**Body** :
```json
{
  "checks": [
    {
      "project_id": "uuid-1",
      "action": "read",
      "file_id": "uuid-file-1"
    },
    {
      "project_id": "uuid-2",
      "action": "write",
      "file_id": "uuid-file-2"
    }
  ]
}
```

**Réponse** :
```json
{
  "results": [
    {
      "project_id": "uuid-1",
      "action": "read",
      "allowed": true,
      "role": "viewer"
    },
    {
      "project_id": "uuid-2",
      "action": "write",
      "allowed": false,
      "reason": "User is not a member"
    }
  ]
}
```

---

### POST /check-project-access

**Description** : Vérifier si l'utilisateur peut effectuer une action sur le projet lui-même (appelé par Task, Systems, Requirements Services)

**Authentification** : Requise (JWT)

**Body** :
```json
{
  "project_id": "uuid",
  "action": "read|write|manage"
}
```

**Mapping action → permission** :
- `read` → User doit être membre (n'importe quel rôle)
- `write` → `update_project` permission
- `manage` → `manage_members` ou `manage_roles` ou `manage_policies`

**Réponse** :
```json
{
  "allowed": true,
  "role": "admin",
  "project_status": "active"
}
```

**Codes de retour** :
- `200` - Vérification effectuée
- `400` - Requête invalide
- `404` - Projet non trouvé
- `500` - Erreur serveur

---

### POST /check-project-access-batch

**Description** : Vérifier l'accès à plusieurs projets en une seule requête

**Authentification** : Requise (JWT)

**Body** :
```json
{
  "checks": [
    {
      "project_id": "uuid-1",
      "action": "read"
    },
    {
      "project_id": "uuid-2",
      "action": "write"
    }
  ]
}
```

**Réponse** :
```json
{
  "results": [
    {
      "project_id": "uuid-1",
      "action": "read",
      "allowed": true,
      "project_status": "active"
    },
    {
      "project_id": "uuid-2",
      "action": "write",
      "allowed": false,
      "reason": "Insufficient permissions"
    }
  ]
}
```

**Dernière mise à jour** : 2025-11-11  
**Auteur** : bengeek06
