from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..security import get_current_user, UserInDB

router = APIRouter(prefix="/power-platform", tags=["Power Platform Governance"])

class HealthStatus(BaseModel):
    status: str
    message: str
    module_enabled: bool

@router.get("/health", response_model=HealthStatus)
async def get_health(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get Power Platform module health status (stub)"""
    return HealthStatus(
        status="coming_soon",
        message="Module Power Platform Governance en cours de développement",
        module_enabled=False
    )
