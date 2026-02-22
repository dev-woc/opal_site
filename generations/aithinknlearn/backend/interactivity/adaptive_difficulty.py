"""
Adaptive Difficulty Manager

Manages difficulty progression and boss level triggers
"""

from typing import List, Dict, Optional, Any
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Difficulty level tiers"""
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    BOSS = 99  # Special boss level


class AdaptiveDifficultyManager:
    """Manages adaptive difficulty and gamification loops"""

    def __init__(self):
        self.current_level = DifficultyLevel.BEGINNER
        self.xp_points = 0
        self.level_thresholds = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.EASY: 50,
            DifficultyLevel.MEDIUM: 150,
            DifficultyLevel.HARD: 300,
            DifficultyLevel.EXPERT: 500
        }
        self.boss_level_unlocked = False
        self.boss_level_attempts = 0

        # Word pools for each difficulty level
        self.word_pools = self._initialize_word_pools()

    def _initialize_word_pools(self) -> Dict[DifficultyLevel, List[Dict[str, Any]]]:
        """Initialize word pools for each difficulty level"""
        return {
            DifficultyLevel.BEGINNER: [
                {'word': 'cat', 'phonemes': ['c', 'a', 't'], 'pattern': 'CVC'},
                {'word': 'dog', 'phonemes': ['d', 'o', 'g'], 'pattern': 'CVC'},
                {'word': 'hat', 'phonemes': ['h', 'a', 't'], 'pattern': 'CVC'},
                {'word': 'pig', 'phonemes': ['p', 'i', 'g'], 'pattern': 'CVC'},
                {'word': 'sun', 'phonemes': ['s', 'u', 'n'], 'pattern': 'CVC'},
            ],
            DifficultyLevel.EASY: [
                {'word': 'ship', 'phonemes': ['sh', 'i', 'p'], 'pattern': 'CVC with digraph'},
                {'word': 'chat', 'phonemes': ['ch', 'a', 't'], 'pattern': 'CVC with digraph'},
                {'word': 'fish', 'phonemes': ['f', 'i', 'sh'], 'pattern': 'CVC with digraph'},
                {'word': 'jump', 'phonemes': ['j', 'u', 'm', 'p'], 'pattern': 'CVCC'},
                {'word': 'hand', 'phonemes': ['h', 'a', 'n', 'd'], 'pattern': 'CVCC'},
            ],
            DifficultyLevel.MEDIUM: [
                {'word': 'plate', 'phonemes': ['p', 'l', 'a_e', 't'], 'pattern': 'CVCe'},
                {'word': 'shine', 'phonemes': ['sh', 'i_e', 'n'], 'pattern': 'CVCe with digraph'},
                {'word': 'train', 'phonemes': ['t', 'r', 'ai', 'n'], 'pattern': 'CVVC'},
                {'word': 'cloud', 'phonemes': ['c', 'l', 'ou', 'd'], 'pattern': 'CVVC'},
                {'word': 'beach', 'phonemes': ['b', 'ea', 'ch'], 'pattern': 'CVV'},
            ],
            DifficultyLevel.HARD: [
                {'word': 'bright', 'phonemes': ['b', 'r', 'igh', 't'], 'pattern': 'CCVCC'},
                {'word': 'thread', 'phonemes': ['th', 'r', 'ea', 'd'], 'pattern': 'CCVVC'},
                {'word': 'stripe', 'phonemes': ['s', 't', 'r', 'i_e', 'p'], 'pattern': 'CCCVC'},
                {'word': 'strong', 'phonemes': ['s', 't', 'r', 'o', 'ng'], 'pattern': 'CCCVCC'},
                {'word': 'splint', 'phonemes': ['s', 'p', 'l', 'i', 'n', 't'], 'pattern': 'CCCCVC'},
            ],
            DifficultyLevel.EXPERT: [
                {'word': 'through', 'phonemes': ['th', 'r', 'ough'], 'pattern': 'Complex'},
                {'word': 'straight', 'phonemes': ['s', 't', 'r', 'aigh', 't'], 'pattern': 'Complex'},
                {'word': 'thought', 'phonemes': ['th', 'ough', 't'], 'pattern': 'Complex'},
                {'word': 'treasure', 'phonemes': ['t', 'r', 'ea', 's', 'u', 'r', 'e'], 'pattern': 'Complex'},
                {'word': 'freight', 'phonemes': ['f', 'r', 'eigh', 't'], 'pattern': 'Complex'},
            ],
            DifficultyLevel.BOSS: [
                # Multisyllabic boss words
                {'word': 'butterfly', 'phonemes': ['b', 'u', 't', 't', 'er', 'f', 'l', 'y'], 'pattern': 'Multisyllabic', 'syllables': 3},
                {'word': 'fantastic', 'phonemes': ['f', 'a', 'n', 't', 'a', 's', 't', 'i', 'c'], 'pattern': 'Multisyllabic', 'syllables': 3},
                {'word': 'understand', 'phonemes': ['u', 'n', 'd', 'er', 's', 't', 'a', 'n', 'd'], 'pattern': 'Multisyllabic', 'syllables': 3},
                {'word': 'adventure', 'phonemes': ['a', 'd', 'v', 'e', 'n', 't', 'u', 'r', 'e'], 'pattern': 'Multisyllabic', 'syllables': 3},
                {'word': 'magnificent', 'phonemes': ['m', 'a', 'g', 'n', 'i', 'f', 'i', 'c', 'e', 'n', 't'], 'pattern': 'Multisyllabic', 'syllables': 4},
            ]
        }

    def add_xp(self, points: int) -> Dict[str, Any]:
        """
        Add XP points and check for level up

        Args:
            points: XP points to add

        Returns:
            Level update information
        """
        old_level = self.current_level
        self.xp_points += points

        # Check for level up
        new_level = self._calculate_level()
        leveled_up = new_level != old_level

        # Check boss level unlock
        boss_unlocked = self._check_boss_unlock()

        result = {
            'xp_added': points,
            'total_xp': self.xp_points,
            'current_level': self.current_level.name,
            'current_level_value': self.current_level.value,
            'leveled_up': leveled_up,
            'boss_level_unlocked': boss_unlocked,
            'next_level_xp': self._get_next_level_xp()
        }

        if leveled_up:
            logger.info(f"Level up! {old_level.name} -> {self.current_level.name}")
            result['level_up_message'] = f"Congratulations! You've reached {self.current_level.name} level!"

        if boss_unlocked and not self.boss_level_unlocked:
            self.boss_level_unlocked = True
            logger.info("Boss level unlocked!")
            result['boss_unlock_message'] = "Boss Level Unlocked! Ready for a challenge?"

        return result

    def get_next_word(self, force_boss: bool = False) -> Dict[str, Any]:
        """
        Get next word based on current difficulty

        Args:
            force_boss: Force boss level word

        Returns:
            Word challenge
        """
        if force_boss and self.boss_level_unlocked:
            level = DifficultyLevel.BOSS
        else:
            level = self.current_level

        word_pool = self.word_pools.get(level, self.word_pools[DifficultyLevel.BEGINNER])
        word_data = random.choice(word_pool)

        challenge = {
            'word': word_data['word'],
            'phonemes': word_data['phonemes'],
            'pattern': word_data['pattern'],
            'difficulty_level': level.name,
            'is_boss_level': level == DifficultyLevel.BOSS,
            'syllable_count': word_data.get('syllables', 1),
            'hint': self._generate_hint(word_data)
        }

        if level == DifficultyLevel.BOSS:
            self.boss_level_attempts += 1
            challenge['boss_attempt_number'] = self.boss_level_attempts

        logger.info(f"Generated {level.name} word: {word_data['word']}")
        return challenge

    def adjust_difficulty(self, success_rate: float, current_streak: int) -> Dict[str, Any]:
        """
        Adjust difficulty based on performance

        Args:
            success_rate: Recent success rate (0.0-1.0)
            current_streak: Current success streak

        Returns:
            Difficulty adjustment info
        """
        old_level = self.current_level

        # Increase difficulty if doing well
        if success_rate > 0.8 and current_streak >= 3:
            if self.current_level.value < DifficultyLevel.EXPERT.value:
                next_level_value = self.current_level.value + 1
                self.current_level = DifficultyLevel(next_level_value)

        # Decrease difficulty if struggling
        elif success_rate < 0.4 and self.current_level.value > DifficultyLevel.BEGINNER.value:
            prev_level_value = self.current_level.value - 1
            self.current_level = DifficultyLevel(prev_level_value)

        adjustment = {
            'old_level': old_level.name,
            'new_level': self.current_level.name,
            'adjusted': old_level != self.current_level,
            'success_rate': round(success_rate * 100, 2),
            'current_streak': current_streak
        }

        if old_level != self.current_level:
            logger.info(f"Difficulty adjusted: {old_level.name} -> {self.current_level.name}")

        return adjustment

    def get_boss_level_status(self) -> Dict[str, Any]:
        """Get boss level status"""
        return {
            'unlocked': self.boss_level_unlocked,
            'attempts': self.boss_level_attempts,
            'unlock_threshold_xp': 100,
            'ready': self.boss_level_unlocked and self.xp_points >= 100
        }

    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get current difficulty information"""
        return {
            'current_level': self.current_level.name,
            'current_level_value': self.current_level.value,
            'xp_points': self.xp_points,
            'next_level_xp': self._get_next_level_xp(),
            'progress_percentage': self._get_progress_percentage(),
            'boss_level_status': self.get_boss_level_status(),
            'available_word_count': len(self.word_pools.get(self.current_level, []))
        }

    def _calculate_level(self) -> DifficultyLevel:
        """Calculate level based on XP"""
        for level in reversed(list(DifficultyLevel)):
            if level == DifficultyLevel.BOSS:
                continue
            threshold = self.level_thresholds.get(level, 0)
            if self.xp_points >= threshold:
                return level
        return DifficultyLevel.BEGINNER

    def _check_boss_unlock(self) -> bool:
        """Check if boss level should be unlocked"""
        # Unlock boss level at 100 XP
        return self.xp_points >= 100

    def _get_next_level_xp(self) -> Optional[int]:
        """Get XP needed for next level"""
        current_value = self.current_level.value

        for level, threshold in self.level_thresholds.items():
            if level.value == current_value + 1:
                return threshold

        return None

    def _get_progress_percentage(self) -> float:
        """Get progress to next level as percentage"""
        next_xp = self._get_next_level_xp()

        if next_xp is None:
            return 100.0

        current_threshold = self.level_thresholds[self.current_level]
        progress = (self.xp_points - current_threshold) / (next_xp - current_threshold)

        return round(min(100.0, max(0.0, progress * 100)), 2)

    def _generate_hint(self, word_data: Dict[str, Any]) -> str:
        """Generate hint for word"""
        pattern = word_data['pattern']

        hints = {
            'CVC': 'Consonant-Vowel-Consonant pattern',
            'CVC with digraph': 'Contains a two-letter sound',
            'CVCC': 'Ends with two consonants',
            'CVCe': 'Silent E makes the vowel say its name',
            'CVVC': 'Two vowels work together',
            'Complex': 'Advanced spelling pattern',
            'Multisyllabic': 'Multiple syllables - break it down!'
        }

        return hints.get(pattern, 'Sound it out carefully!')
