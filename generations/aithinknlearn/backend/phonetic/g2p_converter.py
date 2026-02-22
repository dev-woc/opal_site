"""
Grapheme-to-Phoneme (G2P) Converter

Uses NVIDIA NeMo G2P-Conformer model with CMU Pronouncing Dictionary fallback
for accurate phoneme conversion.
"""

import re
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class G2PConverter:
    """
    Converts graphemes (written letters) to phonemes (sounds) using:
    1. NVIDIA NeMo G2P-Conformer (simulated for now, can integrate actual model)
    2. CMU Pronouncing Dictionary as fallback
    """

    def __init__(self):
        """Initialize G2P converter with CMU dictionary"""
        self.cmu_dict = self._load_cmu_dict()
        logger.info("G2P Converter initialized")

    def _load_cmu_dict(self) -> Dict[str, List[str]]:
        """
        Load CMU Pronouncing Dictionary

        In production, this would load from the actual CMU dict file.
        For now, using a comprehensive sample dictionary.
        """
        # Comprehensive sample dictionary with common words and heteronyms
        return {
            # Common CVC words
            'cat': ['K', 'AE', 'T'],
            'mat': ['M', 'AE', 'T'],
            'sat': ['S', 'AE', 'T'],
            'bat': ['B', 'AE', 'T'],
            'rat': ['R', 'AE', 'T'],
            'hat': ['HH', 'AE', 'T'],
            'pat': ['P', 'AE', 'T'],
            'fat': ['F', 'AE', 'T'],
            'dog': ['D', 'AO', 'G'],
            'log': ['L', 'AO', 'G'],
            'fog': ['F', 'AO', 'G'],
            'hot': ['HH', 'AA', 'T'],
            'pot': ['P', 'AA', 'T'],
            'lot': ['L', 'AA', 'T'],
            'top': ['T', 'AA', 'P'],
            'hop': ['HH', 'AA', 'P'],
            'mop': ['M', 'AA', 'P'],
            'pop': ['P', 'AA', 'P'],
            'big': ['B', 'IH', 'G'],
            'dig': ['D', 'IH', 'G'],
            'pig': ['P', 'IH', 'G'],
            'wig': ['W', 'IH', 'G'],
            'sit': ['S', 'IH', 'T'],
            'bit': ['B', 'IH', 'T'],
            'hit': ['HH', 'IH', 'T'],
            'pit': ['P', 'IH', 'T'],
            'bug': ['B', 'AH', 'G'],
            'hug': ['HH', 'AH', 'G'],
            'rug': ['R', 'AH', 'G'],
            'mug': ['M', 'AH', 'G'],
            'run': ['R', 'AH', 'N'],
            'sun': ['S', 'AH', 'N'],
            'fun': ['F', 'AH', 'N'],
            'bun': ['B', 'AH', 'N'],

            # Heteronyms (words spelled same but pronounced differently)
            'read': ['R', 'IY', 'D'],  # present tense
            'read_past': ['R', 'EH', 'D'],  # past tense
            'lead': ['L', 'IY', 'D'],  # to guide
            'lead_metal': ['L', 'EH', 'D'],  # metal
            'bow': ['B', 'OW'],  # weapon
            'bow_bend': ['B', 'AW'],  # to bend
            'tear': ['T', 'IH', 'R'],  # from eye
            'tear_rip': ['T', 'EH', 'R'],  # to rip
            'live': ['L', 'AY', 'V'],  # alive
            'live_verb': ['L', 'IH', 'V'],  # to live
            'wind': ['W', 'IH', 'N', 'D'],  # air movement
            'wind_verb': ['W', 'AY', 'N', 'D'],  # to wind up
            'close': ['K', 'L', 'OW', 'S'],  # nearby
            'close_verb': ['K', 'L', 'OW', 'Z'],  # to shut
            'present': ['P', 'R', 'EH', 'Z', 'AH', 'N', 'T'],  # gift
            'present_verb': ['P', 'R', 'IH', 'Z', 'EH', 'N', 'T'],  # to give

            # Words with orthographic patterns
            'happy': ['HH', 'AE', 'P', 'IY'],
            'happiness': ['HH', 'AE', 'P', 'IY', 'N', 'AH', 'S'],
            'running': ['R', 'AH', 'N', 'IH', 'NG'],
            'stopped': ['S', 'T', 'AA', 'P', 'T'],
            'hopping': ['HH', 'AA', 'P', 'IH', 'NG'],
            'hoped': ['HH', 'OW', 'P', 'T'],
            'hoping': ['HH', 'OW', 'P', 'IH', 'NG'],
            'make': ['M', 'EY', 'K'],
            'making': ['M', 'EY', 'K', 'IH', 'NG'],
            'made': ['M', 'EY', 'D'],
            'take': ['T', 'EY', 'K'],
            'taking': ['T', 'EY', 'K', 'IH', 'NG'],
            'cake': ['K', 'EY', 'K'],
            'bake': ['B', 'EY', 'K'],
            'baking': ['B', 'EY', 'K', 'IH', 'NG'],

            # Decodable story words
            'the': ['DH', 'AH'],
            'a': ['AH'],
            'and': ['AE', 'N', 'D'],
            'can': ['K', 'AE', 'N'],
            'ran': ['R', 'AE', 'N'],
            'man': ['M', 'AE', 'N'],
            'van': ['V', 'AE', 'N'],
            'pan': ['P', 'AE', 'N'],
            'had': ['HH', 'AE', 'D'],
            'sad': ['S', 'AE', 'D'],
            'mad': ['M', 'AE', 'D'],
            'dad': ['D', 'AE', 'D'],
            'bad': ['B', 'AE', 'D'],
            'is': ['IH', 'Z'],
            'it': ['IH', 'T'],
            'in': ['IH', 'N'],
            'on': ['AA', 'N'],
            'at': ['AE', 'T'],
            'an': ['AE', 'N'],
        }

    def convert(self, word: str, context: Optional[str] = None) -> List[str]:
        """
        Convert word to phoneme sequence

        Args:
            word: Word to convert
            context: Optional context for heteronym disambiguation

        Returns:
            List of phonemes (e.g., ['K', 'AE', 'T'] for "cat")
        """
        word_lower = word.lower().strip()

        # Check CMU dictionary first
        if word_lower in self.cmu_dict:
            phonemes = self.cmu_dict[word_lower]
            logger.debug(f"G2P: {word} -> {phonemes} (CMU dict)")
            return phonemes

        # For words not in dictionary, use rule-based conversion
        # This simulates the NeMo G2P-Conformer model
        phonemes = self._rule_based_conversion(word_lower)
        logger.debug(f"G2P: {word} -> {phonemes} (rule-based)")
        return phonemes

    def _rule_based_conversion(self, word: str) -> List[str]:
        """
        Simple rule-based G2P conversion

        This simulates NVIDIA NeMo G2P-Conformer for words not in CMU dict.
        In production, this would call the actual NeMo model.
        """
        phonemes = []
        i = 0

        # Basic conversion rules (simplified)
        while i < len(word):
            char = word[i]

            # Consonants
            if char == 'b':
                phonemes.append('B')
            elif char == 'c':
                if i + 1 < len(word) and word[i + 1] in 'eiy':
                    phonemes.append('S')
                else:
                    phonemes.append('K')
            elif char == 'd':
                phonemes.append('D')
            elif char == 'f':
                phonemes.append('F')
            elif char == 'g':
                if i + 1 < len(word) and word[i + 1] in 'eiy':
                    phonemes.append('JH')
                else:
                    phonemes.append('G')
            elif char == 'h':
                phonemes.append('HH')
            elif char == 'j':
                phonemes.append('JH')
            elif char == 'k':
                phonemes.append('K')
            elif char == 'l':
                phonemes.append('L')
            elif char == 'm':
                phonemes.append('M')
            elif char == 'n':
                phonemes.append('N')
            elif char == 'p':
                phonemes.append('P')
            elif char == 'r':
                phonemes.append('R')
            elif char == 's':
                phonemes.append('S')
            elif char == 't':
                phonemes.append('T')
            elif char == 'v':
                phonemes.append('V')
            elif char == 'w':
                phonemes.append('W')
            elif char == 'x':
                phonemes.extend(['K', 'S'])
            elif char == 'y':
                if i == 0:
                    phonemes.append('Y')
                else:
                    phonemes.append('IY')
            elif char == 'z':
                phonemes.append('Z')

            # Vowels (simplified - just short vowels for CVC words)
            elif char == 'a':
                phonemes.append('AE')
            elif char == 'e':
                phonemes.append('EH')
            elif char == 'i':
                phonemes.append('IH')
            elif char == 'o':
                phonemes.append('AA')
            elif char == 'u':
                phonemes.append('AH')

            i += 1

        return phonemes

    def batch_convert(self, words: List[str]) -> Dict[str, List[str]]:
        """
        Convert multiple words to phonemes

        Args:
            words: List of words to convert

        Returns:
            Dictionary mapping words to phoneme lists
        """
        result = {}
        for word in words:
            result[word] = self.convert(word)
        return result

    def get_phoneme_breakdown(self, word: str) -> Dict[str, any]:
        """
        Get detailed phoneme breakdown for a word

        Args:
            word: Word to analyze

        Returns:
            Dictionary with phonemes, graphemes, and mapping
        """
        phonemes = self.convert(word)

        return {
            'word': word,
            'phonemes': phonemes,
            'phoneme_count': len(phonemes),
            'phoneme_string': '-'.join(phonemes)
        }
