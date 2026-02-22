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

try:
    from backend.orchestrator import MultiAgentOrchestrator
    _HAS_ORCHESTRATOR = True
except Exception as e:
    MultiAgentOrchestrator = None
    _HAS_ORCHESTRATOR = False
    import logging as _log; _log.warning(f"Orchestrator import failed: {e}")

try:
    from backend.rag import VectorDatabase, PedagogicalRulesRetriever, ConstraintValidator
    _HAS_RAG = True
except Exception as e:
    VectorDatabase = PedagogicalRulesRetriever = ConstraintValidator = None
    _HAS_RAG = False
    import logging as _log; _log.warning(f"RAG import failed: {e}")

try:
    from backend.phonetic import G2PConverter, DecodabilityChecker, OrthographicRuleEngine, HeteronymHandler
    _HAS_PHONETIC = True
except Exception as e:
    G2PConverter = DecodabilityChecker = OrthographicRuleEngine = HeteronymHandler = None
    _HAS_PHONETIC = False
    import logging as _log; _log.warning(f"Phonetic import failed: {e}")

try:
    from backend.interactivity import (
        BlendingBoard, TTSEngine, HapticsHandler,
        PerformanceTracker, AdaptiveDifficultyManager
    )
    _HAS_INTERACTIVITY = True
except Exception as e:
    BlendingBoard = TTSEngine = HapticsHandler = PerformanceTracker = AdaptiveDifficultyManager = None
    _HAS_INTERACTIVITY = False
    import logging as _log; _log.warning(f"Interactivity import failed: {e}")

try:
    from backend.pdf_generation import (
        WordCardGenerator, SyllableCardGenerator,
        SoundMappingGenerator, CanvaAPIClient
    )
    _HAS_PDF = True
except Exception as e:
    WordCardGenerator = SyllableCardGenerator = SoundMappingGenerator = CanvaAPIClient = None
    _HAS_PDF = False
    import logging as _log; _log.warning(f"PDF generation import failed: {e}")

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

# Initialize interactivity system
blending_board = None
tts_engine = None
haptics_handler = None
performance_tracker = None
difficulty_manager = None

# Initialize PDF generation system
word_card_gen = None
syllable_card_gen = None
sound_mapping_gen = None
canva_client = None


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
    global blending_board, tts_engine, haptics_handler, performance_tracker, difficulty_manager
    global word_card_gen, syllable_card_gen, sound_mapping_gen, canva_client
    logger.info("Starting Multi-Agent Orchestration System")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-test"):
        logger.warning("OPENAI_API_KEY not found or is test key. Agent functionality will be limited.")
        orchestrator = None
    else:
        try:
            orchestrator = MultiAgentOrchestrator(openai_api_key=api_key)
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            orchestrator = None

    # Initialize RAG system
    try:
        logger.info("Initializing RAG system")
        rag_retriever = PedagogicalRulesRetriever()
        constraint_validator = ConstraintValidator()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        rag_retriever = None
        constraint_validator = None

    # Initialize phonetic verification system
    try:
        logger.info("Initializing Phonetic Verification System")
        g2p_converter = G2PConverter()
        decodability_checker = DecodabilityChecker()
        orthographic_engine = OrthographicRuleEngine()
        heteronym_handler = HeteronymHandler()
        logger.info("Phonetic Verification System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize phonetic system: {e}")
        g2p_converter = None
        decodability_checker = None
        orthographic_engine = None
        heteronym_handler = None

    # Initialize interactivity system
    try:
        logger.info("Initializing Digital Interactivity & Gamification System")
        blending_board = BlendingBoard()
        tts_engine = TTSEngine()
        haptics_handler = HapticsHandler()
        performance_tracker = PerformanceTracker()
        difficulty_manager = AdaptiveDifficultyManager()
        logger.info("Digital Interactivity System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize interactivity system: {e}")
        blending_board = None
        tts_engine = None
        haptics_handler = None
        performance_tracker = None
        difficulty_manager = None

    # Initialize PDF generation system
    logger.info("Initializing PDF Generation System")
    word_card_gen = WordCardGenerator(dpi=300)
    syllable_card_gen = SyllableCardGenerator(dpi=300)
    sound_mapping_gen = SoundMappingGenerator(dpi=300)
    canva_client = CanvaAPIClient()
    logger.info("PDF Generation System initialized successfully")


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


# Digital Interactivity & Gamification Endpoints

class TileRequest(BaseModel):
    letter: str
    phoneme: str
    tile_id: Optional[str] = None


