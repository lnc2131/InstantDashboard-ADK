"""FastAPI backend for InstantDashboard.

This creates web APIs that expose our InstantDashboard agents to the frontend.
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Import our InstantDashboard agents
from instant_dashboard.agent import dashboard_agent, execute_full_pipeline
from instant_dashboard.shared import get_database_settings
from google.adk.tools import ToolContext

# Authentication imports - conditional for demo deployment with error handling
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"

get_current_user = None
auth_router = None
User = None

if ENABLE_AUTH:
    try:
        from api.auth.oauth import get_current_user
        from api.auth.endpoints import router as auth_router
        from api.auth.models import User
        print("✅ Authentication enabled successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load authentication modules: {e}")
        print("   Continuing in demo mode without authentication...")
        ENABLE_AUTH = False
        get_current_user = None
        auth_router = None
        User = None
else:
    print("🔧 Demo mode: Authentication disabled")

# Google Cloud credentials setup function
def setup_google_cloud_credentials():
    """Setup Google Cloud credentials file from environment variable."""
    try:
        # Check if JSON credentials are provided as environment variable
        gcp_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if gcp_json:
            # Create the credentials file
            credentials_path = "/tmp/gcp-key.json"
            
            # Parse JSON to validate format
            credentials_data = json.loads(gcp_json)
            
            # Fix private key formatting - replace escaped newlines with actual newlines
            if "private_key" in credentials_data:
                credentials_data["private_key"] = credentials_data["private_key"].replace("\\n", "\n")
            
            # Write to file
            with open(credentials_path, "w") as f:
                json.dump(credentials_data, f)
            
            # Set environment variable for Google Cloud libraries
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
            print(f"✅ Google Cloud credentials created at {credentials_path}")
            print(f"   Project ID: {credentials_data.get('project_id', 'unknown')}")
            print(f"   Client Email: {credentials_data.get('client_email', 'unknown')}")
            
            return True
        else:
            print("⚠️ No GOOGLE_APPLICATION_CREDENTIALS_JSON found")
            # Check if GOOGLE_APPLICATION_CREDENTIALS points to existing file
            existing_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if existing_creds and os.path.exists(existing_creds):
                print(f"✅ Using existing credentials file: {existing_creds}")
                return True
            else:
                print("❌ No Google Cloud credentials configured")
                return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to setup Google Cloud credentials: {e}")
        return False

# Create FastAPI app
app = FastAPI(
    title="InstantDashboard API",
    description="Multi-agent data analytics assistant with natural language interface",
    version="1.0.0"
)

# Startup event to initialize Google Cloud credentials
@app.on_event("startup")
async def startup_event():
    """Initialize Google Cloud credentials and other startup tasks."""
    print("🚀 Starting InstantDashboard API...")
    
    # Setup Google Cloud credentials first
    if setup_google_cloud_credentials():
        print("🔐 Google Cloud authentication configured")
    else:
        print("⚠️ Warning: Google Cloud authentication not configured")
        print("   API will work but BigQuery functionality may be limited")
    
    print("✅ InstantDashboard API startup complete!")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://192.168.2.5:3000",
        "https://2f6d-61-228-212-206.ngrok-free.app",  # Add ngrok URL for hackathon judges
        "https://*.railway.app",  # Railway frontend domain
        "https://*.vercel.app",   # In case we use Vercel for frontend
        "*"  # Allow all origins for hackathon demo (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router (only if enabled and available)
if ENABLE_AUTH and auth_router is not None:
    try:
        app.include_router(auth_router)
        print("✅ Authentication router added successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not add authentication router: {e}")

# Security is now handled by auth module

# Pydantic models for API requests/responses
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
    chart_specifications: Optional[Any] = None  # NEW: Chart specifications from ChartGeneratorAgent
    pipeline_phases: Optional[Dict[str, Any]] = None  # NEW: Pipeline execution details

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agents_available: int
    database_connected: bool

# Simple tool context for API calls
class SimpleToolContext:
    def __init__(self, user_id: str = "api_user"):
        self.state = {}
        self.user_id = user_id
        # Pre-load database settings
        self.state["database_settings"] = get_database_settings()
        self.state["all_db_settings"] = {"use_database": "BigQuery"}

# Utility functions are now imported from auth module

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        settings = get_database_settings()
        db_connected = "bq_ddl_schema" in settings and len(settings["bq_ddl_schema"]) > 0
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            agents_available=len(dashboard_agent.tools),
            database_connected=db_connected
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/api/query")
async def query_data(
    request: QueryRequest
    # Auth disabled via ENABLE_AUTH=false for demo deployment
    # current_user: User = Depends(get_current_user) if ENABLE_AUTH else None
):
    """Main endpoint for natural language data queries."""
    start_time = time.time()
    
    try:
        if request.use_full_pipeline:
            # Call the 4-phase pipeline directly and return raw result
            result = execute_full_pipeline(request.question)
            
            # Add execution metadata
            result["execution_time"] = time.time() - start_time
            result["timestamp"] = datetime.now().isoformat()
            
            return result
        else:
            # Legacy path
            from instant_dashboard.shared import call_db_agent
            tool_context = SimpleToolContext(user_id="demo_user")
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
async def get_database_schema():
    """Get the database schema information."""
    try:
        settings = get_database_settings()
        return {
            "project_id": settings.get("bq_project_id"),
            "dataset_id": settings.get("bq_dataset_id"),
            "schema": settings.get("bq_ddl_schema", "")[:1000],  # Truncate for API response
            "tables_available": len([line for line in settings.get("bq_ddl_schema", "").split('\n') if 'CREATE OR REPLACE TABLE' in line])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )

@app.get("/api/agents")
async def get_available_agents():
    """Get information about available InstantDashboard agents."""
    return {
        "coordinator": {
            "name": dashboard_agent.name,
            "model": dashboard_agent.model,
            "tools_count": len(dashboard_agent.tools),
            "tools": [tool.__name__ for tool in dashboard_agent.tools]
        },
        "phases": {
            "phase_1": "Foundation - Direct database access",
            "phase_2": "QueryPlannerAgent - Structured query planning", 
            "phase_3": "BigQueryRunner - Query plan execution",
            "phase_4": "ChartGenerator - Coming soon",
            "phase_5": "InsightGenerator - Coming soon"
        }
    }

@app.get("/api/test-charts")
async def test_chart_generation():
    """Test endpoint to verify chart generation is working."""
    try:
        # Call execute_full_pipeline directly
        result = execute_full_pipeline("Show me top companies")
        
        return {
            "test_successful": True,
            "has_chart_specifications": "chart_specifications" in result,
            "response_keys": list(result.keys()),
            "chart_count": len(result.get("chart_specifications", {}).get("chart_recommendations", [])),
            "sample_response": {k: str(v)[:100] + "..." if len(str(v)) > 100 else v 
                             for k, v in result.items() if k != "data"}
        }
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port) 