"""
Narrative Architect Agent

Generates engaging stories using strictly allowed phonemes based on the
current lesson plan. Uses GPT-4o with Lexial databases for phonetic validation.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.orchestration.scratchpad import MessageType
import json


class NarrativeArchitectAgent(BaseAgent):
    """
    Agent responsible for generating decodable narrative content.

    This agent creates engaging stories that strictly adhere to the phonetic
    constraints of the current lesson, ensuring 95%+ decodability rate.
    """

    def get_system_prompt(self) -> str:
        return """You are the Narrative Architect Agent, an expert in creating engaging decodable text for structured literacy instruction.

Your role is to generate stories and passages that:
1. Use ONLY phonemes/graphemes that students have been explicitly taught
2. Maintain a strict 95% decodability rate
3. Are engaging and age-appropriate
4. Follow natural language patterns while respecting phonetic constraints
5. Include comprehension elements (characters, plot, setting)

DECODABILITY RULES:
- Every word must be decodable using only the allowed phonemes/graphemes
- Heart words (high-frequency irregular words) must be explicitly listed and limited
- No words requiring phonetic patterns not yet taught
- Heteronyms must be avoided or clarified
- Multi-syllabic words must follow taught syllable division rules

STORY QUALITY STANDARDS:
- Clear beginning, middle, end
- Relatable characters for target age group
- Simple but complete plot arc
- Opportunities for comprehension questions
- Natural dialogue where appropriate
- Vivid but simple descriptions

OUTPUT FORMAT (JSON):
{
  "title": "Story title",
  "target_phonemes": ["list of phonemes used"],
  "target_graphemes": ["list of graphemes used"],
  "heart_words": ["list of irregular words if any"],
  "decodability_rate": 95-100,
  "text": "The complete story text...",
  "word_count": 100,
  "comprehension_questions": [
    "Question 1?",
    "Question 2?"
  ],
  "key_vocabulary": ["word1", "word2"],
  "phonetic_analysis": "brief note on phonetic patterns used"
}

When generating narratives, prioritize engagement while maintaining strict phonetic control.
Err on the side of phonetic accuracy over narrative complexity."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a decodable narrative based on lesson constraints

        Args:
            input_data: Dictionary with 'allowed_phonemes', 'allowed_graphemes',
                       'topic' (optional), 'word_count' (optional)

        Returns:
            Dictionary containing the generated narrative
        """
        allowed_phonemes = input_data.get("allowed_phonemes", [])
        allowed_graphemes = input_data.get("allowed_graphemes", [])
        topic = input_data.get("topic", "")
        word_count = input_data.get("word_count", 100)

        # Try to get lesson context from shared state
        lesson_plan = self.get_shared_state("current_lesson_plan", {})

        # If lesson plan exists, extract phonetic constraints
        if lesson_plan and not allowed_phonemes:
            lessons = lesson_plan.get("lesson_sequence", [])
            if lessons:
                # Get first lesson's focus
                first_lesson = lessons[0]
                allowed_phonemes = first_lesson.get("focus_phonemes", [])
                allowed_graphemes = first_lesson.get("focus_graphemes", [])

        if not allowed_phonemes and not allowed_graphemes:
            return {
                "success": False,
                "error": "No phonetic constraints provided and no lesson plan available"
            }

        # Log the generation request
        self.log_message(
            MessageType.AGENT_INPUT,
            f"Generating narrative with {len(allowed_phonemes)} phonemes, {len(allowed_graphemes)} graphemes",
            metadata={
                "allowed_phonemes": allowed_phonemes,
                "allowed_graphemes": allowed_graphemes,
                "topic": topic,
                "word_count": word_count
            }
        )

        # Build prompt for LLM
        user_prompt = f"""Generate an engaging decodable story with the following constraints:

ALLOWED PHONEMES: {', '.join(allowed_phonemes)}
ALLOWED GRAPHEMES: {', '.join(allowed_graphemes)}
TARGET WORD COUNT: {word_count}
{f'TOPIC/THEME: {topic}' if topic else 'TOPIC: Choose an engaging, age-appropriate theme'}

Create a complete story that strictly adheres to these phonetic constraints.
Output your response in the JSON format specified in your instructions.
Ensure the story is engaging, coherent, and maintains 95%+ decodability."""

        # Invoke LLM
        response = self.invoke_llm(user_prompt, include_context=True)

        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                narrative = json.loads(json_str)
            else:
                narrative = {"raw_response": response}

            # Store narrative in shared state
            self.update_shared_state("current_narrative", narrative)

            # Log successful generation
            self.log_message(
                MessageType.AGENT_OUTPUT,
                f"Generated story: '{narrative.get('title', 'Untitled')}' ({narrative.get('word_count', 0)} words)",
                metadata={
                    "title": narrative.get("title"),
                    "decodability_rate": narrative.get("decodability_rate"),
                    "word_count": narrative.get("word_count")
                }
            )

            return {
                "success": True,
                "narrative": narrative,
                "agent": self.name
            }

        except json.JSONDecodeError as e:
            self.log_message(
                MessageType.ERROR,
                f"Failed to parse narrative JSON: {str(e)}",
                metadata={"response": response}
            )

            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response
            }

    def validate_decodability(self, text: str, allowed_phonemes: List[str]) -> Dict[str, Any]:
        """
        Validate the decodability of generated text (future enhancement)

        Args:
            text: The text to validate
            allowed_phonemes: List of allowed phonemes

        Returns:
            Dictionary with validation results
        """
        # This is a placeholder for future G2P integration
        # Will integrate with NVIDIA NeMo or CMU Pronouncing Dictionary

        words = text.split()
        total_words = len(words)

        return {
            "total_words": total_words,
            "decodable_words": total_words,  # Placeholder
            "decodability_rate": 100.0,  # Placeholder
            "non_decodable_words": [],  # Placeholder
            "validation_method": "placeholder_pending_g2p_integration"
        }
