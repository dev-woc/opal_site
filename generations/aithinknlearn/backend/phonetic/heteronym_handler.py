"""
Heteronym Handler

Handles context-aware disambiguation of heteronyms (words spelled the same
but pronounced differently, like "read" present vs past tense).
"""

import re
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class HeteronymHandler:
    """
    Disambiguates heteronyms using context clues
    """

    def __init__(self):
        """Initialize heteronym handler with known heteronyms"""
        self.heteronyms = self._load_heteronyms()
        logger.info("Heteronym Handler initialized")

    def _load_heteronyms(self) -> Dict[str, Dict[str, any]]:
        """
        Load known heteronyms with context rules

        Returns:
            Dictionary of heteronyms with pronunciation variants
        """
        return {
            'read': {
                'variants': {
                    'present': {
                        'phonemes': ['R', 'IY', 'D'],
                        'context_clues': ['will', 'can', 'to', 'should', 'must', 'read'],
                        'tense': 'present'
                    },
                    'past': {
                        'phonemes': ['R', 'EH', 'D'],
                        'context_clues': ['had', 'has', 'was', 'were', 'yesterday', 'already'],
                        'tense': 'past'
                    }
                },
                'default': 'present'
            },
            'lead': {
                'variants': {
                    'verb': {
                        'phonemes': ['L', 'IY', 'D'],
                        'context_clues': ['will', 'to', 'can', 'the way', 'leader'],
                        'meaning': 'to guide'
                    },
                    'noun': {
                        'phonemes': ['L', 'EH', 'D'],
                        'context_clues': ['metal', 'heavy', 'pencil', 'pipe'],
                        'meaning': 'metal element'
                    }
                },
                'default': 'verb'
            },
            'bow': {
                'variants': {
                    'weapon': {
                        'phonemes': ['B', 'OW'],
                        'context_clues': ['arrow', 'archery', 'weapon', 'shoot'],
                        'meaning': 'weapon'
                    },
                    'verb': {
                        'phonemes': ['B', 'AW'],
                        'context_clues': ['down', 'head', 'respect', 'bend'],
                        'meaning': 'to bend'
                    }
                },
                'default': 'weapon'
            },
            'tear': {
                'variants': {
                    'noun': {
                        'phonemes': ['T', 'IH', 'R'],
                        'context_clues': ['cry', 'eye', 'sad', 'drop'],
                        'meaning': 'from eye'
                    },
                    'verb': {
                        'phonemes': ['T', 'EH', 'R'],
                        'context_clues': ['rip', 'apart', 'paper', 'cloth'],
                        'meaning': 'to rip'
                    }
                },
                'default': 'noun'
            },
            'live': {
                'variants': {
                    'adjective': {
                        'phonemes': ['L', 'AY', 'V'],
                        'context_clues': ['broadcast', 'performance', 'ammunition', 'wire'],
                        'meaning': 'alive/in person'
                    },
                    'verb': {
                        'phonemes': ['L', 'IH', 'V'],
                        'context_clues': ['in', 'at', 'here', 'there', 'where'],
                        'meaning': 'to reside'
                    }
                },
                'default': 'verb'
            },
            'wind': {
                'variants': {
                    'noun': {
                        'phonemes': ['W', 'IH', 'N', 'D'],
                        'context_clues': ['blow', 'breeze', 'gust', 'air'],
                        'meaning': 'air movement'
                    },
                    'verb': {
                        'phonemes': ['W', 'AY', 'N', 'D'],
                        'context_clues': ['up', 'clock', 'toy', 'coil'],
                        'meaning': 'to coil'
                    }
                },
                'default': 'noun'
            },
            'close': {
                'variants': {
                    'adjective': {
                        'phonemes': ['K', 'L', 'OW', 'S'],
                        'context_clues': ['near', 'by', 'friend', 'relationship'],
                        'meaning': 'nearby'
                    },
                    'verb': {
                        'phonemes': ['K', 'L', 'OW', 'Z'],
                        'context_clues': ['door', 'window', 'shut', 'the'],
                        'meaning': 'to shut'
                    }
                },
                'default': 'verb'
            },
            'present': {
                'variants': {
                    'noun': {
                        'phonemes': ['P', 'R', 'EH', 'Z', 'AH', 'N', 'T'],
                        'context_clues': ['gift', 'birthday', 'give', 'receive'],
                        'meaning': 'gift'
                    },
                    'verb': {
                        'phonemes': ['P', 'R', 'IH', 'Z', 'EH', 'N', 'T'],
                        'context_clues': ['to', 'will', 'awards', 'show'],
                        'meaning': 'to give formally'
                    }
                },
                'default': 'noun'
            }
        }

    def disambiguate(self, word: str, context: Optional[str] = None) -> Tuple[List[str], str]:
        """
        Disambiguate heteronym based on context

        Args:
            word: The heteronym word
            context: Surrounding text for context clues

        Returns:
            Tuple of (phonemes, variant_name)
        """
        word_lower = word.lower().strip()

        # Check if word is a known heteronym
        if word_lower not in self.heteronyms:
            logger.debug(f"Word '{word}' is not a known heteronym")
            return None, None

        heteronym_data = self.heteronyms[word_lower]
        variants = heteronym_data['variants']
        default = heteronym_data['default']

        # If no context provided, use default
        if not context:
            logger.debug(f"No context for '{word}', using default: {default}")
            return variants[default]['phonemes'], default

        # Analyze context for clues
        context_lower = context.lower()
        best_match = default
        max_score = 0

        for variant_name, variant_data in variants.items():
            score = 0
            for clue in variant_data['context_clues']:
                if clue in context_lower:
                    score += 1

            if score > max_score:
                max_score = score
                best_match = variant_name

        phonemes = variants[best_match]['phonemes']
        logger.debug(f"Disambiguated '{word}' as '{best_match}' based on context")

        return phonemes, best_match

    def get_all_variants(self, word: str) -> Dict[str, List[str]]:
        """
        Get all pronunciation variants for a heteronym

        Args:
            word: The heteronym word

        Returns:
            Dictionary mapping variant names to phoneme lists
        """
        word_lower = word.lower().strip()

        if word_lower not in self.heteronyms:
            return {}

        variants = self.heteronyms[word_lower]['variants']
        result = {}

        for variant_name, variant_data in variants.items():
            result[variant_name] = variant_data['phonemes']

        return result

    def is_heteronym(self, word: str) -> bool:
        """
        Check if word is a known heteronym

        Args:
            word: Word to check

        Returns:
            True if word is a heteronym
        """
        return word.lower().strip() in self.heteronyms

    def analyze_heteronym(self, word: str, context: Optional[str] = None) -> Dict[str, any]:
        """
        Get detailed analysis of heteronym

        Args:
            word: The heteronym word
            context: Optional context for disambiguation

        Returns:
            Dictionary with heteronym analysis
        """
        word_lower = word.lower().strip()

        if not self.is_heteronym(word):
            return {
                'word': word,
                'is_heteronym': False
            }

        heteronym_data = self.heteronyms[word_lower]
        phonemes, selected_variant = self.disambiguate(word, context)

        variants_info = {}
        for variant_name, variant_data in heteronym_data['variants'].items():
            variants_info[variant_name] = {
                'phonemes': variant_data['phonemes'],
                'phoneme_string': '-'.join(variant_data['phonemes']),
                'meaning': variant_data.get('meaning', variant_data.get('tense', '')),
                'context_clues': variant_data['context_clues'],
                'selected': variant_name == selected_variant
            }

        return {
            'word': word,
            'is_heteronym': True,
            'selected_variant': selected_variant,
            'selected_phonemes': phonemes,
            'selected_phoneme_string': '-'.join(phonemes),
            'all_variants': variants_info,
            'context_used': context if context else None
        }
