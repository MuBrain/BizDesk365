from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ..security import get_current_user, get_tenant_id, UserInDB
from ..db import get_database

router = APIRouter(prefix="/compliance", tags=["Compliance"])

class KPI(BaseModel):
    id: str
    name: str
    value: float
    measured_at: str

class MaturityResponse(BaseModel):
    score: float
    band: str  # "red", "yellow", "green"
    inputs: Dict[str, Any]
    iso_referentials: List[str]

@router.get("/kpis/latest", response_model=List[KPI])
async def get_latest_kpis(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get the latest compliance KPIs for the tenant"""
    database = await get_database()
    kpis = await database.compliance_kpis.find(
        {"tenant_id": tenant_id},
        {"_id": 0}
    ).to_list(100)
    return kpis

@router.get("/maturity", response_model=MaturityResponse)
async def get_maturity_score(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Calculate and return the maturity score with band classification"""
    database = await get_database()
    
    # Get KPIs
    kpis = await database.compliance_kpis.find(
        {"tenant_id": tenant_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get enabled ISO profiles
    iso_profiles = await database.tenant_iso_profiles.find(
        {"tenant_id": tenant_id, "enabled": True},
        {"_id": 0}
    ).to_list(100)
    
    # Calculate maturity score from KPIs
    maturity_index = 0.0
    policy_coverage = 0.0
    audit_freshness = 30
    
    inputs = {}
    for kpi in kpis:
        inputs[kpi["name"]] = kpi["value"]
        if kpi["name"] == "MaturityIndex":
            maturity_index = kpi["value"]
        elif kpi["name"] == "PolicyCoverage":
            policy_coverage = kpi["value"]
        elif kpi["name"] == "AuditFreshnessDays":
            audit_freshness = kpi["value"]
    
    # Compute composite score (weighted average)
    # Freshness score: 1.0 if < 7 days, 0.5 if < 30 days, 0.0 otherwise
    freshness_score = 1.0 if audit_freshness < 7 else (0.5 if audit_freshness < 30 else 0.0)
    
    score = (maturity_index * 0.4) + (policy_coverage * 0.4) + (freshness_score * 0.2)
    
    # Determine band
    if score >= 0.75:
        band = "green"
    elif score >= 0.50:
        band = "yellow"
    else:
        band = "red"
    
    iso_codes = [p["iso_code"] for p in iso_profiles]
    
    return MaturityResponse(
        score=round(score, 2),
        band=band,
        inputs=inputs,
        iso_referentials=iso_codes
    )
