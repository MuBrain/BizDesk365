# Bizdesk365

Portail web multi-tenant sécurisé pour la gouvernance et la conformité.

## 🚀 Démarrage rapide

### Prérequis
- Docker & Docker Compose
- Node.js 18+ (pour le développement local)
- Python 3.11+ (pour le développement local)

### Lancer avec Docker Compose

```bash
cd infra
docker compose up --build
```

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Connexion démo

- **Email**: demo@bizdesk365.local
- **Mot de passe**: demo

## 📁 Structure du projet

```
bizdesk365/
├── infra/                    # Infrastructure Docker
│   └── docker-compose.yml
├── apps/
│   ├── api/                  # Backend FastAPI
│   │   └── app/
│   │       ├── main.py
│   │       ├── db.py
│   │       ├── security.py
│   │       └── modules/      # Modules métier
│   └── ui/                   # Frontend React
│       └── src/
│           ├── pages/
│           ├── layout/
│           └── modules/
└── docs/                     # Documentation GitHub Pages
```

## 🔧 Modules

| Module | Description | Statut |
|--------|-------------|--------|
| Conformité ISO | KPIs et score de maturité | ✅ Actif |
| Enterprise Brain | Qualité documentaire (IQI) | ✅ Actif |
| Gouvernance IA | Dashboard exécutif IA | ✅ Actif |
| Paramètres | Configuration tenant | ✅ Actif |
| Power Platform | Gouvernance Power Platform | 🚧 À venir |

## 🏗️ Architecture

- **Multi-tenant**: Isolation par `tenant_id` dans JWT
- **Modulaire**: Système de modules extensible
- **API-first**: FastAPI avec documentation OpenAPI
- **Sécurisé**: JWT avec validation JWKS-ready

## 📖 Documentation

Voir [docs/](./docs/) pour la documentation complète.
