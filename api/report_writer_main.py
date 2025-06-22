"""
FastAPI backend for Interactive Analytics Report Writer

This creates web APIs for the AI-powered business intelligence report generator,
including document management, real-time collaboration, and multi-tenant architecture.
"""

import os
import sys
# Add parent directory to path for instant_dashboard imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import json

# Import existing InstantDashboard functionality
from instant_dashboard.agent import dashboard_agent, execute_full_pipeline
from instant_dashboard.shared import get_database_settings

# Import new Report Writer infrastructure
from report_writer.database.config import get_db, init_database, check_database_health
from report_writer.database.models import (
    User, Organization, Document, ReportTemplate, 
    UserRole, DocumentPermission, ReportTemplateCategory
)

# Import new AI agents
try:
    from report_writer.agents import (
        content_coordinator_agent,
        report_template_agent,
        title_suggestion_agent,
        section_generator_agent,
        outline_manager_agent
    )
    print("✅ Report Writer agents imported successfully")
except ImportError as e:
    print(f"⚠️ Failed to import Report Writer agents: {e}")
    content_coordinator_agent = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="Interactive Analytics Report Writer API",
    description="AI-powered business intelligence report generator with real-time collaboration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS middleware for development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Next.js dev server
        "http://127.0.0.1:3000", 
        "http://localhost:3001",     # Alternative frontend port
        "https://script.google.com", # Google Apps Script
        "https://script.googleusercontent.com", # Google Apps Script
        "https://*.googleusercontent.com", # Google Apps Script
        "https://your-production-domain.com"  # Add your production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and check connections on startup"""
    try:
        logger.info("🚀 Starting Interactive Analytics Report Writer API...")
        
        # Initialize database
        if init_database():
            logger.info("✅ Database initialized successfully")
        else:
            logger.error("❌ Database initialization failed")
            
        # Test InstantDashboard integration
        settings = get_database_settings()
        if "bq_ddl_schema" in settings and len(settings["bq_ddl_schema"]) > 0:
            logger.info("✅ InstantDashboard BigQuery integration working")
        else:
            logger.warning("⚠️ InstantDashboard BigQuery integration may have issues")
            
        logger.info("🎯 API startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


# Pydantic models for API requests/responses

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    google_id: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationCreate(BaseModel):
    name: str
    slug: str

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    plan_type: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    template_id: Optional[int] = None
    content: Dict[str, Any] = {}

class DocumentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    version_number: int
    is_archived: bool
    
    class Config:
        from_attributes = True

class ReportTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: ReportTemplateCategory
    is_public: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Legacy InstantDashboard models (keep existing functionality)
class QueryRequest(BaseModel):
    question: str
    use_full_pipeline: bool = True
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    data: Any
    execution_time: float
    timestamp: str
    query_plan_used: bool = False
    row_count: int = 0
    error_message: Optional[str] = None
    chart_specifications: Optional[Any] = None
    pipeline_phases: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, Any]

# WebSocket connection manager for real-time collaboration
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}  # document_id -> connections
        
    async def connect(self, websocket: WebSocket, document_id: int):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)
        logger.info(f"WebSocket connected to document {document_id}")
        
    def disconnect(self, websocket: WebSocket, document_id: int):
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
        logger.info(f"WebSocket disconnected from document {document_id}")
        
    async def broadcast_to_document(self, message: str, document_id: int, exclude_websocket: Optional[WebSocket] = None):
        if document_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[document_id]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(message)
                    except:
                        disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, document_id)

manager = ConnectionManager()

# Utility functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token (placeholder for now)"""
    # TODO: Implement proper JWT token validation
    # For now, return a demo user for development
    return {
        "user_id": 1,
        "email": "demo@example.com",
        "name": "Demo User",
        "is_authenticated": credentials is not None
    }

