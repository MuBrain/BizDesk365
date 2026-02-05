# Bizdesk365 - Product Requirements Document

## Original Problem Statement
Build "Bizdesk365", a secure multi-tenant web portal for governance dashboards and reports for Compliance (ISO) and Enterprise Brain, with modular architecture supporting paid add-on modules like "Power Platform Governance".

## User Choices
- **Database**: MongoDB (adapted from PostgreSQL requirement)
- **Authentication**: Simple JWT (simulating Keycloak behavior)
- **Project Structure**: `/app/bizdesk365/` (exact structure as requested)
- **UI Framework**: Shadcn/Tailwind (instead of MUI)
- **Documentation**: Jekyll for GitHub Pages
- **Language**: French (fr-FR)

## User Personas
1. **Compliance Officer** - Tracks ISO conformity and maturity scores
2. **IT Governance Manager** - Monitors document quality and AI usage policies
3. **Executive** - Views high-level AI governance metrics
4. **Administrator** - Configures ISO profiles and AI policy thresholds

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
- ✅ Power Platform stub endpoint
- ✅ Database seeding with demo data

#### Frontend (React + Shadcn/Tailwind)
- ✅ Login page with split-screen design
- ✅ Sidebar navigation with module-based menu
- ✅ Dashboard Home with KPI cards
- ✅ Compliance Overview with circular maturity chart
- ✅ Enterprise Brain with IQI gauge and document table
- ✅ AI Governance with pie chart and traceability
- ✅ Settings with ISO toggles and AI policy sliders
- ✅ Power Platform placeholder page

#### Infrastructure
- ✅ Complete project structure in `/app/bizdesk365/`
- ✅ Docker Compose configuration
- ✅ Dockerfiles for API and UI
- ✅ Jekyll documentation setup
- ✅ README with quick start guide

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Multi-tenant JWT authentication
- [x] All 5 module endpoints
- [x] Core dashboard pages
- [x] French localization

### P1 (Important) - Future
- [ ] Real Keycloak integration
- [ ] Row-Level Security (RLS) migration
- [ ] User management CRUD
- [ ] Audit logging

### P2 (Nice to Have) - Future
- [ ] Power Platform module full implementation
- [ ] Email notifications
- [ ] Export reports (PDF/Excel)
- [ ] Dark mode theme
- [ ] Mobile responsive improvements

## Next Tasks List
1. Implement actual Keycloak OIDC integration if needed
2. Add user registration and management features
3. Implement Power Platform Governance module
4. Add report export functionality (PDF/Excel)
5. Implement real-time notifications
6. Add comprehensive audit logging
7. Consider adding chart animations and transitions

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/login` | POST | JWT authentication |
| `/api/me` | GET | Current user info |
| `/api/modules` | GET | Module list |
| `/api/compliance/kpis/latest` | GET | Compliance KPIs |
| `/api/compliance/maturity` | GET | Maturity score |
| `/api/enterprise-brain/quality` | GET | IQI metrics |
| `/api/enterprise-brain/documents` | GET | Document list |
| `/api/ai/usage/document/{id}` | GET | AI usage status |
| `/api/governance/ai/summary` | GET | AI governance summary |
| `/api/settings/iso` | GET/PUT | ISO profiles |
| `/api/settings/ai-policy` | GET/PUT | AI policy thresholds |
| `/api/power-platform/health` | GET | Module status |

## Demo Credentials
- **Email**: demo@bizdesk365.local
- **Password**: demo
- **Tenant**: Demo Org (UUID: 11111111-1111-1111-1111-111111111111)
