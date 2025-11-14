# TODO: Integration Tests for Project Service

> **Scope:** Tests d'intégration avec services externes **mockés**. Focus sur les workflows complets internes, RBAC, et validation de la cohérence du système.

---

## 🔄 Workflow Tests (Priorité Haute)

## 🔄 Workflow Tests (Priorité Haute)

### 1. Lifecycle Complet d'un Projet
**Workflow:**
```
POST /projects (owner créé automatiquement)
→ POST /projects/{id}/members (ajouter contributor)
→ POST /projects/{id}/milestones (créer jalons)
→ POST /projects/{id}/deliverables (créer livrables)
→ POST /milestones/{mid}/deliverables/{did} (associer via WBS)
→ GET /projects/{id}/wbs-structure (vérifier structure complète)
→ PATCH /projects/{id} (modifier statut → completed)
→ POST /projects/{id}/archive (archiver)
→ POST /projects/{id}/restore (restaurer)
→ GET /projects/{id}/history (vérifier audit trail complet)
```
- [ ] Créer projet avec JWT mocké (company_id, user_id)
- [ ] Vérifier création automatique des 4 roles par défaut (owner, validator, contributor, viewer)
- [ ] Vérifier que le créateur est automatiquement member avec role owner
- [ ] Ajouter 3 members avec des roles différents
- [ ] Créer 5 milestones avec dates différentes
- [ ] Créer 10 deliverables attachés à différents milestones
- [ ] Créer associations milestone-deliverable via `/milestones/{mid}/deliverables/{did}`
- [ ] Valider que WBS structure retourne la hiérarchie complète
- [ ] Modifier projet → status = "completed"
- [ ] Archiver projet (valider status="completed" requis)
- [ ] Tenter d'archiver projet "in-progress" → 400
- [ ] Restaurer projet archivé
- [ ] Vérifier ProjectHistory contient toutes les opérations

### 2. WBS Structure Building & Validation
**Workflow:**
```
Créer projet → Créer milestones M1, M2, M3
→ Créer deliverables D1, D2, D3, D4
→ Associer: M1→[D1,D2], M2→[D3], M3→[D4]
→ GET /projects/{id}/wbs-structure
→ Vérifier structure JSON retournée
```
- [ ] Créer projet avec 3 milestones
- [ ] Créer 4 deliverables (2 pour M1, 1 pour M2, 1 pour M3)
- [ ] Créer associations via POST `/milestones/{mid}/deliverables/{did}`
- [ ] GET `/projects/{id}/wbs-structure` et valider:
  - Structure JSON correcte
  - Tous les milestones présents
  - Tous les deliverables présents
  - Associations correctement mappées
  - Champs attendus pour Task Service (id, name, dates, etc.)
- [ ] Soft delete d'un deliverable → WBS ne doit plus le contenir
- [ ] Restaurer deliverable → réapparaît dans WBS

### 3. Multi-Milestone Multi-Deliverable Management
**Workflow complexe:**
```
Projet avec 10 milestones, 30 deliverables
→ Associations croisées (certains deliverables sur plusieurs milestones)
→ Modifications en cascade
→ Soft deletes et restaurations
```
- [ ] Créer 10 milestones avec dates séquentielles
- [ ] Créer 30 deliverables
- [ ] Créer 50+ associations (certains deliverables liés à plusieurs milestones)
- [ ] Lister deliverables d'un milestone spécifique
- [ ] Lister milestones d'un deliverable spécifique
- [ ] Modifier date d'un milestone → vérifier cohérence
- [ ] Soft delete milestone → associations toujours en DB mais filtrées
- [ ] Supprimer association → DELETE `/milestones/{mid}/deliverables/{did}`
- [ ] Vérifier que suppression d'association ne supprime pas les entités

---

## 🔐 RBAC Internal Tests (Priorité Haute)
## 🔐 RBAC Internal Tests (Priorité Haute)