class MoveTileRequest(BaseModel):
    tile_id: str
    new_position: int


class LoadWordRequest(BaseModel):
    word: str
    phoneme_map: Dict[str, str]


class AttemptRequest(BaseModel):
    word: str
    phonemes: List[str]
    success: bool
    time_ms: int
    error_type: Optional[str] = None


class HapticRequest(BaseModel):
    pattern: str
    intensity: Optional[float] = None


class PhonemeHapticRequest(BaseModel):
    phoneme: str
    is_vowel: bool = False


class TTSRequest(BaseModel):
    phoneme: Optional[str] = None
    phonemes: Optional[List[str]] = None
    word: Optional[str] = None
    blend_speed: float = 1.0


@app.post("/api/interactivity/blending-board/add-tile")
async def add_tile_to_board(request: TileRequest) -> Dict[str, Any]:
    """Add a letter tile to the blending board"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        tile = blending_board.add_tile(request.letter, request.phoneme, request.tile_id)
        blend = blending_board.get_blend()

        return {
            "success": True,
            "data": {
                "tile": {
                    "id": tile.tile_id,
                    "letter": tile.letter,
                    "phoneme": tile.phoneme,
                    "position": tile.position
                },
                "current_blend": blend
            }
        }

    except Exception as e:
        logger.error(f"Error adding tile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/interactivity/blending-board/remove-tile/{tile_id}")
async def remove_tile_from_board(tile_id: str) -> Dict[str, Any]:
    """Remove a tile from the blending board"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        removed = blending_board.remove_tile(tile_id)
        blend = blending_board.get_blend()

        return {
            "success": removed,
            "data": {
                "current_blend": blend
            }
        }

    except Exception as e:
        logger.error(f"Error removing tile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/blending-board/move-tile")
async def move_tile_on_board(request: MoveTileRequest) -> Dict[str, Any]:
    """Move a tile to a new position"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        moved = blending_board.move_tile(request.tile_id, request.new_position)
        blend = blending_board.get_blend()

        return {
            "success": moved,
            "data": {
                "current_blend": blend
            }
        }

    except Exception as e:
        logger.error(f"Error moving tile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/blending-board/get-blend")
async def get_current_blend() -> Dict[str, Any]:
    """Get current blend from the board"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        blend = blending_board.get_blend()

        return {
            "success": True,
            "data": blend
        }

    except Exception as e:
        logger.error(f"Error getting blend: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/blending-board/load-word")