def get_current_user_from_db(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from database"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        # Create demo user if not exists
        user = User(
            id=1,
            email=current_user["email"],
            name=current_user["name"],
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Health and system endpoints

@app.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for all services"""
    try:
        # Check database health
        db_health = check_database_health()
        
        # Check InstantDashboard BigQuery connection
        try:
            settings = get_database_settings()
            bigquery_health = {
                "status": "healthy" if "bq_ddl_schema" in settings else "unhealthy",
                "project_id": settings.get("bq_project_id"),
                "dataset_id": settings.get("bq_dataset_id"),
                "tables_available": len([line for line in settings.get("bq_ddl_schema", "").split('\n') 
                                       if 'CREATE OR REPLACE TABLE' in line])
            }
        except Exception as e:
            bigquery_health = {"status": "unhealthy", "error": str(e)}
        
        # Check InstantDashboard agents
        agent_health = {
            "status": "healthy",
            "coordinator_available": dashboard_agent is not None,
            "tools_count": len(dashboard_agent.tools) if dashboard_agent else 0
        }
        
        overall_status = "healthy" if all([
            db_health["status"] == "healthy",
            bigquery_health["status"] == "healthy",
            agent_health["status"] == "healthy"
        ]) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            services={
                "database": db_health,
                "bigquery": bigquery_health,
                "instant_dashboard": agent_health
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

# Legacy InstantDashboard endpoints (preserve existing functionality)

@app.post("/api/query", response_model=QueryResponse)
async def query_data(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Legacy endpoint for InstantDashboard natural language queries"""
    start_time = time.time()
    
    try:
        if request.use_full_pipeline:
            result = execute_full_pipeline(request.question)
            result["execution_time"] = time.time() - start_time
            result["timestamp"] = datetime.now().isoformat()
            return result
        else:
            # Legacy path
            from instant_dashboard.shared import call_db_agent
            # Simple tool context for API calls
            class SimpleToolContext:
                def __init__(self, user_id: str = "api_user"):
                    self.state = {}
                    self.user_id = user_id
                    self.state["database_settings"] = get_database_settings()
                    self.state["all_db_settings"] = {"use_database": "BigQuery"}
            
            tool_context = SimpleToolContext(user_id=current_user["user_id"])
            result = await call_db_agent(request.question, tool_context)
            
            try:
                parsed_result = json.loads(result) if isinstance(result, str) else result
            except json.JSONDecodeError:
                parsed_result = {"response": result}
            
            return {
                "success": True,
                "data": parsed_result,
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "query_plan_used": False,
                "row_count": 0
            }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "error_message": str(e)
        }

@app.get("/api/schema")
async def get_database_schema(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get BigQuery database schema information"""
    try:
        settings = get_database_settings()
        return {
            "project_id": settings.get("bq_project_id"),
            "dataset_id": settings.get("bq_dataset_id"),
            "schema": settings.get("bq_ddl_schema", "")[:1000],
            "tables_available": len([line for line in settings.get("bq_ddl_schema", "").split('\n') 
                                   if 'CREATE OR REPLACE TABLE' in line])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )

# NEW: Interactive Analytics Report Writer endpoints

@app.get("/api/report-writer/templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    category: Optional[ReportTemplateCategory] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_db)
):
    """Get available report templates"""
    query = db.query(ReportTemplate).filter(ReportTemplate.is_public == True)
    
    if category:
        query = query.filter(ReportTemplate.category == category)
    
    templates = query.order_by(ReportTemplate.usage_count.desc()).all()
    return templates

@app.post("/api/report-writer/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_db)
):
    """Create a new business report document"""
    # For demo, create a default organization if not exists
    org = db.query(Organization).first()
    if not org:
        org = Organization(
            name="Demo Organization",
            slug="demo-org",
            plan_type="free"
        )
        db.add(org)
        db.commit()
        db.refresh(org)
    
    db_document = Document(
        organization_id=org.id,
        title=document.title,
        description=document.description,
        content=document.content,
        template_id=document.template_id,
        created_by=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    logger.info(f"Created document '{document.title}' for user {current_user.email}")
    return db_document

@app.get("/api/report-writer/documents", response_model=List[DocumentResponse])
async def get_user_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_db)
):
    """Get user's documents"""
    documents = db.query(Document).filter(
        Document.created_by == current_user.id,
        Document.is_archived == False
    ).order_by(Document.updated_at.desc()).offset(skip).limit(limit).all()
    
    return documents

@app.get("/api/report-writer/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id  # TODO: Check permissions properly
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@app.put("/api/report-writer/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_db)
):
    """Update a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.created_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update allowed fields
    if "title" in updates:
        document.title = updates["title"]
    if "content" in updates:
        document.content = updates["content"]
        document.version_number += 1
    
    db.commit()
    db.refresh(document)
    
    # Broadcast update to connected clients
    await manager.broadcast_to_document(
        json.dumps({
            "type": "document_updated",
            "document_id": document_id,
            "updates": updates,
            "updated_by": current_user.email
        }),
        document_id
    )
    
    return document

# Google Apps Script specific endpoints

@app.post("/api/apps-script/auth")
async def apps_script_auth(request: Dict[str, Any]):
    """Simple authentication for Google Apps Script add-on"""
    try:
        # For now, accept any user from Google Apps Script
        # In production, validate the Google OAuth token
        user_email = request.get("email", "apps-script-user@example.com")
        
        return {
            "success": True,
            "user_id": "apps_script_user",
            "email": user_email,
            "token": "demo_token"  # In production, generate proper JWT
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/apps-script/analyze-pdf")
async def analyze_pdf_content(request: Dict[str, Any]):
    """Analyze PDF content for insights (placeholder for future implementation)"""
    try:
        pdf_content = request.get("content", "")
        analysis_type = request.get("analysis_type", "summary")
        
        # Placeholder response - in future, implement PDF analysis
        return {
            "success": True,
            "analysis": {
                "summary": "PDF analysis not yet implemented",
                "key_insights": [],
                "recommendations": "Upload BigQuery data for detailed analysis"
            },
            "next_steps": "Use 'Analyze Data' for BigQuery integration"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/apps-script/quick-query")
async def quick_query(request: Dict[str, Any]):
    """Simplified query endpoint optimized for Google Apps Script"""
    try:
        question = request.get("question", "")
        if not question:
            return {"success": False, "error": "Question is required"}
        
        # Use the existing pipeline
        result = execute_full_pipeline(question)
        
        # Simplify response for Apps Script
        simplified_result = {
            "success": result.get("success", False),
            "data": result.get("data", {}).get("data", [])[:10],  # Limit to 10 rows
            "summary": f"Found {result.get('row_count', 0)} rows in {result.get('execution_time', 0):.1f}s",
            "charts": result.get("chart_specifications", {}),
            "error": result.get("error_message")
        }
        
        return simplified_result
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/report-writer/generate-full-report")
async def generate_full_report(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user_from_db)
):
    """Generate a complete business report using the AI agent pipeline."""
    try:
        logger.info("🎯 Starting full report generation...")
        
        # Extract request parameters
        user_requirements = request.get("requirements", "")
        business_context = request.get("business_context", "")
        target_audience = request.get("target_audience", "executives")
        
        if not user_requirements:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User requirements are required"
            )
        
        # Use Content Coordinator Agent if available
        if content_coordinator_agent:
            # Create a simple tool context for the agent
            class SimpleToolContext:
                def __init__(self):
                    self.state = {}
                    self.state["database_settings"] = get_database_settings()
            
            tool_context = SimpleToolContext()
            
            # Call the orchestrate_full_report_generation tool
            from report_writer.agents.content_coordinator_agent import orchestrate_full_report_generation
            
            result = orchestrate_full_report_generation(
                user_requirements=user_requirements,
                business_context=business_context,
                target_audience=target_audience,
                tool_context=tool_context
            )
            
            # Parse the result
            import json
            try:
                report_data = json.loads(result)
                logger.info("✅ Full report generation completed successfully")
                return report_data
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse agent response")
                return {
                    "status": "error",
                    "error": "Failed to parse agent response",
                    "raw_response": result
                }
        
        else:
            # Fallback if agents not available
            logger.warning("⚠️ Content Coordinator Agent not available, using fallback")
            return {
                "status": "success",
                "report_metadata": {
                    "title": f"Business Report: {business_context}",
                    "target_audience": target_audience,
                    "total_sections": 4,
                    "generation_method": "fallback"
                },
                "message": "Report Writer agents not fully initialized. This is a fallback response.",
                "next_steps": [
                    "Ensure all agents are properly loaded",
                    "Check agent import status in server logs",
                    "Verify database connections and environment setup"
                ]
            }
            
    except Exception as e:
        logger.error(f"❌ Error generating full report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws/documents/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket for real-time document collaboration"""
    await manager.connect(websocket, document_id)
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "cursor_position":
                # Broadcast cursor position to other clients
                await manager.broadcast_to_document(
                    json.dumps({
                        "type": "cursor_update",
                        "user": message.get("user"),
                        "position": message.get("position")
                    }),
                    document_id,
                    exclude_websocket=websocket
                )
            elif message["type"] == "content_change":
                # Broadcast content changes to other clients
                await manager.broadcast_to_document(
                    json.dumps({
                        "type": "content_changed", 
                        "changes": message.get("changes"),
                        "user": message.get("user")
                    }),
                    document_id,
                    exclude_websocket=websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, document_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, document_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 