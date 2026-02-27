#!/usr/bin/env python3
"""
Gamification API for ALPA-4 Interactive Interface

Provides backend support for:
- Word validation using phonetics system
- Adaptive difficulty adjustment
- Progress tracking
- TTS phoneme generation
"""

import json
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.phonetics import G2PEngine, DecodabilityValidator, PhonemeAnalyzer


class GamificationEngine:
    """Manages adaptive gamification and difficulty adjustment"""

    def __init__(self):
        self.g2p_engine = G2PEngine()
        self.decodability_validator = DecodabilityValidator(self.g2p_engine)
        self.phoneme_analyzer = PhonemeAnalyzer(self.g2p_engine)

        # FCRR Activity Levels
        self.activity_levels = {
            'phonological': {
                'name': 'Phonological Awareness',
                'color': '#9b59b6',
                'focus': ['syllable_awareness', 'rhyme', 'sound_segmentation']
            },
            'phonics': {
                'name': 'Phonics',
                'color': '#e67e22',
                'focus': ['letter_sound_correspondence', 'blending', 'decoding']
            },
            'fluency': {
                'name': 'Fluency',
                'color': '#27ae60',
                'focus': ['reading_speed', 'accuracy', 'expression']
            }
        }

        # Word lists by difficulty (using FCRR progression)
        self.word_lists = {
            1: {
                'description': 'CVC Short Vowels',
                'phoneme_count': 3,
                'syllables': 1,
                'words': ['cat', 'dog', 'mat', 'hat', 'bat', 'rat', 'sat', 'fat', 'pig', 'big']
            },
            2: {
                'description': 'Digraphs & Blends',
                'phoneme_count': 4,
                'syllables': 1,
                'words': ['ship', 'shop', 'chat', 'chip', 'thin', 'that', 'fish', 'wish', 'lock', 'rock']
            },
            3: {
                'description': 'Complex Consonant Blends',
                'phoneme_count': 5,
                'syllables': 1,
                'words': ['black', 'plant', 'clock', 'trash', 'click', 'grass', 'flash', 'twist']
            },
            4: {
                'description': 'Boss Level: Multisyllabic',
                'phoneme_count': 6,
                'syllables': 2,
                'words': ['button', 'rabbit', 'kitten', 'happen', 'pattern', 'basket', 'sunset', 'rocket']
            }
        }

    def validate_word(self, word: str, user_input: str) -> Dict:
        """
        Validate user's spelling attempt using phonetics system

        Args:
            word: Target word
            user_input: User's spelling attempt

        Returns:
            Validation result with detailed feedback
        """
        is_correct = word.lower() == user_input.lower()

        # Get phoneme breakdown for feedback
        target_phonemes = self.g2p_engine.convert_word(word)
        attempt_phonemes = self.g2p_engine.convert_word(user_input) if user_input else []

        # Analyze phoneme differences
        phoneme_match_rate = self._calculate_phoneme_similarity(target_phonemes, attempt_phonemes)

        return {
            'correct': is_correct,
            'target_word': word,
            'user_input': user_input,
            'target_phonemes': target_phonemes,
            'attempt_phonemes': attempt_phonemes,
            'phoneme_match_rate': phoneme_match_rate,
            'feedback': self._generate_feedback(word, user_input, is_correct, phoneme_match_rate)
        }

    def _calculate_phoneme_similarity(self, target: List[str], attempt: List[str]) -> float:
        """Calculate similarity between phoneme sequences"""
        if not target or not attempt:
            return 0.0

        matching = sum(1 for t, a in zip(target, attempt) if t == a)
        max_length = max(len(target), len(attempt))

        return (matching / max_length) * 100

    def _generate_feedback(self, target: str, attempt: str, correct: bool, similarity: float) -> str:
        """Generate contextual feedback for the student"""
        if correct:
            return f"Perfect! You spelled '{target}' correctly!"

        if similarity >= 75:
            return f"Very close! The correct spelling is '{target}'. You almost had it!"
        elif similarity >= 50:
            return f"Good try! The correct spelling is '{target}'. Check your vowels."
        else:
            return f"The correct spelling is '{target}'. Try sounding it out slowly."

    def get_word_list(self, difficulty: int, activity_level: str = 'phonics') -> Dict:
        """
        Get word list for given difficulty level

        Args:
            difficulty: Difficulty level (1-4)
            activity_level: FCRR activity level (phonological/phonics/fluency)

        Returns:
            Word list with metadata
        """
        difficulty = max(1, min(4, difficulty))
        word_data = self.word_lists[difficulty]

        return {
            'difficulty': difficulty,
            'activity_level': activity_level,
            'description': word_data['description'],
            'words': word_data['words'],
            'phoneme_count': word_data['phoneme_count'],
            'syllables': word_data['syllables'],
            'is_boss_level': difficulty == 4
        }

    def adjust_difficulty(self, current_difficulty: int, streak: int, recent_scores: List[bool]) -> int:
        """
        Adaptive difficulty adjustment based on performance

        Args:
            current_difficulty: Current difficulty level
            streak: Current correct streak
            recent_scores: List of recent correct/incorrect attempts

        Returns:
            New difficulty level
        """
        if not recent_scores:
            return current_difficulty

        # Calculate recent success rate
        success_rate = sum(recent_scores) / len(recent_scores)

        # Increase difficulty if doing well
        if success_rate >= 0.8 and streak >= 3:
            return min(4, current_difficulty + 1)

        # Decrease difficulty if struggling
        elif success_rate < 0.5 and streak == 0:
            return max(1, current_difficulty - 1)

        return current_difficulty

    def get_phoneme_breakdown(self, word: str) -> Dict:
        """
        Get detailed phoneme breakdown for TTS and learning support

        Args:
            word: Word to analyze

        Returns:
            Phoneme breakdown with grapheme-phoneme mapping
        """
        phonemes = self.g2p_engine.convert_word(word)

        # Get grapheme-to-phoneme mapping
        analysis = self.phoneme_analyzer.analyze_text(word)

        return {
            'word': word,
            'phonemes': phonemes,
            'phoneme_count': len(phonemes),
            'syllables': self._count_syllables(phonemes),
            'grapheme_phoneme_map': self._create_gp_mapping(word, phonemes)
        }

    def _count_syllables(self, phonemes: List[str]) -> int:
        """Count syllables based on vowel phonemes"""
        vowel_markers = ['0', '1', '2']  # Stress markers in CMU dict
        syllables = 0

        for phoneme in phonemes:
            if any(marker in phoneme for marker in vowel_markers):
                syllables += 1

        return max(1, syllables)

    def _create_gp_mapping(self, word: str, phonemes: List[str]) -> List[Dict]:
        """Create grapheme-to-phoneme mapping for visual feedback"""
        # Simplified mapping - in production, use more sophisticated alignment
        mapping = []

        for i, letter in enumerate(word):
            phoneme = phonemes[i] if i < len(phonemes) else ''
            mapping.append({
                'grapheme': letter,
                'phoneme': phoneme,
                'position': i
            })

        return mapping

    def check_decodability(self, word: str, allowed_phonemes: Optional[List[str]] = None) -> Dict:
        """
        Check if word is decodable at current student level

        Args:
            word: Word to check
            allowed_phonemes: List of phonemes student has learned (optional)

        Returns:
            Decodability analysis
        """
        if allowed_phonemes:
            result = self.decodability_validator.validate_text(
                word,
                allowed_phonemes=allowed_phonemes,
                sight_words=['the', 'a', 'is']
            )
        else:
            # Default validation
            result = self.decodability_validator.validate_text(word)

        return {
            'word': word,
            'decodable': result.get('decodability_rate', 0) >= 95,
            'decodability_rate': result.get('decodability_rate', 0),
            'analysis': result
        }


