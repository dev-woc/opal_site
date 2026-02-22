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
from backend.rag import VectorDatabase, PedagogicalRulesRetriever, ConstraintValidator
from backend.phonetic import G2PConverter, DecodabilityChecker, OrthographicRuleEngine, HeteronymHandler

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

# Initialize orchestrator and RAG system
orchestrator = None
rag_retriever = None
constraint_validator = None

# Initialize phonetic verification system
g2p_converter = None
decodability_checker = None
orthographic_engine = None
heteronym_handler = None


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


class RAGQueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5
    source_filter: Optional[str] = None
    category_filter: Optional[str] = None


class ValidationRequest(BaseModel):
    text: str
    allowed_phonemes: List[str]
    allowed_sight_words: Optional[List[str]] = None


class ConstraintValidationRequest(BaseModel):
    generated_output: str
    allowed_phonemes: List[str]
    retrieved_rules: List[Dict[str, Any]]
    allowed_sight_words: Optional[List[str]] = None


# Phonetic Verification Request Models
class G2PConversionRequest(BaseModel):
    words: List[str]
    context: Optional[str] = None


class HeteronymAnalysisRequest(BaseModel):
    word: str
    context: Optional[str] = None


class DecodabilityRequest(BaseModel):
    text: str
    allowed_phonemes: List[str]
    allowed_sight_words: Optional[List[str]] = None


