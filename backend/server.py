from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "bizdesk365-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI(
    title="Bizdesk365 API",
    description="API multi-tenant pour la gouvernance et conformité",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== Models ==============

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
    roles: List[str]

class UserInDB(BaseModel):
    id: str
    email: str
    tenant_id: str
    roles: List[str] = []

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

class KPI(BaseModel):
    id: str
    name: str
    value: float
    measured_at: str

class MaturityResponse(BaseModel):
    score: float
    band: str
    inputs: Dict[str, Any]
    iso_referentials: List[str]

class QualityResponse(BaseModel):
    iqi_global: float
    evidences: Dict[str, Any]

class Document(BaseModel):
    id: str
    title: str
    doc_type: str
    url: str
    last_updated: str
    confidence_score: float
    validated: bool
    owner: str

class AIUsageResponse(BaseModel):
    document_id: str
    document_title: str
    usage_status: str
    iqi_score: float
    reason: str

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

class ISOProfile(BaseModel):
    iso_code: str
    name: str
    enabled: bool

class ISOProfileUpdate(BaseModel):
    profiles: List[ISOProfile]

class AIPolicy(BaseModel):
    min_iqi_authorized: float
    min_iqi_assisted: float

class HealthStatus(BaseModel):
    status: str
    message: str
    module_enabled: bool

# ============== Security ==============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "iss": "bizdesk365"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        tenant_id = payload.get("tenant_id")
        if user_id is None or tenant_id is None:
            raise credentials_exception
        return UserInDB(id=user_id, email=email or "", tenant_id=tenant_id, roles=payload.get("roles", []))
    except JWTError:
        raise credentials_exception

def get_tenant_id(current_user: UserInDB = Depends(get_current_user)) -> str:
    return current_user.tenant_id

# ============== Module Registry ==============

MODULES: Dict[str, Module] = {
    "compliance": Module(
        id="compliance", name="Conformité ISO", description="Tableaux de bord et rapports de conformité ISO", enabled=True,
        nav_items=[NavItem(id="compliance-overview", label="Vue d'ensemble", path="/dashboards/compliance", icon="ShieldCheck")],
        feature_flags={"maturity_score": True, "audit_tracking": True}
    ),
    "enterprise_brain": Module(
        id="enterprise_brain", name="Enterprise Brain", description="Intelligence documentaire et qualité de l'information", enabled=True,
        nav_items=[NavItem(id="eb-overview", label="Qualité documentaire", path="/dashboards/enterprise-brain", icon="Brain")],
        feature_flags={"iqi_score": True, "document_validation": True}
    ),
    "ai_governance": Module(
        id="ai_governance", name="Gouvernance IA", description="Tableau de bord exécutif de gouvernance IA", enabled=True,
        nav_items=[NavItem(id="ai-gov-dashboard", label="Tableau de bord IA", path="/dashboards/ai-governance", icon="Bot")],
        feature_flags={"usage_tracking": True, "policy_enforcement": True}
    ),
    "settings": Module(
        id="settings", name="Paramètres", description="Configuration de l'organisation", enabled=True,
        nav_items=[NavItem(id="settings-main", label="Paramètres", path="/settings", icon="Settings")],
        feature_flags={}
    ),
    "power_platform": Module(
        id="power_platform", name="Power Platform Governance", description="Gouvernance Microsoft Power Platform", enabled=False,
        nav_items=[NavItem(id="pp-overview", label="Power Platform", path="/dashboards/power-platform", icon="Zap")],
        feature_flags={"monitoring": False, "policy_enforcement": False}
    )
}

def get_enabled_modules(tenant_id: str) -> List[Module]:
    return list(MODULES.values())

# ============== Database Seeding ==============

