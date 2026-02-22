"""
Haptics Handler for Mobile Device Feedback

Provides vibration patterns to replicate multisensory sound segmenting
"""

from typing import List, Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HapticPattern(Enum):
    """Predefined haptic feedback patterns"""
    LIGHT_TAP = "light_tap"
    MEDIUM_TAP = "medium_tap"
    HEAVY_TAP = "heavy_tap"
    DOUBLE_TAP = "double_tap"
    SUCCESS = "success"
    ERROR = "error"
    PHONEME_SEGMENT = "phoneme_segment"
    BLEND_COMPLETE = "blend_complete"


class HapticsHandler:
    """Handler for mobile haptic feedback"""

    def __init__(self):
        self.enabled = True
        self.intensity = 0.7  # 70% intensity
        self.pattern_library = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, List[int]]:
        """Initialize haptic vibration patterns (duration in ms)"""
        return {
            HapticPattern.LIGHT_TAP.value: [10],
            HapticPattern.MEDIUM_TAP.value: [30],
            HapticPattern.HEAVY_TAP.value: [50],
            HapticPattern.DOUBLE_TAP.value: [20, 50, 20],
            HapticPattern.SUCCESS.value: [30, 50, 100],
            HapticPattern.ERROR.value: [100, 50, 100, 50, 100],
            HapticPattern.PHONEME_SEGMENT.value: [15, 30, 15],
            HapticPattern.BLEND_COMPLETE.value: [50, 100, 150]
        }

    def generate_haptic_feedback(self, pattern: str, custom_intensity: Optional[float] = None) -> Dict[str, any]:
        """
        Generate haptic feedback configuration

        Args:
            pattern: Haptic pattern name
            custom_intensity: Optional custom intensity (0.0-1.0)

        Returns:
            Haptic feedback configuration for client
        """
        intensity = custom_intensity if custom_intensity is not None else self.intensity
        intensity = max(0.0, min(1.0, intensity))

        vibration_pattern = self.pattern_library.get(pattern, self.pattern_library[HapticPattern.LIGHT_TAP.value])

        haptic_config = {
            'enabled': self.enabled,
            'pattern': pattern,
            'vibration_sequence': vibration_pattern,
            'intensity': intensity,
            'total_duration_ms': sum(vibration_pattern),
            'api_type': 'vibration'  # Use Vibration API for web
        }

        logger.info(f"Generated haptic feedback: {pattern} (intensity: {intensity})")
        return haptic_config

    def generate_phoneme_tap(self, phoneme: str, is_vowel: bool = False) -> Dict[str, any]:
        """
        Generate haptic feedback for phoneme tap

        Args:
            phoneme: The phoneme being tapped
            is_vowel: Whether the phoneme is a vowel

        Returns:
            Haptic configuration
        """
        # Vowels get longer vibration, consonants get shorter
        pattern = HapticPattern.MEDIUM_TAP if is_vowel else HapticPattern.LIGHT_TAP

        haptic_config = self.generate_haptic_feedback(pattern.value)
        haptic_config['phoneme'] = phoneme
        haptic_config['phoneme_type'] = 'vowel' if is_vowel else 'consonant'

        return haptic_config

    def generate_blend_feedback(self, num_phonemes: int) -> Dict[str, any]:
        """
        Generate haptic feedback for blending sequence

        Args:
            num_phonemes: Number of phonemes being blended

        Returns:
            Haptic configuration for blend
        """
        # Create progressive vibration for each phoneme
        vibration_sequence = []
        base_duration = 15

        for i in range(num_phonemes):
            vibration_sequence.append(base_duration + (i * 10))
            if i < num_phonemes - 1:
                vibration_sequence.append(30)  # Pause between phonemes

        # Final blend complete vibration
        vibration_sequence.append(150)

        haptic_config = {
            'enabled': self.enabled,
            'pattern': 'custom_blend',
            'vibration_sequence': vibration_sequence,
            'intensity': self.intensity,
            'total_duration_ms': sum(vibration_sequence),
            'num_phonemes': num_phonemes,
            'api_type': 'vibration'
        }

        logger.info(f"Generated blend haptic for {num_phonemes} phonemes")
        return haptic_config

    def generate_success_feedback(self) -> Dict[str, any]:
        """Generate success haptic feedback"""
        return self.generate_haptic_feedback(HapticPattern.SUCCESS.value, intensity=0.8)

    def generate_error_feedback(self) -> Dict[str, any]:
        """Generate error haptic feedback"""
        return self.generate_haptic_feedback(HapticPattern.ERROR.value, intensity=0.6)

    def set_intensity(self, intensity: float):
        """Set global haptic intensity"""
        self.intensity = max(0.0, min(1.0, intensity))
        logger.info(f"Haptic intensity set to: {self.intensity}")

    def enable_haptics(self):
        """Enable haptic feedback"""
        self.enabled = True
        logger.info("Haptics enabled")

    def disable_haptics(self):
        """Disable haptic feedback"""
        self.enabled = False
        logger.info("Haptics disabled")

    def get_haptic_settings(self) -> Dict[str, any]:
        """Get current haptic settings"""
        return {
            'enabled': self.enabled,
            'intensity': self.intensity,
            'available_patterns': list(self.pattern_library.keys()),
            'pattern_count': len(self.pattern_library)
        }

    def create_custom_pattern(self, pattern_name: str, vibration_sequence: List[int]) -> bool:
        """
        Create a custom haptic pattern

        Args:
            pattern_name: Name for the custom pattern
            vibration_sequence: List of vibration durations in ms

        Returns:
            Success status
        """
        if not vibration_sequence or any(d < 0 for d in vibration_sequence):
            logger.warning(f"Invalid vibration sequence for pattern: {pattern_name}")
            return False

        self.pattern_library[pattern_name] = vibration_sequence
        logger.info(f"Created custom haptic pattern: {pattern_name}")
        return True
