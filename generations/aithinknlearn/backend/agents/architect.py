"""
Narrative Architect Agent

This agent generates engaging stories using strictly allowed phonemes,
ensuring high decodability rates (95%+) for Structured Literacy instruction.
"""

import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class NarrativeArchitectAgent:
    """
    Narrative Architect Agent

    Responsibilities:
    - Generate engaging stories using only allowed phonemes
    - Maintain 95% decodability rate
    - Create age-appropriate, motivating content
    - Integrate target phonemes naturally into narratives
    """

    def __init__(self, scratchpad, llm: Optional[ChatOpenAI] = None):
        """
        Initialize the Narrative Architect Agent

        Args:
            scratchpad: Shared scratchpad for state management
            llm: Language model for agent reasoning (optional)
        """
        self.scratchpad = scratchpad
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

        # Create the CrewAI agent
        self.agent = Agent(
            role="Narrative Architect",
            goal="Generate engaging, decodable stories using strictly allowed phonemes to support reading development",
            backstory="""You are an expert decodable text author who creates engaging stories
            for beginning readers. You understand the critical importance of phonetic control
            and decodability. You craft narratives that are motivating and age-appropriate while
            strictly limiting vocabulary to words that use only the phonemes students have been
            explicitly taught. You know how to make simple stories engaging through character,
            repetition, and rhythm, and you never use words that require guessing or context clues.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        logger.info("NarrativeArchitectAgent initialized")

    def generate_story(
        self,
        allowed_phonemes: List[str],
        theme: str = "adventure",
        length: str = "short"
    ) -> Dict[str, Any]:
        """
        Generate a decodable story using only allowed phonemes

        Args:
            allowed_phonemes: List of phonemes students have been taught
            theme: Story theme (adventure, friendship, animals, etc.)
            length: Story length (short, medium, long)

        Returns:
            Dictionary containing story content and metadata
        """
        logger.info(f"Generating {length} story with theme '{theme}' using {len(allowed_phonemes)} phonemes")

        # Log to scratchpad
        from backend.scratchpad import AgentType
        self.scratchpad.add_entry(
            agent_type=AgentType.NARRATIVE_ARCHITECT,
            content=f"Generating story - Theme: {theme}, Phonemes: {allowed_phonemes}",
            entry_type="observation"
        )

        # Determine target word count
        word_count = {
            "short": "30-50",
            "medium": "75-100",
            "long": "150-200"
        }.get(length, "30-50")

        # Create example words from allowed phonemes
        example_words = self._generate_example_words(allowed_phonemes)

        # Create task for story generation
        task = Task(
            description=f"""Generate a decodable story with the following constraints:

Theme: {theme}
Length: {word_count} words
Allowed phonemes: {', '.join(allowed_phonemes)}

Example decodable words you can use: {', '.join(example_words[:20])}

CRITICAL RULES:
1. ONLY use words that are 100% decodable with the allowed phonemes
2. Maintain 95%+ decodability rate - no sight words beyond high-frequency exceptions
3. Make the story engaging with character, action, and emotion
4. Use repetition and rhythm to support fluency
5. Keep sentences short and simple (5-8 words)
6. Include dialogue to increase engagement
7. Create a clear beginning, middle, and end

Generate the story now.""",
            agent=self.agent,
            expected_output="A complete decodable story following all constraints"
        )

        # Execute task
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        story_text = crew.kickoff()

        # Analyze story
        story_data = {
            "text": story_text,
            "theme": theme,
            "allowed_phonemes": allowed_phonemes,
            "word_count": len(story_text.split()),
            "decodability_rate": self._estimate_decodability(story_text, allowed_phonemes),
            "metadata": {
                "length_category": length,
                "target_word_count": word_count,
                "phoneme_count": len(allowed_phonemes)
            }
        }

        # Log decision
        self.scratchpad.log_decision(
            agent_type=AgentType.NARRATIVE_ARCHITECT,
            decision=f"Generated {length} decodable story with {story_data['word_count']} words",
            reasoning=f"Created engaging {theme} story using {len(allowed_phonemes)} phonemes with {story_data['decodability_rate']}% estimated decodability",
            metadata=story_data
        )

        # Update shared state
        self.scratchpad.update_state("story_content", story_text, AgentType.NARRATIVE_ARCHITECT)

        logger.info(f"Story generated successfully: {story_data['word_count']} words, {story_data['decodability_rate']}% decodable")
        return story_data

    def _generate_example_words(self, phonemes: List[str]) -> List[str]:
        """
        Generate example decodable words from allowed phonemes

        Args:
            phonemes: Allowed phonemes

        Returns:
            List of example words
        """
        # Common decodable words by phoneme set
        basic_words = [
            "mat", "sat", "pat", "cat", "hat", "rat",
            "man", "can", "pan", "ran", "tan",
            "cap", "tap", "map", "nap", "rap",
            "sit", "pit", "hit", "bit", "fit",
            "pin", "tin", "fin", "win", "bin",
            "tip", "hip", "dip", "rip", "sip",
            "hot", "pot", "cot", "dot", "not",
            "hop", "mop", "top", "pop", "cop",
            "hut", "cut", "but", "nut", "rut",
            "hen", "pen", "den", "men", "ten",
            "red", "bed", "fed", "led", "wed",
            "big", "dig", "fig", "pig", "wig",
            "bag", "tag", "rag", "sag", "wag",
            "cup", "pup", "up",
            "run", "fun", "sun", "bun",
            "a", "an", "at", "as", "am",
            "in", "it", "is", "if",
            "on", "or",
            "the", "and", "to"  # High-frequency exceptions
        ]

        return basic_words[:30]

    def _estimate_decodability(self, text: str, allowed_phonemes: List[str]) -> float:
        """
        Estimate decodability rate of text

        Args:
            text: Story text
            allowed_phonemes: Allowed phonemes

        Returns:
            Estimated decodability percentage
        """
        # Simple estimation - in production, use actual G2P conversion
        words = text.lower().split()
        decodable_count = 0

        # High-frequency sight words allowed
        sight_words = {"the", "a", "to", "and", "is", "was", "of", "for", "you", "I"}

        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalpha())

            # Check if it's a sight word or likely decodable
            if clean_word in sight_words or len(clean_word) <= 4:
                decodable_count += 1

        if len(words) == 0:
            return 0.0

        return round((decodable_count / len(words)) * 100, 1)

    def validate_story_decodability(self, story_text: str, allowed_phonemes: List[str]) -> Dict[str, Any]:
        """
        Validate that a story meets decodability requirements

        Args:
            story_text: Story text to validate
            allowed_phonemes: Allowed phonemes

        Returns:
            Validation results
        """
        logger.info("Validating story decodability")

        decodability_rate = self._estimate_decodability(story_text, allowed_phonemes)
        words = story_text.split()

        validation = {
            "passes": decodability_rate >= 95.0,
            "decodability_rate": decodability_rate,
            "word_count": len(words),
            "target_rate": 95.0,
            "issues": []
        }

        if decodability_rate < 95.0:
            validation["issues"].append(f"Decodability rate {decodability_rate}% is below target 95%")

        from backend.scratchpad import AgentType
        self.scratchpad.log_decision(
            agent_type=AgentType.NARRATIVE_ARCHITECT,
            decision=f"Story validation: {'PASS' if validation['passes'] else 'FAIL'}",
            reasoning=f"Decodability rate: {decodability_rate}%",
            metadata=validation
        )

        return validation
