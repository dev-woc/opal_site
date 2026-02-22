"""
Core PDF Generator using ReportLab

Provides base functionality for all PDF generation tasks
with FCRR color-coding support.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FCRRColors:
    """FCRR Color-Coding System"""
    PURPLE = HexColor('#9B59B6')  # Phonological Awareness
    ORANGE = HexColor('#E67E22')  # Phonics
    GREEN = HexColor('#27AE60')   # Vocabulary
    BLUE = HexColor('#3498DB')    # Fluency
    RED = HexColor('#E74C3C')     # Comprehension
    BLACK = HexColor('#000000')   # Default text


class PDFGenerator:
    """Base PDF Generator with ReportLab"""

    def __init__(self, page_size=letter, dpi=300):
        """
        Initialize PDF Generator

        Args:
            page_size: Page size tuple (width, height)
            dpi: Print quality in DPI (default 300 for high-quality print)
        """
        self.page_size = page_size
        self.dpi = dpi
        self.width, self.height = page_size

        # Typography settings
        self.default_font = "Helvetica"
        self.title_font = "Helvetica-Bold"
        self.title_size = 24
        self.heading_size = 18
        self.body_size = 12
        self.small_size = 10

        # Layout margins
        self.margin_top = 0.75 * inch
        self.margin_bottom = 0.75 * inch
        self.margin_left = 0.75 * inch
        self.margin_right = 0.75 * inch

        logger.info(f"PDF Generator initialized with {dpi} DPI")

    def create_canvas(self) -> Tuple[canvas.Canvas, BytesIO]:
        """
        Create a new canvas and buffer

        Returns:
            Tuple of (canvas, buffer)
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=self.page_size)
        return c, buffer

    def draw_header(self, c: canvas.Canvas, text: str, y_position: float, color=FCRRColors.BLACK):
        """Draw header text with FCRR color"""
        c.setFont(self.title_font, self.title_size)
        c.setFillColor(color)
        c.drawString(self.margin_left, y_position, text)

    def draw_text(self, c: canvas.Canvas, text: str, x: float, y: float,
                  font_size: int = None, color=FCRRColors.BLACK):
        """Draw text at specific position"""
        if font_size is None:
            font_size = self.body_size
        c.setFont(self.default_font, font_size)
        c.setFillColor(color)
        c.drawString(x, y, text)

    def draw_card_border(self, c: canvas.Canvas, x: float, y: float,
                         width: float, height: float, color=FCRRColors.BLACK):
        """Draw a bordered card rectangle"""
        c.setStrokeColor(color)
        c.setLineWidth(2)
        c.rect(x, y, width, height, stroke=1, fill=0)

    def draw_filled_rectangle(self, c: canvas.Canvas, x: float, y: float,
                             width: float, height: float, fill_color,
                             stroke_color=None):
        """Draw a filled rectangle with optional border"""
        c.setFillColor(fill_color)
        if stroke_color:
            c.setStrokeColor(stroke_color)
            c.rect(x, y, width, height, stroke=1, fill=1)
        else:
            c.rect(x, y, width, height, stroke=0, fill=1)

    def add_phonetic_notation(self, c: canvas.Canvas, word: str, phonemes: str,
                             x: float, y: float):
        """Add word with phonetic notation"""
        # Draw word
        c.setFont(self.title_font, 16)
        c.setFillColor(FCRRColors.BLACK)
        c.drawString(x, y, word)

        # Draw phonetic notation below
        c.setFont("Helvetica-Oblique", 12)
        c.setFillColor(FCRRColors.ORANGE)
        c.drawString(x, y - 20, f"/{phonemes}/")

    def finalize_pdf(self, c: canvas.Canvas, buffer: BytesIO) -> bytes:
        """
        Finalize PDF and return bytes

        Args:
            c: Canvas object
            buffer: BytesIO buffer

        Returns:
            PDF content as bytes
        """
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    def get_color_for_category(self, category: str) -> HexColor:
        """
        Get FCRR color for literacy category

        Args:
            category: Category name (phonological, phonics, vocabulary, fluency, comprehension)

        Returns:
            HexColor for the category
        """
        category_map = {
            'phonological': FCRRColors.PURPLE,
            'phonological_awareness': FCRRColors.PURPLE,
            'phonics': FCRRColors.ORANGE,
            'vocabulary': FCRRColors.GREEN,
            'fluency': FCRRColors.BLUE,
            'comprehension': FCRRColors.RED,
        }
        return category_map.get(category.lower(), FCRRColors.BLACK)
