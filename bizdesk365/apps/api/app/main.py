from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

from app.db import connect_to_mongo, close_mongo_connection, get_database, seed_database
from app.security import (
    get_current_user, 
    UserInDB, 
    create_access_token, 
    verify_password,
    Token
)
from app.modules.registry import get_enabled_modules, Module
from app.modules.compliance import router as compliance_router
from app.modules.enterprise_brain import router as eb_router, ai_router
from app.modules.ai_governance import router as ai_gov_router
from app.modules.settings import router as settings_router
from app.modules.power_platform import router as pp_router

from datetime import timedelta

# Create FastAPI app
app = FastAPI(
    title="Bizdesk365 API",
    description="API multi-tenant pour la gouvernance et conformité",
    version="1.0.0"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for auth
class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
    roles: List[str]

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bizdesk365-api"}

# Auth endpoints
@api_router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    database = await get_database()
    
    user = await database.users.find_one(
        {"email": request.email},
        {"_id": 0}
    )
    
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "email": user["email"],
            "tenant_id": user["tenant_id"],
            "roles": user.get("roles", [])
        },
        expires_delta=timedelta(hours=8)
    )
    
    return Token(access_token=access_token, token_type="bearer")

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        tenant_id=current_user.tenant_id,
        roles=current_user.roles
    )

@api_router.get("/modules", response_model=List[Module])
async def get_modules(current_user: UserInDB = Depends(get_current_user)):
    """Get enabled modules for the current tenant"""
    return get_enabled_modules(current_user.tenant_id)

# Include module routers
api_router.include_router(compliance_router)
api_router.include_router(eb_router)
api_router.include_router(ai_router)
api_router.include_router(ai_gov_router)
api_router.include_router(settings_router)
api_router.include_router(pp_router)

# Include API router in app
app.include_router(api_router)

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    await seed_database()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()