async def seed_database():
    demo_tenant_id = "11111111-1111-1111-1111-111111111111"
    
    existing_tenant = await db.tenants.find_one({"id": demo_tenant_id})
    if existing_tenant:
        logger.info("Database already seeded")
        return
    
    await db.tenants.insert_one({"id": demo_tenant_id, "name": "Demo Org", "created_at": datetime.now(timezone.utc).isoformat()})
    
    await db.compliance_kpis.insert_many([
        {"id": "kpi-001", "tenant_id": demo_tenant_id, "name": "MaturityIndex", "value": 0.72, "measured_at": "2024-01-15T10:00:00Z"},
        {"id": "kpi-002", "tenant_id": demo_tenant_id, "name": "PolicyCoverage", "value": 0.85, "measured_at": "2024-01-15T10:00:00Z"},
        {"id": "kpi-003", "tenant_id": demo_tenant_id, "name": "AuditFreshnessDays", "value": 15, "measured_at": "2024-01-15T10:00:00Z"},
    ])
    
    await db.tenant_iso_profiles.insert_many([
        {"tenant_id": demo_tenant_id, "iso_code": "ISO9001", "enabled": True, "name": "Qualité"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO27001", "enabled": True, "name": "Sécurité de l'information"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO14001", "enabled": False, "name": "Environnement"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO45001", "enabled": False, "name": "Santé et sécurité"},
    ])
    
    await db.ai_usage_policies.insert_one({"tenant_id": demo_tenant_id, "min_iqi_authorized": 0.80, "min_iqi_assisted": 0.60})
    
    source_id = "source-001"
    await db.knowledge_sources.insert_one({
        "id": source_id, "tenant_id": demo_tenant_id, "type": "SharePoint",
        "name": "Documentation Interne", "description": "Base documentaire SharePoint principale"
    })
    
    await db.knowledge_documents.insert_many([
        {"id": "doc-001", "tenant_id": demo_tenant_id, "source_id": source_id, "title": "Politique de Sécurité Informatique", "doc_type": "Politique", "url": "https://sharepoint.example.com/doc/001", "last_updated": "2024-01-10T14:30:00Z", "confidence_score": 0.92, "validated": True, "owner": "Jean Dupont"},
        {"id": "doc-002", "tenant_id": demo_tenant_id, "source_id": source_id, "title": "Procédure de Gestion des Incidents", "doc_type": "Procédure", "url": "https://sharepoint.example.com/doc/002", "last_updated": "2023-11-20T09:15:00Z", "confidence_score": 0.75, "validated": True, "owner": "Marie Martin"},
        {"id": "doc-003", "tenant_id": demo_tenant_id, "source_id": source_id, "title": "Guide d'Utilisation IA", "doc_type": "Guide", "url": "https://sharepoint.example.com/doc/003", "last_updated": "2024-01-05T16:45:00Z", "confidence_score": 0.88, "validated": False, "owner": "Pierre Durand"},
        {"id": "doc-004", "tenant_id": demo_tenant_id, "source_id": source_id, "title": "Charte Éthique IA", "doc_type": "Charte", "url": "https://sharepoint.example.com/doc/004", "last_updated": "2023-08-01T11:00:00Z", "confidence_score": 0.55, "validated": False, "owner": "Sophie Bernard"},
    ])
    
    await db.ai_usage_logs.insert_many([
        {"tenant_id": demo_tenant_id, "document_id": "doc-001", "decision": "authorized", "checked_at": "2024-01-15T08:00:00Z", "intent": "Analyse de conformité"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-002", "decision": "assisted", "checked_at": "2024-01-15T09:00:00Z", "intent": "Recherche procédure"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-003", "decision": "authorized", "checked_at": "2024-01-15T10:00:00Z", "intent": "Formation utilisateur"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-004", "decision": "forbidden", "checked_at": "2024-01-15T11:00:00Z", "intent": "Rédaction rapport"},
    ])
    
    await db.users.insert_one({
        "id": "user-001", "username": "demo@bizdesk365.local", "email": "demo@bizdesk365.local",
        "password_hash": pwd_context.hash("demo"), "tenant_id": demo_tenant_id, "roles": ["admin", "user"]
    })
    
    logger.info("Database seeded successfully")

# ============== Routes ==============

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bizdesk365-api"}

@api_router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    user = await db.users.find_one({"email": request.email}, {"_id": 0})
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    access_token = create_access_token(data={"sub": user["id"], "email": user["email"], "tenant_id": user["tenant_id"], "roles": user.get("roles", [])})
    return Token(access_token=access_token, token_type="bearer")

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=current_user.email, tenant_id=current_user.tenant_id, roles=current_user.roles)

@api_router.get("/modules", response_model=List[Module])
async def get_modules(current_user: UserInDB = Depends(get_current_user)):
    return get_enabled_modules(current_user.tenant_id)

# Compliance endpoints
@api_router.get("/compliance/kpis/latest", response_model=List[KPI])
async def get_latest_kpis(tenant_id: str = Depends(get_tenant_id)):
    kpis = await db.compliance_kpis.find({"tenant_id": tenant_id}, {"_id": 0}).to_list(100)
    return kpis

@api_router.get("/compliance/maturity", response_model=MaturityResponse)
async def get_maturity_score(tenant_id: str = Depends(get_tenant_id)):
    kpis = await db.compliance_kpis.find({"tenant_id": tenant_id}, {"_id": 0}).to_list(100)
    iso_profiles = await db.tenant_iso_profiles.find({"tenant_id": tenant_id, "enabled": True}, {"_id": 0}).to_list(100)
    
    maturity_index, policy_coverage, audit_freshness = 0.0, 0.0, 30
    inputs = {}
    for kpi in kpis:
        inputs[kpi["name"]] = kpi["value"]
        if kpi["name"] == "MaturityIndex": maturity_index = kpi["value"]
        elif kpi["name"] == "PolicyCoverage": policy_coverage = kpi["value"]
        elif kpi["name"] == "AuditFreshnessDays": audit_freshness = kpi["value"]
    
    freshness_score = 1.0 if audit_freshness < 7 else (0.5 if audit_freshness < 30 else 0.0)
    score = (maturity_index * 0.4) + (policy_coverage * 0.4) + (freshness_score * 0.2)
    band = "green" if score >= 0.75 else ("yellow" if score >= 0.50 else "red")
    
    return MaturityResponse(score=round(score, 2), band=band, inputs=inputs, iso_referentials=[p["iso_code"] for p in iso_profiles])

# Enterprise Brain endpoints
@api_router.get("/enterprise-brain/quality", response_model=QualityResponse)
async def get_quality_metrics(tenant_id: str = Depends(get_tenant_id)):
    documents = await db.knowledge_documents.find({"tenant_id": tenant_id}, {"_id": 0}).to_list(1000)
    if not documents:
        return QualityResponse(iqi_global=0.0, evidences={"total_documents": 0, "validated_count": 0, "avg_confidence": 0.0, "freshness_score": 0.0})
    
    total = len(documents)
    validated = sum(1 for d in documents if d.get("validated", False))
    avg_confidence = sum(d.get("confidence_score", 0) for d in documents) / total
    
    now = datetime.now(timezone.utc)
    fresh_count = 0
    for doc in documents:
        try:
            last_updated = datetime.fromisoformat(doc["last_updated"].replace("Z", "+00:00"))
            if (now - last_updated).days < 90: fresh_count += 1
        except: pass
    
    freshness_score = fresh_count / total if total > 0 else 0
    validation_score = validated / total if total > 0 else 0
    iqi_global = (validation_score * 0.3) + (avg_confidence * 0.5) + (freshness_score * 0.2)
    
    return QualityResponse(iqi_global=round(iqi_global, 2), evidences={
        "total_documents": total, "validated_count": validated, "validation_rate": round(validation_score * 100, 1),
        "avg_confidence": round(avg_confidence * 100, 1), "freshness_score": round(freshness_score * 100, 1), "fresh_documents": fresh_count
    })

@api_router.get("/enterprise-brain/documents", response_model=List[Document])
async def get_documents(tenant_id: str = Depends(get_tenant_id)):
    documents = await db.knowledge_documents.find({"tenant_id": tenant_id}, {"_id": 0, "source_id": 0, "tenant_id": 0}).to_list(1000)
    return documents

@api_router.get("/enterprise-brain/document/{document_id}")
async def get_document(document_id: str, tenant_id: str = Depends(get_tenant_id)):
    document = await db.knowledge_documents.find_one({"id": document_id, "tenant_id": tenant_id}, {"_id": 0})
    if not document: raise HTTPException(status_code=404, detail="Document non trouvé")
    return document

@api_router.get("/ai/usage/document/{document_id}", response_model=AIUsageResponse)
async def get_ai_usage_for_document(document_id: str, tenant_id: str = Depends(get_tenant_id)):
    document = await db.knowledge_documents.find_one({"id": document_id, "tenant_id": tenant_id}, {"_id": 0})
    if not document: raise HTTPException(status_code=404, detail="Document non trouvé")
    
    policy = await db.ai_usage_policies.find_one({"tenant_id": tenant_id}, {"_id": 0})
    if not policy: policy = {"min_iqi_authorized": 0.80, "min_iqi_assisted": 0.60}
    
    iqi_score = document.get("confidence_score", 0)
    is_validated = document.get("validated", False)
    
    if is_validated and iqi_score >= policy["min_iqi_authorized"]:
        usage_status, reason = "authorized", "Document validé avec un score IQI suffisant"
    elif iqi_score >= policy["min_iqi_assisted"]:
        usage_status, reason = "assisted", "Score IQI intermédiaire - utilisation assistée uniquement"
    else:
        usage_status, reason = "forbidden", "Score IQI insuffisant ou document non validé"
    
    return AIUsageResponse(document_id=document_id, document_title=document.get("title", ""), usage_status=usage_status, iqi_score=iqi_score, reason=reason)

# AI Governance endpoints
@api_router.get("/governance/ai/summary", response_model=GovernanceSummary)
async def get_governance_summary(tenant_id: str = Depends(get_tenant_id)):
    usage_logs = await db.ai_usage_logs.find({"tenant_id": tenant_id}, {"_id": 0}).to_list(10000)
    total = len(usage_logs)
    
    if total == 0:
        return GovernanceSummary(authorized_percentage=0, assisted_percentage=0, forbidden_percentage=0, total_usages=0, critical_actions=[], traceability={"logged": 0, "audited": 0, "anomalies": 0})
    
    authorized = sum(1 for log in usage_logs if log.get("decision") == "authorized")
    assisted = sum(1 for log in usage_logs if log.get("decision") == "assisted")
    forbidden = sum(1 for log in usage_logs if log.get("decision") == "forbidden")
    
    critical_actions = [
        CriticalAction(id="action-001", title="Revalider les documents avec IQI < 0.6", priority="high", status="pending"),
        CriticalAction(id="action-002", title="Mettre à jour la politique d'utilisation IA", priority="medium", status="in_progress"),
        CriticalAction(id="action-003", title="Former les utilisateurs aux bonnes pratiques IA", priority="low", status="planned")
    ]
    
    return GovernanceSummary(
        authorized_percentage=round((authorized / total) * 100, 1),
        assisted_percentage=round((assisted / total) * 100, 1),
        forbidden_percentage=round((forbidden / total) * 100, 1),
        total_usages=total,
        critical_actions=critical_actions,
        traceability={"logged": total, "audited": int(total * 0.85), "anomalies": forbidden}
    )

# Settings endpoints
@api_router.get("/settings/iso", response_model=List[ISOProfile])
async def get_iso_profiles(tenant_id: str = Depends(get_tenant_id)):
    profiles = await db.tenant_iso_profiles.find({"tenant_id": tenant_id}, {"_id": 0, "tenant_id": 0}).to_list(100)
    return profiles

@api_router.put("/settings/iso", response_model=List[ISOProfile])
async def update_iso_profiles(update: ISOProfileUpdate, tenant_id: str = Depends(get_tenant_id)):
    for profile in update.profiles:
        await db.tenant_iso_profiles.update_one({"tenant_id": tenant_id, "iso_code": profile.iso_code}, {"$set": {"enabled": profile.enabled}}, upsert=True)
    profiles = await db.tenant_iso_profiles.find({"tenant_id": tenant_id}, {"_id": 0, "tenant_id": 0}).to_list(100)
    return profiles

@api_router.get("/settings/ai-policy", response_model=AIPolicy)
async def get_ai_policy(tenant_id: str = Depends(get_tenant_id)):
    policy = await db.ai_usage_policies.find_one({"tenant_id": tenant_id}, {"_id": 0, "tenant_id": 0})
    if not policy: return AIPolicy(min_iqi_authorized=0.80, min_iqi_assisted=0.60)
    return AIPolicy(min_iqi_authorized=policy.get("min_iqi_authorized", 0.80), min_iqi_assisted=policy.get("min_iqi_assisted", 0.60))

@api_router.put("/settings/ai-policy", response_model=AIPolicy)
async def update_ai_policy(policy: AIPolicy, tenant_id: str = Depends(get_tenant_id)):
    if policy.min_iqi_authorized < policy.min_iqi_assisted:
        raise HTTPException(status_code=400, detail="Le seuil autorisé doit être supérieur au seuil assisté")
    if not (0 <= policy.min_iqi_authorized <= 1) or not (0 <= policy.min_iqi_assisted <= 1):
        raise HTTPException(status_code=400, detail="Les seuils doivent être compris entre 0 et 1")
    await db.ai_usage_policies.update_one({"tenant_id": tenant_id}, {"$set": {"min_iqi_authorized": policy.min_iqi_authorized, "min_iqi_assisted": policy.min_iqi_assisted}}, upsert=True)
    return policy

# Power Platform stub
@api_router.get("/power-platform/health", response_model=HealthStatus)
async def get_power_platform_health(current_user: UserInDB = Depends(get_current_user)):
    return HealthStatus(status="coming_soon", message="Module Power Platform Governance en cours de développement", module_enabled=False)

# Include the router
app.include_router(api_router)

# Events
@app.on_event("startup")
async def startup():
    await seed_database()

@app.on_event("shutdown")
async def shutdown():
    client.close()