async def load_word_on_board(request: LoadWordRequest) -> Dict[str, Any]:
    """Load a word onto the blending board"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        tiles = blending_board.load_word(request.word, request.phoneme_map)
        blend = blending_board.get_blend()

        return {
            "success": True,
            "data": {
                "tiles": [
                    {"id": t.tile_id, "letter": t.letter, "phoneme": t.phoneme, "position": t.position}
                    for t in tiles
                ],
                "current_blend": blend
            }
        }

    except Exception as e:
        logger.error(f"Error loading word: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/blending-board/clear")
async def clear_blending_board() -> Dict[str, Any]:
    """Clear all tiles from the board"""
    if blending_board is None:
        raise HTTPException(status_code=500, detail="Blending board not initialized")

    try:
        blending_board.clear_board()

        return {
            "success": True,
            "message": "Board cleared"
        }

    except Exception as e:
        logger.error(f"Error clearing board: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/tts/generate")
async def generate_tts_audio(request: TTSRequest) -> Dict[str, Any]:
    """Generate TTS audio parameters"""
    if tts_engine is None:
        raise HTTPException(status_code=500, detail="TTS engine not initialized")

    try:
        if request.phoneme:
            audio = tts_engine.generate_phoneme_audio(request.phoneme)
        elif request.phonemes:
            audio = tts_engine.generate_blend_audio(request.phonemes, request.blend_speed)
        elif request.word:
            audio = tts_engine.generate_word_audio(request.word)
        else:
            raise HTTPException(status_code=400, detail="Must provide phoneme, phonemes, or word")

        return {
            "success": True,
            "data": audio
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/tts/settings")
async def get_tts_settings() -> Dict[str, Any]:
    """Get TTS voice settings"""
    if tts_engine is None:
        raise HTTPException(status_code=500, detail="TTS engine not initialized")

    try:
        settings = tts_engine.get_voice_settings()

        return {
            "success": True,
            "data": settings
        }

    except Exception as e:
        logger.error(f"Error getting TTS settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/haptics/generate")
async def generate_haptic_feedback(request: HapticRequest) -> Dict[str, Any]:
    """Generate haptic feedback configuration"""
    if haptics_handler is None:
        raise HTTPException(status_code=500, detail="Haptics handler not initialized")

    try:
        haptic_config = haptics_handler.generate_haptic_feedback(request.pattern, request.intensity)

        return {
            "success": True,
            "data": haptic_config
        }

    except Exception as e:
        logger.error(f"Error generating haptics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/haptics/phoneme-tap")
async def generate_phoneme_haptic(request: PhonemeHapticRequest) -> Dict[str, Any]:
    """Generate haptic feedback for phoneme tap"""
    if haptics_handler is None:
        raise HTTPException(status_code=500, detail="Haptics handler not initialized")

    try:
        haptic_config = haptics_handler.generate_phoneme_tap(request.phoneme, request.is_vowel)

        return {
            "success": True,
            "data": haptic_config
        }

    except Exception as e:
        logger.error(f"Error generating phoneme haptic: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/haptics/settings")
async def get_haptic_settings() -> Dict[str, Any]:
    """Get haptic settings"""
    if haptics_handler is None:
        raise HTTPException(status_code=500, detail="Haptics handler not initialized")

    try:
        settings = haptics_handler.get_haptic_settings()

        return {
            "success": True,
            "data": settings
        }

    except Exception as e:
        logger.error(f"Error getting haptic settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/performance/record-attempt")
async def record_performance_attempt(request: AttemptRequest) -> Dict[str, Any]:
    """Record a student attempt"""
    if performance_tracker is None:
        raise HTTPException(status_code=500, detail="Performance tracker not initialized")

    try:
        metrics = performance_tracker.record_attempt(
            request.word,
            request.phonemes,
            request.success,
            request.time_ms,
            request.error_type
        )

        return {
            "success": True,
            "data": metrics
        }

    except Exception as e:
        logger.error(f"Error recording attempt: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/performance/metrics")
async def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics"""
    if performance_tracker is None:
        raise HTTPException(status_code=500, detail="Performance tracker not initialized")

    try:
        metrics = performance_tracker.get_current_metrics()

        return {
            "success": True,
            "data": metrics
        }

    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/performance/summary")
