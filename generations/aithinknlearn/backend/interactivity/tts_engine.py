"""
Text-to-Speech Engine for Phoneme Feedback

Provides high-quality TTS for individual phonemes and blended sounds
"""

from typing import Dict, List, Optional
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceType(Enum):
    """Available voice types for TTS"""
    CHILD_FRIENDLY = "child_friendly"
    CLEAR_PRONUNCIATION = "clear_pronunciation"
    SLOW_PACE = "slow_pace"
    NORMAL = "normal"


class TTSEngine:
    """Text-to-Speech engine for phoneme and word pronunciation"""

    def __init__(self):
        self.voice_type = VoiceType.CHILD_FRIENDLY
        self.speech_rate = 1.0  # Normal speed
        self.pitch = 1.0  # Normal pitch
        self.volume = 0.8  # 80% volume

        # Phoneme to IPA mapping for accurate pronunciation
        self.phoneme_ipa_map = {
            # Consonants
            'b': 'b', 'p': 'p', 't': 't', 'd': 'd', 'k': 'k', 'g': 'g',
            'f': 'f', 'v': 'v', 's': 's', 'z': 'z', 'th': 'θ', 'dh': 'ð',
            'sh': 'ʃ', 'zh': 'ʒ', 'ch': 'tʃ', 'j': 'dʒ',
            'm': 'm', 'n': 'n', 'ng': 'ŋ',
            'l': 'l', 'r': 'r',
            'w': 'w', 'y': 'j', 'h': 'h',

            # Short vowels
            'a': 'æ', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɑ', 'u': 'ʌ',

            # Long vowels
            'a_e': 'eɪ', 'e_e': 'i', 'i_e': 'aɪ', 'o_e': 'oʊ', 'u_e': 'ju',

            # Diphthongs
            'ai': 'aɪ', 'ay': 'eɪ', 'ee': 'i', 'ea': 'i', 'oa': 'oʊ',
            'oo': 'u', 'ou': 'aʊ', 'ow': 'aʊ', 'oi': 'ɔɪ', 'oy': 'ɔɪ'
        }

    def generate_phoneme_audio(self, phoneme: str) -> Dict[str, any]:
        """
        Generate audio data for a single phoneme

        Args:
            phoneme: The phoneme to pronounce

        Returns:
            Audio generation parameters for client-side synthesis
        """
        ipa = self.phoneme_ipa_map.get(phoneme.lower(), phoneme)

        audio_params = {
            'text': phoneme,
            'ipa': ipa,
            'voice_type': self.voice_type.value,
            'rate': self.speech_rate,
            'pitch': self.pitch,
            'volume': self.volume,
            'duration_ms': self._estimate_duration(phoneme),
            'emphasis': 'strong' if len(phoneme) == 1 else 'normal'
        }

        logger.info(f"Generated audio params for phoneme: {phoneme} ({ipa})")
        return audio_params

    def generate_blend_audio(self, phonemes: List[str], blend_speed: float = 1.0) -> Dict[str, any]:
        """
        Generate audio for blended phoneme sequence

        Args:
            phonemes: List of phonemes to blend
            blend_speed: Speed multiplier for blending (slower = clearer)

        Returns:
            Audio generation parameters for blended sound
        """
        blended_text = ''.join(phonemes)
        ipa_sequence = [self.phoneme_ipa_map.get(p.lower(), p) for p in phonemes]

        audio_params = {
            'text': blended_text,
            'phonemes': phonemes,
            'ipa_sequence': ipa_sequence,
            'voice_type': self.voice_type.value,
            'rate': self.speech_rate * blend_speed,
            'pitch': self.pitch,
            'volume': self.volume,
            'duration_ms': self._estimate_blend_duration(phonemes, blend_speed),
            'blend_mode': True,
            'pause_between_phonemes_ms': 50 if blend_speed < 1.0 else 0
        }

        logger.info(f"Generated blend audio for: {blended_text}")
        return audio_params

    def generate_word_audio(self, word: str, phoneme_breakdown: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Generate audio for complete word pronunciation

        Args:
            word: The word to pronounce
            phoneme_breakdown: Optional phoneme breakdown for accuracy

        Returns:
            Audio generation parameters for word
        """
        audio_params = {
            'text': word,
            'phoneme_breakdown': phoneme_breakdown,
            'voice_type': self.voice_type.value,
            'rate': self.speech_rate,
            'pitch': self.pitch,
            'volume': self.volume,
            'duration_ms': self._estimate_word_duration(word),
            'emphasis': 'normal'
        }

        logger.info(f"Generated word audio for: {word}")
        return audio_params

    def set_voice_parameters(self, voice_type: Optional[str] = None,
                            rate: Optional[float] = None,
                            pitch: Optional[float] = None,
                            volume: Optional[float] = None):
        """Update TTS voice parameters"""
        if voice_type:
            try:
                self.voice_type = VoiceType(voice_type)
            except ValueError:
                logger.warning(f"Invalid voice type: {voice_type}")

        if rate is not None:
            self.speech_rate = max(0.5, min(2.0, rate))

        if pitch is not None:
            self.pitch = max(0.5, min(2.0, pitch))

        if volume is not None:
            self.volume = max(0.0, min(1.0, volume))

        logger.info(f"Updated voice parameters: {self.voice_type.value}, rate={self.speech_rate}")

    def _estimate_duration(self, phoneme: str) -> int:
        """Estimate duration in milliseconds for phoneme"""
        base_duration = 300  # 300ms base
        if len(phoneme) > 1:  # Digraph
            base_duration = 450
        return int(base_duration / self.speech_rate)

    def _estimate_blend_duration(self, phonemes: List[str], blend_speed: float) -> int:
        """Estimate duration for blended phonemes"""
        total_duration = sum(self._estimate_duration(p) for p in phonemes)
        return int(total_duration / blend_speed)

    def _estimate_word_duration(self, word: str) -> int:
        """Estimate duration for word pronunciation"""
        # Rough estimate: 100ms per letter
        return int((len(word) * 100) / self.speech_rate)

    def get_supported_phonemes(self) -> List[str]:
        """Get list of supported phonemes"""
        return list(self.phoneme_ipa_map.keys())

    def get_voice_settings(self) -> Dict[str, any]:
        """Get current voice settings"""
        return {
            'voice_type': self.voice_type.value,
            'speech_rate': self.speech_rate,
            'pitch': self.pitch,
            'volume': self.volume,
            'supported_phonemes': len(self.phoneme_ipa_map)
        }