### 4. Permission Chain Validation (User → Member → Role → Policy → Permission)
**Workflow:**
```
1. Créer projet (user1 devient owner automatiquement)
2. Ajouter user2 comme contributor
3. user2 tente manage_project → 403
4. user1 modifie role de user2 → owner
5. user2 tente manage_project → 200 OK
6. user1 rétrograde user2 → viewer
7. user2 tente write_files → 403
8. user2 tente read_files → 200 OK
```
- [ ] Mock JWT avec user1 (company_id, user_id)
- [ ] POST /projects → user1 devient member avec role "owner" automatiquement
- [ ] Vérifier que user1 a permissions: manage_project, manage_members, manage_roles, read/write/validate_files
- [ ] Ajouter user2 avec role "contributor"
- [ ] Mock JWT avec user2
- [ ] user2 tente PUT /projects/{id} → 403 (manque manage_project)
- [ ] user2 tente POST /projects/{id}/milestones → 200 OK (a write_files)
- [ ] user1 (owner) modifie member user2 → role="owner"
- [ ] user2 tente PUT /projects/{id} → 200 OK (a manage_project maintenant)
- [ ] user1 modifie member user2 → role="viewer"
- [ ] user2 tente POST /projects/{id}/milestones → 403 (n'a plus write_files)
- [ ] user2 tente GET /projects/{id} → 200 OK (a read_files)

### 5. Custom Roles & Policies Creation
**Workflow:**
```
Créer custom role "project_manager"
→ Créer custom policy "pm_policy"
→ Associer permissions spécifiques
→ Assigner role à un member
→ Tester permissions effectives
```
- [ ] POST /projects/{id}/roles avec name="project_manager"
- [ ] POST /projects/{id}/policies avec name="pm_policy"
- [ ] Associer permissions: manage_project, read_files, write_files (pas validate_files ni manage_members)
- [ ] POST `/roles/{role_id}/policies/{policy_id}` (associer policy au role)
- [ ] Ajouter user3 comme member avec role "project_manager"
- [ ] user3 peut: GET /projects/{id} ✓, PUT /projects/{id} ✓, POST /milestones ✓
- [ ] user3 ne peut pas: POST /projects/{id}/members ✗ (pas manage_members)
- [ ] user3 ne peut pas: valider fichiers ✗ (pas validate_files)

### 6. Policy Reuse Across Roles
**Workflow:**
```
Créer policy "file_operations" (read_files, write_files)
→ Créer role "editor" avec cette policy
→ Créer role "reviewer" avec cette policy + validate_files
→ Tester que les 2 roles partagent la même policy
```
- [ ] POST /projects/{id}/policies name="file_operations"
- [ ] Associer permissions: read_files, write_files
- [ ] Créer role "editor" → associer policy "file_operations"
- [ ] Créer role "reviewer" → associer policy "file_operations" + autre policy pour validate
- [ ] Ajouter user4 avec role "editor"
- [ ] Ajouter user5 avec role "reviewer"
- [ ] Vérifier que user4 et user5 ont tous les 2 read/write_files
- [ ] user5 a en plus validate_files

### 7. Default Roles Protection
**Workflow:**
```
Tenter de supprimer role "owner" → 400
Tenter de supprimer role "viewer" → 400
Tenter de modifier role "owner" → possibilités limitées
Supprimer custom role → 200 OK
```
- [ ] DELETE /roles/{owner_role_id} → 400 {"error": "Cannot delete default role"}
- [ ] DELETE /roles/{viewer_role_id} → 400
- [ ] DELETE /roles/{custom_role_id} → 200 OK (si aucun member ne l'utilise)
- [ ] Créer custom role, assigner à un member
- [ ] Tenter DELETE custom role → 400 (role in use)
- [ ] Retirer member ou changer son role
- [ ] DELETE custom role → 200 OK

### 8. Policy In-Use Protection
**Workflow:**
```
Policy utilisée par un role → ne peut pas être supprimée
Retirer association → puis supprimer policy OK
```
- [ ] Créer policy "test_policy"
- [ ] Associer policy à role "contributor"
- [ ] DELETE /policies/{policy_id} → 400 {"error": "Policy is in use by X roles"}
- [ ] DELETE `/roles/{contributor_id}/policies/{policy_id}`
- [ ] DELETE /policies/{policy_id} → 200 OK

---

## 🔍 Access Control Endpoints (Priorité Moyenne)
## 🔍 Access Control Endpoints (Priorité Moyenne)

### 9. Check Project Access (Single & Batch)
**Workflow:**
```
Mock Guardian Service responses
→ Tester check-project-access pour différents users/roles
→ Tester batch operations avec 50+ projets
```
- [ ] Mock Guardian Service: `POST /check-access` retourne {"allowed": true}
- [ ] Créer 3 projets (P1, P2, P3) avec company_id="company-123"
- [ ] user1 est member de P1 (owner), P2 (contributor)
- [ ] user1 n'est pas member de P3
- [ ] POST `/check-project-access` project_id=P1, user_id=user1, action="manage_project"
  - → {"allowed": true, "role": "owner", "reason": "Has permission via role owner"}
- [ ] POST `/check-project-access` project_id=P2, user_id=user1, action="manage_project"
  - → {"allowed": false, "role": "contributor", "reason": "Missing permission manage_project"}
- [ ] POST `/check-project-access` project_id=P3, user_id=user1, action="read_files"
  - → {"allowed": false, "role": null, "reason": "User is not a member"}
- [ ] POST `/check-project-access-batch` avec checks=[P1, P2, P3]
  - Valider que les 3 réponses sont correctes
  - Valider performance < 200ms

### 10. Check File Access (Mock File Service)
**Workflow:**
```
Mock File Service metadata responses
→ Vérifier que permissions projet s'appliquent aux fichiers
```
- [ ] Mock File Service: `GET /files/{id}/metadata` retourne {project_id, ...}
- [ ] Créer projet P1, user1 est contributor (read/write_files)
- [ ] POST `/check-file-access` file_id=F1, user_id=user1, action="read_files"
  - Mock File Service dit F1 appartient à P1
  - → {"allowed": true, "role": "contributor"}
- [ ] POST `/check-file-access` file_id=F1, user_id=user1, action="validate_files"
  - → {"allowed": false, "reason": "Missing permission validate_files"}
- [ ] POST `/check-file-access-batch` avec 100 fichiers
  - Valider performance < 500ms
  - Vérifier que N+1 queries est évité (use eager loading)

---

## 🛡️ Multi-Tenant Isolation (Priorité Haute)

### 11. Company Isolation Tests
**Workflow:**
```
Company A crée projet
→ Company B tente d'accéder → 404 (pas 403, pas de leak d'info)
→ Vérifier que company_id du JWT est toujours utilisé
```
- [ ] Mock JWT avec company_id="company-A", user_id="user1"
- [ ] POST /projects → projet créé avec company_id="company-A"
- [ ] Mock JWT avec company_id="company-B", user_id="user2"
- [ ] GET /projects/{project_A_id} → 404 (projet n'existe pas pour company-B)
- [ ] GET /projects → liste vide (aucun projet de company-B)
- [ ] POST /projects → projet créé avec company_id="company-B"
- [ ] Vérifier que les 2 projets existent en DB mais sont isolés

### 12. Authority of Sources Validation
**Workflow:**
```
Client tente d'override company_id dans request body
→ Valeur JWT est utilisée
→ Security warning loggé
```
- [ ] Mock JWT avec company_id="company-A", user_id="user1"
- [ ] POST /projects avec body {"name": "P1", "company_id": "company-B"}
- [ ] Vérifier que projet créé a company_id="company-A" (pas "company-B")
- [ ] Vérifier log de sécurité: "Client attempted to override company_id"
- [ ] Vérifier que created_by="user1" (du JWT, pas du body si fourni)
- [ ] PUT /projects/{id} avec body {"company_id": "company-C"}
- [ ] Vérifier que company_id reste "company-A" (inchangé)
- [ ] Vérifier log de sécurité

---

## ⚙️ Data Integrity & Constraints (Priorité Moyenne)

## ⚙️ Data Integrity & Constraints (Priorité Moyenne)

### 13. Soft Delete Cascading
**Workflow:**
```
Soft delete projet → milestones/deliverables restent accessibles
Hard delete (si implémenté) → cascade cleanup
```
- [ ] Créer projet avec 5 milestones, 10 deliverables
- [ ] DELETE /projects/{id} (soft delete: removed_at timestamp)
- [ ] Vérifier projet.removed_at est set
- [ ] Vérifier milestones/deliverables existent toujours en DB (removed_at null)
- [ ] GET /projects → projet n'apparaît plus dans liste
- [ ] GET /projects/{id} → 404
- [ ] POST /projects/{id}/restore → projet restauré
- [ ] GET /projects → projet réapparaît
- [ ] Vérifier milestones/deliverables toujours intacts

### 14. Association Constraints & Validation
**Workflow:**
```
Milestone et Deliverable doivent appartenir au même projet
→ Tenter association cross-project → 400
```
- [ ] Créer projet P1 avec milestone M1
- [ ] Créer projet P2 avec deliverable D1
- [ ] POST `/milestones/{M1}/deliverables/{D1}` → 400 {"error": "Milestone and Deliverable must belong to same project"}
- [ ] Créer deliverable D2 dans P1
- [ ] POST `/milestones/{M1}/deliverables/{D2}` → 201 Created
- [ ] Supprimer milestone M1 (soft delete)
- [ ] Vérifier associations sont filtrées (milestone supprimé)
- [ ] GET `/milestones/{M1}/deliverables` → 404 ou liste vide

### 15. Date Validation & Business Rules
**Workflow:**
```
end_date doit être >= start_date
Milestone dates doivent être dans range du projet
Archive uniquement si status="completed"
```
- [ ] POST /projects avec start_date="2025-01-01", end_date="2024-12-31" → 400
- [ ] POST /projects avec dates valides → 201
- [ ] POST /milestones avec end_date < start_date → 400
- [ ] POST /projects/{id}/archive avec status="in-progress" → 400 {"error": "Project must be completed"}
- [ ] PATCH /projects/{id} status="completed"
- [ ] POST /projects/{id}/archive → 200 OK
- [ ] POST /projects/{id}/restore avec status != "archived" → 400

### 16. Unique Constraints & Duplicates
**Workflow:**
```
Tester contraintes d'unicité (si définies)
Associations en double
```
- [ ] POST /projects/{id}/milestones name="Milestone 1"
- [ ] POST /projects/{id}/milestones name="Milestone 1" → 201 (noms dupliqués autorisés)
- [ ] POST `/milestones/{M1}/deliverables/{D1}` → 201
- [ ] POST `/milestones/{M1}/deliverables/{D1}` → 409 Conflict (association déjà existe)
- [ ] POST /projects/{id}/members user_id="user2" → 201
- [ ] POST /projects/{id}/members user_id="user2" → 409 (member déjà existe)

---

## � Audit Trail & History (Priorité Moyenne)

### 17. ProjectHistory Completeness
**Workflow:**
```
Toutes les modifications doivent être enregistrées
Vérifier champs: entity_type, entity_id, action, changes, user_id
```
- [ ] POST /projects → vérifier ProjectHistory: action="created"
- [ ] PUT /projects/{id} → vérifier action="updated", changes={old, new}
- [ ] POST /projects/{id}/members → vérifier action="member_added"
- [ ] PATCH /projects/{id}/members/{user_id} role → vérifier action="member_role_changed"
- [ ] DELETE /projects/{id}/members/{user_id} → vérifier action="member_removed"
- [ ] DELETE /projects/{id} → vérifier action="deleted" (soft)
- [ ] POST /projects/{id}/restore → vérifier action="restored"
- [ ] GET /projects/{id}/history → vérifier tous les événements dans l'ordre chronologique

### 18. History Filtering & Pagination
**Workflow:**
```
Projet avec 100+ history entries
→ Tester pagination, filtrage par entity_type, date range
```
- [ ] Créer projet et faire 50+ modifications
- [ ] GET /projects/{id}/history?limit=10&offset=0
- [ ] Vérifier pagination (10 résultats, offset fonctionne)
- [ ] GET /projects/{id}/history?entity_type=member
- [ ] Vérifier filtrage (seulement actions liées aux members)
- [ ] Vérifier ordre chronologique (DESC: plus récent en premier)

---

## 🧪 Error Handling & Edge Cases (Priorité Basse)

### 19. Invalid UUIDs & 404 Handling
**Workflow:**
```
UUIDs malformés, ressources inexistantes
```
- [ ] GET /projects/not-a-uuid → 400 {"error": "Invalid UUID format"}
- [ ] GET /projects/00000000-0000-0000-0000-000000000000 → 404
- [ ] PUT /milestones/{non_existent_id} → 404
- [ ] DELETE /deliverables/{deleted_deliverable_id} → 404 (déjà soft deleted)

### 20. Concurrent Modifications (Basic)
**Workflow:**
```
2 users modifient le même projet simultanément
Pas d'optimistic locking, mais vérifier pas de data corruption
```
- [ ] user1 et user2 sont owners du même projet
- [ ] user1: PATCH /projects/{id} name="New Name 1"
- [ ] user2: PATCH /projects/{id} name="New Name 2" (quasi simultané)
- [ ] Vérifier que les 2 updates passent (last write wins)
- [ ] Vérifier ProjectHistory a les 2 entrées
- [ ] Vérifier pas de data corruption en DB

### 21. Transaction Rollback on Error
**Workflow:**
```
Opération qui échoue au milieu → rollback complet
```
- [ ] POST /projects avec données valides mais erreur DB simulée
- [ ] Vérifier que projet n'est pas créé
- [ ] Vérifier que default roles ne sont pas créés non plus
- [ ] Vérifier pas de ProjectHistory entry
- [ ] Mock erreur lors de création du 3ème default role
- [ ] Vérifier que projet + 2 premiers roles sont rollback

---

## 🎯 Mock Strategy

### Services Externes à Mocker
- **Guardian Service:**
  - `POST /check-access` → `{"allowed": true/false}`
  - JWT validation (extraire claims)
  - Utiliser `requests-mock` ou créer fixture pytest

- **Task Service:**
  - Pas d'appels entrants pour l'instant
  - WBS structure endpoint sera appelé par Task Service (pas testé ici)

- **File Service:**
  - `GET /files/{id}/metadata` → `{"project_id": "...", ...}`
  - Pour tests de check-file-access

### JWT Mock Fixture
```python
@pytest.fixture
def mock_jwt(mocker):
    """Mock JWT avec claims configurables"""
    def _mock(company_id="test-company", user_id="test-user"):
        # Mock de require_jwt_auth decorator
        # Injecter g.company_id et g.user_id
        pass
    return _mock
```

---

## � Structure des Tests

```
tests/
├── integration/
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures communes (mock JWT, Guardian, etc.)
│   │
│   ├── workflows/
│   │   ├── test_project_lifecycle.py           # Test 1
│   │   ├── test_wbs_structure_building.py      # Test 2
│   │   └── test_multi_milestone_management.py  # Test 3
│   │
│   ├── rbac/
│   │   ├── test_permission_chain.py            # Test 4
│   │   ├── test_custom_roles_policies.py       # Test 5, 6
│   │   ├── test_default_roles_protection.py    # Test 7
│   │   └── test_policy_protection.py           # Test 8
│   │
│   ├── access_control/
│   │   ├── test_check_project_access.py        # Test 9
│   │   └── test_check_file_access.py           # Test 10
│   │
│   ├── security/
│   │   ├── test_multi_tenant_isolation.py      # Test 11
│   │   └── test_authority_of_sources.py        # Test 12
│   │
│   ├── data_integrity/
│   │   ├── test_soft_delete_cascading.py       # Test 13
│   │   ├── test_association_constraints.py     # Test 14
│   │   ├── test_date_validation.py             # Test 15
│   │   └── test_unique_constraints.py          # Test 16
│   │
│   ├── audit/
│   │   ├── test_project_history.py             # Test 17, 18
│   │
│   └── edge_cases/
│       ├── test_invalid_inputs.py              # Test 19
│       ├── test_concurrent_modifications.py     # Test 20
│       └── test_transaction_rollback.py        # Test 21
```

---

## 🚀 Getting Started

### 1. Installation Dépendances
```bash
pip install pytest pytest-mock requests-mock faker pytest-cov
```

### 2. Configuration Environnement
```bash
# Utiliser .env.test existant
export FLASK_ENV=testing
```

### 3. Créer Fixtures Communes
```bash
touch tests/integration/conftest.py
```

**Contenu initial:**
```python
import pytest
from unittest.mock import MagicMock
from app import create_app
from app.models.db import db

@pytest.fixture
def app():
    """Flask app pour tests d'intégration"""
    app = create_app("app.config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def mock_jwt():
    """Mock JWT avec claims configurables"""
    def _mock(company_id="test-company", user_id="test-user"):
        # À implémenter: mock de require_jwt_auth
        pass
    return _mock

@pytest.fixture
def mock_guardian(requests_mock):
    """Mock Guardian Service responses"""
    requests_mock.post(
        "http://guardian:5000/check-access",
        json={"allowed": True}
    )
```

### 4. Lancer Premier Test
```bash
# Créer premier workflow test
touch tests/integration/workflows/test_project_lifecycle.py

# Lancer
pytest tests/integration/workflows/test_project_lifecycle.py -v
```

### 5. Coverage
```bash
pytest tests/integration/ --cov=app --cov-report=html --cov-report=term
open htmlcov/index.html
```

---

## 📋 Priorités de Développement

### Phase 1: Workflows Core (Semaine 1)
- [ ] Test 1: Lifecycle complet
- [ ] Test 2: WBS structure
- [ ] Test 3: Multi-milestone management

### Phase 2: RBAC (Semaine 2)
- [ ] Test 4: Permission chain
- [ ] Test 5-6: Custom roles/policies
- [ ] Test 7-8: Protection rules

### Phase 3: Security (Semaine 2-3)
- [ ] Test 11: Multi-tenant isolation
- [ ] Test 12: Authority of sources

### Phase 4: Access Control (Semaine 3)
- [ ] Test 9-10: Check access endpoints

### Phase 5: Data Integrity (Semaine 4)
- [ ] Test 13-16: Constraints & validation

### Phase 6: Audit & Edge Cases (Backlog)
- [ ] Test 17-18: History
- [ ] Test 19-21: Edge cases

---

**Last Updated:** 2025-11-11  
**Status:** Planning - Ready to Start  
**First Test:** `test_project_lifecycle.py`
