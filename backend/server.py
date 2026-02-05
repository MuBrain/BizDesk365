from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query
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

# Import Power Platform seed data
from power_platform_seed import WORKSHOP_DEFINITIONS, ITEM_DEFINITIONS, get_items_for_workshop

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

# ============== Power Platform Models ==============

class PPWorkshopDefinition(BaseModel):
    workshop_number: int
    title: str
    description: str
    completion_criteria: List[str]

class PPItemDefinition(BaseModel):
    item_id: str
    workshop_number: int
    title: str
    module_name: str
    status_requirement: str
    user_story_fr: str
    acceptance_criteria: List[str]

class PPProgram(BaseModel):
    id: str
    tenant_id: str
    name: str
    status: str  # not_started, in_progress, completed
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_by: str
    created_at: str
    updated_at: str

class PPWorkshopInstance(BaseModel):
    id: str
    program_id: str
    workshop_number: int
    status: str  # not_started, in_progress, completed
    completion_criteria_state: Dict[str, bool] = {}
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class PPItemInstance(BaseModel):
    id: str
    program_id: str
    item_id: str
    workshop_number: int
    status: str  # not_started, in_progress, done, validated
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None
    notes_markdown: Optional[str] = None
    acceptance_state: Dict[str, bool] = {}
    done_override: bool = False
    validated_by: Optional[str] = None
    validated_at: Optional[str] = None
    created_at: str
    updated_at: str

class PPAction(BaseModel):
    id: str
    program_id: str
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str  # low, medium, high, critical
    status: str  # open, in_progress, done, closed
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None
    created_at: str
    updated_at: str

class PPDecision(BaseModel):
    id: str
    program_id: str
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    decision_text: str
    decided_by: str
    decided_at: str
    evidence_links: List[str] = []
    created_at: str

class PPEvidence(BaseModel):
    id: str
    program_id: str
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    evidence_type: str  # document, link, screenshot, file
    title: str
    url: Optional[str] = None
    file_id: Optional[str] = None
    date: str
    owner_user_id: Optional[str] = None
    created_at: str

class PPKPIs(BaseModel):
    workshop_completion_pct: float
    workshops_completed: int
    total_workshops: int
    items_total: int
    items_done: int
    items_validated: int
    items_in_progress: int
    items_not_started: int
    actions_open_count: int
    actions_ageing_avg_days: float
    actions_ageing_max_days: int
    decisions_count: int
    evidence_count: int
    ownership_missing_pct: float

# ============== Update/Create Models ==============

class PPItemInstanceUpdate(BaseModel):
    status: Optional[str] = None
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None
    notes_markdown: Optional[str] = None
    acceptance_state: Optional[Dict[str, bool]] = None
    done_override: Optional[bool] = None

class PPItemInstanceValidate(BaseModel):
    validated: bool

class PPWorkshopUpdate(BaseModel):
    status: Optional[str] = None
    completion_criteria_state: Optional[Dict[str, bool]] = None

class PPActionCreate(BaseModel):
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None

class PPActionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None

class PPDecisionCreate(BaseModel):
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    decision_text: str
    evidence_links: List[str] = []

class PPEvidenceCreate(BaseModel):
    workshop_number: Optional[int] = None
    item_id: Optional[str] = None
    evidence_type: str
    title: str
    url: Optional[str] = None

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
        id="power_platform", name="Power Platform Governance", description="Gouvernance Microsoft Power Platform", enabled=True,
        nav_items=[NavItem(id="pp-overview", label="Power Platform", path="/dashboards/power-platform", icon="Zap")],
        feature_flags={"monitoring": True, "policy_enforcement": True}
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
        "password_hash": pwd_context.hash("demo"), "tenant_id": demo_tenant_id, "roles": ["admin", "user", "PlatformOwner"]
    })
    
    # Seed workshop and item definitions (global)
    existing_workshops = await db.pp_workshop_definitions.find_one()
    if not existing_workshops:
        await db.pp_workshop_definitions.insert_many(WORKSHOP_DEFINITIONS)
        await db.pp_item_definitions.insert_many(ITEM_DEFINITIONS)
        logger.info("Power Platform definitions seeded")
    
    logger.info("Database seeded successfully")

