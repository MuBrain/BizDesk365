# Power Platform Governance Module - Seed Data and Business Logic

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

# ============== Workshop Definitions ==============

WORKSHOP_DEFINITIONS = [
    {
        "workshop_number": 1,
        "title": "Cadrage & Baseline",
        "description": "Définir le périmètre, identifier les parties prenantes et capturer la baseline initiale",
        "completion_criteria": [
            "Sponsor + Platform Owner identifiés",
            "Périmètre défini (in/out)",
            "RACI v0 complété (au moins 6 processus)",
            "Baseline v0 saisie (même approximative)",
            "Backlog Atelier 2 créé (au moins 5 actions)"
        ]
    },
    {
        "workshop_number": 2,
        "title": "Environnements & DLP",
        "description": "Stratégie d'environnements, DLP et catalogue de connecteurs",
        "completion_criteria": [
            "Environment Strategy v0 validée (types + naming + création)",
            "DLP Strategy v0 validée (par posture d'env)",
            "Catalogue connecteurs v0 (au moins top 10 + sensibles)",
            "Process d'exception défini (durée, approbation, preuves)",
            "Licensing Snapshot capturé (contraintes + questions ouvertes)",
            "Backlog Atelier 3 créé (accès + exports + mise en œuvre DLP)"
        ]
    },
    {
        "workshop_number": 3,
        "title": "Onboarding & Collecte",
        "description": "Setup Bizdesk365, méthode de collecte et baseline v1",
        "completion_criteria": [
            "Tenant Bizdesk365 client créé + RBAC en place",
            "Méthode de collecte décidée (API/Export/Hybride)",
            "Au moins une collecte baseline v1 exécutée (coverage affiché)",
            "Dashboard 'risques évidents' opérationnel",
            "Top 10 risques + Top 10 actions saisis et assignés",
            "Cadence de revue gouvernance définie"
        ]
    },
    {
        "workshop_number": 4,
        "title": "ALM & Solutions",
        "description": "Stratégie ALM, standards solutions et checklist release",
        "completion_criteria": [
            "ALM Strategy v0 validée",
            "Standards Solutions validés",
            "Registre 'prod hors solution' créé (au moins top 10 items)",
            "Release checklist v0 créée",
            "Connection strategy définie (au moins règles de base)",
            "Backlog migration ALM créé et assigné"
        ]
    },
    {
        "workshop_number": 5,
        "title": "CI/CD Foundation",
        "description": "Blueprint CI/CD, Azure DevOps setup et pipelines v0",
        "completion_criteria": [
            "CICD Strategy v0 validée",
            "ADO projet/repo défini (et idéalement créé)",
            "Service identity définie + plan permissions",
            "Pipelines v0 définis (build + test)",
            "Approvals prod définis (même si pas encore implémentés)",
            "Backlog atelier 6 créé"
        ]
    },
    {
        "workshop_number": 6,
        "title": "Quality Gates & Release",
        "description": "Quality gates, smoke tests et release logging",
        "completion_criteria": [
            "Gates v1 définis et validés (au moins 5 bloquants)",
            "Smoke Test Pack v1 défini (3–5 tests)",
            "Release report standard défini",
            "Au moins 1 déploiement vers Test journalisé (release log)",
            "Bizdesk365 : register 'deployments' + 'findings' opérationnels",
            "Backlog atelier 7 alimenté par findings réels"
        ]
    },
    {
        "workshop_number": 7,
        "title": "Sécurité & RBAC",
        "description": "RBAC plateforme, DLP avancé et classification",
        "completion_criteria": [
            "RBAC plateforme v0 défini (rôles + groupes + scope)",
            "DLP v1 défini (par env + exceptions + revue)",
            "Prod Policy v0 validée (règles non négociables)",
            "Modèle de classification défini",
            "Backlog sécurité créé et priorisé (top 10 actions)",
            "Preuves / décisions enregistrées"
        ]
    },
    {
        "workshop_number": 8,
        "title": "Canvas Apps Quality",
        "description": "Standards UX/UI, checklist qualité et scoring apps",
        "completion_criteria": [
            "Canvas Standard v0 validé (UX/UI + patterns)",
            "Checklist qualité prod v0 validée",
            "Au moins 1–3 apps auditées (quality index saisi)",
            "Backlog d'amélioration créé (top 10 actions)",
            "Stratégie composants décidée (même 'non' assumé)",
            "Règles erreurs/logging décidées"
        ]
    },
    {
        "workshop_number": 9,
        "title": "Flows Governance",
        "description": "Politique flows, intégrations et monitoring",
        "completion_criteria": [
            "Flow Governance Policy validée",
            "Integration Policy v0 validée (connecteurs + HTTP/custom)",
            "Identity strategy pour flows définie (service accounts)",
            "Monitoring minimal défini (qui reçoit quoi)",
            "Top 10 flows critiques renseignés dans Bizdesk365",
            "Flow Risk Index v0 validé",
            "Backlog priorisé (top 10 actions)"
        ]
    },
    {
        "workshop_number": 10,
        "title": "Run & Transition",
        "description": "Playbook, roadmap et transition vers le Run",
        "completion_criteria": [
            "Playbook v1 approuvé + lien stocké",
            "Roadmap 30/60/90 validée et saisie",
            "Operating model (cadence + comité + owners) validé",
            "Adoption plan v0 validé",
            "KPI pack validé (définitions + fréquence)",
            "Programme marqué 'Completed' + transition Run"
        ]
    }
]

