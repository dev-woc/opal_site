"""
Virtual Blending Board Implementation

Provides draggable letter tiles with phoneme blending logic
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class LetterTile:
    """Represents a draggable letter tile"""
    letter: str
    phoneme: str
    position: int
    tile_id: str
    is_vowel: bool = False
    is_digraph: bool = False


class BlendingBoard:
    """Virtual blending board for interactive letter manipulation"""

    def __init__(self):
        self.tiles: List[LetterTile] = []
        self.current_blend: str = ""
        self.phoneme_sequence: List[str] = []
        self.interaction_history: List[Dict[str, Any]] = []

    def add_tile(self, letter: str, phoneme: str, tile_id: Optional[str] = None) -> LetterTile:
        """Add a letter tile to the board"""
        if tile_id is None:
            tile_id = f"tile_{len(self.tiles)}_{datetime.now().timestamp()}"

        is_vowel = letter.lower() in 'aeiou'
        is_digraph = len(letter) > 1

        tile = LetterTile(
            letter=letter,
            phoneme=phoneme,
            position=len(self.tiles),
            tile_id=tile_id,
            is_vowel=is_vowel,
            is_digraph=is_digraph
        )

        self.tiles.append(tile)
        self._update_blend()

        logger.info(f"Added tile: {letter} ({phoneme}) at position {tile.position}")
        return tile

    def remove_tile(self, tile_id: str) -> bool:
        """Remove a tile from the board"""
        initial_count = len(self.tiles)
        self.tiles = [t for t in self.tiles if t.tile_id != tile_id]

        if len(self.tiles) < initial_count:
            self._reindex_tiles()
            self._update_blend()
            logger.info(f"Removed tile: {tile_id}")
            return True

        return False

    def move_tile(self, tile_id: str, new_position: int) -> bool:
        """Move a tile to a new position"""
        tile = next((t for t in self.tiles if t.tile_id == tile_id), None)

        if tile is None:
            return False

        # Remove tile from current position
        self.tiles = [t for t in self.tiles if t.tile_id != tile_id]

        # Insert at new position
        new_position = max(0, min(new_position, len(self.tiles)))
        self.tiles.insert(new_position, tile)

        self._reindex_tiles()
        self._update_blend()

        self._record_interaction('move', tile_id, new_position)
        logger.info(f"Moved tile {tile_id} to position {new_position}")

        return True

    def get_blend(self) -> Dict[str, Any]:
        """Get current blend information"""
        return {
            'word': self.current_blend,
            'phonemes': self.phoneme_sequence,
            'tiles': [
                {
                    'id': t.tile_id,
                    'letter': t.letter,
                    'phoneme': t.phoneme,
                    'position': t.position,
                    'is_vowel': t.is_vowel,
                    'is_digraph': t.is_digraph
                }
                for t in self.tiles
            ],
            'is_valid_word': self._is_valid_blend()
        }

    def clear_board(self):
        """Clear all tiles from the board"""
        self.tiles = []
        self.current_blend = ""
        self.phoneme_sequence = []
        logger.info("Board cleared")

    def load_word(self, word: str, phoneme_map: Dict[str, str]) -> List[LetterTile]:
        """Load a word onto the board with phoneme mappings"""
        self.clear_board()

        created_tiles = []
        for i, letter in enumerate(word):
            phoneme = phoneme_map.get(letter.lower(), letter)
            tile = self.add_tile(letter, phoneme)
            created_tiles.append(tile)

        logger.info(f"Loaded word: {word}")
        return created_tiles

    def _update_blend(self):
        """Update current blend and phoneme sequence"""
        self.current_blend = ''.join(t.letter for t in self.tiles)
        self.phoneme_sequence = [t.phoneme for t in self.tiles]

    def _reindex_tiles(self):
        """Reindex all tiles after position change"""
        for i, tile in enumerate(self.tiles):
            tile.position = i

    def _is_valid_blend(self) -> bool:
        """Check if current blend forms a valid pattern"""
        if len(self.tiles) == 0:
            return False

        # Basic validation: at least one vowel
        has_vowel = any(t.is_vowel for t in self.tiles)

        return has_vowel and len(self.current_blend) >= 2

    def _record_interaction(self, action: str, tile_id: str, data: Any):
        """Record user interaction for analytics"""
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'tile_id': tile_id,
            'data': data
        })

    def get_interaction_history(self) -> List[Dict[str, Any]]:
        """Get complete interaction history"""
        return self.interaction_history.copy()
