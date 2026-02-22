"""
Orthographic Rule Engine

Validates orthographic patterns including:
- 1-1-1 Doubling Rule (CVC + suffix)
- Y-to-I Changes
- Silent E Patterns
"""

import re
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OrthographicRuleEngine:
    """
    Validates and applies orthographic rules for English spelling patterns
    """

    def __init__(self):
        """Initialize orthographic rule engine"""
        logger.info("Orthographic Rule Engine initialized")

    def validate_111_rule(self, base_word: str, suffix: str, result_word: str) -> Dict[str, any]:
        """
        Validate 1-1-1 Doubling Rule

        Rule: When adding a vowel suffix to a CVC word (Consonant-Vowel-Consonant),
        double the final consonant.

        Examples:
        - hop + ing = hopping (not hoping)
        - run + ing = running (not runing)
        - stop + ed = stopped (not stoped)

        Args:
            base_word: Base word (e.g., "hop")
            suffix: Suffix being added (e.g., "ing")
            result_word: Resulting word (e.g., "hopping")

        Returns:
            Validation result with explanation
        """
        base_clean = base_word.lower().strip()
        suffix_clean = suffix.lower().strip()
        result_clean = result_word.lower().strip()

        # Check if suffix starts with a vowel
        vowel_suffix = suffix_clean[0] in 'aeiouy'

        # Check if base word is CVC pattern
        is_cvc = self._is_cvc_pattern(base_clean)

        # Determine if doubling should occur
        should_double = is_cvc and vowel_suffix

        # Check actual result
        if should_double:
            expected = base_clean + base_clean[-1] + suffix_clean
            correct = result_clean == expected
        else:
            expected = base_clean + suffix_clean
            correct = result_clean == expected

        return {
            'rule': '1-1-1 Doubling Rule',
            'base_word': base_word,
            'suffix': suffix,
            'result_word': result_word,
            'is_cvc': is_cvc,
            'vowel_suffix': vowel_suffix,
            'should_double': should_double,
            'expected': expected,
            'correct': correct,
            'explanation': self._explain_111_rule(base_clean, suffix_clean, is_cvc, vowel_suffix, should_double)
        }

    def _is_cvc_pattern(self, word: str) -> bool:
        """
        Check if word follows CVC (Consonant-Vowel-Consonant) pattern

        Args:
            word: Word to check

        Returns:
            True if word is CVC pattern
        """
        if len(word) != 3:
            return False

        consonants = 'bcdfghjklmnpqrstvwxyz'
        vowels = 'aeiou'

        return (
            word[0] in consonants and
            word[1] in vowels and
            word[2] in consonants
        )

    def _explain_111_rule(self, base: str, suffix: str, is_cvc: bool, vowel_suffix: bool, should_double: bool) -> str:
        """Generate explanation for 1-1-1 rule application"""
        if not is_cvc:
            return f"Base word '{base}' is not a CVC pattern, so no doubling needed."

        if not vowel_suffix:
            return f"Suffix '{suffix}' starts with a consonant, so no doubling needed."

        if should_double:
            return f"Base word '{base}' is CVC and suffix '{suffix}' starts with a vowel, so double the final consonant."

        return "No doubling needed."

    def validate_y_to_i_rule(self, base_word: str, suffix: str, result_word: str) -> Dict[str, any]:
        """
        Validate Y-to-I Change Rule

        Rule: When adding a suffix to a word ending in consonant + y,
        change y to i (unless suffix is -ing).

        Examples:
        - happy + ness = happiness (not happyness)
        - carry + ed = carried (not carryed)
        - play + ing = playing (vowel + y, no change)
        - carry + ing = carrying (exception: -ing suffix)

        Args:
            base_word: Base word (e.g., "happy")
            suffix: Suffix being added (e.g., "ness")
            result_word: Resulting word (e.g., "happiness")

        Returns:
            Validation result with explanation
        """
        base_clean = base_word.lower().strip()
        suffix_clean = suffix.lower().strip()
        result_clean = result_word.lower().strip()

        # Check if base word ends in y
        ends_in_y = base_clean.endswith('y')

        if not ends_in_y:
            return {
                'rule': 'Y-to-I Change Rule',
                'base_word': base_word,
                'suffix': suffix,
                'result_word': result_word,
                'ends_in_y': False,
                'correct': result_clean == base_clean + suffix_clean,
                'explanation': f"Base word '{base_word}' does not end in 'y', so no change needed."
            }

        # Check if y is preceded by a consonant
        consonant_before_y = len(base_clean) >= 2 and base_clean[-2] not in 'aeiou'

        # Exception: -ing suffix keeps the y
        is_ing_suffix = suffix_clean == 'ing'

        # Determine if y should change to i
        should_change = consonant_before_y and not is_ing_suffix

        # Calculate expected result
        if should_change:
            expected = base_clean[:-1] + 'i' + suffix_clean
        else:
            expected = base_clean + suffix_clean

        correct = result_clean == expected

        return {
            'rule': 'Y-to-I Change Rule',
            'base_word': base_word,
            'suffix': suffix,
            'result_word': result_word,
            'ends_in_y': True,
            'consonant_before_y': consonant_before_y,
            'is_ing_suffix': is_ing_suffix,
            'should_change': should_change,
            'expected': expected,
            'correct': correct,
            'explanation': self._explain_y_to_i_rule(base_clean, suffix_clean, consonant_before_y, is_ing_suffix, should_change)
        }

    def _explain_y_to_i_rule(self, base: str, suffix: str, consonant_before_y: bool, is_ing: bool, should_change: bool) -> str:
        """Generate explanation for Y-to-I rule application"""
        if not consonant_before_y:
            return f"Base word '{base}' has a vowel before 'y', so no change needed."

        if is_ing:
            return f"Suffix is '-ing', so keep the 'y' in '{base}'."

        if should_change:
            return f"Base word '{base}' ends in consonant + 'y', so change 'y' to 'i' before adding '{suffix}'."

        return "No change needed."

    def validate_silent_e_rule(self, base_word: str, suffix: str, result_word: str) -> Dict[str, any]:
        """
        Validate Silent E Rule

        Rule: When adding a vowel suffix to a word ending in silent e,
        drop the e. Keep the e when adding a consonant suffix.

        Examples:
        - make + ing = making (not makeing)
        - hope + ed = hoped (not hopeed)
        - make + less = makeless (keep e? - actually "make" doesn't take -less)
        - safe + ly = safely (keep e before consonant)

        Args:
            base_word: Base word (e.g., "make")
            suffix: Suffix being added (e.g., "ing")
            result_word: Resulting word (e.g., "making")

        Returns:
            Validation result with explanation
        """
        base_clean = base_word.lower().strip()
        suffix_clean = suffix.lower().strip()
        result_clean = result_word.lower().strip()

        # Check if base word ends in e
        ends_in_e = base_clean.endswith('e')

        if not ends_in_e:
            return {
                'rule': 'Silent E Rule',
                'base_word': base_word,
                'suffix': suffix,
                'result_word': result_word,
                'ends_in_e': False,
                'correct': result_clean == base_clean + suffix_clean,
                'explanation': f"Base word '{base_word}' does not end in 'e', so no change needed."
            }

        # Check if suffix starts with a vowel
        vowel_suffix = suffix_clean[0] in 'aeiouy'

        # Determine if e should be dropped
        should_drop_e = vowel_suffix

        # Calculate expected result
        if should_drop_e:
            expected = base_clean[:-1] + suffix_clean
        else:
            expected = base_clean + suffix_clean

        correct = result_clean == expected

        return {
            'rule': 'Silent E Rule',
            'base_word': base_word,
            'suffix': suffix,
            'result_word': result_word,
            'ends_in_e': True,
            'vowel_suffix': vowel_suffix,
            'should_drop_e': should_drop_e,
            'expected': expected,
            'correct': correct,
            'explanation': self._explain_silent_e_rule(base_clean, suffix_clean, vowel_suffix, should_drop_e)
        }

    def _explain_silent_e_rule(self, base: str, suffix: str, vowel_suffix: bool, should_drop: bool) -> str:
        """Generate explanation for Silent E rule application"""
        if vowel_suffix and should_drop:
            return f"Base word '{base}' ends in 'e' and suffix '{suffix}' starts with a vowel, so drop the 'e'."
        elif not vowel_suffix:
            return f"Suffix '{suffix}' starts with a consonant, so keep the 'e' in '{base}'."
        return "No change needed."

    def validate_word_formation(self, base_word: str, suffix: str, result_word: str) -> Dict[str, any]:
        """
        Validate word formation using all applicable rules

        Args:
            base_word: Base word
            suffix: Suffix being added
            result_word: Resulting word

        Returns:
            Comprehensive validation result
        """
        validations = []

        # Check 1-1-1 rule
        if self._is_cvc_pattern(base_word.lower()):
            validations.append(self.validate_111_rule(base_word, suffix, result_word))

        # Check Y-to-I rule
        if base_word.lower().endswith('y'):
            validations.append(self.validate_y_to_i_rule(base_word, suffix, result_word))

        # Check Silent E rule
        if base_word.lower().endswith('e'):
            validations.append(self.validate_silent_e_rule(base_word, suffix, result_word))

        # If no specific rules apply, just check simple concatenation
        if not validations:
            expected = base_word.lower() + suffix.lower()
            correct = result_word.lower() == expected
            validations.append({
                'rule': 'Simple Concatenation',
                'base_word': base_word,
                'suffix': suffix,
                'result_word': result_word,
                'expected': expected,
                'correct': correct,
                'explanation': 'No special orthographic rules apply; simple concatenation.'
            })

        # Determine overall correctness
        all_correct = all(v['correct'] for v in validations)

        return {
            'base_word': base_word,
            'suffix': suffix,
            'result_word': result_word,
            'correct': all_correct,
            'validations': validations,
            'rules_applied': len(validations)
        }
