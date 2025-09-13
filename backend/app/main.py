"""
Quantum Code Inspector - FastAPI Backend
Advanced AI-powered code quality analysis platform
"""

import asyncio
import tempfile
import shutil
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer 
from loguru import logger
import time
import os
from datetime import datetime

# Import with error handling
try:
    from app.agents.quality_agent import QualityIntelligenceAgent
except ImportError as e:
    logger.error(f"❌ Failed to import QualityIntelligenceAgent: {str(e)}")
    QualityIntelligenceAgent = None

from app.models.analysis import AnalysisRequest, AnalysisResponse, QARequest, QAResponse
from app.utils.file_handler import FileHandler
from app.utils.config import get_settings
from app.api.auth import router as auth_router, get_current_user, get_current_user_optional
from app.auth.supabase_client import supabase_client

# Global agent instance
quality_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global quality_agent
    
    logger.info("🚀 Starting Quantum Code Inspector...")
    
    try:
        # Initialize the quality agent
        if QualityIntelligenceAgent:
            quality_agent = QualityIntelligenceAgent()
            # REMOVE THIS LINE: await quality_agent.initialize()
            logger.info("✅ Agent initialized successfully")
        else:
            logger.warning("⚠️  QualityIntelligenceAgent not available - some features may be limited")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {str(e)}")
        logger.warning("⚠️  Continuing without full AI capabilities")
    
    yield
    
    logger.info("🔄 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Quantum Code Inspector API",
    description="Advanced AI-powered code quality analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Initialize components
settings = get_settings()
file_handler = FileHandler()
security = HTTPBearer()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 Quantum Code Inspector API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "AI-powered code analysis",
            "Multi-language support", 
            "Security vulnerability detection",
            "Performance optimization suggestions",
            "Interactive Q&A with codebase",
            "RAG for large codebases"
        ],
        "agent_status": "initialized" if quality_agent else "limited"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "agent_initialized": quality_agent is not None,
        "supabase_connected": supabase_client is not None
    }

# File Analysis Endpoints
@app.post("/analyze")
async def analyze_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    name: str = Form(...),
    current_user = Depends(get_current_user)
):
    """Analyze uploaded files"""
    try:
        if not quality_agent:
            raise HTTPException(
                status_code=503, 
                detail="Analysis service not available. Please check server configuration."
            )
        
        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > settings.max_files_per_analysis:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many files. Maximum {settings.max_files_per_analysis} files allowed"
            )
        
        # Process files
        temp_dir = await file_handler.handle_uploaded_files(files)
        
        # Create analysis record with PENDING status initially
        analysis_data = {
            "user_id": current_user["id"],
            "name": name,
            "type": "upload",
            "repository_url": None,
            "repository_info": {
                "path": temp_dir,
                "total_files": len(files),
                "total_lines": 0,  # Will be updated after analysis
                "file_names": [f.filename for f in files]
            },
            "quality_metrics": {},
            "language_stats": [],
            "issues": [],
            "dependencies": [],
            "architecture_insights": [],
            "summary": "",
            "recommendations": [],
            "processing_time": 0,
            "files_analyzed": 0,
            "lines_analyzed": 0,
            "issues_count": 0,
            "status": "pending"  # Fixed: Use "pending" instead of "running"
        }
        
        # Save initial record
        analysis_id = await supabase_client.save_analysis(analysis_data)
        
        # Start background analysis - pass analysis_id
        background_tasks.add_task(
            run_analysis_background,
            temp_dir,
            analysis_data,
            current_user["id"],
            analysis_id
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "Analysis started. You can check the status using the analysis ID.",
            "estimated_time": "1-3 minutes"
        }
        
    except Exception as e:
        logger.error(f"❌ File analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/github")
