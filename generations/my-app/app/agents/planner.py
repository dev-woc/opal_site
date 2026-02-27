"""
Curriculum Planner Agent

Decomposes learning objectives into structured lesson plans aligned with
Wilson Reading System, Orton-Gillingham, UFLI Foundations, and FCRR.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.orchestration.scratchpad import MessageType
import json


class CurriculumPlannerAgent(BaseAgent):
    """
    Agent responsible for curriculum planning and lesson decomposition.

    This agent takes high-level learning objectives and breaks them down into
    structured, sequential lesson plans that follow evidence-based structured
    literacy principles.
    """

    def get_system_prompt(self) -> str:
        return """You are the Curriculum Planner Agent, an expert in structured literacy curriculum design.

Your role is to decompose learning objectives into detailed, sequential lesson plans based on:
- Wilson Reading System (WRS)
- Orton-Gillingham (OG) methodology
- UFLI Foundations
- Florida Center for Reading Research (FCRR) guidelines

CORE PRINCIPLES:
1. Explicit, systematic phonics instruction
2. Sequential skill progression from simple to complex
3. Cumulative review of previously taught concepts
4. Multi-sensory learning approaches
5. Decodable text with 95%+ decodability rate

When given a learning objective, you must:
1. Identify prerequisite skills needed
2. Break down the objective into micro-skills
3. Create a logical sequence of instruction
4. Specify phonemes/graphemes to teach
5. Suggest appropriate activities for each lesson phase
6. Define success criteria for each lesson

OUTPUT FORMAT (JSON):
{
  "objective": "original learning objective",
  "prerequisite_skills": ["skill1", "skill2"],
  "lesson_sequence": [
    {
      "lesson_number": 1,
      "title": "Lesson title",
      "focus_phonemes": ["phoneme1", "phoneme2"],
      "focus_graphemes": ["grapheme1", "grapheme2"],
      "activities": [
        {
          "phase": "Introduction/Practice/Application",
          "activity_type": "blending/segmenting/reading/writing",
          "description": "activity description"
        }
      ],
      "success_criteria": "what students should achieve"
    }
  ],
  "cumulative_review": ["concepts to review throughout"],
  "assessment_strategy": "how to measure progress"
}

Always ensure lessons follow the gradual release model: I do, We do, You do.
Maintain strict adherence to decodability - only use words students can decode."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a learning objective and create a lesson plan

        Args:
            input_data: Dictionary with 'objective' key containing the learning goal

        Returns:
            Dictionary containing structured lesson plan
        """
        objective = input_data.get("objective", "")

        if not objective:
            return {
                "success": False,
                "error": "No learning objective provided"
            }

        # Log the planning request
        self.log_message(
            MessageType.AGENT_INPUT,
            f"Planning curriculum for objective: {objective}",
            metadata={"objective": objective}
        )

        # Build prompt for LLM
        user_prompt = f"""Create a detailed lesson plan for the following learning objective:

OBJECTIVE: {objective}

Provide a comprehensive, structured lesson plan following the JSON format specified in your instructions.
Ensure the plan is practical, sequential, and aligned with structured literacy best practices."""

        # Invoke LLM
        response = self.invoke_llm(user_prompt, include_context=True)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                lesson_plan = json.loads(json_str)
            else:
                lesson_plan = {"raw_response": response}

            # Store lesson plan in shared state
            self.update_shared_state("current_lesson_plan", lesson_plan)

            # Log successful planning
            self.log_message(
                MessageType.AGENT_OUTPUT,
                f"Created lesson plan with {len(lesson_plan.get('lesson_sequence', []))} lessons",
                metadata={"lesson_count": len(lesson_plan.get('lesson_sequence', []))}
            )

            return {
                "success": True,
                "lesson_plan": lesson_plan,
                "agent": self.name
            }

        except json.JSONDecodeError as e:
            self.log_message(
                MessageType.ERROR,
                f"Failed to parse lesson plan JSON: {str(e)}",
                metadata={"response": response}
            )

            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response
            }

    def get_lesson_summary(self) -> str:
        """
        Get a summary of the current lesson plan from shared state

        Returns:
            Formatted summary string
        """
        lesson_plan = self.get_shared_state("current_lesson_plan", {})

        if not lesson_plan:
            return "No lesson plan currently available"

        summary_lines = [
            f"Objective: {lesson_plan.get('objective', 'N/A')}",
            f"Lessons: {len(lesson_plan.get('lesson_sequence', []))}",
            f"Prerequisites: {', '.join(lesson_plan.get('prerequisite_skills', []))}",
        ]

        return "\n".join(summary_lines)