# ============== Item Definitions ==============

ITEM_DEFINITIONS = [
    # Workshop 1
    {"item_id": "A1-01", "workshop_number": 1, "title": "Profil client", "module_name": "Tenant / Organisation", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux documenter le profil du client (contexte, enjeux, contraintes) afin de calibrer le niveau de gouvernance et de risque.", "acceptance_criteria": ["Fiche organisation créée", "Secteur + taille + criticité renseignés", "Contraintes (réglementaires/IT/sécurité) renseignées", "Enjeux business résumés", "Statut de validation (draft/validé) + date"]},
    {"item_id": "A1-02", "workshop_number": 1, "title": "Périmètre de gouvernance", "module_name": "Scope", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux définir clairement le périmètre (in/out) de la gouvernance afin de cadrer les décisions et éviter les zones grises.", "acceptance_criteria": ["Périmètre In défini (types d'actifs/env)", "Périmètre Out défini", "Justification du scope saisie", "Hypothèses/limites documentées", "Statut validé + sponsor/owner associé"]},
    {"item_id": "A1-03", "workshop_number": 1, "title": "Parties prenantes & gouvernance", "module_name": "Stakeholders", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux identifier les parties prenantes et leurs responsabilités afin de garantir l'ownership et la prise de décision.", "acceptance_criteria": ["Sponsor identifié", "Platform Owner identifié", "Contacts clés listés (sécurité, ops, dev, conformité)", "Rôle + responsabilité pour chaque stakeholder", "Backup/adjoint identifié pour rôles critiques"]},
    {"item_id": "A1-04", "workshop_number": 1, "title": "RACI v0", "module_name": "Operating Model", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux établir un RACI v0 des processus clés afin de rendre la gouvernance exécutable et mesurable.", "acceptance_criteria": ["Au moins 6 processus couverts", "R, A, C, I attribués par processus", "Aucun processus sans 'A'", "Coverage RACI calculable", "Version taggée v0 + date"]},
    {"item_id": "A1-05", "workshop_number": 1, "title": "Baseline", "module_name": "Baseline Snapshot", "status_requirement": "À CAPTURER", "user_story_fr": "En tant que Responsable gouvernance, je veux capturer une baseline initiale même approximative afin de démarrer le pilotage et mesurer les progrès.", "acceptance_criteria": ["Snapshot créé avec date", "Valeurs initiales saisies (même approx)", "Source indiquée (approx/export/API)", "Champs manquants explicités", "Prochaine étape d'amélioration notée"]},
    {"item_id": "A1-06", "workshop_number": 1, "title": "Documents existants & contraintes", "module_name": "Evidence / Artefacts", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Auditeur interne / conformité, je veux centraliser les preuves et documents existants afin de rendre la gouvernance audit-proof.", "acceptance_criteria": ["Référentiel preuves créé", "Au moins 3 artefacts liés", "Chaque artefact a un owner", "Chaque artefact a un type + date", "Liens accessibles ou pièce jointe"]},
    {"item_id": "A1-07", "workshop_number": 1, "title": "Backlog d'actions", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux créer un backlog d'actions priorisées afin de transformer les décisions en exécution.", "acceptance_criteria": ["Au moins 5 actions créées", "Chaque action a owner + priorité + due date", "Actions liées à un atelier/module", "Statut initial défini (open)", "Risques/impacts décrits pour actions majeures"]},
    # Workshop 2
    {"item_id": "A2-01", "workshop_number": 2, "title": "Stratégie d'environnements", "module_name": "Environment Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux définir une stratégie d'environnements (types, règles, naming) afin de contrôler la structure et limiter les dérives.", "acceptance_criteria": ["Types d'environnements définis", "Règles de naming définies", "Règles de création documentées", "Règles de cycle de vie", "Statut v0 validé"]},
    {"item_id": "A2-02", "workshop_number": 2, "title": "Règles de création & approbation", "module_name": "Request & Approval", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux mettre en place des règles de demande/approbation afin de contrôler la création d'environnements et d'actifs.", "acceptance_criteria": ["Process de demande décrit", "Critères d'approbation définis", "Rôles d'approbation nommés", "Délais/SLAs indicatifs définis", "Preuves conservées"]},
    {"item_id": "A2-03", "workshop_number": 2, "title": "Stratégie DLP", "module_name": "DLP Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir une stratégie DLP v0 afin de réduire les risques de fuite et encadrer les connecteurs.", "acceptance_criteria": ["Posture DLP par type d'environnement définie", "Groupes de connecteurs définis", "Règles minimales prod listées", "Mode de revue/maintenance défini", "Statut v0 validé"]},
    {"item_id": "A2-04", "workshop_number": 2, "title": "Catalogue de connecteurs", "module_name": "Connector Catalog", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux classifier les connecteurs (top 10 + sensibles) afin de rendre le risque visible et gouvernable.", "acceptance_criteria": ["Top 10 connecteurs majeurs listés", "Au moins 5 connecteurs sensibles identifiés", "Chaque connecteur a une classe de risque", "Statut 'connu/inconnu' géré", "Date de dernière revue enregistrée"]},
    {"item_id": "A2-05", "workshop_number": 2, "title": "Exceptions DLP", "module_name": "Exceptions Register", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir un processus d'exceptions DLP avec durée et preuves afin d'éviter les exceptions permanentes.", "acceptance_criteria": ["Règles d'exception définies", "Durée/expiration obligatoire", "Approbation obligatoire", "Preuves exigées", "Process de revue/renouvellement défini"]},
    {"item_id": "A2-06", "workshop_number": 2, "title": "Licences & contraintes", "module_name": "Licensing Snapshot", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux capturer les contraintes de licences et budgétaires afin de sécuriser la faisabilité et les arbitrages.", "acceptance_criteria": ["Snapshot licences créé", "Hypothèses documentées", "Contraintes budgétaires listées", "Questions ouvertes capturées", "Décisions/licensing risks consignés"]},
    {"item_id": "A2-07", "workshop_number": 2, "title": "Plan d'action Atelier 2", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux formaliser le plan d'action issu de l'atelier 2 afin d'enchaîner sur l'implémentation sans perte.", "acceptance_criteria": ["Actions liées aux sujets env/DLP/connecteurs", "Owners assignés", "Priorités définies", "Dépendances notées", "Backlog atelier 3 préparé"]},
    # Workshop 3
    {"item_id": "A3-01", "workshop_number": 3, "title": "Onboarding Bizdesk365", "module_name": "Tenant Setup", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Administrateur Bizdesk365, je veux initialiser le tenant client dans Bizdesk365 afin de rendre le pilotage opérationnel.", "acceptance_criteria": ["Tenant créé", "Paramètres de base renseignés", "RBAC initial appliqué", "Accès admin vérifié", "Statut 'ready' renseigné"]},
    {"item_id": "A3-02", "workshop_number": 3, "title": "Accès & autorisations", "module_name": "Access Readiness", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Administrateur plateforme, je veux valider les accès nécessaires (RBAC, exports, API) afin de permettre la collecte et le monitoring.", "acceptance_criteria": ["Liste des accès requis documentée", "Accès accordés ou planifiés", "Risques/bloquants listés", "Propriétaire identifié", "Date de vérification enregistrée"]},
    {"item_id": "A3-03", "workshop_number": 3, "title": "Méthode de collecte", "module_name": "Data Collection Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux choisir la méthode de collecte (API / export / hybride) afin de fiabiliser la baseline et réduire l'effort manuel.", "acceptance_criteria": ["Mode choisi (API/export/hybride)", "Fréquence cible définie", "Responsables identifiés", "Stockage des données défini", "Limites documentées"]},
    {"item_id": "A3-04", "workshop_number": 3, "title": "Baseline v1", "module_name": "Baseline Snapshot v1", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux exécuter une baseline v1 avec un indicateur de coverage afin de mesurer la qualité des données et piloter le risque.", "acceptance_criteria": ["Baseline v1 exécutée", "Coverage % calculé et visible", "Date/heure enregistrées", "Top 10 risques identifiés", "Écarts vs v0 notés"]},
    {"item_id": "A3-05", "workshop_number": 3, "title": "Catalogue connecteurs (v1)", "module_name": "Connector Catalog", "status_requirement": "À ENRICHIR", "user_story_fr": "En tant que Responsable Sécurité, je veux enrichir le catalogue de connecteurs afin d'améliorer la couverture du scoring et des politiques.", "acceptance_criteria": ["Nouveaux connecteurs ajoutés", "Connecteurs 'inconnus' réduits", "Classification mise à jour", "Connecteurs sensibles confirmés", "Date de revue + responsable"]},
    {"item_id": "A3-06", "workshop_number": 3, "title": "Scoring / Maturity rules v0", "module_name": "Scoring Configuration", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux configurer les règles de scoring/maturité afin de prioriser les actions sur des critères objectifs.", "acceptance_criteria": ["Dimensions de scoring définies", "Seuils/pondérations définis", "Règles testées sur baseline v1", "Résultats compréhensibles", "Version v0 enregistrée + date"]},
    {"item_id": "A3-07", "workshop_number": 3, "title": "Plan d'action Bizdesk365", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux centraliser le plan d'action dans Bizdesk365 afin de suivre l'avancement, l'assignation et l'aging.", "acceptance_criteria": ["Top 10 actions créées", "Actions assignées", "Dates cibles définies", "Statuts cohérents", "Indicateur ageing possible"]},
    {"item_id": "A3-08", "workshop_number": 3, "title": "Rituel de gouvernance", "module_name": "Governance Cadence", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux définir la cadence et le rituel de gouvernance afin d'assurer la continuité des décisions et du pilotage.", "acceptance_criteria": ["Fréquence définie", "Participants/roles définis", "Agenda type défini", "Mode de décision/validation défini", "Format de compte-rendu défini"]},
    # Workshop 4
    {"item_id": "A4-01", "workshop_number": 4, "title": "Modèle ALM cible", "module_name": "ALM Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux définir une stratégie ALM cible afin de déployer proprement et réduire les erreurs.", "acceptance_criteria": ["Environnements ALM alignés", "Flux de promotion décrit", "Règles de versioning définies", "Rôles et responsabilités ALM définis", "Statut v0 validé"]},
    {"item_id": "A4-02", "workshop_number": 4, "title": "Standards Solutions", "module_name": "Solution Standards", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Lead Dev Power Platform, je veux standardiser l'usage des solutions afin de rendre les déploiements reproductibles.", "acceptance_criteria": ["Naming standards définis", "Publisher/managed/unmanaged clarifiés", "Règles de structure définies", "Exceptions documentées", "Exemples concrets fournis"]},
    {"item_id": "A4-03", "workshop_number": 4, "title": "Registre 'Prod hors solution'", "module_name": "ALM Gaps Register", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux recenser les éléments prod hors solution afin de mesurer et rembourser la dette ALM.", "acceptance_criteria": ["Registre créé", "Au moins 10 items listés", "Chaque item a owner + criticité", "Plan de remédiation pour items top", "Tendance/compteur possible"]},
    {"item_id": "A4-04", "workshop_number": 4, "title": "Stratégie connexions & comptes", "module_name": "Connection Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir les règles de connexions/comptes afin de réduire les risques de comptes personnels en prod.", "acceptance_criteria": ["Règles comptes de service définies", "Interdits prod listés", "Mode de rotation/gestion secrets défini", "Exceptions encadrées", "Statut validé"]},
    {"item_id": "A4-05", "workshop_number": 4, "title": "Checklist de release v0", "module_name": "Release Checklist v0", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux créer une checklist de release afin de rendre chaque déploiement contrôlé et traçable.", "acceptance_criteria": ["Checklist créée", "Contrôles minimaux inclus", "Approvals définis", "Preuves attendues listées", "Version v0 publiée"]},
    {"item_id": "A4-06", "workshop_number": 4, "title": "Plan d'action Atelier 4", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux planifier les actions ALM prioritaires afin de converger vers un modèle de déploiement conforme.", "acceptance_criteria": ["Actions ALM créées", "Owners assignés", "Priorités définies", "Dépendances listées", "Backlog migration ALM alimenté"]},
    # Workshop 5
    {"item_id": "A5-01", "workshop_number": 5, "title": "CI/CD Blueprint", "module_name": "CICD Strategy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux définir un blueprint CI/CD afin de standardiser l'industrialisation des déploiements.", "acceptance_criteria": ["Blueprint documenté", "Étapes pipeline décrites", "Environnements cibles listés", "Contrôles (gates) prévus", "Statut v0 validé"]},
    {"item_id": "A5-02", "workshop_number": 5, "title": "Azure DevOps Setup", "module_name": "Tooling Readiness", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Administrateur DevOps, je veux préparer l'outillage Azure DevOps (projet, repo, permissions) afin de supporter les pipelines.", "acceptance_criteria": ["Projet/repo définis", "Modèle branches défini", "Permissions de base planifiées", "Accès équipes confirmés", "Blocages outillage listés"]},
    {"item_id": "A5-03", "workshop_number": 5, "title": "Identité technique & sécurité", "module_name": "Service Identity", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir les identités techniques et leurs permissions afin de sécuriser l'exécution des pipelines.", "acceptance_criteria": ["Identité technique définie", "Permissions minimales documentées", "Séparation des rôles définie", "Mode de gestion secrets défini", "Blocages sécurité listés"]},
    {"item_id": "A5-04", "workshop_number": 5, "title": "Pipeline v0 définition", "module_name": "Pipeline Definitions", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Ingénieur DevOps, je veux définir les pipelines v0 (build/test) afin d'automatiser les contrôles et réduire les erreurs manuelles.", "acceptance_criteria": ["Pipeline build défini", "Pipeline test défini", "Déclencheurs décrits", "Variables/secrets gérés", "Sorties attendues définies"]},
    {"item_id": "A5-05", "workshop_number": 5, "title": "Mapping checklist", "module_name": "Quality Gates v0", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux mapper la checklist sur des quality gates afin de bloquer automatiquement les releases non conformes.", "acceptance_criteria": ["Checklist reliée à gates", "Gates listés (v0)", "Critères bloquants identifiés", "Exceptions possibles cadrées", "Traçabilité du résultat prévue"]},
    {"item_id": "A5-06", "workshop_number": 5, "title": "Backlog Atelier 6", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux préparer le backlog pour l'atelier 6 afin de traiter les blocages et passer à l'exécution réelle.", "acceptance_criteria": ["Actions pour implémenter gates/tests créées", "Owners/dates définis", "Dépendances tracées", "Priorités ajustées", "Préparation d'un premier déploiement test"]},
    # Workshop 6
    {"item_id": "A6-01", "workshop_number": 6, "title": "Quality Gates v1", "module_name": "CICD Quality Gates", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux définir des quality gates v1 (bloquants) afin de rendre les déploiements contrôlés et prouvables.", "acceptance_criteria": ["Au moins 5 gates bloquants définis", "Critères mesurables (pass/fail)", "Point d'intégration pipeline prévu", "Mode de preuve/rapport défini", "Statut v1 validé"]},
    {"item_id": "A6-02", "workshop_number": 6, "title": "Smoke Test Pack v1", "module_name": "Test Catalog", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que QA / Test lead, je veux définir un pack de smoke tests afin de détecter rapidement les régressions après déploiement.", "acceptance_criteria": ["3 à 5 smoke tests définis", "Préconditions documentées", "Résultat attendu par test", "Mode d'exécution défini", "Statut v1 validé"]},
    {"item_id": "A6-03", "workshop_number": 6, "title": "Release Report Standard", "module_name": "Release Reporting", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable conformité, je veux standardiser le rapport de release afin de prouver ce qui a été déployé, par qui et avec quels contrôles.", "acceptance_criteria": ["Template de rapport défini", "Champs obligatoires", "Résultats gates/tests inclus", "Section risques/écarts incluse", "Lien de stockage défini"]},
    {"item_id": "A6-04", "workshop_number": 6, "title": "Release Log", "module_name": "Deployment Register", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Release Manager, je veux journaliser les déploiements (au minimum vers Test) afin d'assurer la traçabilité et l'auditabilité.", "acceptance_criteria": ["Registre actif", "Au moins 1 déploiement Test journalisé", "Chaque entrée a date + env + initiateur", "Lien vers rapport de release", "Statut succès/échec consigné"]},
    {"item_id": "A6-05", "workshop_number": 6, "title": "Non-conformités & actions automatiques", "module_name": "Compliance Findings", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux enregistrer et suivre les non-conformités afin de déclencher des actions correctives et réduire les risques.", "acceptance_criteria": ["Findings créables", "Chaque finding a sévérité + owner + due date", "Lien au déploiement/artefact", "Règle de clôture définie", "Backlog alimenté depuis findings"]},
    # Workshop 7
    {"item_id": "A7-01", "workshop_number": 7, "title": "RBAC Power Platform", "module_name": "Platform Security", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir les rôles et groupes RBAC Power Platform afin de limiter les privilèges et réduire l'exposition.", "acceptance_criteria": ["Rôles admin identifiés", "Groupes AD/Entra liés", "Scope défini", "Principes 'least privilege' documentés", "Revue périodique planifiée"]},
    {"item_id": "A7-02", "workshop_number": 7, "title": "Dataverse RBAC", "module_name": "Dataverse Security Model", "status_requirement": "OBLIGATOIRE (si scope)", "user_story_fr": "En tant que Administrateur Dataverse, je veux modéliser la sécurité Dataverse (rôles, BU, accès) afin de protéger les données et maîtriser les droits.", "acceptance_criteria": ["Modèle rôles défini", "BU/teams alignées", "Accès aux tables sensibles cadré", "Scénarios d'accès testés", "Statut validé"]},
    {"item_id": "A7-03", "workshop_number": 7, "title": "DLP Advanced Strategy v1", "module_name": "DLP Strategy v1", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir la stratégie DLP v1 par environnement afin d'adapter la posture de sécurité aux usages.", "acceptance_criteria": ["Règles DLP par environnement", "Connecteurs sensibles traités", "Process d'évolution défini", "Mesure de conformité possible", "Statut v1 validé"]},
    {"item_id": "A7-04", "workshop_number": 7, "title": "Exceptions Register", "module_name": "Exceptions", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux gérer les exceptions avec approbation et expiration afin d'éviter les dérogations permanentes.", "acceptance_criteria": ["Registre opérationnel", "Champs obligatoires", "Approbateur défini", "Revue périodique définie", "Indicateur 'exceptions actives + âge' possible"]},
    {"item_id": "A7-05", "workshop_number": 7, "title": "Application & Flow Governance", "module_name": "App/Flow Governance Rules", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux définir des règles de gouvernance pour apps/flows afin de réduire le risque opérationnel en production.", "acceptance_criteria": ["Règles prod définies", "Règles de support définies", "Règles de naming/standards définies", "Exceptions cadrées", "Publication/communication planifiée"]},
    {"item_id": "A7-06", "workshop_number": 7, "title": "Classification Model", "module_name": "Classification Schema", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable conformité, je veux définir un modèle de classification afin d'appliquer des règles cohérentes de protection et de cycle de vie.", "acceptance_criteria": ["Niveaux de classification définis", "Critères par niveau", "Mapping vers règles", "Exemples donnés", "Statut validé"]},
    {"item_id": "A7-07", "workshop_number": 7, "title": "Security Backlog", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux prioriser un backlog sécurité (top 10) afin de réduire rapidement les risques majeurs.", "acceptance_criteria": ["Top 10 actions sécurité identifiées", "Priorité + owner + dates", "Actions liées aux risques", "Suivi ageing possible", "Statut revue défini"]},
    # Workshop 8
    {"item_id": "A8-01", "workshop_number": 8, "title": "Canvas Standard v0", "module_name": "UX/UI Standards", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Lead Dev Canvas Apps, je veux définir des standards UX/UI afin d'améliorer la cohérence et la maintenabilité des apps.", "acceptance_criteria": ["Standards publiés", "Règles navigation/écrans définies", "Règles accessibilité minimales", "Patterns recommandés listés", "Statut v0 validé"]},
    {"item_id": "A8-02", "workshop_number": 8, "title": "Checklist Qualité Prod v0", "module_name": "Quality Checklist", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable qualité, je veux définir une checklist qualité prod afin de déterminer objectivement si une app est prod ready.", "acceptance_criteria": ["Checklist créée", "Critères minimum", "Critères de blocage identifiés", "Format d'évidence défini", "Version v0 publiée"]},
    {"item_id": "A8-03", "workshop_number": 8, "title": "Canvas App Catalog (critique)", "module_name": "App Inventory Enrichment", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux enrichir l'inventaire des apps critiques afin de prioriser la remédiation et la supervision.", "acceptance_criteria": ["Apps critiques identifiées", "Pour chaque app: owner + usage + env", "Criticité renseignée", "Dépendances/connexions notées", "Statut 'auditée/non auditée'"]},
    {"item_id": "A8-04", "workshop_number": 8, "title": "Canvas Quality Score v0", "module_name": "Canvas App Quality Index", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux calculer un score qualité Canvas afin de suivre la tendance et cibler les améliorations.", "acceptance_criteria": ["Méthode de scoring définie", "Score saisi pour 1 à 3 apps", "Causes principales capturées", "Tendance possible", "Version v0 enregistrée"]},
    {"item_id": "A8-05", "workshop_number": 8, "title": "Component Strategy", "module_name": "Reusable Components", "status_requirement": "OPTIONNEL", "user_story_fr": "En tant que Lead Dev, je veux définir une stratégie de composants réutilisables afin de réduire la duplication et améliorer la qualité.", "acceptance_criteria": ["Décision prise (oui/non)", "Si oui: catalogue composants défini", "Règles contribution/validation", "Stratégie versioning", "Exemple d'usage documenté"]},
    {"item_id": "A8-06", "workshop_number": 8, "title": "Observabilité (min)", "module_name": "Telemetry & Monitoring", "status_requirement": "À MINIMA", "user_story_fr": "En tant que Ops / support, je veux définir des règles de logs/monitoring minimales afin de détecter et diagnostiquer les incidents.", "acceptance_criteria": ["Événements à monitorer définis", "Destinataires alertes définis", "Seuils/critères d'alerte définis", "Process incident défini", "Preuves/logs accessibles"]},
    {"item_id": "A8-07", "workshop_number": 8, "title": "Backlog Atelier 8", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux créer un backlog d'amélioration Canvas afin de mettre les apps critiques au niveau prod.", "acceptance_criteria": ["Top 10 actions amélioration créées", "Lien aux apps concernées", "Owners + dates", "Priorités définies", "Mesure d'avancement prévue"]},
    # Workshop 9
    {"item_id": "A9-01", "workshop_number": 9, "title": "Flow Governance Rules", "module_name": "Flow Governance Policy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux définir une politique de gouvernance des flows afin de réduire les risques d'exploitation et de continuité.", "acceptance_criteria": ["Politique flows documentée", "Règles prod définies", "Règles de cycle de vie", "Exceptions cadrées", "Statut validé"]},
    {"item_id": "A9-02", "workshop_number": 9, "title": "Integration Policy v0", "module_name": "Integration & Connectors Policy", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir une politique d'intégration (connecteurs, HTTP, custom) afin de limiter les chemins de fuite et usages risqués.", "acceptance_criteria": ["Règles HTTP/custom listées", "Connecteurs sensibles encadrés", "Conditions d'approbation définies", "Exigences de preuve définies", "Version v0 validée"]},
    {"item_id": "A9-03", "workshop_number": 9, "title": "Identity Strategy for Flows", "module_name": "Flow Identity & Connections", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable Sécurité, je veux définir une stratégie d'identité pour les flows (comptes de service) afin d'éviter les dépendances à des comptes personnels.", "acceptance_criteria": ["Modèle comptes de service défini", "Règles d'utilisation en prod", "Gestion secrets/rotation définie", "Exceptions cadrées", "Statut validé"]},
    {"item_id": "A9-04", "workshop_number": 9, "title": "Flow Catalog (critique)", "module_name": "Flow Inventory", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Ops / support, je veux documenter les flows critiques (owner, objectifs, dépendances) afin de sécuriser le support et la continuité.", "acceptance_criteria": ["Top 10 flows critiques listés", "Owner + backup par flow", "Dépendances notées", "Env prod identifié", "Doc de support minimal lié"]},
    {"item_id": "A9-05", "workshop_number": 9, "title": "Monitoring Model", "module_name": "Operations & Monitoring", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Ops, je veux définir qui surveille quoi et qui est alerté afin de réduire le temps de détection et de résolution.", "acceptance_criteria": ["Modèle d'alerting défini", "Canaux d'alerte définis", "Responsables par périmètre", "SLA/horaires support définis", "Test d'alerte réalisé"]},
    {"item_id": "A9-06", "workshop_number": 9, "title": "Flow Risk Index v0", "module_name": "Risk Scoring", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux attribuer un indice de risque aux flows afin de prioriser les remédiations sur les éléments les plus critiques.", "acceptance_criteria": ["Critères de risque définis", "Scoring appliqué à flows critiques", "Seuils définis", "Résultats exploitables", "Version v0 enregistrée"]},
    {"item_id": "A9-07", "workshop_number": 9, "title": "Backlog Atelier 9", "module_name": "Action Plan", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux prioriser un backlog de remédiation flows afin de réduire le risque opérationnel rapidement.", "acceptance_criteria": ["Top 10 actions remédiation créées", "Actions liées aux flows", "Owners + dates", "Priorités définies", "Mesure d'avancement/aging possible"]},
    # Workshop 10
    {"item_id": "A10-01", "workshop_number": 10, "title": "Governance Playbook v1", "module_name": "Governance Documentation", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux valider un playbook de gouvernance afin de rendre la gouvernance durable et transmissible.", "acceptance_criteria": ["Playbook v1 approuvé", "Lien stocké dans Bizdesk365", "Sections minimales présentes", "Date/valideur enregistrés", "Process de mise à jour défini"]},
    {"item_id": "A10-02", "workshop_number": 10, "title": "Operating Model (cadence & comité)", "module_name": "Governance Cadence & Committee", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Responsable gouvernance, je veux formaliser le modèle opératoire (cadence, comités, owners) afin de faire vivre le run après le programme.", "acceptance_criteria": ["Comité(s) définis", "Cadence fixée", "Rôles/owners confirmés", "Règles de décision/escale définies", "Agenda type + compte-rendu standard"]},
    {"item_id": "A10-03", "workshop_number": 10, "title": "Roadmap 30/60/90", "module_name": "Roadmap", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Platform Owner, je veux définir une roadmap 30/60/90 afin de continuer l'amélioration post-programme.", "acceptance_criteria": ["Roadmap saisie (30/60/90)", "Actions priorisées", "Owners + dates", "Dépendances notées", "Critères de succès définis"]},
    {"item_id": "A10-04", "workshop_number": 10, "title": "Adoption Plan v0", "module_name": "Adoption & Change", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Change Manager, je veux définir un plan d'adoption afin d'augmenter l'usage conforme et réduire le shadow IT.", "acceptance_criteria": ["Publics cibles identifiés", "Messages clés définis", "Plan formations/communications", "Mesure adoption définie", "Version v0 validée"]},
    {"item_id": "A10-05", "workshop_number": 10, "title": "KPI Pack", "module_name": "Governance Metrics", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux définir un pack de KPIs et leurs règles de calcul afin de piloter la gouvernance sur des métriques stables.", "acceptance_criteria": ["Liste KPIs définie", "Définition + formule par KPI", "Fréquence de calcul", "Source de données", "Responsable de suivi"]},
    {"item_id": "A10-06", "workshop_number": 10, "title": "Programme Completion", "module_name": "Workshops Completion", "status_requirement": "OBLIGATOIRE", "user_story_fr": "En tant que Sponsor, je veux marquer le programme comme complété avec les livrables associés afin d'officialiser la transition vers le Run.", "acceptance_criteria": ["Ateliers marqués 'Completed'", "Livrables liés (preuves)", "Décision de transition Run enregistrée", "Backlog post-programme créé", "Date de clôture + sponsor validateur"]}
]

def get_workshop_definitions():
    return WORKSHOP_DEFINITIONS

def get_item_definitions():
    return ITEM_DEFINITIONS

def get_items_for_workshop(workshop_number: int):
    return [item for item in ITEM_DEFINITIONS if item["workshop_number"] == workshop_number]