async def analyze_github_repository(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Analyze GitHub repository"""
    try:
        logger.info(f"🔍 Starting GitHub repository analysis for user {current_user['email']}")
        
        # Validate repository URL
        if not request.repo_url:  # FIXED: Use repo_url instead of repository_url
            raise HTTPException(status_code=400, detail="Repository URL is required")
        
        # Create temporary directory for cloning
        temp_dir = None
        
        # Prepare analysis data
        analysis_data = {
            "user_id": current_user["id"],
            "name": f"GitHub Analysis - {request.repo_url.split('/')[-1]} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",  # FIXED
            "type": "github",
            "repository_url": request.repo_url,  # FIXED: Use repo_url from request
            "repository_info": {
                "path": request.repo_url,  # FIXED
                "branch": request.branch or "main",
                "total_files": 0,  # Will be updated after analysis
                "total_lines": 0
            },
            "quality_metrics": {},
            "language_stats": [],
            "issues": [],
            "dependencies": [],
            "architecture_insights": [],
            "summary": "",
            "recommendations": [],
            "processing_time": 0,
            "files_analyzed": 0,
            "lines_analyzed": 0,
            "issues_count": 0,
            "status": "pending"  # Fixed: Use "pending" instead of "running"
        }
        
        # Save initial record
        analysis_id = await supabase_client.save_analysis(analysis_data)
        
        # Start background analysis
        background_tasks.add_task(
            run_github_analysis_background,  # FIXED: Use separate function for GitHub
            request.repo_url,  # FIXED: Pass repo_url
            request.branch,
            analysis_data,
            current_user["id"],
            analysis_id
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "processing", 
            "message": "Repository analysis started. You can check the status using the analysis ID.",
            "estimated_time": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"❌ GitHub analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_background(
    temp_dir: str, 
    analysis_data: Dict, 
    user_id: str, 
    analysis_id: str
):
    """Run analysis in background"""
    try:
        logger.info(f"🔍 Starting background analysis for user {user_id}")
        
        # Update status to processing (not "running")
        await supabase_client.update_analysis(analysis_id, {"status": "processing"})  # FIXED: Use "processing"
        
        if not quality_agent:
            raise Exception("Quality agent not available")
        
        # Perform analysis
        result = await quality_agent.analyze_codebase(temp_dir)
        
        # FIXED: Set the analysis_id in the result
        result.analysis_id = analysis_id
        
        # Convert result to dict for database storage
        result_dict = {
            "user_id": user_id,
            "name": analysis_data["name"],
            "type": analysis_data["type"],
            "repository_url": analysis_data.get("repository_url"),
            "repository_info": result.repository_info,
            "quality_metrics": result.quality_metrics.dict(),
            "language_stats": [stat.dict() for stat in result.language_stats],
            "issues": [issue.dict() for issue in result.issues],
            "dependencies": [dep.dict() for dep in result.dependencies] if result.dependencies else [],
            "architecture_insights": [insight.dict() for insight in result.architecture_insights] if result.architecture_insights else [],
            "summary": result.summary,
            "recommendations": result.recommendations,
            "processing_time": result.processing_time,
            "files_analyzed": result.files_analyzed,
            "lines_analyzed": result.lines_analyzed,
            "issues_count": len(result.issues),
            "status": "completed"
        }
        
        # Update analysis record
        await supabase_client.update_analysis(analysis_id, result_dict)
        
        logger.info(f"✅ Background analysis completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Background analysis failed: {str(e)}")
        
        # Update status to failed
        await supabase_client.update_analysis(analysis_id, {
            "status": "failed",
            "summary": f"Analysis failed: {str(e)}"
        })
    
    finally:
        # Cleanup temporary directory
        try:
            await file_handler.cleanup_temp_dir(temp_dir)
        except Exception as e:
            logger.warning(f"⚠️  Failed to cleanup temp dir {temp_dir}: {str(e)}")

async def run_github_analysis_background(
    repo_url: str,
    branch: str,
    analysis_data: Dict, 
    user_id: str, 
    analysis_id: str
):
    """Run GitHub repository analysis in background"""
    try:
        logger.info(f"🔍 Starting background GitHub analysis for user {user_id}")
        logger.info(f"📂 Repository: {repo_url}, Branch: {branch}")
        
        # Update status to processing
        await supabase_client.update_analysis(analysis_id, {"status": "processing"})
        
        if not quality_agent:
            raise Exception("Quality agent not available")
        
        # Clone repository to temporary directory
        import tempfile
        import subprocess
        import shutil
        import os
        
        temp_dir = tempfile.mkdtemp(prefix="github_analysis_")
        
        try:
            # Check if git is available
            try:
                subprocess.run(["git", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("Git is not installed or not available in PATH")
            
            # Clone the repository
            logger.info(f"📥 Cloning repository: {repo_url}")
            clone_cmd = ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir]
            result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                # Try with main branch if specified branch doesn't exist
                if branch != "main":
                    logger.warning(f"Branch '{branch}' not found, trying 'main' branch")
                    clone_cmd = ["git", "clone", "--depth", "1", "--branch", "main", repo_url, temp_dir]
                    result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    raise Exception(f"Failed to clone repository: {result.stderr}")
            
            logger.info(f"✅ Repository cloned successfully to {temp_dir}")
            
            # Perform analysis
            result = await quality_agent.analyze_codebase(temp_dir)
            
            # Update analysis record with results
            update_data = {
                "status": "completed",
                "quality_metrics": result.quality_metrics.dict() if result.quality_metrics else {},
                "language_stats": [stat.dict() for stat in result.language_stats] if result.language_stats else [],
                "issues": [issue.dict() for issue in result.issues] if result.issues else [],
                "dependencies": [dep.dict() for dep in result.dependencies] if result.dependencies else [],
                "architecture_insights": [insight.dict() for insight in result.architecture_insights] if result.architecture_insights else [],
                "summary": result.summary or "",
                "recommendations": result.recommendations or [],
                "processing_time": result.processing_time or 0,
                "files_analyzed": result.files_analyzed or 0,
                "lines_analyzed": result.lines_analyzed or 0,
                "issues_count": len(result.issues) if result.issues else 0
            }
            
            await supabase_client.update_analysis(analysis_id, update_data)
            logger.info(f"✅ Background GitHub analysis completed for user {user_id}")
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"🧹 Cleaned up temporary directory: {temp_dir}")
        
    except Exception as e:
        logger.error(f"❌ Background GitHub analysis failed: {str(e)}")
        # Update status to failed
        try:
            await supabase_client.update_analysis(analysis_id, {
                "status": "failed",
                "summary": f"Analysis failed: {str(e)}"
            })
        except Exception as update_error:
            logger.error(f"Failed to update analysis status: {update_error}")

@app.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Get analysis results"""
    try:
        analysis = await supabase_client.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check ownership
        if analysis.get("user_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
async def get_user_analyses(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's analysis history"""
    try:
        analyses = await supabase_client.get_user_analyses(
            current_user["id"], 
            limit=limit, 
            offset=offset
        )
        return {"analyses": analyses, "total": len(analyses)}
        
    except Exception as e:
        logger.error(f"❌ Failed to get user analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """Delete an analysis"""
    try:
        # Verify ownership
        analysis = await supabase_client.get_analysis(analysis_id)
        if not analysis or analysis.get("user_id") != current_user["id"]:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Delete analysis
        await supabase_client.delete_analysis(analysis_id)
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Q&A Endpoints
@app.post("/api/qa")
async def ask_question(
    request: QARequest,
    current_user = Depends(get_current_user)
):
    """Ask a question about code analysis"""
    try:
        logger.info(f"🤔 Q&A request from user {current_user['email']}: {request.question}")
        
        if not quality_agent:
            raise HTTPException(status_code=503, detail="Analysis service not available")
        
        # Get analysis context if analysis_id provided
        context = "General code analysis context."
        if request.analysis_id:
            analysis = await supabase_client.get_analysis(request.analysis_id)
            if analysis and analysis.get("user_id") == current_user["id"]:
                context = f"Analysis summary: {analysis.get('summary', '')}"
        
        # Ask question - FIXED: answer_question returns a string
        answer = await quality_agent.answer_question(request.question, context)
        
        # Save Q&A session if analysis_id provided
        if request.analysis_id:
            await supabase_client.save_qa_session({
                "analysis_id": request.analysis_id,
                "user_id": current_user["id"],
                "question": request.question,
                "answer": answer,  # FIXED: answer is a string
                "confidence": 0.8,  # Default confidence
                "context": context
            })
        
        return QAResponse(
            answer=answer,  # FIXED: answer is a string
            confidence=0.8,  # Default confidence
            follow_up_questions=[]  # Can be enhanced later
        )
        
    except Exception as e:
        logger.error(f"❌ Q&A failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/{analysis_id}")
async def chat_about_analysis(
    analysis_id: str,
    question: str = Form(...),
    current_user = Depends(get_current_user)
):
    """Chat about specific analysis"""
    try:
        if not quality_agent:
            return {
                "answer": "AI chat service is currently unavailable.",
                "confidence": 0.0
            }
        
        # Verify analysis ownership
        analysis = await supabase_client.get_analysis(analysis_id)
        if not analysis or analysis.get("user_id") != current_user["id"]:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get context from analysis
        context = f"""
        Analysis Summary: {analysis.get('summary', '')}
        Issues Found: {analysis.get('issues_count', 0)}
        Files Analyzed: {analysis.get('files_analyzed', 0)}
        """
        
        # Ask question with context
        answer = await quality_agent.answer_question(question, context)
        
        return {
            "answer": answer,  # Fixed: answer is a string
            "confidence": 0.8,  # Default confidence
            "follow_up_questions": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Information Endpoints
@app.get("/api/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": [
            {"name": "Python", "extensions": [".py"], "features": ["AST", "Security", "Performance"]},
            {"name": "JavaScript", "extensions": [".js", ".jsx"], "features": ["AST", "Security", "Performance"]},
            {"name": "TypeScript", "extensions": [".ts", ".tsx"], "features": ["AST", "Security", "Performance"]},
            {"name": "Java", "extensions": [".java"], "features": ["AST", "Security", "Performance"]},
            {"name": "Go", "extensions": [".go"], "features": ["AST", "Security", "Performance"]},
            {"name": "C++", "extensions": [".cpp", ".cc", ".cxx"], "features": ["Security", "Performance"]},
            {"name": "C#", "extensions": [".cs"], "features": ["Security", "Performance"]}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)