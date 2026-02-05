from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
db = Database()

async def get_database():
    return db.client[os.environ.get("DB_NAME", "bizdesk365")]

async def connect_to_mongo():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(mongo_url)
    print(f"Connected to MongoDB at {mongo_url}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")

async def set_tenant_context(tenant_id: str):
    """Prepare for future RLS by setting tenant context"""
    # In MongoDB, we'll handle this through query filters
    # This function prepares the pattern for RLS migration
    pass

async def seed_database():
    """Seed the database with initial data"""
    database = await get_database()
    
    # Demo tenant UUID
    demo_tenant_id = "11111111-1111-1111-1111-111111111111"
    
    # Check if already seeded
    existing_tenant = await database.tenants.find_one({"id": demo_tenant_id})
    if existing_tenant:
        print("Database already seeded")
        return
    
    # Seed tenant
    await database.tenants.insert_one({
        "id": demo_tenant_id,
        "name": "Demo Org",
        "created_at": "2024-01-01T00:00:00Z"
    })
    
    # Seed compliance KPIs
    compliance_kpis = [
        {"id": "kpi-001", "tenant_id": demo_tenant_id, "name": "MaturityIndex", "value": 0.72, "measured_at": "2024-01-15T10:00:00Z"},
        {"id": "kpi-002", "tenant_id": demo_tenant_id, "name": "PolicyCoverage", "value": 0.85, "measured_at": "2024-01-15T10:00:00Z"},
        {"id": "kpi-003", "tenant_id": demo_tenant_id, "name": "AuditFreshnessDays", "value": 15, "measured_at": "2024-01-15T10:00:00Z"},
    ]
    await database.compliance_kpis.insert_many(compliance_kpis)
    
    # Seed ISO profile
    iso_profiles = [
        {"tenant_id": demo_tenant_id, "iso_code": "ISO9001", "enabled": True, "name": "Qualité"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO27001", "enabled": True, "name": "Sécurité de l'information"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO14001", "enabled": False, "name": "Environnement"},
        {"tenant_id": demo_tenant_id, "iso_code": "ISO45001", "enabled": False, "name": "Santé et sécurité"},
    ]
    await database.tenant_iso_profiles.insert_many(iso_profiles)
    
    # Seed AI usage policy
    await database.ai_usage_policies.insert_one({
        "tenant_id": demo_tenant_id,
        "min_iqi_authorized": 0.80,
        "min_iqi_assisted": 0.60
    })
    
    # Seed knowledge source
    source_id = "source-001"
    await database.knowledge_sources.insert_one({
        "id": source_id,
        "tenant_id": demo_tenant_id,
        "type": "SharePoint",
        "name": "Documentation Interne",
        "description": "Base documentaire SharePoint principale"
    })
    
    # Seed knowledge documents
    documents = [
        {
            "id": "doc-001",
            "tenant_id": demo_tenant_id,
            "source_id": source_id,
            "title": "Politique de Sécurité Informatique",
            "doc_type": "Politique",
            "url": "https://sharepoint.example.com/doc/001",
            "last_updated": "2024-01-10T14:30:00Z",
            "confidence_score": 0.92,
            "validated": True,
            "owner": "Jean Dupont"
        },
        {
            "id": "doc-002",
            "tenant_id": demo_tenant_id,
            "source_id": source_id,
            "title": "Procédure de Gestion des Incidents",
            "doc_type": "Procédure",
            "url": "https://sharepoint.example.com/doc/002",
            "last_updated": "2023-11-20T09:15:00Z",
            "confidence_score": 0.75,
            "validated": True,
            "owner": "Marie Martin"
        },
        {
            "id": "doc-003",
            "tenant_id": demo_tenant_id,
            "source_id": source_id,
            "title": "Guide d'Utilisation IA",
            "doc_type": "Guide",
            "url": "https://sharepoint.example.com/doc/003",
            "last_updated": "2024-01-05T16:45:00Z",
            "confidence_score": 0.88,
            "validated": False,
            "owner": "Pierre Durand"
        },
        {
            "id": "doc-004",
            "tenant_id": demo_tenant_id,
            "source_id": source_id,
            "title": "Charte Éthique IA",
            "doc_type": "Charte",
            "url": "https://sharepoint.example.com/doc/004",
            "last_updated": "2023-08-01T11:00:00Z",
            "confidence_score": 0.55,
            "validated": False,
            "owner": "Sophie Bernard"
        },
    ]
    await database.knowledge_documents.insert_many(documents)
    
    # Seed AI usage logs
    ai_usage_logs = [
        {"tenant_id": demo_tenant_id, "document_id": "doc-001", "decision": "authorized", "checked_at": "2024-01-15T08:00:00Z", "intent": "Analyse de conformité"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-002", "decision": "assisted", "checked_at": "2024-01-15T09:00:00Z", "intent": "Recherche procédure"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-003", "decision": "authorized", "checked_at": "2024-01-15T10:00:00Z", "intent": "Formation utilisateur"},
        {"tenant_id": demo_tenant_id, "document_id": "doc-004", "decision": "forbidden", "checked_at": "2024-01-15T11:00:00Z", "intent": "Rédaction rapport"},
    ]
    await database.ai_usage_logs.insert_many(ai_usage_logs)
    
    # Seed demo user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    await database.users.insert_one({
        "id": "user-001",
        "username": "demo@bizdesk365.local",
        "email": "demo@bizdesk365.local",
        "password_hash": pwd_context.hash("demo"),
        "tenant_id": demo_tenant_id,
        "roles": ["admin", "user"]
    })
    
    print("Database seeded successfully")
