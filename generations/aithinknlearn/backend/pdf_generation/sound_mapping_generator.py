"""
Sound Mapping Box Generator

Creates Elkonin boxes for sound-to-grapheme mapping activities.
"""

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from typing import List, Dict
import logging

from .pdf_generator import PDFGenerator, FCRRColors

logger = logging.getLogger(__name__)


class SoundMappingGenerator(PDFGenerator):
    """Generate sound mapping boxes (Elkonin boxes)"""

    def __init__(self, dpi=300):
        super().__init__(page_size=letter, dpi=dpi)

    def generate_sound_mapping_worksheet(self, words: List[Dict[str, any]], category: str = 'phonics') -> bytes:
        """
        Generate sound mapping worksheet with Elkonin boxes

        Args:
            words: List of dicts with 'word', 'graphemes', and 'phonemes' keys
            category: FCRR category for color-coding

        Returns:
            PDF as bytes
        """
        c, buffer = self.create_canvas()
        color = self.get_color_for_category(category)

        # Draw header
        y_position = self.height - self.margin_top
        self.draw_header(c, "Sound Mapping Practice", y_position, color)

        # Instructions
        c.setFont(self.default_font, 11)
        c.setFillColor(FCRRColors.BLACK)
        y_position -= 0.5 * inch
        c.drawString(self.margin_left, y_position, "Say the word. Count the sounds. Write the grapheme for each sound.")

        # Starting position for words
        y_position -= 0.8 * inch

        word_count = 0
        page_count = 1

        for word_data in words:
            # Check if we need a new page
            if y_position < self.margin_bottom + 1.5 * inch:
                c.showPage()
                page_count += 1
                y_position = self.height - self.margin_top
                self.draw_header(c, "Sound Mapping Practice (continued)", y_position, color)
                y_position -= 0.8 * inch

            # Draw sound mapping box for this word
            self._draw_sound_mapping_box(c, word_data, self.margin_left, y_position, color)

            y_position -= 1.8 * inch
            word_count += 1

        logger.info(f"Generated sound mapping worksheet with {len(words)} words on {page_count} page(s)")
        return self.finalize_pdf(c, buffer)

    def _draw_sound_mapping_box(self, c, word_data: Dict[str, any], x: float, y: float, color):
        """Draw sound mapping box for a single word"""
        word = word_data.get('word', '')
        graphemes = word_data.get('graphemes', [])
        phonemes = word_data.get('phonemes', [])

        # Ensure we have data
        if not graphemes and word:
            graphemes = list(word)  # Default to letters if no graphemes provided
        if not phonemes and word:
            phonemes = list(word)  # Default to letters if no phonemes provided

        num_sounds = max(len(graphemes), len(phonemes))

        # Draw word label
        c.setFont(self.title_font, 16)
        c.setFillColor(FCRRColors.BLACK)
        c.drawString(x, y, word)

        # Draw picture placeholder (small box)
        picture_box_size = 0.8 * inch
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.rect(x + 3 * inch, y - 0.1 * inch, picture_box_size, picture_box_size, stroke=1, fill=0)
        c.setFont(self.default_font, 9)
        c.setFillColor(colors.grey)
        c.drawString(x + 3.15 * inch, y + 0.3 * inch, "[image]")

        # Draw Elkonin boxes
        box_y = y - 0.9 * inch
        box_width = 0.6 * inch
        box_height = 0.6 * inch
        box_spacing = 0.05 * inch

        # Label row
        c.setFont(self.default_font, 10)
        c.setFillColor(color)
        c.drawString(x, box_y + box_height + 0.15 * inch, "Graphemes:")

        # Draw boxes for graphemes
        for i in range(num_sounds):
            box_x = x + i * (box_width + box_spacing)

            # Draw box
            c.setStrokeColor(color)
            c.setLineWidth(2)
            c.rect(box_x, box_y, box_width, box_height, stroke=1, fill=0)

            # If we have answer key, draw grapheme lightly
            if i < len(graphemes):
                c.setFont(self.title_font, 18)
                c.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))  # Very light gray
                grapheme = graphemes[i]
                g_width = c.stringWidth(grapheme, self.title_font, 18)
                g_x = box_x + (box_width - g_width) / 2
                g_y = box_y + 0.2 * inch
                c.drawString(g_x, g_y, grapheme)

        # Draw phoneme row below
        phoneme_y = box_y - box_height - 0.3 * inch

        c.setFont(self.default_font, 10)
        c.setFillColor(color)
        c.drawString(x, phoneme_y + box_height + 0.15 * inch, "Phonemes:")

        for i in range(num_sounds):
            box_x = x + i * (box_width + box_spacing)

            # Draw box
            c.setStrokeColor(color)
            c.setLineWidth(2)
            c.rect(box_x, phoneme_y, box_width, box_height, stroke=1, fill=0)

            # If we have answer key, draw phoneme
            if i < len(phonemes):
                c.setFont("Helvetica-Oblique", 14)
                c.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))
                phoneme = f"/{phonemes[i]}/"
                p_width = c.stringWidth(phoneme, "Helvetica-Oblique", 14)
                p_x = box_x + (box_width - p_width) / 2
                p_y = phoneme_y + 0.18 * inch
                c.drawString(p_x, p_y, phoneme)

        # Draw sound count
        c.setFont(self.default_font, 10)
        c.setFillColor(FCRRColors.BLACK)
        c.drawString(x + num_sounds * (box_width + box_spacing) + 0.3 * inch,
                     box_y + 0.2 * inch, f"{num_sounds} sounds")
