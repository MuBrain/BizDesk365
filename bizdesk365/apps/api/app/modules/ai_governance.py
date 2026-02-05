from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from ..security import get_current_user, get_tenant_id, UserInDB
from ..db import get_database

router = APIRouter(prefix="/governance/ai", tags=["AI Governance"])

class CriticalAction(BaseModel):
    id: str
    title: str
    priority: str
    status: str

class GovernanceSummary(BaseModel):
    authorized_percentage: float
    assisted_percentage: float
    forbidden_percentage: float
    total_usages: int
    critical_actions: List[CriticalAction]
    traceability: Dict[str, int]

@router.get("/summary", response_model=GovernanceSummary)
async def get_governance_summary(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get executive AI governance summary"""
    database = await get_database()
    
    # Get all AI usage logs for tenant
    usage_logs = await database.ai_usage_logs.find(
        {"tenant_id": tenant_id},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(usage_logs)
    
    if total == 0:
        return GovernanceSummary(
            authorized_percentage=0,
            assisted_percentage=0,
            forbidden_percentage=0,
            total_usages=0,
            critical_actions=[],
            traceability={"logged": 0, "audited": 0, "anomalies": 0}
        )
    
    # Count by decision type
    authorized = sum(1 for log in usage_logs if log.get("decision") == "authorized")
    assisted = sum(1 for log in usage_logs if log.get("decision") == "assisted")
    forbidden = sum(1 for log in usage_logs if log.get("decision") == "forbidden")
    
    # Calculate percentages
    authorized_pct = round((authorized / total) * 100, 1)
    assisted_pct = round((assisted / total) * 100, 1)
    forbidden_pct = round((forbidden / total) * 100, 1)
    
    # Placeholder critical actions
    critical_actions = [
        CriticalAction(
            id="action-001",
            title="Revalider les documents avec IQI < 0.6",
            priority="high",
            status="pending"
        ),
        CriticalAction(
            id="action-002",
            title="Mettre à jour la politique d'utilisation IA",
            priority="medium",
            status="in_progress"
        ),
        CriticalAction(
            id="action-003",
            title="Former les utilisateurs aux bonnes pratiques IA",
            priority="low",
            status="planned"
        )
    ]
    
    # Traceability metrics (simplified)
    traceability = {
        "logged": total,
        "audited": int(total * 0.85),  # 85% audited
        "anomalies": forbidden  # Anomalies = forbidden usages
    }
    
    return GovernanceSummary(
        authorized_percentage=authorized_pct,
        assisted_percentage=assisted_pct,
        forbidden_percentage=forbidden_pct,
        total_usages=total,
        critical_actions=critical_actions,
        traceability=traceability
    )