async def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary"""
    if performance_tracker is None:
        raise HTTPException(status_code=500, detail="Performance tracker not initialized")

    try:
        summary = performance_tracker.get_performance_summary()

        return {
            "success": True,
            "data": summary
        }

    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/difficulty/info")
async def get_difficulty_info() -> Dict[str, Any]:
    """Get current difficulty information"""
    if difficulty_manager is None:
        raise HTTPException(status_code=500, detail="Difficulty manager not initialized")

    try:
        info = difficulty_manager.get_difficulty_info()

        return {
            "success": True,
            "data": info
        }

    except Exception as e:
        logger.error(f"Error getting difficulty info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/difficulty/next-word")
async def get_next_difficulty_word(force_boss: bool = False) -> Dict[str, Any]:
    """Get next word based on difficulty"""
    if difficulty_manager is None:
        raise HTTPException(status_code=500, detail="Difficulty manager not initialized")

    try:
        word_challenge = difficulty_manager.get_next_word(force_boss)

        return {
            "success": True,
            "data": word_challenge
        }

    except Exception as e:
        logger.error(f"Error getting next word: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interactivity/difficulty/add-xp/{points}")
async def add_xp_points(points: int) -> Dict[str, Any]:
    """Add XP points and check for level up"""
    if difficulty_manager is None:
        raise HTTPException(status_code=500, detail="Difficulty manager not initialized")

    try:
        result = difficulty_manager.add_xp(points)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error adding XP: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/difficulty/boss-status")
async def get_boss_level_status() -> Dict[str, Any]:
    """Get boss level status"""
    if difficulty_manager is None:
        raise HTTPException(status_code=500, detail="Difficulty manager not initialized")

    try:
        status = difficulty_manager.get_boss_level_status()

        return {
            "success": True,
            "data": status
        }

    except Exception as e:
        logger.error(f"Error getting boss status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactivity/stats")
async def get_interactivity_stats() -> Dict[str, Any]:
    """Get interactivity system statistics"""
    if blending_board is None or tts_engine is None or haptics_handler is None:
        raise HTTPException(status_code=500, detail="Interactivity system not initialized")

    try:
        return {
            "success": True,
            "data": {
                "blending_board_tiles": len(blending_board.tiles),
                "tts_supported_phonemes": len(tts_engine.get_supported_phonemes()),
                "haptic_patterns": len(haptics_handler.pattern_library),
                "performance_attempts": performance_tracker.metrics.total_attempts if performance_tracker else 0,
                "current_difficulty": difficulty_manager.current_level.name if difficulty_manager else "N/A",
                "system_status": "operational"
            }
        }

    except Exception as e:
        logger.error(f"Error getting interactivity stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# PDF Generation Endpoints

class WordCardRequest(BaseModel):
    words: List[Dict[str, str]]
    category: Optional[str] = "phonics"


class SyllableCardRequest(BaseModel):
    words: List[Dict[str, Any]]
    category: Optional[str] = "phonological"


class SoundMappingRequest(BaseModel):
    words: List[Dict[str, Any]]
    category: Optional[str] = "phonics"


class TemplateRequest(BaseModel):
    grade_level: str
    activity_type: str


@app.post("/api/pdf/generate-word-cards")
async def generate_word_cards_pdf(request: WordCardRequest):
    """Generate PDF with word cards"""
    if word_card_gen is None:
        raise HTTPException(status_code=500, detail="PDF generator not initialized")

    try:
        logger.info(f"Generating word cards PDF with {len(request.words)} words")
        pdf_bytes = word_card_gen.generate_word_cards(request.words, request.category)

        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=word_cards_{request.category}.pdf"
            }
        )

    except Exception as e:
        logger.error(f"Error generating word cards PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf/generate-syllable-cards")
async def generate_syllable_cards_pdf(request: SyllableCardRequest):
    """Generate PDF with syllable cards"""
    if syllable_card_gen is None:
        raise HTTPException(status_code=500, detail="PDF generator not initialized")

    try:
        logger.info(f"Generating syllable cards PDF with {len(request.words)} words")
        pdf_bytes = syllable_card_gen.generate_syllable_cards(request.words, request.category)

        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=syllable_cards_{request.category}.pdf"
            }
        )

    except Exception as e:
        logger.error(f"Error generating syllable cards PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf/generate-sound-mapping")
async def generate_sound_mapping_pdf(request: SoundMappingRequest):
    """Generate PDF with sound mapping boxes"""
    if sound_mapping_gen is None:
        raise HTTPException(status_code=500, detail="PDF generator not initialized")

    try:
        logger.info(f"Generating sound mapping PDF with {len(request.words)} words")
        pdf_bytes = sound_mapping_gen.generate_sound_mapping_worksheet(request.words, request.category)

        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=sound_mapping_{request.category}.pdf"
            }
        )

    except Exception as e:
        logger.error(f"Error generating sound mapping PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pdf/canva-templates")
async def get_canva_templates(request: TemplateRequest) -> Dict[str, Any]:
    """Get Canva template suggestions"""
    if canva_client is None:
        raise HTTPException(status_code=500, detail="Canva client not initialized")

    try:
        logger.info(f"Getting Canva templates for {request.grade_level} {request.activity_type}")
        templates = canva_client.suggest_templates(request.grade_level, request.activity_type)

        return {
            "success": True,
            "data": {
                "templates": templates,
                "count": len(templates),
                "grade_level": request.grade_level,
                "activity_type": request.activity_type
            }
        }

    except Exception as e:
        logger.error(f"Error getting Canva templates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pdf/canva-colors/{category}")
async def get_canva_color_scheme(category: str) -> Dict[str, Any]:
    """Get FCRR color scheme for category"""
    if canva_client is None:
        raise HTTPException(status_code=500, detail="Canva client not initialized")

    try:
        color_scheme = canva_client.get_color_scheme(category)

        return {
            "success": True,
            "data": {
                "category": category,
                "color_scheme": color_scheme
            }
        }

    except Exception as e:
        logger.error(f"Error getting color scheme: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pdf/stats")
async def get_pdf_stats() -> Dict[str, Any]:
    """Get PDF generation system statistics"""
    if word_card_gen is None:
        raise HTTPException(status_code=500, detail="PDF system not initialized")

    try:
        return {
            "success": True,
            "data": {
                "dpi": word_card_gen.dpi,
                "page_size": f"{word_card_gen.width} x {word_card_gen.height}",
                "supported_categories": ["phonological", "phonics", "vocabulary", "fluency", "comprehension"],
                "card_types": ["word_cards", "syllable_cards", "sound_mapping"],
                "canva_integration": "enabled",
                "system_status": "operational"
            }
        }

    except Exception as e:
        logger.error(f"Error getting PDF stats: {str(e)}", exc_info=True)
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