# ============== Helper Functions for Power Platform ==============

async def get_or_create_program(tenant_id: str, user_id: str) -> dict:
    """Get or create a governance program for the tenant"""
    program = await db.pp_programs.find_one({"tenant_id": tenant_id}, {"_id": 0})
    
    if not program:
        now = datetime.now(timezone.utc).isoformat()
        program = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "name": "Programme de Gouvernance Power Platform",
            "status": "not_started",
            "start_date": None,
            "end_date": None,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now
        }
        await db.pp_programs.insert_one(program)
        
        # Create workshop instances
        for ws_def in WORKSHOP_DEFINITIONS:
            criteria_state = {c: False for c in ws_def["completion_criteria"]}
            workshop = {
                "id": str(uuid.uuid4()),
                "program_id": program["id"],
                "workshop_number": ws_def["workshop_number"],
                "status": "not_started",
                "completion_criteria_state": criteria_state,
                "started_at": None,
                "completed_at": None
            }
            await db.pp_workshops.insert_one(workshop)
        
        # Create item instances
        for item_def in ITEM_DEFINITIONS:
            acceptance_state = {c: False for c in item_def["acceptance_criteria"]}
            item = {
                "id": str(uuid.uuid4()),
                "program_id": program["id"],
                "item_id": item_def["item_id"],
                "workshop_number": item_def["workshop_number"],
                "status": "not_started",
                "owner_user_id": None,
                "due_date": None,
                "notes_markdown": None,
                "acceptance_state": acceptance_state,
                "done_override": False,
                "validated_by": None,
                "validated_at": None,
                "created_at": now,
                "updated_at": now
            }
            await db.pp_item_instances.insert_one(item)
        
        logger.info(f"Created new program for tenant {tenant_id}")
    
    return program

async def calculate_pp_kpis(program_id: str) -> dict:
    """Calculate KPIs for a program"""
    now = datetime.now(timezone.utc)
    
    # Get workshops
    workshops = await db.pp_workshops.find({"program_id": program_id}, {"_id": 0}).to_list(100)
    workshops_completed = sum(1 for w in workshops if w["status"] == "completed")
    
    # Get items
    items = await db.pp_item_instances.find({"program_id": program_id}, {"_id": 0}).to_list(1000)
    items_total = len(items)
    items_done = sum(1 for i in items if i["status"] == "done")
    items_validated = sum(1 for i in items if i["status"] == "validated")
    items_in_progress = sum(1 for i in items if i["status"] == "in_progress")
    items_not_started = sum(1 for i in items if i["status"] == "not_started")
    
    # Get actions
    actions = await db.pp_actions.find({"program_id": program_id}, {"_id": 0}).to_list(10000)
    open_actions = [a for a in actions if a["status"] in ["open", "in_progress"]]
    actions_open_count = len(open_actions)
    
    # Calculate ageing
    ageing_days = []
    for action in open_actions:
        try:
            created = datetime.fromisoformat(action["created_at"].replace("Z", "+00:00"))
            days = (now - created).days
            ageing_days.append(days)
        except:
            pass
    
    actions_ageing_avg_days = sum(ageing_days) / len(ageing_days) if ageing_days else 0
    actions_ageing_max_days = max(ageing_days) if ageing_days else 0
    
    # Get decisions and evidence
    decisions = await db.pp_decisions.find({"program_id": program_id}, {"_id": 0}).to_list(10000)
    evidence = await db.pp_evidence.find({"program_id": program_id}, {"_id": 0}).to_list(10000)
    
    # Calculate ownership missing
    items_without_owner = sum(1 for i in items if not i.get("owner_user_id"))
    actions_without_owner = sum(1 for a in open_actions if not a.get("owner_user_id"))
    total_items_and_actions = items_total + len(open_actions)
    ownership_missing_pct = ((items_without_owner + actions_without_owner) / total_items_and_actions * 100) if total_items_and_actions > 0 else 0
    
    return {
        "workshop_completion_pct": round(workshops_completed / 10 * 100, 1),
        "workshops_completed": workshops_completed,
        "total_workshops": 10,
        "items_total": items_total,
        "items_done": items_done,
        "items_validated": items_validated,
        "items_in_progress": items_in_progress,
        "items_not_started": items_not_started,
        "actions_open_count": actions_open_count,
        "actions_ageing_avg_days": round(actions_ageing_avg_days, 1),
        "actions_ageing_max_days": actions_ageing_max_days,
        "decisions_count": len(decisions),
        "evidence_count": len(evidence),
        "ownership_missing_pct": round(ownership_missing_pct, 1)
    }