class OrthographicRuleRequest(BaseModel):
    base_word: str
    suffix: str
    result_word: str
    rule_type: Optional[str] = "auto"  # "111", "y_to_i", "silent_e", "auto"


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator and RAG system on startup"""
    global orchestrator, rag_retriever, constraint_validator
    global g2p_converter, decodability_checker, orthographic_engine, heteronym_handler
    logger.info("Starting Multi-Agent Orchestration System")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment. Agent functionality will be limited.")

    orchestrator = MultiAgentOrchestrator(openai_api_key=api_key)
    logger.info("Orchestrator initialized successfully")

    # Initialize RAG system
    logger.info("Initializing RAG system")
    rag_retriever = PedagogicalRulesRetriever()
    constraint_validator = ConstraintValidator()
    logger.info("RAG system initialized successfully")

    # Initialize phonetic verification system
    logger.info("Initializing Phonetic Verification System")
    g2p_converter = G2PConverter()
    decodability_checker = DecodabilityChecker()
    orthographic_engine = OrthographicRuleEngine()
    heteronym_handler = HeteronymHandler()
    logger.info("Phonetic Verification System initialized successfully")


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


# RAG System Endpoints

@app.post("/api/rag/retrieve-rules")
async def retrieve_pedagogical_rules(request: RAGQueryRequest) -> Dict[str, Any]:
    """
    Retrieve pedagogical rules from RAG system

    Args:
        request: Query parameters for rule retrieval

    Returns:
        Retrieved rules with source citations
    """
    if rag_retriever is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")

    try:
        logger.info(f"Retrieving rules for query: {request.query}")

        rules = rag_retriever.retrieve_rules(
            query=request.query,
            n_results=request.n_results,
            source_filter=request.source_filter,
            category_filter=request.category_filter
        )

        return {
            "success": True,
            "data": {
                "rules": rules,
                "count": len(rules),
                "query": request.query
            }
        }

    except Exception as e:
        logger.error(f"Error retrieving rules: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/word-list/{grade_level}")
async def get_word_list(grade_level: str) -> Dict[str, Any]:
    """
    Get grade-appropriate word list from FCRR database

    Args:
        grade_level: Grade level (kindergarten, grade1, grade2, grade3)

    Returns:
        Word list for specified grade level
    """
    if rag_retriever is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")

    try:
        logger.info(f"Retrieving word list for grade level: {grade_level}")

        word_list = rag_retriever.get_word_list(grade_level)

        return {
            "success": True,
            "data": {
                "word_list": word_list,
                "count": len(word_list),
                "grade_level": grade_level
            }
        }

    except Exception as e:
        logger.error(f"Error retrieving word list: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/validate-decodability")
async def validate_decodability(request: ValidationRequest) -> Dict[str, Any]:
    """
    Validate text decodability against allowed phonemes

    Args:
        request: Text and allowed phonemes

    Returns:
        Validation results
    """
    if constraint_validator is None:
        raise HTTPException(status_code=500, detail="Constraint validator not initialized")

    try:
        logger.info(f"Validating decodability of text ({len(request.text)} chars)")

        validation = constraint_validator.validate_decodability(
            text=request.text,
            allowed_phonemes=request.allowed_phonemes,
            allowed_sight_words=request.allowed_sight_words
        )

        return {
            "success": True,
            "data": validation
        }

    except Exception as e:
        logger.error(f"Error validating decodability: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/validate-output")
async def validate_output(request: ConstraintValidationRequest) -> Dict[str, Any]:
    """
    Validate generated output against RAG constraints

    Args:
        request: Generated output and constraints

    Returns:
        Comprehensive validation results
    """
    if constraint_validator is None:
        raise HTTPException(status_code=500, detail="Constraint validator not initialized")

    try:
        logger.info(f"Validating output against RAG constraints")

        constraints = {
            "allowed_phonemes": request.allowed_phonemes,
            "retrieved_rules": request.retrieved_rules,
            "allowed_sight_words": request.allowed_sight_words
        }

        validation = constraint_validator.validate_output(
            generated_output=request.generated_output,
            constraints=constraints
        )

        # Also check if output should be rejected
        rejection_check = constraint_validator.reject_non_compliant(
            generated_output=request.generated_output,
            constraints=constraints
        )

        return {
            "success": True,
            "data": {
                "validation": validation,
                "accepted": rejection_check["accepted"],
                "rejection_reason": rejection_check["rejection_reason"]
            }
        }

    except Exception as e:
        logger.error(f"Error validating output: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/stats")
async def get_rag_stats() -> Dict[str, Any]:
    """
    Get RAG system statistics

    Returns:
        Statistics about loaded rules
    """
    if rag_retriever is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")

    try:
        total_rules = rag_retriever.vector_db.count_rules()

        # Get counts by source
        sources = ["WRS", "OG", "UFLI", "FCRR"]
        source_counts = {}
        for source in sources:
            rules = rag_retriever.get_rules_by_source(source)
            source_counts[source] = len(rules)

        return {
            "success": True,
            "data": {
                "total_rules": total_rules,
                "source_counts": source_counts,
                "available_word_lists": list(rag_retriever.SAMPLE_WORD_LISTS.keys())
            }
        }

    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phonetic Verification Endpoints

@app.post("/api/phonetic/g2p-convert")
async def convert_g2p(request: G2PConversionRequest) -> Dict[str, Any]:
    """
    Convert words to phoneme sequences using G2P

    Args:
        request: Words to convert and optional context

    Returns:
        Phoneme conversions for each word
    """
    if g2p_converter is None:
        raise HTTPException(status_code=500, detail="G2P converter not initialized")

    try:
        logger.info(f"Converting {len(request.words)} words to phonemes")

        results = {}
        for word in request.words:
            phonemes = g2p_converter.convert(word, context=request.context)
            breakdown = g2p_converter.get_phoneme_breakdown(word)
            results[word] = breakdown

        return {
            "success": True,
            "data": {
                "conversions": results,
                "count": len(results)
            }
        }

    except Exception as e:
        logger.error(f"Error converting to phonemes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phonetic/analyze-heteronym")
async def analyze_heteronym(request: HeteronymAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze heteronym with context-based disambiguation

    Args:
        request: Word and optional context

    Returns:
        Heteronym analysis with all variants
    """
    if heteronym_handler is None:
        raise HTTPException(status_code=500, detail="Heteronym handler not initialized")

    try:
        logger.info(f"Analyzing heteronym: {request.word}")

        analysis = heteronym_handler.analyze_heteronym(request.word, request.context)

        return {
            "success": True,
            "data": analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing heteronym: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phonetic/check-decodability")
async def check_decodability(request: DecodabilityRequest) -> Dict[str, Any]:
    """
    Check text decodability against allowed phonemes

    Args:
        request: Text, allowed phonemes, and optional sight words

    Returns:
        Decodability analysis with pass/fail status
    """
    if decodability_checker is None or g2p_converter is None:
        raise HTTPException(status_code=500, detail="Decodability system not initialized")

    try:
        logger.info(f"Checking decodability of text ({len(request.text)} chars)")

        validation = decodability_checker.validate_content(
            text=request.text,
            allowed_phonemes=request.allowed_phonemes,
            allowed_sight_words=request.allowed_sight_words,
            g2p_converter=g2p_converter
        )

        return {
            "success": True,
            "data": validation
        }

    except Exception as e:
        logger.error(f"Error checking decodability: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phonetic/validate-orthographic")
async def validate_orthographic(request: OrthographicRuleRequest) -> Dict[str, Any]:
    """
    Validate orthographic rule application

    Args:
        request: Base word, suffix, result, and rule type

    Returns:
        Orthographic rule validation
    """
    if orthographic_engine is None:
        raise HTTPException(status_code=500, detail="Orthographic engine not initialized")

    try:
        logger.info(f"Validating orthographic rule: {request.base_word} + {request.suffix}")

        if request.rule_type == "auto":
            result = orthographic_engine.validate_word_formation(
                base_word=request.base_word,
                suffix=request.suffix,
                result_word=request.result_word
            )
        elif request.rule_type == "111":
            result = orthographic_engine.validate_111_rule(
                base_word=request.base_word,
                suffix=request.suffix,
                result_word=request.result_word
            )
        elif request.rule_type == "y_to_i":
            result = orthographic_engine.validate_y_to_i_rule(
                base_word=request.base_word,
                suffix=request.suffix,
                result_word=request.result_word
            )
        elif request.rule_type == "silent_e":
            result = orthographic_engine.validate_silent_e_rule(
                base_word=request.base_word,
                suffix=request.suffix,
                result_word=request.result_word
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown rule type: {request.rule_type}")

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating orthographic rule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phonetic/stats")
async def get_phonetic_stats() -> Dict[str, Any]:
    """
    Get phonetic verification system statistics

    Returns:
        Statistics about the phonetic system
    """
    if g2p_converter is None or heteronym_handler is None:
        raise HTTPException(status_code=500, detail="Phonetic system not initialized")

    try:
        return {
            "success": True,
            "data": {
                "g2p_dictionary_size": len(g2p_converter.cmu_dict),
                "known_heteronyms": len(heteronym_handler.heteronyms),
                "decodability_threshold": decodability_checker.decodability_threshold,
                "decodability_threshold_percentage": decodability_checker.decodability_threshold * 100,
                "system_status": "operational"
            }
        }

    except Exception as e:
        logger.error(f"Error getting phonetic stats: {str(e)}", exc_info=True)
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
