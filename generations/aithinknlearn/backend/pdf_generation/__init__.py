"""
PDF Generation Module for Print Materials

Supports:
- ReportLab for pixel-precise layouts
- WeasyPrint for HTML-to-PDF conversion
- Canva API integration for template suggestions
- FCRR color-coding system
"""

from .pdf_generator import PDFGenerator
from .word_card_generator import WordCardGenerator
from .syllable_card_generator import SyllableCardGenerator
from .sound_mapping_generator import SoundMappingGenerator
from .canva_integration import CanvaAPIClient

__all__ = [
    'PDFGenerator',
    'WordCardGenerator',
    'SyllableCardGenerator',
    'SoundMappingGenerator',
    'CanvaAPIClient'
]
