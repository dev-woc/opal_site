"""
Multi-Agent Orchestrator

Coordinates the three specialized agents (Curriculum Planner, Narrative Architect,
Diagnostic Specialist) using CrewAI, with shared scratchpad for unified state management.
"""

import logging
from typing import Dict, List, Any, Optional
import os
from crewai import Crew, Process
from langchain_ollama import ChatOllama

from backend.scratchpad import SharedScratchpad, AgentType
from backend.agents import (
    CurriculumPlannerAgent,
    NarrativeArchitectAgent,
    DiagnosticSpecialistAgent
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Multi-Agent Orchestration System

    Coordinates three specialized agents:
    1. Curriculum Planner - Decomposes learning objectives into lesson plans
    2. Narrative Architect - Generates decodable stories
    3. Diagnostic Specialist - Analyzes errors and suggests interventions

    All agents share a unified scratchpad for state management and decision logging.
    """

    def __init__(self):
        """Initialize the Multi-Agent Orchestrator using Ollama."""
        logger.info("Initializing Multi-Agent Orchestrator")

        # Initialize shared scratchpad
        self.scratchpad = SharedScratchpad()
        logger.info("Shared scratchpad initialized")

        # Initialize LLM via Ollama
        # Configure with OLLAMA_BASE_URL and OLLAMA_MODEL env vars
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        logger.info(f"Connecting to Ollama at {base_url} with model '{model}'")

        self.llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=0.7,
        )

        # Initialize agents
        self.curriculum_planner = CurriculumPlannerAgent(
            scratchpad=self.scratchpad,
            llm=self.llm
        )
        logger.info("Curriculum Planner agent initialized")

        self.narrative_architect = NarrativeArchitectAgent(
            scratchpad=self.scratchpad,
            llm=self.llm
        )
        logger.info("Narrative Architect agent initialized")

        self.diagnostic_specialist = DiagnosticSpecialistAgent(
            scratchpad=self.scratchpad,
            llm=self.llm
        )
        logger.info("Diagnostic Specialist agent initialized")

        logger.info("Multi-Agent Orchestrator initialization complete")

    def create_lesson_with_story(
        self,
        learning_objective: str,
        story_theme: str = "adventure",
        story_length: str = "short"
    ) -> Dict[str, Any]:
        """
        Orchestrate curriculum planning and story generation

        Args:
            learning_objective: Learning objective to teach
            story_theme: Theme for the decodable story
            story_length: Length of story (short, medium, long)

        Returns:
            Dictionary containing lesson plan and story
        """
        logger.info(f"Creating lesson with story - Objective: {learning_objective}")

        # Step 1: Curriculum Planner creates lesson plan
        self.scratchpad.add_conversation_message(
            role="system",
            content=f"Starting lesson creation for objective: {learning_objective}"
        )

        lesson_plan = self.curriculum_planner.decompose_learning_objective(learning_objective)

        # Step 2: Narrative Architect generates story using allowed phonemes from lesson plan
        allowed_phonemes = self.scratchpad.get_state("allowed_phonemes")

        story = self.narrative_architect.generate_story(
            allowed_phonemes=allowed_phonemes,
            theme=story_theme,
            length=story_length
        )

        # Step 3: Validate story decodability
        validation = self.narrative_architect.validate_story_decodability(
            story_text=story["text"],
            allowed_phonemes=allowed_phonemes
        )

        result = {
            "lesson_plan": lesson_plan,
            "story": story,
            "validation": validation,
            "scratchpad_summary": {
                "total_entries": len(self.scratchpad.entries),
                "total_decisions": len(self.scratchpad.decisions),
                "agents_involved": ["curriculum_planner", "narrative_architect"]
            }
        }

        self.scratchpad.add_conversation_message(
            role="assistant",
            content=f"Lesson creation complete. Lesson plan with {len(lesson_plan['lesson_sequence'])} steps and {story['word_count']}-word story generated."
        )

        logger.info("Lesson with story creation complete")
        return result

    def analyze_and_intervene(
        self,
        student_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze student errors and generate intervention recommendations

        Args:
            student_errors: List of student errors to analyze

        Returns:
            Dictionary containing error analysis and recommendations
        """
        logger.info(f"Analyzing {len(student_errors)} student errors")

        self.scratchpad.add_conversation_message(
            role="system",
            content=f"Starting error analysis for {len(student_errors)} errors"
        )

        # Diagnostic Specialist analyzes errors
        analysis = self.diagnostic_specialist.analyze_errors(student_errors)

        # Generate teacher report
        report = self.diagnostic_specialist.generate_error_report(analysis)

        result = {
            "analysis": analysis,
            "report": report,
            "scratchpad_summary": {
                "total_entries": len(self.scratchpad.entries),
                "total_decisions": len(self.scratchpad.decisions),
                "agents_involved": ["diagnostic_specialist"]
            }
        }

        self.scratchpad.add_conversation_message(
            role="assistant",
            content=f"Error analysis complete. {len(analysis['error_patterns'])} patterns identified."
        )

        logger.info("Error analysis and intervention complete")
        return result

    def full_diagnostic_cycle(
        self,
        learning_objective: str,
        student_errors: List[Dict[str, Any]],
        story_theme: str = "adventure"
    ) -> Dict[str, Any]:
        """
        Complete diagnostic cycle: analyze errors, adjust lesson plan, generate targeted story

        Args:
            learning_objective: Learning objective
            student_errors: Student errors to analyze
            story_theme: Theme for remedial story

        Returns:
            Complete diagnostic and intervention package
        """
        logger.info("Starting full diagnostic cycle")

        self.scratchpad.add_conversation_message(
            role="system",
            content="Starting full diagnostic cycle with error analysis and adaptive lesson planning"
        )

        # Step 1: Analyze errors
        error_analysis = self.diagnostic_specialist.analyze_errors(student_errors)

        # Step 2: Create targeted lesson plan based on teaching focuses
        teaching_focuses = self.scratchpad.get_state("teaching_focuses")
        adjusted_objective = f"{learning_objective} - Focus on: {', '.join(teaching_focuses[:2])}"

        lesson_plan = self.curriculum_planner.decompose_learning_objective(adjusted_objective)

        # Step 3: Generate remedial story with allowed phonemes
        allowed_phonemes = self.scratchpad.get_state("allowed_phonemes")

        story = self.narrative_architect.generate_story(
            allowed_phonemes=allowed_phonemes,
            theme=story_theme,
            length="short"
        )

        result = {
            "error_analysis": error_analysis,
            "adjusted_lesson_plan": lesson_plan,
            "remedial_story": story,
            "teaching_focuses": teaching_focuses,
            "scratchpad_summary": {
                "total_entries": len(self.scratchpad.entries),
                "total_decisions": len(self.scratchpad.decisions),
                "agents_involved": ["diagnostic_specialist", "curriculum_planner", "narrative_architect"]
            }
        }

        self.scratchpad.add_conversation_message(
            role="assistant",
            content=f"Full diagnostic cycle complete. {len(error_analysis['error_patterns'])} error patterns addressed in adjusted lesson plan."
        )

        logger.info("Full diagnostic cycle complete")
        return result

    def get_scratchpad_log(self) -> Dict[str, Any]:
        """
        Get complete scratchpad log for teacher review

        Returns:
            Complete log of all agent decisions and state changes
        """
        return self.scratchpad.export_log()

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.scratchpad.get_conversation_history()

    def get_agent_decisions(self, agent_type: Optional[AgentType] = None) -> List[Any]:
        """
        Get agent decisions

        Args:
            agent_type: Specific agent type, or None for all decisions

        Returns:
            List of agent decisions
        """
        if agent_type is None:
            return self.scratchpad.get_all_decisions()
        return self.scratchpad.get_decisions_by_agent(agent_type)

    def verify_state_consistency(self) -> Dict[str, Any]:
        """
        Verify that shared state is consistent across agents

        Returns:
            Consistency verification results
        """
        logger.info("Verifying state consistency across agents")

        state = self.scratchpad.get_state()

        consistency_check = {
            "state_keys": list(state.keys()),
            "lesson_plan_set": state.get("lesson_plan") is not None and len(state.get("lesson_plan", {})) > 0,
            "allowed_phonemes_set": len(state.get("allowed_phonemes", [])) > 0,
            "story_content_set": len(state.get("story_content", "")) > 0,
            "teaching_focuses_set": len(state.get("teaching_focuses", [])) > 0,
            "consistent": True,
            "issues": []
        }

        # Check for consistency issues
        if consistency_check["lesson_plan_set"] and not consistency_check["allowed_phonemes_set"]:
            consistency_check["consistent"] = False
            consistency_check["issues"].append("Lesson plan exists but allowed phonemes not set")

        if consistency_check["story_content_set"] and not consistency_check["allowed_phonemes_set"]:
            consistency_check["consistent"] = False
            consistency_check["issues"].append("Story exists but allowed phonemes not set")

        logger.info(f"State consistency check: {'PASS' if consistency_check['consistent'] else 'FAIL'}")
        return consistency_check

    def reset(self) -> None:
        """Reset the orchestrator and scratchpad"""
        logger.info("Resetting orchestrator")
        self.scratchpad.clear()
        logger.info("Orchestrator reset complete")
