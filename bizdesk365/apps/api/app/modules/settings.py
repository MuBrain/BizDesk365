from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from ..security import get_current_user, get_tenant_id, UserInDB
from ..db import get_database

router = APIRouter(prefix="/settings", tags=["Settings"])

class ISOProfile(BaseModel):
    iso_code: str
    name: str
    enabled: bool

class ISOProfileUpdate(BaseModel):
    profiles: List[ISOProfile]

class AIPolicy(BaseModel):
    min_iqi_authorized: float
    min_iqi_assisted: float

@router.get("/iso", response_model=List[ISOProfile])
async def get_iso_profiles(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get ISO profiles for the tenant"""
    database = await get_database()
    
    profiles = await database.tenant_iso_profiles.find(
        {"tenant_id": tenant_id},
        {"_id": 0, "tenant_id": 0}
    ).to_list(100)
    
    return profiles

@router.put("/iso", response_model=List[ISOProfile])
async def update_iso_profiles(
    update: ISOProfileUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Update ISO profiles for the tenant"""
    database = await get_database()
    
    # Update each profile
    for profile in update.profiles:
        await database.tenant_iso_profiles.update_one(
            {"tenant_id": tenant_id, "iso_code": profile.iso_code},
            {"$set": {"enabled": profile.enabled}},
            upsert=True
        )
    
    # Return updated profiles
    profiles = await database.tenant_iso_profiles.find(
        {"tenant_id": tenant_id},
        {"_id": 0, "tenant_id": 0}
    ).to_list(100)
    
    return profiles

@router.get("/ai-policy", response_model=AIPolicy)
async def get_ai_policy(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get AI usage policy thresholds"""
    database = await get_database()
    
    policy = await database.ai_usage_policies.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0, "tenant_id": 0}
    )
    
    if not policy:
        # Return defaults
        return AIPolicy(min_iqi_authorized=0.80, min_iqi_assisted=0.60)
    
    return AIPolicy(
        min_iqi_authorized=policy.get("min_iqi_authorized", 0.80),
        min_iqi_assisted=policy.get("min_iqi_assisted", 0.60)
    )

@router.put("/ai-policy", response_model=AIPolicy)
async def update_ai_policy(
    policy: AIPolicy,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Update AI usage policy thresholds"""
    database = await get_database()
    
    # Validate thresholds
    if policy.min_iqi_authorized < policy.min_iqi_assisted:
        raise HTTPException(
            status_code=400,
            detail="Le seuil autorisé doit être supérieur au seuil assisté"
        )
    
    if not (0 <= policy.min_iqi_authorized <= 1) or not (0 <= policy.min_iqi_assisted <= 1):
        raise HTTPException(
            status_code=400,
            detail="Les seuils doivent être compris entre 0 et 1"
        )
    
    await database.ai_usage_policies.update_one(
        {"tenant_id": tenant_id},
        {"$set": {
            "min_iqi_authorized": policy.min_iqi_authorized,
            "min_iqi_assisted": policy.min_iqi_assisted
        }},
        upsert=True
    )
    
    return policy
