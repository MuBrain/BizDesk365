from typing import List, Dict, Any
from pydantic import BaseModel

class NavItem(BaseModel):
    id: str
    label: str
    path: str
    icon: str

class Module(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool = True
    nav_items: List[NavItem] = []
    feature_flags: Dict[str, bool] = {}

# Module definitions
MODULES: Dict[str, Module] = {
    "compliance": Module(
        id="compliance",
        name="Conformité ISO",
        description="Tableaux de bord et rapports de conformité ISO",
        enabled=True,
        nav_items=[
            NavItem(id="compliance-overview", label="Vue d'ensemble", path="/dashboards/compliance", icon="ShieldCheck")
        ],
        feature_flags={"maturity_score": True, "audit_tracking": True}
    ),
    "enterprise_brain": Module(
        id="enterprise_brain",
        name="Enterprise Brain",
        description="Intelligence documentaire et qualité de l'information",
        enabled=True,
        nav_items=[
            NavItem(id="eb-overview", label="Qualité documentaire", path="/dashboards/enterprise-brain", icon="Brain")
        ],
        feature_flags={"iqi_score": True, "document_validation": True}
    ),
    "ai_governance": Module(
        id="ai_governance",
        name="Gouvernance IA",
        description="Tableau de bord exécutif de gouvernance IA",
        enabled=True,
        nav_items=[
            NavItem(id="ai-gov-dashboard", label="Tableau de bord IA", path="/dashboards/ai-governance", icon="Bot")
        ],
        feature_flags={"usage_tracking": True, "policy_enforcement": True}
    ),
    "settings": Module(
        id="settings",
        name="Paramètres",
        description="Configuration de l'organisation",
        enabled=True,
        nav_items=[
            NavItem(id="settings-main", label="Paramètres", path="/settings", icon="Settings")
        ],
        feature_flags={}
    ),
    "power_platform": Module(
        id="power_platform",
        name="Power Platform Governance",
        description="Gouvernance Microsoft Power Platform",
        enabled=False,  # Stub - coming soon
        nav_items=[
            NavItem(id="pp-overview", label="Power Platform", path="/dashboards/power-platform", icon="Zap")
        ],
        feature_flags={"monitoring": False, "policy_enforcement": False}
    )
}

def get_enabled_modules(tenant_id: str) -> List[Module]:
    """Get all enabled modules for a tenant"""
    # In a real implementation, this would check tenant-specific module subscriptions
    # For MVP, we return all modules (including disabled ones for UI purposes)
    return list(MODULES.values())

def get_module(module_id: str) -> Module | None:
    """Get a specific module by ID"""
    return MODULES.get(module_id)

def is_module_enabled(module_id: str, tenant_id: str) -> bool:
    """Check if a module is enabled for a tenant"""
    module = MODULES.get(module_id)
    if not module:
        return False
    # In a real implementation, check tenant subscription
    return module.enabled
