"""
Syllable Card Generator

Creates printable syllable cards with visual syllable division.
"""

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from typing import List, Dict
import logging

from .pdf_generator import PDFGenerator, FCRRColors

logger = logging.getLogger(__name__)


class SyllableCardGenerator(PDFGenerator):
    """Generate syllable cards with visual division indicators"""

    def __init__(self, dpi=300):
        super().__init__(page_size=letter, dpi=dpi)

        # Card dimensions (3x3 cards per page)
        self.card_width = 2.5 * inch
        self.card_height = 2.0 * inch
        self.cards_per_row = 3
        self.cards_per_column = 4
        self.card_spacing = 0.2 * inch

    def generate_syllable_cards(self, words: List[Dict[str, any]], category: str = 'phonological') -> bytes:
        """
        Generate PDF with syllable cards

        Args:
            words: List of dicts with 'word' and 'syllables' keys
            category: FCRR category for color-coding

        Returns:
            PDF as bytes
        """
        c, buffer = self.create_canvas()
        color = self.get_color_for_category(category)

        start_x = self.margin_left
        start_y = self.height - self.margin_top - self.card_height

        card_count = 0
        page_count = 1

        for word_data in words:
            word = word_data.get('word', '')
            syllables = word_data.get('syllables', [])

            # Calculate position
            col = card_count % self.cards_per_row
            row = (card_count // self.cards_per_row) % self.cards_per_column

            x = start_x + col * (self.card_width + self.card_spacing)
            y = start_y - row * (self.card_height + self.card_spacing)

            # Draw card
            self._draw_syllable_card(c, word, syllables, x, y, color)

            card_count += 1

            # New page if needed
            if card_count % (self.cards_per_row * self.cards_per_column) == 0:
                c.showPage()
                page_count += 1
                logger.info(f"Starting page {page_count}")

        logger.info(f"Generated {len(words)} syllable cards on {page_count} page(s)")
        return self.finalize_pdf(c, buffer)

    def _draw_syllable_card(self, c, word: str, syllables: List[str], x: float, y: float, color):
        """Draw a single syllable card"""
        # Draw border
        self.draw_card_border(c, x, y, self.card_width, self.card_height, color)

        # Draw colored header
        header_height = 0.35 * inch
        self.draw_filled_rectangle(
            c, x, y + self.card_height - header_height,
            self.card_width, header_height,
            color, stroke_color=color
        )

        # Label
        c.setFont(self.default_font, 9)
        c.setFillColor(colors.white)
        c.drawString(x + 0.1 * inch, y + self.card_height - 0.22 * inch, "SYLLABLES")

        # Draw full word at top
        c.setFont(self.title_font, 14)
        c.setFillColor(FCRRColors.BLACK)
        word_width = c.stringWidth(word, self.title_font, 14)
        c.drawString(x + (self.card_width - word_width) / 2, y + self.card_height - 0.65 * inch, word)

        # Draw syllables with division markers
        if not syllables:
            syllables = [word]  # Default to whole word if no syllables provided

        # Calculate syllable box dimensions
        num_syllables = len(syllables)
        syllable_box_width = (self.card_width - 0.4 * inch) / num_syllables
        syllable_start_x = x + 0.2 * inch
        syllable_y = y + self.card_height / 2

        for i, syllable in enumerate(syllables):
            box_x = syllable_start_x + i * syllable_box_width

            # Draw syllable box
            c.setStrokeColor(color)
            c.setLineWidth(1.5)
            c.rect(box_x, syllable_y - 0.3 * inch, syllable_box_width, 0.6 * inch, stroke=1, fill=0)

            # Draw syllable text
            c.setFont(self.title_font, 18)
            c.setFillColor(color)
            syl_width = c.stringWidth(syllable, self.title_font, 18)
            syl_x = box_x + (syllable_box_width - syl_width) / 2
            c.drawString(syl_x, syllable_y - 0.08 * inch, syllable)

        # Draw syllable count
        c.setFont(self.default_font, 9)
        c.setFillColor(FCRRColors.BLACK)
        count_text = f"{len(syllables)} syllable{'s' if len(syllables) != 1 else ''}"
        c.drawString(x + 0.1 * inch, y + 0.1 * inch, count_text)
