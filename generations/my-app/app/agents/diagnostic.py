"""
Diagnostic Specialist Agent

Analyzes student errors to identify patterns and suggest prescriptive
teaching focuses based on structured literacy principles.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.orchestration.scratchpad import MessageType
import json


class DiagnosticSpecialistAgent(BaseAgent):
    """
    Agent responsible for error analysis and diagnostic assessment.

    This agent examines student performance data to identify specific
    skill gaps and recommend targeted instructional interventions.
    """

    def get_system_prompt(self) -> str:
        return """You are the Diagnostic Specialist Agent, an expert in analyzing student reading errors and prescribing targeted interventions.

Your role is to:
1. Analyze student error patterns
2. Identify underlying skill deficits
3. Recommend specific instructional focuses
4. Suggest appropriate scaffolding strategies
5. Determine prerequisite skills that need reinforcement

ERROR ANALYSIS FRAMEWORK:
- Phonemic Awareness: Can the student segment and blend sounds?
- Phonics: Does the student know grapheme-phoneme correspondences?
- Decoding: Can the student apply phonics rules to unknown words?
- Fluency: Is the reading accurate, automatic, and prosodic?
- Encoding: Can the student spell words using known patterns?
- Comprehension: Does the student understand what they read?

COMMON ERROR TYPES:
- Substitution: wrong phoneme/grapheme
- Omission: missing sounds or letters
- Addition: extra sounds or letters
- Reversal: letter/sound order errors
- Guessing: using context instead of decoding

OUTPUT FORMAT (JSON):
{
  "student_id": "identifier if provided",
  "error_summary": {
    "total_errors": 10,
    "error_types": {
      "substitution": 5,
      "omission": 3,
      "addition": 1,
      "reversal": 1
    }
  },
  "patterns_identified": [
    {
      "pattern": "description of error pattern",
      "frequency": "high/medium/low",
      "examples": ["word1", "word2"],
      "underlying_skill": "specific skill deficit"
    }
  ],
  "diagnostic_findings": [
    "Finding 1",
    "Finding 2"
  ],
  "recommended_interventions": [
    {
      "priority": "high/medium/low",
      "focus_area": "specific skill to teach",
      "activities": ["activity1", "activity2"],
      "duration": "suggested practice time"
    }
  ],
  "prerequisite_review": ["skills to review before new instruction"],
  "progress_monitoring": "how to track improvement"
}

Always base recommendations on evidence-based structured literacy practices.
Provide specific, actionable interventions rather than generic advice."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze student errors and provide diagnostic recommendations

        Args:
            input_data: Dictionary with 'errors' (list of error instances) and
                       optionally 'student_id', 'context'

        Returns:
            Dictionary containing diagnostic analysis and recommendations
        """
        errors = input_data.get("errors", [])
        student_id = input_data.get("student_id", "unknown")
        context = input_data.get("context", "")

        if not errors:
            return {
                "success": False,
                "error": "No error data provided for analysis"
            }

        # Log the diagnostic request
        self.log_message(
            MessageType.AGENT_INPUT,
            f"Analyzing {len(errors)} errors for student {student_id}",
            metadata={
                "student_id": student_id,
                "error_count": len(errors),
                "context": context
            }
        )

        # Format errors for analysis
        error_descriptions = []
        for i, error in enumerate(errors, 1):
            if isinstance(error, dict):
                error_desc = f"{i}. Target: '{error.get('target', 'N/A')}', Student response: '{error.get('response', 'N/A')}'"
                if 'type' in error:
                    error_desc += f", Type: {error['type']}"
            else:
                error_desc = f"{i}. {error}"
            error_descriptions.append(error_desc)

        errors_text = "\n".join(error_descriptions)

        # Build prompt for LLM
        user_prompt = f"""Analyze the following student reading errors and provide diagnostic recommendations:

STUDENT ID: {student_id}
{f'CONTEXT: {context}' if context else ''}

ERRORS:
{errors_text}

Provide a comprehensive diagnostic analysis following the JSON format specified in your instructions.
Identify patterns, underlying skill deficits, and specific, prioritized interventions."""

        # Invoke LLM
        response = self.invoke_llm(user_prompt, include_context=True)

        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                diagnosis = json.loads(json_str)
            else:
                diagnosis = {"raw_response": response}

            # Store diagnosis in shared state
            self.update_shared_state(f"diagnosis_{student_id}", diagnosis)

            # Count high-priority interventions
            interventions = diagnosis.get("recommended_interventions", [])
            high_priority = sum(1 for i in interventions if i.get("priority") == "high")

            # Log successful diagnosis
            self.log_message(
                MessageType.AGENT_OUTPUT,
                f"Completed diagnostic analysis for {student_id}: {len(interventions)} interventions ({high_priority} high priority)",
                metadata={
                    "student_id": student_id,
                    "intervention_count": len(interventions),
                    "high_priority_count": high_priority
                }
            )

            return {
                "success": True,
                "diagnosis": diagnosis,
                "agent": self.name
            }

        except json.JSONDecodeError as e:
            self.log_message(
                MessageType.ERROR,
                f"Failed to parse diagnosis JSON: {str(e)}",
                metadata={"response": response}
            )

            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response
            }

    def get_intervention_summary(self, student_id: str) -> str:
        """
        Get a summary of recommended interventions for a student

        Args:
            student_id: Student identifier

        Returns:
            Formatted summary string
        """
        diagnosis = self.get_shared_state(f"diagnosis_{student_id}", {})

        if not diagnosis:
            return f"No diagnosis available for student {student_id}"

        interventions = diagnosis.get("recommended_interventions", [])
        summary_lines = [f"Interventions for {student_id}:"]

        for i, intervention in enumerate(interventions, 1):
            priority = intervention.get("priority", "unknown")
            focus = intervention.get("focus_area", "N/A")
            summary_lines.append(f"{i}. [{priority.upper()}] {focus}")

        return "\n".join(summary_lines)