async def check_workshop_completion(program_id: str, workshop_number: int):
    """Check if workshop should be marked as completed"""
    workshop = await db.pp_workshops.find_one(
        {"program_id": program_id, "workshop_number": workshop_number},
        {"_id": 0}
    )
    if not workshop:
        return
    
    # Check all completion criteria are checked
    criteria_all_checked = all(workshop.get("completion_criteria_state", {}).values())
    
    # Check all mandatory items are done or validated
    items = await db.pp_item_instances.find(
        {"program_id": program_id, "workshop_number": workshop_number},
        {"_id": 0}
    ).to_list(100)
    
    # Get item definitions to check mandatory status
    item_defs = {item["item_id"]: item for item in ITEM_DEFINITIONS if item["workshop_number"] == workshop_number}
    
    mandatory_items_complete = True
    for item in items:
        item_def = item_defs.get(item["item_id"])
        if item_def and item_def["status_requirement"] == "OBLIGATOIRE":
            if item["status"] not in ["done", "validated"]:
                mandatory_items_complete = False
                break
    
    if criteria_all_checked and mandatory_items_complete:
        await db.pp_workshops.update_one(
            {"program_id": program_id, "workshop_number": workshop_number},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )

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

# ============== Power Platform Governance Endpoints ==============

@api_router.get("/power-platform/program")
async def get_pp_program(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get or create the governance program for the tenant"""
    program = await get_or_create_program(tenant_id, current_user.id)
    return program

@api_router.get("/power-platform/kpis", response_model=PPKPIs)
async def get_pp_kpis(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get KPIs for the governance program"""
    program = await get_or_create_program(tenant_id, current_user.id)
    return await calculate_pp_kpis(program["id"])

@api_router.get("/power-platform/workshops")
async def get_pp_workshops(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all workshops with their status and progress"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    workshops = await db.pp_workshops.find(
        {"program_id": program["id"]},
        {"_id": 0}
    ).sort("workshop_number", 1).to_list(100)
    
    # Enrich with definitions and item progress
    result = []
    for ws in workshops:
        ws_def = next((d for d in WORKSHOP_DEFINITIONS if d["workshop_number"] == ws["workshop_number"]), None)
        
        # Get items for this workshop
        items = await db.pp_item_instances.find(
            {"program_id": program["id"], "workshop_number": ws["workshop_number"]},
            {"_id": 0}
        ).to_list(100)
        
        items_total = len(items)
        items_done = sum(1 for i in items if i["status"] in ["done", "validated"])
        
        # Get actions count for this workshop
        actions = await db.pp_actions.find(
            {"program_id": program["id"], "workshop_number": ws["workshop_number"], "status": {"$in": ["open", "in_progress"]}},
            {"_id": 0}
        ).to_list(1000)
        
        # Get decisions count for this workshop
        decisions = await db.pp_decisions.find(
            {"program_id": program["id"], "workshop_number": ws["workshop_number"]},
            {"_id": 0}
        ).to_list(1000)
        
        result.append({
            **ws,
            "title": ws_def["title"] if ws_def else "",
            "description": ws_def["description"] if ws_def else "",
            "completion_criteria": ws_def["completion_criteria"] if ws_def else [],
            "items_total": items_total,
            "items_done": items_done,
            "items_progress_pct": round(items_done / items_total * 100, 1) if items_total > 0 else 0,
            "open_actions_count": len(actions),
            "decisions_count": len(decisions)
        })
    
    return result

@api_router.get("/power-platform/workshops/{workshop_number}")
async def get_pp_workshop_detail(
    workshop_number: int,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get detailed workshop with items"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    workshop = await db.pp_workshops.find_one(
        {"program_id": program["id"], "workshop_number": workshop_number},
        {"_id": 0}
    )
    
    if not workshop:
        raise HTTPException(status_code=404, detail="Atelier non trouvé")
    
    ws_def = next((d for d in WORKSHOP_DEFINITIONS if d["workshop_number"] == workshop_number), None)
    
    # Get items with definitions
    items = await db.pp_item_instances.find(
        {"program_id": program["id"], "workshop_number": workshop_number},
        {"_id": 0}
    ).to_list(100)
    
    enriched_items = []
    for item in items:
        item_def = next((d for d in ITEM_DEFINITIONS if d["item_id"] == item["item_id"]), None)
        enriched_items.append({
            **item,
            "title": item_def["title"] if item_def else "",
            "module_name": item_def["module_name"] if item_def else "",
            "status_requirement": item_def["status_requirement"] if item_def else "",
            "user_story_fr": item_def["user_story_fr"] if item_def else "",
            "acceptance_criteria": item_def["acceptance_criteria"] if item_def else []
        })
    
    return {
        **workshop,
        "title": ws_def["title"] if ws_def else "",
        "description": ws_def["description"] if ws_def else "",
        "completion_criteria": ws_def["completion_criteria"] if ws_def else [],
        "items": enriched_items
    }

@api_router.patch("/power-platform/workshops/{workshop_number}")
async def update_pp_workshop(
    workshop_number: int,
    update: PPWorkshopUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Update workshop status or completion criteria"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    update_data = {}
    if update.status:
        update_data["status"] = update.status
        if update.status == "in_progress" and not await db.pp_workshops.find_one(
            {"program_id": program["id"], "workshop_number": workshop_number, "started_at": {"$ne": None}}
        ):
            update_data["started_at"] = datetime.now(timezone.utc).isoformat()
    
    if update.completion_criteria_state:
        update_data["completion_criteria_state"] = update.completion_criteria_state
    
    if update_data:
        await db.pp_workshops.update_one(
            {"program_id": program["id"], "workshop_number": workshop_number},
            {"$set": update_data}
        )
    
    # Check if workshop should be completed
    await check_workshop_completion(program["id"], workshop_number)
    
    return await db.pp_workshops.find_one(
        {"program_id": program["id"], "workshop_number": workshop_number},
        {"_id": 0}
    )

@api_router.get("/power-platform/items")
async def get_pp_items(
    workshop_number: Optional[int] = None,
    status: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get item instances with optional filters"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    query = {"program_id": program["id"]}
    if workshop_number:
        query["workshop_number"] = workshop_number
    if status:
        query["status"] = status
    
    items = await db.pp_item_instances.find(query, {"_id": 0}).to_list(1000)
    
    # Enrich with definitions
    enriched_items = []
    for item in items:
        item_def = next((d for d in ITEM_DEFINITIONS if d["item_id"] == item["item_id"]), None)
        enriched_items.append({
            **item,
            "title": item_def["title"] if item_def else "",
            "module_name": item_def["module_name"] if item_def else "",
            "status_requirement": item_def["status_requirement"] if item_def else "",
            "user_story_fr": item_def["user_story_fr"] if item_def else "",
            "acceptance_criteria": item_def["acceptance_criteria"] if item_def else []
        })
    
    return enriched_items

@api_router.get("/power-platform/items/{item_id}")
async def get_pp_item(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific item instance"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    item = await db.pp_item_instances.find_one(
        {"program_id": program["id"], "item_id": item_id},
        {"_id": 0}
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    
    item_def = next((d for d in ITEM_DEFINITIONS if d["item_id"] == item_id), None)
    
    return {
        **item,
        "title": item_def["title"] if item_def else "",
        "module_name": item_def["module_name"] if item_def else "",
        "status_requirement": item_def["status_requirement"] if item_def else "",
        "user_story_fr": item_def["user_story_fr"] if item_def else "",
        "acceptance_criteria": item_def["acceptance_criteria"] if item_def else []
    }

@api_router.patch("/power-platform/items/{item_id}")
async def update_pp_item(
    item_id: str,
    update: PPItemInstanceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Update an item instance"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update.status is not None:
        update_data["status"] = update.status
    if update.owner_user_id is not None:
        update_data["owner_user_id"] = update.owner_user_id
    if update.due_date is not None:
        update_data["due_date"] = update.due_date
    if update.notes_markdown is not None:
        update_data["notes_markdown"] = update.notes_markdown
    if update.acceptance_state is not None:
        update_data["acceptance_state"] = update.acceptance_state
    if update.done_override is not None:
        update_data["done_override"] = update.done_override
    
    await db.pp_item_instances.update_one(
        {"program_id": program["id"], "item_id": item_id},
        {"$set": update_data}
    )
    
    # Get item to check workshop completion
    item = await db.pp_item_instances.find_one(
        {"program_id": program["id"], "item_id": item_id},
        {"_id": 0}
    )
    
    if item:
        await check_workshop_completion(program["id"], item["workshop_number"])
    
    return await db.pp_item_instances.find_one(
        {"program_id": program["id"], "item_id": item_id},
        {"_id": 0}
    )

@api_router.post("/power-platform/items/{item_id}/validate")
async def validate_pp_item(
    item_id: str,
    validation: PPItemInstanceValidate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Validate or unvalidate an item"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    now = datetime.now(timezone.utc).isoformat()
    
    if validation.validated:
        update_data = {
            "status": "validated",
            "validated_by": current_user.id,
            "validated_at": now,
            "updated_at": now
        }
    else:
        update_data = {
            "status": "done",
            "validated_by": None,
            "validated_at": None,
            "updated_at": now
        }
    
    await db.pp_item_instances.update_one(
        {"program_id": program["id"], "item_id": item_id},
        {"$set": update_data}
    )
    
    item = await db.pp_item_instances.find_one(
        {"program_id": program["id"], "item_id": item_id},
        {"_id": 0}
    )
    
    if item:
        await check_workshop_completion(program["id"], item["workshop_number"])
    
    return item

# Actions CRUD
@api_router.get("/power-platform/actions")
async def get_pp_actions(
    workshop_number: Optional[int] = None,
    item_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get actions with optional filters"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    query = {"program_id": program["id"]}
    if workshop_number is not None:
        query["workshop_number"] = workshop_number
    if item_id:
        query["item_id"] = item_id
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    
    actions = await db.pp_actions.find(query, {"_id": 0}).sort("created_at", -1).to_list(10000)
    
    # Calculate ageing for each action
    now = datetime.now(timezone.utc)
    for action in actions:
        try:
            created = datetime.fromisoformat(action["created_at"].replace("Z", "+00:00"))
            action["ageing_days"] = (now - created).days
        except:
            action["ageing_days"] = 0
    
    return actions

@api_router.post("/power-platform/actions")
async def create_pp_action(
    action: PPActionCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new action"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    now = datetime.now(timezone.utc).isoformat()
    new_action = {
        "id": str(uuid.uuid4()),
        "program_id": program["id"],
        "workshop_number": action.workshop_number,
        "item_id": action.item_id,
        "title": action.title,
        "description": action.description,
        "priority": action.priority,
        "status": "open",
        "owner_user_id": action.owner_user_id,
        "due_date": action.due_date,
        "created_at": now,
        "updated_at": now
    }
    
    await db.pp_actions.insert_one(new_action)
    return new_action

@api_router.patch("/power-platform/actions/{action_id}")
async def update_pp_action(
    action_id: str,
    update: PPActionUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Update an action"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update.title is not None:
        update_data["title"] = update.title
    if update.description is not None:
        update_data["description"] = update.description
    if update.priority is not None:
        update_data["priority"] = update.priority
    if update.status is not None:
        update_data["status"] = update.status
    if update.owner_user_id is not None:
        update_data["owner_user_id"] = update.owner_user_id
    if update.due_date is not None:
        update_data["due_date"] = update.due_date
    
    await db.pp_actions.update_one(
        {"id": action_id, "program_id": program["id"]},
        {"$set": update_data}
    )
    
    return await db.pp_actions.find_one({"id": action_id}, {"_id": 0})

@api_router.delete("/power-platform/actions/{action_id}")
async def delete_pp_action(
    action_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete an action"""
    program = await get_or_create_program(tenant_id, current_user.id)
    await db.pp_actions.delete_one({"id": action_id, "program_id": program["id"]})
    return {"deleted": True}

# Decisions CRUD
@api_router.get("/power-platform/decisions")
async def get_pp_decisions(
    workshop_number: Optional[int] = None,
    item_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get decisions with optional filters"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    query = {"program_id": program["id"]}
    if workshop_number is not None:
        query["workshop_number"] = workshop_number
    if item_id:
        query["item_id"] = item_id
    
    return await db.pp_decisions.find(query, {"_id": 0}).sort("decided_at", -1).to_list(10000)

@api_router.post("/power-platform/decisions")
async def create_pp_decision(
    decision: PPDecisionCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new decision"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    now = datetime.now(timezone.utc).isoformat()
    new_decision = {
        "id": str(uuid.uuid4()),
        "program_id": program["id"],
        "workshop_number": decision.workshop_number,
        "item_id": decision.item_id,
        "decision_text": decision.decision_text,
        "decided_by": current_user.id,
        "decided_at": now,
        "evidence_links": decision.evidence_links,
        "created_at": now
    }
    
    await db.pp_decisions.insert_one(new_decision)
    return new_decision

@api_router.delete("/power-platform/decisions/{decision_id}")
async def delete_pp_decision(
    decision_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a decision"""
    program = await get_or_create_program(tenant_id, current_user.id)
    await db.pp_decisions.delete_one({"id": decision_id, "program_id": program["id"]})
    return {"deleted": True}

# Evidence CRUD
@api_router.get("/power-platform/evidence")
async def get_pp_evidence(
    workshop_number: Optional[int] = None,
    item_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get evidence with optional filters"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    query = {"program_id": program["id"]}
    if workshop_number is not None:
        query["workshop_number"] = workshop_number
    if item_id:
        query["item_id"] = item_id
    
    return await db.pp_evidence.find(query, {"_id": 0}).sort("created_at", -1).to_list(10000)

@api_router.post("/power-platform/evidence")
async def create_pp_evidence(
    evidence: PPEvidenceCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Create new evidence"""
    program = await get_or_create_program(tenant_id, current_user.id)
    
    now = datetime.now(timezone.utc).isoformat()
    new_evidence = {
        "id": str(uuid.uuid4()),
        "program_id": program["id"],
        "workshop_number": evidence.workshop_number,
        "item_id": evidence.item_id,
        "evidence_type": evidence.evidence_type,
        "title": evidence.title,
        "url": evidence.url,
        "file_id": None,
        "date": now,
        "owner_user_id": current_user.id,
        "created_at": now
    }
    
    await db.pp_evidence.insert_one(new_evidence)
    return new_evidence

@api_router.delete("/power-platform/evidence/{evidence_id}")
async def delete_pp_evidence(
    evidence_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete evidence"""
    program = await get_or_create_program(tenant_id, current_user.id)
    await db.pp_evidence.delete_one({"id": evidence_id, "program_id": program["id"]})
    return {"deleted": True}

# Workshop definitions (static)
@api_router.get("/power-platform/definitions/workshops")
async def get_pp_workshop_definitions():
    """Get workshop definitions"""
    return WORKSHOP_DEFINITIONS

@api_router.get("/power-platform/definitions/items")
async def get_pp_item_definitions(workshop_number: Optional[int] = None):
    """Get item definitions"""
    if workshop_number:
        return get_items_for_workshop(workshop_number)
    return ITEM_DEFINITIONS

# Include the router
app.include_router(api_router)

# Events
@app.on_event("startup")
async def startup():
    await seed_database()

@app.on_event("shutdown")
async def shutdown():
    client.close()
