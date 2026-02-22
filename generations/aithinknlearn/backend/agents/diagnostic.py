"""
Diagnostic Specialist Agent

This agent analyzes student errors to identify patterns and suggest
prescriptive teaching focuses following Structured Literacy principles.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class DiagnosticSpecialistAgent:
    """
    Diagnostic Specialist Agent

    Responsibilities:
    - Analyze student error patterns
    - Identify skill gaps and misconceptions
    - Suggest prescriptive teaching interventions
    - Determine appropriate instructional focus
    """

    def __init__(self, scratchpad, llm: Optional[ChatOpenAI] = None):
        """
        Initialize the Diagnostic Specialist Agent

        Args:
            scratchpad: Shared scratchpad for state management
            llm: Language model for agent reasoning (optional)
        """
        self.scratchpad = scratchpad
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

        # Create the CrewAI agent
        self.agent = Agent(
            role="Diagnostic Specialist",
            goal="Analyze student reading errors to identify precise skill gaps and recommend targeted, evidence-based interventions",
            backstory="""You are an expert in diagnostic assessment for reading difficulties,
            with deep knowledge of the Science of Reading and Structured Literacy. You understand
            common error patterns in decoding, encoding, and fluency. You can distinguish between
            errors caused by phonological awareness gaps, phonics knowledge gaps, orthographic
            processing issues, or fluency challenges. You provide specific, actionable
            recommendations that are tier-appropriate and aligned with the student's zone of
            proximal development. You never make assumptions - you analyze error patterns
            systematically and provide evidence-based diagnoses.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        logger.info("DiagnosticSpecialistAgent initialized")

    def analyze_errors(self, student_errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze student error patterns and suggest teaching focuses

        Args:
            student_errors: List of student errors with context
                Each error: {"target_word": str, "student_response": str, "context": str}

        Returns:
            Dictionary containing analysis and recommendations
        """
        logger.info(f"Analyzing {len(student_errors)} student errors")

        # Log to scratchpad
        from backend.scratchpad import AgentType
        self.scratchpad.add_entry(
            agent_type=AgentType.DIAGNOSTIC_SPECIALIST,
            content=f"Received {len(student_errors)} errors for analysis",
            entry_type="observation",
            metadata={"error_count": len(student_errors)}
        )

        # Format errors for analysis
        error_summary = self._format_errors(student_errors)

        # Create task for error analysis
        task = Task(
            description=f"""Analyze the following student reading errors to identify patterns and recommend interventions:

{error_summary}

Provide a comprehensive diagnostic analysis that includes:

1. ERROR PATTERN IDENTIFICATION:
   - What specific skills are breaking down?
   - Are errors related to phonological awareness, phonics, fluency, or comprehension?
   - What is the pattern across errors?

2. ROOT CAUSE ANALYSIS:
   - What prerequisite skills might be missing?
   - Are there specific phonemes, graphemes, or rules the student doesn't know?
   - Is this a knowledge gap or a processing/fluency issue?

3. PRESCRIPTIVE RECOMMENDATIONS:
   - What specific skills should be taught/reviewed first?
   - What instructional sequence would address the gaps?
   - What multisensory activities would support learning?
   - What decodable texts at what level should be used?

4. MONITORING PLAN:
   - What checkpoints would indicate progress?
   - How should we assess mastery?

Be specific and evidence-based. Reference Structured Literacy principles.""",
            agent=self.agent,
            expected_output="A detailed diagnostic analysis with specific, actionable recommendations"
        )

        # Execute task
        analysis_text = task.execute()

        # Parse analysis into structured format
        analysis = {
            "error_count": len(student_errors),
            "errors_analyzed": student_errors,
            "error_patterns": self._extract_patterns(analysis_text, student_errors),
            "root_causes": self._extract_root_causes(analysis_text),
            "skill_gaps": self._identify_skill_gaps(student_errors),
            "teaching_focuses": self._extract_teaching_focuses(analysis_text),
            "prescriptive_interventions": self._extract_interventions(analysis_text),
            "monitoring_plan": self._extract_monitoring(analysis_text),
            "full_analysis": analysis_text
        }

        # Log decision
        self.scratchpad.log_decision(
            agent_type=AgentType.DIAGNOSTIC_SPECIALIST,
            decision=f"Completed error analysis for {len(student_errors)} errors",
            reasoning=f"Identified {len(analysis['error_patterns'])} error patterns and {len(analysis['teaching_focuses'])} teaching focuses",
            metadata=analysis
        )

        # Update shared state
        self.scratchpad.update_state("student_errors", student_errors, AgentType.DIAGNOSTIC_SPECIALIST)
        self.scratchpad.update_state("teaching_focuses", analysis["teaching_focuses"], AgentType.DIAGNOSTIC_SPECIALIST)

        logger.info(f"Error analysis complete: {len(analysis['error_patterns'])} patterns identified")
        return analysis

    def _format_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Format errors for LLM analysis"""
        formatted = []
        for i, error in enumerate(errors, 1):
            target = error.get("target_word", "")
            response = error.get("student_response", "")
            context = error.get("context", "")

            formatted.append(f"Error {i}:")
            formatted.append(f"  Target word: '{target}'")
            formatted.append(f"  Student read: '{response}'")
            if context:
                formatted.append(f"  Context: {context}")
            formatted.append("")

        return "\n".join(formatted)

    def _extract_patterns(self, analysis_text: str, errors: List[Dict[str, Any]]) -> List[str]:
        """Extract error patterns from analysis"""
        # Analyze actual errors for common patterns
        patterns = []

        # Check for phoneme substitutions
        phoneme_errors = []
        for error in errors:
            target = error.get("target_word", "").lower()
            response = error.get("student_response", "").lower()

            if target and response:
                if target[0] != response[0]:
                    phoneme_errors.append(f"Initial phoneme confusion: {target[0]} -> {response[0]}")
                if len(target) > 2 and len(response) > 2 and target[-1] != response[-1]:
                    phoneme_errors.append(f"Final phoneme confusion: {target[-1]} -> {response[-1]}")

        if phoneme_errors:
            patterns.append("Phoneme substitution errors")

        # Add patterns from analysis text
        if "blend" in analysis_text.lower():
            patterns.append("Difficulty with consonant blends")
        if "vowel" in analysis_text.lower():
            patterns.append("Vowel confusion")
        if "reversal" in analysis_text.lower():
            patterns.append("Letter/sound reversals")

        return patterns or ["General decoding difficulty"]

    def _extract_root_causes(self, analysis_text: str) -> List[str]:
        """Extract root causes from analysis"""
        causes = []

        if "phonological awareness" in analysis_text.lower():
            causes.append("Weak phonological awareness foundation")
        if "phoneme" in analysis_text.lower() and "knowledge" in analysis_text.lower():
            causes.append("Incomplete phoneme-grapheme knowledge")
        if "blend" in analysis_text.lower():
            causes.append("Difficulty with blending skills")
        if "fluency" in analysis_text.lower():
            causes.append("Lack of automaticity with basic skills")

        return causes or ["Needs systematic phonics instruction"]

    def _identify_skill_gaps(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Identify specific skill gaps from errors"""
        gaps = set()

        for error in errors:
            target = error.get("target_word", "").lower()
            response = error.get("student_response", "").lower()

            if len(target) != len(response):
                gaps.add("Phoneme segmentation")

            if target and response and target[0] != response[0]:
                gaps.add(f"Letter-sound correspondence: {target[0]}")

        return list(gaps) or ["Basic phoneme-grapheme mapping"]

    def _extract_teaching_focuses(self, analysis_text: str) -> List[str]:
        """Extract teaching focuses from analysis"""
        focuses = []

        # Common teaching focuses based on analysis keywords
        focus_mapping = {
            "phonological awareness": "Explicit phonological awareness activities (phoneme segmentation, blending)",
            "sound": "Letter-sound correspondence review with multisensory practice",
            "blend": "Systematic blending instruction with visual supports",
            "vowel": "Short vowel discrimination and practice",
            "consonant": "Consonant sound mastery with sky-writing and sound cards",
            "fluency": "Repeated reading with decodable texts for automaticity"
        }

        analysis_lower = analysis_text.lower()
        for keyword, focus in focus_mapping.items():
            if keyword in analysis_lower:
                focuses.append(focus)

        # Always include at least one focus
        if not focuses:
            focuses.append("Review previously taught phonemes with cumulative practice")

        return focuses[:5]  # Top 5 focuses

    def _extract_interventions(self, analysis_text: str) -> List[Dict[str, str]]:
        """Extract prescriptive interventions from analysis"""
        interventions = [
            {
                "intervention": "Sound Card Drill",
                "description": "Daily review of phoneme-grapheme correspondences using multisensory techniques",
                "frequency": "Daily, 5-10 minutes",
                "materials": "Sound cards, mirror for articulation"
            },
            {
                "intervention": "Blending Board Practice",
                "description": "Explicit blending instruction moving from sound-by-sound to whole word",
                "frequency": "3-4 times per week, 10-15 minutes",
                "materials": "Blending board, word cards, letter tiles"
            },
            {
                "intervention": "Decodable Text Reading",
                "description": "Controlled text reading at 95% decodability with error correction",
                "frequency": "Daily, 10-15 minutes",
                "materials": "Decodable readers matched to student's phoneme knowledge"
            }
        ]

        return interventions

    def _extract_monitoring(self, analysis_text: str) -> Dict[str, Any]:
        """Extract monitoring plan from analysis"""
        return {
            "checkpoints": [
                "Daily sound card accuracy (target: 90%+ in 1 minute)",
                "Weekly nonsense word reading fluency check",
                "Bi-weekly decodable text accuracy and fluency probe"
            ],
            "mastery_criteria": {
                "phoneme_knowledge": "90% accuracy on isolated phoneme assessment",
                "blending": "Accurately blend 4-5 phoneme words with 85% accuracy",
                "text_reading": "95% accuracy on grade-level decodable text"
            },
            "progress_indicators": [
                "Increased accuracy on sound card drills",
                "Faster blending speed",
                "Reduced error rate in connected text",
                "Self-correction of errors"
            ]
        }

    def generate_error_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a teacher-friendly error analysis report

        Args:
            analysis: Analysis results from analyze_errors

        Returns:
            Formatted report string
        """
        logger.info("Generating error analysis report")

        report_lines = [
            "=" * 60,
            "STUDENT ERROR ANALYSIS REPORT",
            "=" * 60,
            "",
            f"Errors Analyzed: {analysis['error_count']}",
            "",
            "ERROR PATTERNS IDENTIFIED:",
        ]

        for pattern in analysis['error_patterns']:
            report_lines.append(f"  - {pattern}")

        report_lines.extend([
            "",
            "ROOT CAUSES:",
        ])

        for cause in analysis['root_causes']:
            report_lines.append(f"  - {cause}")

        report_lines.extend([
            "",
            "RECOMMENDED TEACHING FOCUSES:",
        ])

        for i, focus in enumerate(analysis['teaching_focuses'], 1):
            report_lines.append(f"  {i}. {focus}")

        report_lines.extend([
            "",
            "PRESCRIPTIVE INTERVENTIONS:",
        ])

        for intervention in analysis['prescriptive_interventions']:
            report_lines.extend([
                f"  - {intervention['intervention']}",
                f"    {intervention['description']}",
                f"    Frequency: {intervention['frequency']}",
                ""
            ])

        report_lines.extend([
            "MONITORING PLAN:",
            "Checkpoints:",
        ])

        for checkpoint in analysis['monitoring_plan']['checkpoints']:
            report_lines.append(f"  - {checkpoint}")

        report_lines.extend([
            "",
            "=" * 60,
        ])

        report = "\n".join(report_lines)

        from backend.scratchpad import AgentType
        self.scratchpad.add_entry(
            agent_type=AgentType.DIAGNOSTIC_SPECIALIST,
            content="Generated teacher error analysis report",
            entry_type="result",
            metadata={"report_length": len(report)}
        )

        return report
