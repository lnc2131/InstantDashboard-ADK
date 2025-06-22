"""
Simplified API Server for Google Apps Script Add-on

This is a lightweight FastAPI server that provides the essential endpoints
for the Google Apps Script add-on without requiring the full database setup.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for instant_dashboard imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing InstantDashboard functionality
try:
    from instant_dashboard.agent import execute_full_pipeline
    from instant_dashboard.shared import get_database_settings
    print("✅ InstantDashboard imports successful")
except ImportError as e:
    print(f"❌ InstantDashboard import failed: {e}")
    execute_full_pipeline = None
    get_database_settings = None

# Create FastAPI app
app = FastAPI(
    title="InstantDashboard Google Apps Script API",
    description="Simplified API for Google Apps Script add-on integration",
    version="1.0.0"
)

# Enhanced CORS middleware for Google Apps Script
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://script.google.com",
        "https://script.googleusercontent.com",
        "https://*.googleusercontent.com",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuickQueryRequest(BaseModel):
    question: str

class QuickQueryResponse(BaseModel):
    success: bool
    data: list
    summary: str
    charts: Dict[str, Any]
    error: str = None

class AuthRequest(BaseModel):
    email: str = "demo@example.com"

# Health check endpoint
@app.get("/")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "InstantDashboard Google Apps Script API",
        "instant_dashboard_available": execute_full_pipeline is not None
    }

# Google Apps Script specific endpoints
@app.post("/api/apps-script/auth")
async def apps_script_auth(request: AuthRequest):
    """Simple authentication for Google Apps Script add-on"""
    try:
        return {
            "success": True,
            "user_id": "apps_script_user",
            "email": request.email,
            "token": "demo_token"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/apps-script/quick-query")
async def quick_query(request: QuickQueryRequest):
    """Simplified query endpoint optimized for Google Apps Script"""
    try:
        question = request.question
        if not question:
            return {"success": False, "error": "Question is required", "data": [], "summary": "", "charts": {}}
        
        if not execute_full_pipeline:
            return {
                "success": False, 
                "error": "InstantDashboard not available", 
                "data": [],
                "summary": "InstantDashboard service unavailable",
                "charts": {}
            }
        
        print(f"🔍 Processing query: {question}")
        
        # Use the existing pipeline
        result = execute_full_pipeline(question)
        
        # Extract data safely
        data = []
        if result.get("success") and result.get("data"):
            if isinstance(result["data"], dict) and "data" in result["data"]:
                data = result["data"]["data"][:10]  # Limit to 10 rows
            elif isinstance(result["data"], list):
                data = result["data"][:10]
        
        # Simplify response for Apps Script
        simplified_result = {
            "success": result.get("success", False),
            "data": data,
            "summary": f"Found {result.get('row_count', 0)} rows in {result.get('execution_time', 0):.1f}s",
            "charts": result.get("chart_specifications", {}),
            "error": result.get("error_message")
        }
        
        print(f"✅ Query processed successfully: {len(data)} rows returned")
        return simplified_result
        
    except Exception as e:
        print(f"❌ Query error: {e}")
        return {
            "success": False, 
            "error": str(e), 
            "data": [],
            "summary": "Query failed",
            "charts": {}
        }

@app.get("/api/schema")
async def get_database_schema():
    """Get BigQuery database schema information"""
    try:
        if not get_database_settings:
            return {
                "project_id": "unavailable",
                "dataset_id": "unavailable", 
                "schema": "InstantDashboard not available",
                "tables_available": 0
            }
        
        settings = get_database_settings()
        return {
            "project_id": settings.get("bq_project_id", "unknown"),
            "dataset_id": settings.get("bq_dataset_id", "unknown"),
            "schema": settings.get("bq_ddl_schema", "")[:1000],
            "tables_available": len([line for line in settings.get("bq_ddl_schema", "").split('\n') 
                                   if 'CREATE OR REPLACE TABLE' in line])
        }
    except Exception as e:
        return {
            "project_id": "error",
            "dataset_id": "error",
            "schema": f"Error: {str(e)}",
            "tables_available": 0
        }

@app.post("/api/apps-script/analyze-pdf")
async def analyze_pdf_content(request: Dict[str, Any]):
    """Analyze PDF content for insights (placeholder for future implementation)"""
    try:
        return {
            "success": True,
            "analysis": {
                "summary": "PDF analysis feature coming soon!",
                "key_insights": ["Feature in development"],
                "recommendations": "Use 'Analyze Data' for BigQuery integration"
            },
            "next_steps": "Use the data analysis feature for now"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Demo endpoint for testing
@app.post("/api/demo")
async def demo_analysis():
    """Demo endpoint that returns sample data for testing"""
    return {
        "success": True,
        "data": [
            {"region": "North", "sales": 150000, "growth": "12%"},
            {"region": "South", "sales": 120000, "growth": "8%"},
            {"region": "East", "sales": 180000, "growth": "15%"},
            {"region": "West", "sales": 110000, "growth": "5%"}
        ],
        "summary": "Demo data: 4 regions analyzed",
        "charts": {
            "chart_recommendations": [
                {"type": "bar", "title": "Sales by Region"},
                {"type": "line", "title": "Growth Trends"}
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting InstantDashboard Google Apps Script API...")
    print("🔗 API will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🎯 Google Apps Script ready endpoints:")
    print("   • POST /api/apps-script/quick-query")
    print("   • GET /api/schema") 
    print("   • POST /api/apps-script/auth")
    print("   • POST /api/demo (for testing)")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 