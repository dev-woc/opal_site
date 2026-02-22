"""
Word Card Generator using ReportLab

Creates printable word cards with phonetic notation
and FCRR color-coding.
"""

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from typing import List, Dict, Optional
import logging

from .pdf_generator import PDFGenerator, FCRRColors

logger = logging.getLogger(__name__)


class WordCardGenerator(PDFGenerator):
    """Generate printable word cards with phonetic notation"""

    def __init__(self, dpi=300):
        super().__init__(page_size=letter, dpi=dpi)

        # Card dimensions (2x4 cards per page)
        self.card_width = 3.5 * inch
        self.card_height = 2.5 * inch
        self.cards_per_row = 2
        self.cards_per_column = 4
        self.card_spacing = 0.25 * inch

    def generate_word_cards(self, words: List[Dict[str, str]], category: str = 'phonics') -> bytes:
        """
        Generate PDF with word cards

        Args:
            words: List of dicts with 'word' and 'phonemes' keys
            category: FCRR category for color-coding

        Returns:
            PDF as bytes
        """
        c, buffer = self.create_canvas()
        color = self.get_color_for_category(category)

        # Calculate starting positions
        start_x = self.margin_left
        start_y = self.height - self.margin_top - self.card_height

        card_count = 0
        page_count = 1

        for word_data in words:
            word = word_data.get('word', '')
            phonemes = word_data.get('phonemes', '')

            # Calculate position
            col = card_count % self.cards_per_row
            row = (card_count // self.cards_per_row) % self.cards_per_column

            x = start_x + col * (self.card_width + self.card_spacing)
            y = start_y - row * (self.card_height + self.card_spacing)

            # Draw card
            self._draw_word_card(c, word, phonemes, x, y, color)

            card_count += 1

            # New page if needed
            if card_count % (self.cards_per_row * self.cards_per_column) == 0:
                c.showPage()
                page_count += 1
                logger.info(f"Starting page {page_count}")

        logger.info(f"Generated {len(words)} word cards on {page_count} page(s)")
        return self.finalize_pdf(c, buffer)

    def _draw_word_card(self, c, word: str, phonemes: str, x: float, y: float, color):
        """Draw a single word card"""
        # Draw border
        self.draw_card_border(c, x, y, self.card_width, self.card_height, color)

        # Draw colored header bar
        header_height = 0.4 * inch
        self.draw_filled_rectangle(
            c, x, y + self.card_height - header_height,
            self.card_width, header_height,
            color, stroke_color=color
        )

        # Draw "WORD" label in white
        c.setFont(self.default_font, 10)
        c.setFillColor(FCRRColors.BLACK)
        label_x = x + self.card_width / 2 - 0.2 * inch
        label_y = y + self.card_height - header_height + 0.15 * inch
        c.setFillColor(colors.white)
        c.drawString(label_x, label_y, "WORD")

        # Draw word in center (large, bold)
        c.setFont(self.title_font, 32)
        c.setFillColor(FCRRColors.BLACK)
        word_width = c.stringWidth(word, self.title_font, 32)
        word_x = x + (self.card_width - word_width) / 2
        word_y = y + self.card_height / 2 + 0.2 * inch
        c.drawString(word_x, word_y, word)

        # Draw phonetic notation below word
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(color)
        phoneme_text = f"/{phonemes}/"
        phoneme_width = c.stringWidth(phoneme_text, "Helvetica-Oblique", 14)
        phoneme_x = x + (self.card_width - phoneme_width) / 2
        phoneme_y = y + self.card_height / 2 - 0.3 * inch
        c.drawString(phoneme_x, phoneme_y, phoneme_text)

        # Draw small syllable count indicator
        syllable_count = len(phonemes.split())
        c.setFont(self.default_font, 9)
        c.setFillColor(FCRRColors.BLACK)
        c.drawString(x + 0.1 * inch, y + 0.1 * inch, f"{syllable_count} syllables")
