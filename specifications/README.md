# Spécifications du Project Service API

Ce répertoire contient les spécifications détaillées de l'API du **Project Service** de la plateforme Waterfall.

## Structure des spécifications

Les spécifications ont été développées selon une méthodologie en 4 étapes, chaque étape correspondant à un fichier dédié :

### 1. [ENDPOINTS_SPECIFICATION.md](./ENDPOINTS_SPECIFICATION.md)
**Étape 1 : Définition des endpoints**

Catalogue complet de tous les endpoints de l'API :
- 40+ endpoints organisés en 13 catégories
- Endpoints système (/health, /version, /config)
- Gestion du cycle de vie des projets
- Gestion des membres, jalons et livrables
- Système RBAC (Rôles, Politiques, Permissions)
- Endpoints de contrôle d'accès pour intégration avec Storage et Task services
- Structure WBS pour le Task Service

### 2. [SCHEMAS_SPECIFICATION.md](./SCHEMAS_SPECIFICATION.md)
**Étape 2 : Définition des schémas de données**

Schémas de données détaillés au format OpenAPI YAML :
- **Projets** : 30+ champs couvrant le cycle de vie complet
- **Milestones & Deliverables** : États, types, associations
- **Membres** : Liaison utilisateurs-projets avec rôles
- **RBAC** : Rôles, Politiques, Permissions avec flags is_default
- **Contrôle d'accès** : Schémas de requête/réponse pour Storage/Task
- **Historique** : Traçabilité des modifications
- Règles de validation, énumérations, exemples

### 3. [RESPONSES_SPECIFICATION.md](./RESPONSES_SPECIFICATION.md)
**Étape 3 : Définition des réponses HTTP**

Codes de statut et formats de réponse pour chaque endpoint :
- Codes de succès (200, 201, 204)
- Codes d'erreur client (400, 401, 403, 404, 409)
- Codes d'erreur serveur (500, 502, 503, 504)
- Exemples JSON pour chaque scénario
- Cas d'erreur spécifiques (validation, permissions, contraintes)
- Tableau récapitulatif par catégorie d'endpoint

### 4. ../openapi.yml
**Étape 4 : Spécification OpenAPI complète**

Fichier OpenAPI 3.0.3 complet intégrant :
- Toutes les spécifications des étapes 1-3
- Schémas dans `components/schemas`
- Réponses réutilisables dans `components/responses`
- Endpoints dans `paths`
- Tags et descriptions

## Architecture de l'API

### Cycle de vie des projets

```
created → initialized → consultation → [active | lost]
                                          ↓
                                      suspended ↔ completed → archived
```

### Système RBAC à deux niveaux

1. **Guardian (niveau endpoint)** : Contrôle qui peut appeler quels endpoints
2. **Project Service (niveau contexte)** : Contrôle qui peut accéder à quelles ressources

### Rôles par défaut

- `owner` : Créateur du projet, tous les droits
- `validator` : Peut valider les fichiers et livrables
- `contributor` : Peut lire et écrire les fichiers
- `viewer` : Lecture seule

### Permissions prédéfinies

**Fichiers** :
- `read_files` : Lire et télécharger
- `write_files` : Créer et modifier
- `delete_files` : Supprimer
- `lock_files` : Verrouiller/déverrouiller
- `validate_files` : Approuver/rejeter

**Projet** :
- `update_project` : Modifier les informations
- `delete_project` : Supprimer le projet

**Membres** :
- `manage_members` : Gérer les membres

**RBAC** :
- `manage_roles` : Gérer les rôles
- `manage_policies` : Gérer les politiques

## Intégration avec l'écosystème Waterfall

### Services appelants
- **Storage Service** : Appelle `/check-file-access` pour validation des permissions fichiers
- **Task Service** : Appelle `/projects/{id}/wbs-structure` pour générer la WBS

### Services référencés
- **Identity Service** : Utilisateurs et clients
- **Guardian Service** : RBAC niveau endpoint
- **Auth Service** : Authentification JWT

## Multi-tenancy

Toutes les ressources sont isolées par `company_id` extrait automatiquement du token JWT.

## Suivi des dates

### Phase consultation
- `consultation_date` : Début consultation
- `submission_deadline` : Date limite proposition
- `notification_date` : Notification décision (gagné/perdu)

### Phase exécution
- `contract_start_date` : Début contractuel
- `planned_start_date` : Début planifié
- `actual_start_date` : Début réel

### Phase livraison
- `contract_delivery_date` : Livraison contractuelle
- `planned_delivery_date` : Livraison planifiée
- `actual_delivery_date` : Livraison réelle

---

**Version** : 0.0.1  
**Date de création** : 2025-11-11  
**Auteurs** : bengeek06  
**Licence** : AGPL v3 / Commercial
