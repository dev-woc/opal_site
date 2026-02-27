"""
Agent Orchestrator

Coordinates the multi-agent system, managing agent interactions and
ensuring proper sequencing of tasks.
"""

from typing import Dict, Any, List, Optional
from app.orchestration.scratchpad import SharedScratchpad, MessageType
from app.agents import (
    CurriculumPlannerAgent,
    NarrativeArchitectAgent,
    DiagnosticSpecialistAgent
)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent system for literacy instruction.

    Manages three specialized agents:
    - Curriculum Planner: Decomposes learning objectives
    - Narrative Architect: Generates decodable stories
    - Diagnostic Specialist: Analyzes student errors

    All agents share a unified scratchpad for state management.
    """

    def __init__(self, max_history: int = 50):
        """
        Initialize the orchestrator with all agents

        Args:
            max_history: Maximum messages to keep in scratchpad
        """
        # Create shared scratchpad
        self.scratchpad = SharedScratchpad(max_history=max_history)

        # Initialize agents
        self.planner = CurriculumPlannerAgent(
            name="CurriculumPlanner",
            scratchpad=self.scratchpad
        )

        self.architect = NarrativeArchitectAgent(
            name="NarrativeArchitect",
            scratchpad=self.scratchpad
        )

        self.diagnostic = DiagnosticSpecialistAgent(
            name="DiagnosticSpecialist",
            scratchpad=self.scratchpad
        )

        # Log orchestrator initialization
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content="Multi-agent orchestration system initialized with 3 agents"
        )

    def plan_curriculum(self, learning_objective: str) -> Dict[str, Any]:
        """
        Use Curriculum Planner to create a lesson plan

        Args:
            learning_objective: The learning goal to plan for

        Returns:
            Dictionary containing the lesson plan
        """
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Initiating curriculum planning for: {learning_objective}"
        )

        result = self.planner.process({
            "objective": learning_objective
        })

        return result

    def generate_narrative(
        self,
        allowed_phonemes: Optional[List[str]] = None,
        allowed_graphemes: Optional[List[str]] = None,
        topic: str = "",
        word_count: int = 100
    ) -> Dict[str, Any]:
        """
        Use Narrative Architect to generate a decodable story

        Args:
            allowed_phonemes: List of phonemes students know
            allowed_graphemes: List of graphemes students know
            topic: Optional story topic/theme
            word_count: Target word count

        Returns:
            Dictionary containing the narrative
        """
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Initiating narrative generation (topic: {topic or 'auto'})"
        )

        result = self.architect.process({
            "allowed_phonemes": allowed_phonemes or [],
            "allowed_graphemes": allowed_graphemes or [],
            "topic": topic,
            "word_count": word_count
        })

        return result

    def diagnose_errors(
        self,
        errors: List[Dict[str, Any]],
        student_id: str = "unknown",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Use Diagnostic Specialist to analyze student errors

        Args:
            errors: List of error instances
            student_id: Student identifier
            context: Additional context about the assessment

        Returns:
            Dictionary containing diagnostic analysis
        """
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Initiating error diagnosis for student {student_id} ({len(errors)} errors)"
        )

        result = self.diagnostic.process({
            "errors": errors,
            "student_id": student_id,
            "context": context
        })

        return result

    def run_full_pipeline(
        self,
        learning_objective: str,
        student_errors: Optional[List[Dict[str, Any]]] = None,
        student_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Run the complete multi-agent pipeline:
        1. Plan curriculum based on objective
        2. Generate narrative based on lesson plan
        3. Optionally analyze student errors if provided

        Args:
            learning_objective: The learning goal
            student_errors: Optional list of student errors to analyze
            student_id: Student identifier

        Returns:
            Dictionary with results from all agents
        """
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Starting full pipeline for objective: {learning_objective}"
        )

        results = {
            "objective": learning_objective,
            "pipeline_steps": []
        }

        # Step 1: Curriculum Planning
        planning_result = self.plan_curriculum(learning_objective)
        results["planning"] = planning_result
        results["pipeline_steps"].append("curriculum_planning")

        # Step 2: Narrative Generation (using lesson plan)
        if planning_result.get("success"):
            narrative_result = self.generate_narrative()
            results["narrative"] = narrative_result
            results["pipeline_steps"].append("narrative_generation")

        # Step 3: Diagnostic Analysis (if errors provided)
        if student_errors:
            diagnostic_result = self.diagnose_errors(
                errors=student_errors,
                student_id=student_id,
                context=f"Errors from lesson on: {learning_objective}"
            )
            results["diagnosis"] = diagnostic_result
            results["pipeline_steps"].append("error_diagnosis")

        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Pipeline complete. Executed {len(results['pipeline_steps'])} steps."
        )

        results["scratchpad_summary"] = {
            "total_messages": len(self.scratchpad.messages),
            "agents_active": ["CurriculumPlanner", "NarrativeArchitect", "DiagnosticSpecialist"]
        }

        return results

    def get_scratchpad_history(self) -> str:
        """
        Export complete scratchpad history

        Returns:
            JSON string of all messages
        """
        return self.scratchpad.export_history()

    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agents and their current state

        Returns:
            Dictionary with agent information
        """
        return {
            "agents": [
                {
                    "name": self.planner.name,
                    "type": "CurriculumPlanner",
                    "model": self.planner.model_name
                },
                {
                    "name": self.architect.name,
                    "type": "NarrativeArchitect",
                    "model": self.architect.model_name
                },
                {
                    "name": self.diagnostic.name,
                    "type": "DiagnosticSpecialist",
                    "model": self.diagnostic.model_name
                }
            ],
            "scratchpad": {
                "messages": len(self.scratchpad.messages),
                "state_variables": len(self.scratchpad.shared_state)
            }
        }

    def reset(self) -> None:
        """Reset the scratchpad (clear all history and state)"""
        self.scratchpad.clear()
        self.scratchpad.add_message(
            agent_name="Orchestrator",
            message_type=MessageType.SYSTEM_EVENT,
            content="Orchestrator reset - all history and state cleared"
        )
