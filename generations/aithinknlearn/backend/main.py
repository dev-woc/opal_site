"""
Main entry point for the Multi-Agent Orchestration System

Provides a FastAPI server with endpoints for testing the agent system.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.orchestrator import MultiAgentOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Literacy Pipeline - Multi-Agent Orchestration",
    description="Multi-agent system for literacy instruction using CrewAI",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = None


# Request/Response Models
class LearningObjectiveRequest(BaseModel):
    objective: str
    story_theme: Optional[str] = "adventure"
    story_length: Optional[str] = "short"


class StudentError(BaseModel):
    target_word: str
    student_response: str
    context: Optional[str] = ""


class ErrorAnalysisRequest(BaseModel):
    errors: List[StudentError]


class DiagnosticCycleRequest(BaseModel):
    learning_objective: str
    errors: List[StudentError]
    story_theme: Optional[str] = "adventure"


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup"""
    global orchestrator
    logger.info("Starting Multi-Agent Orchestration System")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment. Agent functionality will be limited.")

    orchestrator = MultiAgentOrchestrator(openai_api_key=api_key)
    logger.info("Orchestrator initialized successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Literacy Pipeline - Multi-Agent Orchestration API",
        "version": "0.1.0",
        "status": "running",
        "agents": [
            "Curriculum Planner",
            "Narrative Architect",
            "Diagnostic Specialist"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "orchestrator_initialized": orchestrator is not None
    }


@app.post("/api/lesson/create")
async def create_lesson(request: LearningObjectiveRequest) -> Dict[str, Any]:
    """
    Create a lesson plan with accompanying decodable story

    Args:
        request: Learning objective and story parameters

    Returns:
        Lesson plan and story
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        logger.info(f"Creating lesson for objective: {request.objective}")

        result = orchestrator.create_lesson_with_story(
            learning_objective=request.objective,
            story_theme=request.story_theme,
            story_length=request.story_length
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error creating lesson: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/errors/analyze")
async def analyze_errors(request: ErrorAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze student errors and generate intervention recommendations

    Args:
        request: List of student errors

    Returns:
        Error analysis and recommendations
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        logger.info(f"Analyzing {len(request.errors)} student errors")

        # Convert Pydantic models to dicts
        errors = [error.dict() for error in request.errors]

        result = orchestrator.analyze_and_intervene(student_errors=errors)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error analyzing errors: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/diagnostic/full-cycle")
async def full_diagnostic_cycle(request: DiagnosticCycleRequest) -> Dict[str, Any]:
    """
    Run complete diagnostic cycle: analyze errors, adjust lesson, generate story

    Args:
        request: Learning objective and student errors

    Returns:
        Complete diagnostic and intervention package
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        logger.info(f"Running full diagnostic cycle for: {request.learning_objective}")

        # Convert Pydantic models to dicts
        errors = [error.dict() for error in request.errors]

        result = orchestrator.full_diagnostic_cycle(
            learning_objective=request.learning_objective,
            student_errors=errors,
            story_theme=request.story_theme
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error in diagnostic cycle: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scratchpad/log")
async def get_scratchpad_log() -> Dict[str, Any]:
    """
    Get complete scratchpad log for teacher review

    Returns:
        Complete log of all agent decisions and state changes
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        log = orchestrator.get_scratchpad_log()
        return {
            "success": True,
            "data": log
        }

    except Exception as e:
        logger.error(f"Error getting scratchpad log: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scratchpad/state")
async def get_scratchpad_state() -> Dict[str, Any]:
    """
    Get current scratchpad state

    Returns:
        Current shared state
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        state = orchestrator.scratchpad.get_state()
        return {
            "success": True,
            "data": state
        }

    except Exception as e:
        logger.error(f"Error getting scratchpad state: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scratchpad/verify-consistency")
async def verify_state_consistency() -> Dict[str, Any]:
    """
    Verify that shared state is consistent across agents

    Returns:
        Consistency verification results
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        consistency = orchestrator.verify_state_consistency()
        return {
            "success": True,
            "data": consistency
        }

    except Exception as e:
        logger.error(f"Error verifying consistency: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scratchpad/reset")
async def reset_orchestrator() -> Dict[str, Any]:
    """
    Reset the orchestrator and scratchpad

    Returns:
        Success message
    """
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        orchestrator.reset()
        return {
            "success": True,
            "message": "Orchestrator reset successfully"
        }

    except Exception as e:
        logger.error(f"Error resetting orchestrator: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on port {port}")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
