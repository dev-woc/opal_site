"""
Decodability Checker

Validates that text maintains 95% decodability rate to ensure
students can decode content phonetically without guessing.
"""

import re
from typing import List, Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)


class DecodabilityChecker:
    """
    Checks text decodability against allowed phonemes and sight words
    """

    def __init__(self):
        """Initialize decodability checker"""
        self.decodability_threshold = 0.95  # 95% minimum
        logger.info("Decodability Checker initialized (threshold: 95%)")

    def calculate_decodability(
        self,
        text: str,
        allowed_phonemes: List[str],
        allowed_sight_words: Optional[List[str]] = None,
        g2p_converter=None
    ) -> Dict[str, any]:
        """
        Calculate decodability rate for text

        Args:
            text: Text to check
            allowed_phonemes: List of phonemes students have learned
            allowed_sight_words: Optional list of sight words students know
            g2p_converter: G2P converter instance for phoneme checking

        Returns:
            Decodability analysis with rate and details
        """
        if allowed_sight_words is None:
            allowed_sight_words = []

        # Normalize allowed phonemes to uppercase
        allowed_phonemes_set = set(p.upper() for p in allowed_phonemes)
        allowed_sight_words_set = set(w.lower() for w in allowed_sight_words)

        # Extract words from text
        words = self._extract_words(text)
        total_words = len(words)

        if total_words == 0:
            return {
                'decodability_rate': 1.0,
                'decodable_count': 0,
                'total_words': 0,
                'passes_threshold': True,
                'threshold': self.decodability_threshold,
                'words_analysis': []
            }

        # Analyze each word
        decodable_count = 0
        words_analysis = []

        for word in words:
            word_lower = word.lower()
            is_decodable = False
            reason = ""

            # Check if it's an allowed sight word
            if word_lower in allowed_sight_words_set:
                is_decodable = True
                reason = "sight word"
            # Check if word is decodable with allowed phonemes
            elif g2p_converter:
                phonemes = g2p_converter.convert(word)
                all_allowed = all(p in allowed_phonemes_set for p in phonemes)

                if all_allowed:
                    is_decodable = True
                    reason = "all phonemes allowed"
                else:
                    disallowed = [p for p in phonemes if p not in allowed_phonemes_set]
                    reason = f"contains disallowed phonemes: {', '.join(disallowed)}"
            else:
                # Without G2P converter, we can't verify
                reason = "no G2P converter provided"

            if is_decodable:
                decodable_count += 1

            words_analysis.append({
                'word': word,
                'is_decodable': is_decodable,
                'reason': reason
            })

        # Calculate decodability rate
        decodability_rate = decodable_count / total_words if total_words > 0 else 0
        passes_threshold = decodability_rate >= self.decodability_threshold

        return {
            'decodability_rate': round(decodability_rate, 4),
            'decodability_percentage': round(decodability_rate * 100, 2),
            'decodable_count': decodable_count,
            'total_words': total_words,
            'non_decodable_count': total_words - decodable_count,
            'passes_threshold': passes_threshold,
            'threshold': self.decodability_threshold,
            'threshold_percentage': self.decodability_threshold * 100,
            'words_analysis': words_analysis
        }

    def _extract_words(self, text: str) -> List[str]:
        """
        Extract words from text, removing punctuation

        Args:
            text: Input text

        Returns:
            List of words
        """
        # Remove punctuation and split on whitespace
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        words = cleaned.split()

        # Filter out empty strings and numbers
        words = [w for w in words if w and not w.isdigit()]

        return words

    def validate_content(
        self,
        text: str,
        allowed_phonemes: List[str],
        allowed_sight_words: Optional[List[str]] = None,
        g2p_converter=None
    ) -> Dict[str, any]:
        """
        Validate content meets decodability requirements

        Args:
            text: Text to validate
            allowed_phonemes: List of allowed phonemes
            allowed_sight_words: Optional sight words
            g2p_converter: G2P converter instance

        Returns:
            Validation result with pass/fail status
        """
        analysis = self.calculate_decodability(
            text=text,
            allowed_phonemes=allowed_phonemes,
            allowed_sight_words=allowed_sight_words,
            g2p_converter=g2p_converter
        )

        # Generate validation message
        if analysis['passes_threshold']:
            status = "PASS"
            message = f"Content meets {analysis['threshold_percentage']}% decodability requirement."
        else:
            status = "FAIL"
            message = (
                f"Content does not meet {analysis['threshold_percentage']}% decodability requirement. "
                f"Current rate: {analysis['decodability_percentage']}%"
            )

        # Identify non-decodable words
        non_decodable_words = [
            w['word'] for w in analysis['words_analysis']
            if not w['is_decodable']
        ]

        return {
            'status': status,
            'passes': analysis['passes_threshold'],
            'message': message,
            'decodability_rate': analysis['decodability_rate'],
            'decodability_percentage': analysis['decodability_percentage'],
            'decodable_count': analysis['decodable_count'],
            'total_words': analysis['total_words'],
            'non_decodable_count': analysis['non_decodable_count'],
            'non_decodable_words': non_decodable_words,
            'detailed_analysis': analysis
        }

    def get_non_decodable_words(
        self,
        text: str,
        allowed_phonemes: List[str],
        allowed_sight_words: Optional[List[str]] = None,
        g2p_converter=None
    ) -> List[Dict[str, any]]:
        """
        Get list of non-decodable words with reasons

        Args:
            text: Text to analyze
            allowed_phonemes: Allowed phonemes
            allowed_sight_words: Optional sight words
            g2p_converter: G2P converter instance

        Returns:
            List of non-decodable words with details
        """
        analysis = self.calculate_decodability(
            text=text,
            allowed_phonemes=allowed_phonemes,
            allowed_sight_words=allowed_sight_words,
            g2p_converter=g2p_converter
        )

        non_decodable = [
            w for w in analysis['words_analysis']
            if not w['is_decodable']
        ]

        return non_decodable

    def suggest_replacements(
        self,
        word: str,
        allowed_phonemes: List[str],
        word_list: Optional[List[str]] = None,
        g2p_converter=None
    ) -> List[str]:
        """
        Suggest decodable replacements for a non-decodable word

        Args:
            word: Word to replace
            allowed_phonemes: Allowed phonemes
            word_list: Optional list of candidate words
            g2p_converter: G2P converter instance

        Returns:
            List of suggested replacement words
        """
        if not word_list or not g2p_converter:
            return []

        allowed_phonemes_set = set(p.upper() for p in allowed_phonemes)
        suggestions = []

        for candidate in word_list:
            # Skip if same word
            if candidate.lower() == word.lower():
                continue

            # Check if candidate is decodable
            phonemes = g2p_converter.convert(candidate)
            if all(p in allowed_phonemes_set for p in phonemes):
                suggestions.append(candidate)

        return suggestions[:5]  # Return top 5 suggestions