# Flask API setup
app = Flask(__name__)
CORS(app)

# Initialize gamification engine
engine = GamificationEngine()


@app.route('/api/word-list', methods=['GET'])
def get_word_list():
    """Get word list for difficulty level"""
    difficulty = int(request.args.get('difficulty', 1))
    activity_level = request.args.get('activity_level', 'phonics')

    result = engine.get_word_list(difficulty, activity_level)
    return jsonify(result)


@app.route('/api/validate-word', methods=['POST'])
def validate_word():
    """Validate user's spelling attempt"""
    data = request.json
    word = data.get('word', '')
    user_input = data.get('user_input', '')

    result = engine.validate_word(word, user_input)
    return jsonify(result)


@app.route('/api/phoneme-breakdown', methods=['GET'])
def get_phoneme_breakdown():
    """Get phoneme breakdown for word"""
    word = request.args.get('word', '')

    result = engine.get_phoneme_breakdown(word)
    return jsonify(result)


@app.route('/api/adjust-difficulty', methods=['POST'])
def adjust_difficulty():
    """Adjust difficulty based on performance"""
    data = request.json
    current_difficulty = data.get('current_difficulty', 1)
    streak = data.get('streak', 0)
    recent_scores = data.get('recent_scores', [])

    new_difficulty = engine.adjust_difficulty(current_difficulty, streak, recent_scores)

    return jsonify({
        'old_difficulty': current_difficulty,
        'new_difficulty': new_difficulty,
        'adjustment': new_difficulty - current_difficulty
    })


@app.route('/api/check-decodability', methods=['POST'])
def check_decodability():
    """Check if word is decodable at student level"""
    data = request.json
    word = data.get('word', '')
    allowed_phonemes = data.get('allowed_phonemes', None)

    result = engine.check_decodability(word, allowed_phonemes)
    return jsonify(result)


@app.route('/api/activity-levels', methods=['GET'])
def get_activity_levels():
    """Get FCRR activity level information"""
    return jsonify(engine.activity_levels)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ALPA-4 Gamification API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
