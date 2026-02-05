from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..security import get_current_user, get_tenant_id, UserInDB
from ..db import get_database

router = APIRouter(prefix="/enterprise-brain", tags=["Enterprise Brain"])

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

class DocumentDetail(Document):
    source_id: str
    tenant_id: str

class AIUsageResponse(BaseModel):
    document_id: str
    document_title: str
    usage_status: str  # "authorized", "assisted", "forbidden"
    iqi_score: float
    reason: str

@router.get("/quality", response_model=QualityResponse)
async def get_quality_metrics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get Information Quality Index (IQI) global score and breakdown"""
    database = await get_database()
    
    # Get all documents for tenant
    documents = await database.knowledge_documents.find(
        {"tenant_id": tenant_id},
        {"_id": 0}
    ).to_list(1000)
    
    if not documents:
        return QualityResponse(
            iqi_global=0.0,
            evidences={
                "total_documents": 0,
                "validated_count": 0,
                "avg_confidence": 0.0,
                "freshness_score": 0.0
            }
        )
    
    # Calculate IQI components
    total = len(documents)
    validated = sum(1 for d in documents if d.get("validated", False))
    avg_confidence = sum(d.get("confidence_score", 0) for d in documents) / total
    
    # Calculate freshness (simplified: based on last_updated dates)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    fresh_count = 0
    for doc in documents:
        try:
            last_updated = datetime.fromisoformat(doc["last_updated"].replace("Z", "+00:00"))
            days_old = (now - last_updated).days
            if days_old < 90:  # Less than 90 days old = fresh
                fresh_count += 1
        except:
            pass
    
    freshness_score = fresh_count / total if total > 0 else 0
    
    # IQI = weighted combination
    validation_score = validated / total if total > 0 else 0
    iqi_global = (validation_score * 0.3) + (avg_confidence * 0.5) + (freshness_score * 0.2)
    
    return QualityResponse(
        iqi_global=round(iqi_global, 2),
        evidences={
            "total_documents": total,
            "validated_count": validated,
            "validation_rate": round(validation_score * 100, 1),
            "avg_confidence": round(avg_confidence * 100, 1),
            "freshness_score": round(freshness_score * 100, 1),
            "fresh_documents": fresh_count
        }
    )

@router.get("/documents", response_model=List[Document])
async def get_documents(
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all knowledge documents for the tenant"""
    database = await get_database()
    
    documents = await database.knowledge_documents.find(
        {"tenant_id": tenant_id},
        {"_id": 0, "source_id": 0, "tenant_id": 0}
    ).to_list(1000)
    
    return documents

@router.get("/document/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific document by ID"""
    database = await get_database()
    
    document = await database.knowledge_documents.find_one(
        {"id": document_id, "tenant_id": tenant_id},
        {"_id": 0}
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    return document

# AI Usage endpoint (under /api prefix but related to documents)
ai_router = APIRouter(prefix="/ai", tags=["AI"])

@ai_router.get("/usage/document/{document_id}", response_model=AIUsageResponse)
async def get_ai_usage_for_document(
    document_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get AI usage authorization status for a document"""
    database = await get_database()
    
    # Get document
    document = await database.knowledge_documents.find_one(
        {"id": document_id, "tenant_id": tenant_id},
        {"_id": 0}
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Get AI policy thresholds
    policy = await database.ai_usage_policies.find_one(
        {"tenant_id": tenant_id},
        {"_id": 0}
    )
    
    if not policy:
        policy = {"min_iqi_authorized": 0.80, "min_iqi_assisted": 0.60}
    
    iqi_score = document.get("confidence_score", 0)
    is_validated = document.get("validated", False)
    
    # Determine usage status based on IQI and validation
    if is_validated and iqi_score >= policy["min_iqi_authorized"]:
        usage_status = "authorized"
        reason = "Document validé avec un score IQI suffisant"
    elif iqi_score >= policy["min_iqi_assisted"]:
        usage_status = "assisted"
        reason = "Score IQI intermédiaire - utilisation assistée uniquement"
    else:
        usage_status = "forbidden"
        reason = "Score IQI insuffisant ou document non validé"
    
    return AIUsageResponse(
        document_id=document_id,
        document_title=document.get("title", ""),
        usage_status=usage_status,
        iqi_score=iqi_score,
        reason=reason
    )
