"""
Digital Interactivity & Gamification Module

Provides multi-modal learning experiences including:
- Virtual blending boards with TTS feedback
- Haptic feedback for mobile devices
- Adaptive difficulty gamification
- Performance tracking and analytics
"""

from .blending_board import BlendingBoard, LetterTile
from .tts_engine import TTSEngine
from .haptics_handler import HapticsHandler
from .performance_tracker import PerformanceTracker
from .adaptive_difficulty import AdaptiveDifficultyManager

__all__ = [
    'BlendingBoard',
    'LetterTile',
    'TTSEngine',
    'HapticsHandler',
    'PerformanceTracker',
    'AdaptiveDifficultyManager'
]
