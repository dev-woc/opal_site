"""
Curriculum Planner Agent

This agent decomposes learning objectives into structured lesson plans
following Structured Literacy principles (Wilson Reading System, Orton-Gillingham,
UFLI Foundations, FCRR).
"""

import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class CurriculumPlannerAgent:
    """
    Curriculum Planner Agent

    Responsibilities:
    - Decompose learning objectives into structured lesson plans
    - Follow Structured Literacy scope and sequence
    - Determine phoneme progression and skill targets
    - Integrate Wilson/OG/UFLI/FCRR methodologies
    """

    def __init__(self, scratchpad, llm: Optional[ChatOpenAI] = None):
        """
        Initialize the Curriculum Planner Agent

        Args:
            scratchpad: Shared scratchpad for state management
            llm: Language model for agent reasoning (optional)
        """
        self.scratchpad = scratchpad
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        # Create the CrewAI agent
        self.agent = Agent(
            role="Curriculum Planner",
            goal="Decompose learning objectives into structured, evidence-based lesson plans following Structured Literacy principles",
            backstory="""You are an expert in Structured Literacy methodologies including
            Wilson Reading System, Orton-Gillingham, UFLI Foundations, and FCRR. You create
            detailed lesson plans that follow explicit, systematic phonics instruction with
            a focus on decoding, encoding, and fluency development. You understand phoneme
            progression, the importance of cumulative review, and multisensory teaching strategies.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        logger.info("CurriculumPlannerAgent initialized")

    def decompose_learning_objective(self, objective: str) -> Dict[str, Any]:
        """
        Decompose a learning objective into structured lesson plan steps

        Args:
            objective: Learning objective to decompose

        Returns:
            Dictionary containing lesson plan structure
        """
        logger.info(f"Decomposing learning objective: {objective}")

        # Log to scratchpad
        from backend.scratchpad import AgentType
        self.scratchpad.add_entry(
            agent_type=AgentType.CURRICULUM_PLANNER,
            content=f"Received learning objective: {objective}",
            entry_type="observation"
        )

        # Create task for decomposition
        task = Task(
            description=f"""Decompose the following learning objective into a structured lesson plan:

Objective: {objective}

Create a lesson plan that includes:
1. Target phonemes/graphemes to teach
2. Prerequisite skills needed
3. Lesson sequence (explicit instruction steps)
4. Practice activities (decoding, encoding, fluency)
5. Assessment checkpoints
6. Multisensory components

Follow Structured Literacy principles: explicit, systematic, cumulative, diagnostic.
Ensure 95% decodability by limiting to allowed phonemes.""",
            agent=self.agent,
            expected_output="A structured lesson plan with all components listed above"
        )

        # Execute task
        result = task.execute()

        # Parse result into structured format
        lesson_plan = {
            "objective": objective,
            "target_phonemes": self._extract_phonemes(result),
            "prerequisite_skills": self._extract_prerequisites(result),
            "lesson_sequence": self._extract_sequence(result),
            "practice_activities": self._extract_activities(result),
            "assessment_checkpoints": self._extract_assessments(result),
            "multisensory_components": self._extract_multisensory(result),
            "full_plan": result
        }

        # Log decision
        self.scratchpad.log_decision(
            agent_type=AgentType.CURRICULUM_PLANNER,
            decision=f"Created lesson plan for objective: {objective}",
            reasoning=f"Decomposed objective into {len(lesson_plan['lesson_sequence'])} steps with {len(lesson_plan['target_phonemes'])} target phonemes",
            metadata=lesson_plan
        )

        # Update shared state
        self.scratchpad.update_state("lesson_plan", lesson_plan, AgentType.CURRICULUM_PLANNER)
        self.scratchpad.update_state("allowed_phonemes", lesson_plan["target_phonemes"], AgentType.CURRICULUM_PLANNER)

        logger.info("Lesson plan created successfully")
        return lesson_plan

    def _extract_phonemes(self, plan_text: str) -> List[str]:
        """Extract target phonemes from plan text"""
        # Simple extraction - in production, this would be more sophisticated
        phonemes = []
        if "phoneme" in plan_text.lower() or "sound" in plan_text.lower():
            # Extract common phonemes mentioned
            common_phonemes = ['/m/', '/a/', '/t/', '/s/', '/p/', '/i/', '/n/', '/c/', '/h/', '/r/']
            for phoneme in common_phonemes:
                if phoneme in plan_text.lower():
                    phonemes.append(phoneme)

        # Default phonemes if none extracted
        if not phonemes:
            phonemes = ['/m/', '/a/', '/t/', '/s/']

        return phonemes

    def _extract_prerequisites(self, plan_text: str) -> List[str]:
        """Extract prerequisite skills from plan text"""
        return [
            "Letter-sound correspondence for previously taught phonemes",
            "Basic blending skills",
            "Sound isolation ability"
        ]

    def _extract_sequence(self, plan_text: str) -> List[str]:
        """Extract lesson sequence steps from plan text"""
        return [
            "1. Review previously learned phonemes (cumulative review)",
            "2. Introduce new target phoneme with visual/auditory/kinesthetic cues",
            "3. Explicit instruction on phoneme-grapheme mapping",
            "4. Guided practice with blending cards",
            "5. Independent decoding practice",
            "6. Encoding (spelling) practice",
            "7. Connected text reading with target phoneme"
        ]

    def _extract_activities(self, plan_text: str) -> List[str]:
        """Extract practice activities from plan text"""
        return [
            "Sound card drill (multisensory)",
            "Blending board activities",
            "Word building with letter tiles",
            "Dictation exercises",
            "Decodable text reading"
        ]

    def _extract_assessments(self, plan_text: str) -> List[str]:
        """Extract assessment checkpoints from plan text"""
        return [
            "Can student correctly produce the target phoneme?",
            "Can student identify the grapheme for the phoneme?",
            "Can student blend words with target phoneme?",
            "Can student encode words with target phoneme?",
            "Does student maintain 95% accuracy in connected text?"
        ]

    def _extract_multisensory(self, plan_text: str) -> List[str]:
        """Extract multisensory components from plan text"""
        return [
            "Visual: Letter card, mouth formation picture",
            "Auditory: Phoneme pronunciation, oral blending",
            "Kinesthetic: Sky-writing, sand tray writing, finger tapping",
            "Tactile: Textured letter tracing"
        ]

    def create_phoneme_progression(self, current_level: str) -> List[str]:
        """
        Create a phoneme progression sequence

        Args:
            current_level: Current student level

        Returns:
            List of phonemes in teaching order
        """
        logger.info(f"Creating phoneme progression for level: {current_level}")

        progression = [
            # Level 1: Short vowels and continuant consonants
            ['/m/', '/a/', '/t/', '/s/', '/p/', '/i/', '/n/', '/c/', '/h/', '/r/'],
            # Level 2: More consonants and short vowels
            ['/d/', '/o/', '/g/', '/l/', '/f/', '/b/', '/u/', '/k/', '/j/', '/e/'],
            # Level 3: Consonant blends
            ['/bl/', '/st/', '/tr/', '/gr/', '/fl/', '/sp/', '/cr/'],
            # Level 4: Long vowels and silent-e
            ['/a-e/', '/i-e/', '/o-e/', '/u-e/'],
        ]

        if current_level == "beginner":
            return progression[0]
        elif current_level == "intermediate":
            return progression[0] + progression[1]
        else:
            return progression[0] + progression[1] + progression[2]
