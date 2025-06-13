"""FastAPI backend for InstantDashboard.

This creates web APIs that expose our InstantDashboard agents to the frontend.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import json

# Import our InstantDashboard agents
from instant_dashboard.agent import dashboard_agent, execute_full_pipeline
from instant_dashboard.shared import get_database_settings
from google.adk.tools import ToolContext

# Create FastAPI app
app = FastAPI(
    title="InstantDashboard API",
    description="Multi-agent data analytics assistant with natural language interface",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

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

# Utility functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token (placeholder for now)."""
    # For now, return a demo user. We'll implement proper OAuth later.
    return {
        "user_id": "demo_user",
        "email": "demo@example.com",
        "is_authenticated": credentials is not None
    }

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

@app.post("/api/query", response_model=QueryResponse)
async def query_data(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Main endpoint for natural language data queries."""
    start_time = time.time()
    
    try:
        # Create tool context
        tool_context = SimpleToolContext(user_id=current_user["user_id"])
        
        # Execute the query using our InstantDashboard agents
        if request.use_full_pipeline:
            # Use the full Phase 2 + 3 pipeline
            result = execute_full_pipeline(request.question, tool_context)
        else:
            # Use direct database agent (Phase 1)
            from instant_dashboard.shared import call_db_agent
            result = await call_db_agent(request.question, tool_context)
        
        # Parse the result
        try:
            result_data = json.loads(result) if isinstance(result, str) else result
        except json.JSONDecodeError:
            # If not JSON, treat as plain text response
            result_data = {"response": result}
        
        execution_time = time.time() - start_time
        
        # Extract metadata if available
        query_plan_used = result_data.get("query_plan_used", False) if isinstance(result_data, dict) else False
        row_count = result_data.get("row_count", 0) if isinstance(result_data, dict) else 0
        
        return QueryResponse(
            success=True,
            data=result_data,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            query_plan_used=query_plan_used,
            row_count=row_count
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=False,
            data=None,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            error_message=str(e)
        )

@app.get("/api/schema")
async def get_database_schema(current_user: Dict[str, Any] = Depends(get_current_user)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 