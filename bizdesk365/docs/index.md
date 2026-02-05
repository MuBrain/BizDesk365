---
layout: default
title: Accueil
---

# Bizdesk365 Documentation

Bienvenue dans la documentation de **Bizdesk365**, le portail web multi-tenant pour la gouvernance et la conformité.

## 🚀 Démarrage rapide

### Lancer l'application

```bash
cd infra
docker compose up --build
```

### URLs d'accès

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:5173](http://localhost:5173) |
| API | [http://localhost:8000](http://localhost:8000) |
| Documentation API | [http://localhost:8000/docs](http://localhost:8000/docs) |

### Connexion démo

- **Email**: `demo@bizdesk365.local`
- **Mot de passe**: `demo`

---

## 📦 Concept de Modules

Bizdesk365 utilise une architecture modulaire. Chaque module représente un domaine fonctionnel distinct :

### Modules disponibles

| Module | ID | Description |
|--------|----|-----------| 
| **Conformité ISO** | `compliance` | Suivi des KPIs de conformité et calcul du score de maturité |
| **Enterprise Brain** | `enterprise_brain` | Qualité de l'information (IQI) et gestion documentaire |
| **Gouvernance IA** | `ai_governance` | Tableau de bord exécutif pour le suivi de l'utilisation IA |
| **Paramètres** | `settings` | Configuration des référentiels ISO et seuils IA |
| **Power Platform** | `power_platform` | *(À venir)* Gouvernance Microsoft Power Platform |

### Activation des modules

Les modules sont activés par tenant. L'API `/api/modules` retourne la liste des modules disponibles pour le tenant connecté.

---

## 🔧 Ajouter un nouveau module

### 1. Backend (FastAPI)

Créer un fichier dans `apps/api/app/modules/`:

```python
# apps/api/app/modules/mon_module.py
from fastapi import APIRouter, Depends
from ..security import get_current_user, get_tenant_id

router = APIRouter(prefix="/mon-module", tags=["Mon Module"])

@router.get("/data")
async def get_data(tenant_id: str = Depends(get_tenant_id)):
    return {"message": "Hello from mon module", "tenant": tenant_id}
```

Enregistrer dans le registry (`registry.py`) et inclure le router dans `main.py`.

### 2. Frontend (React)

Créer une page dans `apps/ui/src/pages/`:

```tsx
// MonModule.tsx
export default function MonModule() {
  return <h1>Mon Module</h1>
}
```

Ajouter la route et l'entrée dans le module registry côté client.

---

## 🔐 Authentification

Bizdesk365 utilise JWT pour l'authentification :

- **Login**: `POST /api/auth/login`
- **Token**: Bearer token dans l'en-tête `Authorization`
- **Claims**: `sub` (user_id), `email`, `tenant_id`, `roles`

Le `tenant_id` est extrait du JWT pour assurer l'isolation multi-tenant.

---

## 📊 API Reference

Consultez la documentation interactive Swagger à [http://localhost:8000/docs](http://localhost:8000/docs).

### Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/login` | POST | Authentification |
| `/api/me` | GET | Utilisateur courant |
| `/api/modules` | GET | Liste des modules |
| `/api/compliance/*` | GET | Conformité ISO |
| `/api/enterprise-brain/*` | GET | Enterprise Brain |
| `/api/governance/ai/*` | GET | Gouvernance IA |
| `/api/settings/*` | GET/PUT | Paramètres |

---

## 🏗️ Architecture technique

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │────▶│    MongoDB      │
│  React + Vite   │     │    FastAPI      │     │                 │
│  Port: 5173     │     │    Port: 8000   │     │   Port: 27017   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Multi-tenancy

- Chaque requête API est associée à un `tenant_id`
- L'isolation est assurée par filtrage des queries MongoDB
- Prêt pour migration vers Row-Level Security (RLS)
