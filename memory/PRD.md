# Bizdesk365 - Product Requirements Document

## Original Problem Statement
Build "Bizdesk365", a secure multi-tenant web portal for governance dashboards and reports for Compliance (ISO), Enterprise Brain, AI Governance and Power Platform Governance, with modular architecture supporting paid add-on modules.

## User Choices
- **Database**: MongoDB (adapted from PostgreSQL requirement)
- **Authentication**: Simple JWT (simulating Keycloak behavior)
- **Project Structure**: `/app/backend` and `/app/frontend`
- **UI Framework**: Shadcn/Tailwind (instead of MUI)
- **Language**: French (fr-FR)

## User Personas
1. **Compliance Officer** - Tracks ISO conformity and maturity scores
2. **IT Governance Manager** - Monitors document quality and AI usage policies
3. **Power Platform Admin** - Manages governance program with 10 workshops
4. **Executive** - Views high-level governance metrics
5. **Administrator** - Configures ISO profiles and AI policy thresholds

## Core Requirements (Static)
- Multi-tenant architecture with tenant isolation via JWT `tenant_id` claim
- Module-based navigation system
- French language UI throughout
- Professional enterprise dashboard aesthetic
- Real-time data from backend APIs

## What's Been Implemented

### Date: 2026-02-05

#### Backend (FastAPI + MongoDB)
- ✅ JWT Authentication with login/logout
- ✅ Module registry system (5 modules)
- ✅ Compliance endpoints (KPIs, Maturity score)
- ✅ Enterprise Brain endpoints (IQI, Documents, AI Usage)
- ✅ AI Governance endpoints (Summary with charts data)
- ✅ Settings endpoints (ISO profiles, AI policy thresholds)
- ✅ Database seeding with demo data
- ✅ **Power Platform Governance Module (COMPLETE)**:
  - Program management (get/create)
  - KPIs calculation (workshop completion, items, actions, decisions, ownership)
  - 10 Workshops CRUD with completion criteria
  - 66 Items with acceptance criteria
  - Actions CRUD with priority, status, ageing
  - Decisions CRUD with evidence links
  - Evidence CRUD
  - Automatic workshop completion detection
- ✅ Pytest test suite for Power Platform module (22 tests)

#### Frontend (React + Shadcn/Tailwind)
- ✅ Login page with split-screen design
- ✅ Sidebar navigation with module-based menu
- ✅ Dashboard Home with KPI cards
- ✅ Compliance Overview with circular maturity chart
- ✅ Enterprise Brain with IQI gauge and document table
- ✅ AI Governance with pie chart and traceability
- ✅ Settings with ISO toggles and AI policy sliders
- ✅ **Power Platform Governance Pages (COMPLETE)**:
  - Main dashboard with KPI cards (6 metrics)
  - Horizontal timeline with 10 workshops
  - Workshop list with progress indicators
  - Workshop detail page with completion criteria checkboxes
  - Items list with status, owner, due date, acceptance criteria
  - Item dialog with user story, notes, acceptance criteria
  - Actions management page with filters and CRUD
  - Decisions management page with filters and CRUD
  - Tabs navigation (Ateliers, Actions, Décisions)

## Prioritized Backlog

### P0 (Critical) - DONE ✅
- [x] Multi-tenant JWT authentication
- [x] All 5 module endpoints
- [x] Core dashboard pages
- [x] French localization
- [x] Power Platform Governance full implementation

### P1 (Important) - Future
- [ ] Evidence/Artefacts page for Power Platform (dedicated UI)
- [ ] Real Keycloak integration
- [ ] User management CRUD
- [ ] Audit logging
- [ ] Export reports (PDF/Excel)

### P2 (Nice to Have) - Future
- [ ] Email notifications
- [ ] Dark mode theme
- [ ] Mobile responsive improvements
- [ ] Real-time notifications (WebSocket)

## Next Tasks List
1. Create dedicated Evidence/Artefacts page for Power Platform
2. Implement actual Keycloak OIDC integration if needed
3. Add user registration and management features
4. Add report export functionality (PDF/Excel)
5. Implement real-time notifications
6. Add comprehensive audit logging

## API Endpoints Summary

### Authentication & Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/login` | POST | JWT authentication |
| `/api/me` | GET | Current user info |
| `/api/modules` | GET | Module list |

### Compliance
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/compliance/kpis/latest` | GET | Compliance KPIs |
| `/api/compliance/maturity` | GET | Maturity score |

### Enterprise Brain
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/enterprise-brain/quality` | GET | IQI metrics |
| `/api/enterprise-brain/documents` | GET | Document list |
| `/api/ai/usage/document/{id}` | GET | AI usage status |

### AI Governance
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/governance/ai/summary` | GET | AI governance summary |

### Settings
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/settings/iso` | GET/PUT | ISO profiles |
| `/api/settings/ai-policy` | GET/PUT | AI policy thresholds |

### Power Platform Governance
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/power-platform/program` | GET | Get/create program |
| `/api/power-platform/kpis` | GET | Calculate KPIs |
| `/api/power-platform/workshops` | GET | List all workshops |
| `/api/power-platform/workshops/{num}` | GET/PATCH | Workshop detail/update |
| `/api/power-platform/items` | GET | List items |
| `/api/power-platform/items/{id}` | GET/PATCH | Item detail/update |
| `/api/power-platform/items/{id}/validate` | POST | Validate item |
| `/api/power-platform/actions` | GET/POST | Actions list/create |
| `/api/power-platform/actions/{id}` | PATCH/DELETE | Action update/delete |
| `/api/power-platform/decisions` | GET/POST | Decisions list/create |
| `/api/power-platform/decisions/{id}` | DELETE | Decision delete |
| `/api/power-platform/evidence` | GET/POST | Evidence list/create |
| `/api/power-platform/evidence/{id}` | DELETE | Evidence delete |
| `/api/power-platform/definitions/workshops` | GET | Workshop definitions |
| `/api/power-platform/definitions/items` | GET | Item definitions |

## Demo Credentials
- **Email**: demo@bizdesk365.local
- **Password**: demo
- **Tenant**: Demo Org (UUID: 11111111-1111-1111-1111-111111111111)

## Test Files
- `/app/backend/tests/test_power_platform.py` - 22 comprehensive API tests
- `/app/test_reports/iteration_2.json` - Latest test results (100% pass rate)

## Known Issues Fixed
- MongoDB `_id` serialization bug in POST endpoints for actions, decisions, evidence (fixed 2026-02-05)
