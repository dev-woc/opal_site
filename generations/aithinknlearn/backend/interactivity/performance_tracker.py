"""
Performance Tracker for Student Progress

Tracks student performance metrics for adaptive difficulty
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Student performance metrics"""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    average_time_ms: float = 0.0
    success_rate: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    total_points: int = 0


@dataclass
class AttemptRecord:
    """Record of a single attempt"""
    timestamp: str
    word: str
    phonemes: List[str]
    success: bool
    time_ms: int
    attempts_count: int = 1
    error_type: Optional[str] = None


class PerformanceTracker:
    """Tracks student performance and learning progress"""

    def __init__(self, student_id: Optional[str] = None):
        self.student_id = student_id or "anonymous"
        self.metrics = PerformanceMetrics()
        self.attempt_history: List[AttemptRecord] = []
        self.session_start = datetime.now()
        self.difficulty_level = 1

    def record_attempt(self, word: str, phonemes: List[str], success: bool,
                      time_ms: int, error_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Record a learning attempt

        Args:
            word: The word attempted
            phonemes: Phoneme breakdown
            success: Whether attempt was successful
            time_ms: Time taken in milliseconds
            error_type: Type of error if failed

        Returns:
            Updated metrics
        """
        # Create attempt record
        attempt = AttemptRecord(
            timestamp=datetime.now().isoformat(),
            word=word,
            phonemes=phonemes,
            success=success,
            time_ms=time_ms,
            error_type=error_type
        )
        self.attempt_history.append(attempt)

        # Update metrics
        self.metrics.total_attempts += 1

        if success:
            self.metrics.successful_attempts += 1
            self.metrics.current_streak += 1
            self.metrics.best_streak = max(self.metrics.best_streak, self.metrics.current_streak)

            # Award points based on difficulty and speed
            points = self._calculate_points(time_ms, len(phonemes))
            self.metrics.total_points += points
        else:
            self.metrics.failed_attempts += 1
            self.metrics.current_streak = 0

        # Update success rate
        self.metrics.success_rate = (
            self.metrics.successful_attempts / self.metrics.total_attempts
            if self.metrics.total_attempts > 0 else 0.0
        )

        # Update average time
        total_time = sum(a.time_ms for a in self.attempt_history)
        self.metrics.average_time_ms = total_time / len(self.attempt_history)

        logger.info(f"Recorded attempt: {word} - {'SUCCESS' if success else 'FAIL'} ({time_ms}ms)")

        return self.get_current_metrics()

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'student_id': self.student_id,
            'total_attempts': self.metrics.total_attempts,
            'successful_attempts': self.metrics.successful_attempts,
            'failed_attempts': self.metrics.failed_attempts,
            'success_rate': round(self.metrics.success_rate * 100, 2),
            'average_time_ms': round(self.metrics.average_time_ms, 2),
            'current_streak': self.metrics.current_streak,
            'best_streak': self.metrics.best_streak,
            'total_points': self.metrics.total_points,
            'difficulty_level': self.difficulty_level,
            'session_duration_minutes': self._get_session_duration()
        }

    def get_recent_performance(self, n: int = 10) -> Dict[str, Any]:
        """Get performance stats for recent N attempts"""
        recent_attempts = self.attempt_history[-n:] if len(self.attempt_history) >= n else self.attempt_history

        if not recent_attempts:
            return {'recent_success_rate': 0.0, 'recent_avg_time': 0.0, 'attempt_count': 0}

        recent_successes = sum(1 for a in recent_attempts if a.success)
        recent_success_rate = recent_successes / len(recent_attempts)
        recent_avg_time = sum(a.time_ms for a in recent_attempts) / len(recent_attempts)

        return {
            'recent_success_rate': round(recent_success_rate * 100, 2),
            'recent_avg_time_ms': round(recent_avg_time, 2),
            'attempt_count': len(recent_attempts),
            'trend': self._calculate_trend(recent_attempts)
        }

    def should_increase_difficulty(self) -> bool:
        """Determine if difficulty should increase"""
        if self.metrics.total_attempts < 5:
            return False

        recent_perf = self.get_recent_performance(5)

        # Increase if recent success rate > 80% and streak >= 3
        return (
            recent_perf['recent_success_rate'] > 80 and
            self.metrics.current_streak >= 3
        )

    def should_decrease_difficulty(self) -> bool:
        """Determine if difficulty should decrease"""
        if self.metrics.total_attempts < 3:
            return False

        recent_perf = self.get_recent_performance(3)

        # Decrease if recent success rate < 40%
        return recent_perf['recent_success_rate'] < 40

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'metrics': self.get_current_metrics(),
            'recent_performance': self.get_recent_performance(),
            'attempt_history_size': len(self.attempt_history),
            'session_start': self.session_start.isoformat(),
            'recommendations': self._generate_recommendations()
        }

    def reset_session(self):
        """Reset session metrics (keep historical data)"""
        self.session_start = datetime.now()
        logger.info("Session reset")

    def _calculate_points(self, time_ms: int, num_phonemes: int) -> int:
        """Calculate points for successful attempt"""
        base_points = 10 * self.difficulty_level

        # Time bonus (faster = more points)
        time_bonus = 0
        if time_ms < 3000:
            time_bonus = 5
        elif time_ms < 5000:
            time_bonus = 3

        # Complexity bonus
        complexity_bonus = num_phonemes * 2

        # Streak bonus
        streak_bonus = min(self.metrics.current_streak, 10)

        total_points = base_points + time_bonus + complexity_bonus + streak_bonus

        return total_points

    def _get_session_duration(self) -> float:
        """Get session duration in minutes"""
        duration = datetime.now() - self.session_start
        return round(duration.total_seconds() / 60, 2)

    def _calculate_trend(self, attempts: List[AttemptRecord]) -> str:
        """Calculate performance trend"""
        if len(attempts) < 3:
            return 'stable'

        recent_half = attempts[len(attempts)//2:]
        earlier_half = attempts[:len(attempts)//2]

        recent_success = sum(1 for a in recent_half if a.success) / len(recent_half)
        earlier_success = sum(1 for a in earlier_half if a.success) / len(earlier_half)

        if recent_success > earlier_success + 0.2:
            return 'improving'
        elif recent_success < earlier_success - 0.2:
            return 'declining'
        else:
            return 'stable'

    def _generate_recommendations(self) -> List[str]:
        """Generate performance-based recommendations"""
        recommendations = []

        if self.metrics.success_rate < 0.5:
            recommendations.append("Consider reviewing phoneme sounds before blending")

        if self.metrics.average_time_ms > 10000:
            recommendations.append("Take your time - accuracy is more important than speed")

        if self.should_increase_difficulty():
            recommendations.append("Ready for more challenging words!")

        if self.should_decrease_difficulty():
            recommendations.append("Try simpler words to build confidence")

        if self.metrics.current_streak >= 5:
            recommendations.append("Amazing streak! Keep up the great work!")

        return recommendations
