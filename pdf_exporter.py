"""
PDF Exporter - Visual Novel/Comic Style
Creates beautiful PDF exports combining storyboard text with generated images
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List, Dict, Any
import os


class StoryboardPDFExporter:
    """Export storyboards to beautiful PDF in visual novel/comic style"""

    def __init__(self):
        """Initialize PDF exporter with custom styling"""

        # Register Unicode fonts for Cyrillic support
        self._register_fonts()

        # Page dimensions
        self.page_width, self.page_height = A4

        # Margins
        self.margin_left = 1.5 * cm
        self.margin_right = 1.5 * cm
        self.margin_top = 2 * cm
        self.margin_bottom = 2 * cm

        # Colors - Kazakh theme (warm earth tones)
        self.color_primary = colors.HexColor('#D4AF37')  # Golden
        self.color_secondary = colors.HexColor('#8B4513')  # Saddle Brown
        self.color_text = colors.HexColor('#2C1810')  # Dark Brown
        self.color_background = colors.HexColor('#FFF8DC')  # Cornsilk
        self.color_border = colors.HexColor('#DAA520')  # Goldenrod

    def _register_fonts(self):
        """Register Unicode-compatible fonts for Cyrillic support"""
        try:
            # Try to register Arial Unicode (macOS)
            arial_unicode_path = '/Library/Fonts/Arial Unicode.ttf'
            if os.path.exists(arial_unicode_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_unicode_path))
                self.font_regular = 'ArialUnicode'
                self.font_bold = 'ArialUnicode'
                self.font_italic = 'ArialUnicode'
                return

            # Fallback to system Arial (if available)
            arial_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
            arial_bold_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
            arial_italic_path = '/System/Library/Fonts/Supplemental/Arial Italic.ttf'

            if os.path.exists(arial_path):
                pdfmetrics.registerFont(TTFont('ArialReg', arial_path))
                self.font_regular = 'ArialReg'

                if os.path.exists(arial_bold_path):
                    pdfmetrics.registerFont(TTFont('ArialBold', arial_bold_path))
                    self.font_bold = 'ArialBold'
                else:
                    self.font_bold = 'ArialReg'

                if os.path.exists(arial_italic_path):
                    pdfmetrics.registerFont(TTFont('ArialItalic', arial_italic_path))
                    self.font_italic = 'ArialItalic'
                else:
                    self.font_italic = 'ArialReg'
                return

        except Exception as e:
            print(f"Warning: Could not register Unicode fonts: {e}")

        # Fallback to Helvetica (will have encoding issues with Cyrillic)
        self.font_regular = 'Helvetica'
        self.font_bold = 'Helvetica-Bold'
        self.font_italic = 'Helvetica-Oblique'

    def export_storyboard(
        self,
        storyboard_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Export storyboard to PDF

        Args:
            storyboard_data: Dict with 'storyboard' (frames) and 'metadata'
            output_path: Path to save PDF file

        Returns:
            Path to generated PDF
        """

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom,
            title="Aldar Köse - Storyboard"
        )

        # Build story elements
        story_elements = []

        # Add title page
        story_elements.extend(self._create_title_page(storyboard_data))
        story_elements.append(PageBreak())

        # Add each frame
        frames = storyboard_data.get('storyboard', [])
        for i, frame in enumerate(frames, 1):
            story_elements.extend(self._create_frame_page(frame, i, len(frames)))

            # Page break after each frame (except last)
            if i < len(frames):
                story_elements.append(PageBreak())

        # Build PDF
        doc.build(story_elements, onFirstPage=self._add_page_decoration)

        return output_path

    def _create_title_page(self, storyboard_data: Dict[str, Any]) -> List:
        """Create beautiful title page"""
        elements = []

        # Styles
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=32,
            textColor=self.color_secondary,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName=self.font_bold
        )

        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=self.color_text,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName=self.font_regular
        )

        # Metadata style
        meta_style = ParagraphStyle(
            'CustomMeta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.color_text,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName=self.font_regular
        )

        # Add spacing from top
        elements.append(Spacer(1, 3 * cm))

        # Title
        elements.append(Paragraph("🎭 Алдар Көсе", title_style))
        elements.append(Spacer(1, 0.5 * cm))

        # Decorative line
        elements.append(self._create_decorative_line())
        elements.append(Spacer(1, 1 * cm))

        # Story title/prompt
        metadata = storyboard_data.get('metadata', {})
        original_prompt = metadata.get('original_prompt', 'Untitled Story')
        aldar_story = metadata.get('aldar_story', '')

        elements.append(Paragraph(f"<b>{original_prompt}</b>", subtitle_style))
        elements.append(Spacer(1, 0.5 * cm))

        # Story text (if available)
        if aldar_story:
            story_style = ParagraphStyle(
                'StoryText',
                parent=styles['Normal'],
                fontSize=12,
                textColor=self.color_text,
                alignment=TA_JUSTIFY,
                spaceAfter=20,
                leading=18,
                fontName=self.font_regular
            )
            elements.append(Paragraph(aldar_story, story_style))

        elements.append(Spacer(1, 2 * cm))

        # Metadata
        num_frames = metadata.get('num_frames', 0)
        generated_at = metadata.get('generated_at', datetime.now().isoformat())

        # Format date
        try:
            dt = datetime.fromisoformat(generated_at)
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except:
            date_str = generated_at

        elements.append(Paragraph(f"<b>Frames:</b> {num_frames}", meta_style))
        elements.append(Paragraph(f"<b>Generated:</b> {date_str}", meta_style))

        return elements

    def _create_frame_page(self, frame: Dict[str, Any], frame_num: int, total_frames: int) -> List:
        """
        Create a page for a single frame in visual novel/comic style

        Layout:
        - Frame number header
        - Large image (taking most of the page)
        - Text box below with description and dialogue
        """
        elements = []

        styles = getSampleStyleSheet()

        # Frame header
        header_style = ParagraphStyle(
            'FrameHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.color_primary,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName=self.font_bold
        )

        elements.append(Paragraph(f"Frame {frame_num} / {total_frames}", header_style))
        elements.append(Spacer(1, 0.3 * cm))

        # Image (if exists)
        image_path = frame.get('image_path')
        if image_path and os.path.exists(image_path):
            # Calculate image size to fit page while maintaining aspect ratio
            max_image_width = self.page_width - self.margin_left - self.margin_right - 2*cm
            max_image_height = 12 * cm  # Leave room for text below

            # Get actual image dimensions to preserve aspect ratio
            from PIL import Image as PILImage
            pil_img = PILImage.open(image_path)
            img_width, img_height = pil_img.size
            aspect_ratio = img_width / img_height

            # Calculate dimensions to fit within max bounds while preserving aspect ratio
            if aspect_ratio > (max_image_width / max_image_height):
                # Image is wider - fit to width
                final_width = max_image_width
                final_height = max_image_width / aspect_ratio
            else:
                # Image is taller - fit to height
                final_height = max_image_height
                final_width = max_image_height * aspect_ratio

            # Add image with border
            img = Image(image_path, width=final_width, height=final_height)

            # Image with decorative border
            border_table = Table(
                [[img]],
                colWidths=[final_width + 10],  # Add padding
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 2, self.color_border),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ])
            )

            # Wrap in outer table for centering on page
            centered_image = Table(
                [[border_table]],
                colWidths=[self.page_width - self.margin_left - self.margin_right],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ])
            )

            elements.append(centered_image)
            elements.append(Spacer(1, 0.5 * cm))

        # Text box with frame info
        text_box = self._create_text_box(frame)
        elements.append(text_box)

        return elements

    def _create_text_box(self, frame: Dict[str, Any]) -> Table:
        """Create styled text box with frame information"""

        styles = getSampleStyleSheet()

        # Description style
        desc_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.color_text,
            alignment=TA_LEFT,
            leading=16,
            fontName=self.font_regular
        )

        # Dialogue style (italic, slightly different color)
        dialogue_style = ParagraphStyle(
            'Dialogue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.color_secondary,
            alignment=TA_LEFT,
            leading=14,
            fontName=self.font_italic,
            leftIndent=10
        )

        # Setting style (smaller, muted)
        setting_style = ParagraphStyle(
            'Setting',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT,
            leading=12,
            fontName=self.font_regular
        )

        # Build text content
        text_elements = []

        # Description
        description = frame.get('description', '')
        if description:
            text_elements.append(Paragraph(f"<b>Description:</b> {description}", desc_style))
            text_elements.append(Spacer(1, 0.2 * cm))

        # Dialogue (if exists)
        dialogue = frame.get('dialogue', '')
        if dialogue and dialogue != 'N/A':
            text_elements.append(Paragraph(f'<i>"{dialogue}"</i>', dialogue_style))
            text_elements.append(Spacer(1, 0.2 * cm))

        # Setting and shot type
        setting = frame.get('setting', '')
        shot_type = frame.get('shot_type', '')

        setting_text = []
        if setting:
            setting_text.append(f"<b>Setting:</b> {setting}")
        if shot_type:
            setting_text.append(f"<b>Shot:</b> {shot_type}")

        if setting_text:
            text_elements.append(Paragraph(" | ".join(setting_text), setting_style))

        # Create table with one row per text element
        table_data = [[elem] for elem in text_elements]

        # Create table for text box
        text_table = Table(
            table_data,
            colWidths=[self.page_width - self.margin_left - self.margin_right - 2*cm],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.color_background),
                ('BOX', (0, 0), (-1, -1), 1, self.color_border),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ])
        )

        return text_table

    def _create_decorative_line(self) -> Table:
        """Create decorative horizontal line"""
        line_width = 8 * cm

        line_table = Table(
            [['']],
            colWidths=[line_width],
            rowHeights=[0.1 * cm],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.color_primary),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ])
        )

        # Center the line
        centered_table = Table(
            [[line_table]],
            colWidths=[self.page_width - self.margin_left - self.margin_right],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ])
        )

        return centered_table

    def _add_page_decoration(self, canvas_obj, doc):
        """Add decorative elements to page (header/footer)"""

        canvas_obj.saveState()

        # Footer with page number
        page_num = canvas_obj.getPageNumber()
        footer_text = f"Алдар Көсе - Page {page_num}"

        canvas_obj.setFont(self.font_regular, 9)
        canvas_obj.setFillColor(self.color_text)
        canvas_obj.drawCentredString(
            self.page_width / 2,
            1 * cm,
            footer_text
        )

        # Decorative corner elements (optional)
        canvas_obj.setStrokeColor(self.color_primary)
        canvas_obj.setLineWidth(1)

        # Top-left corner
        canvas_obj.line(1*cm, self.page_height - 1*cm, 2*cm, self.page_height - 1*cm)
        canvas_obj.line(1*cm, self.page_height - 1*cm, 1*cm, self.page_height - 2*cm)

        # Top-right corner
        canvas_obj.line(self.page_width - 1*cm, self.page_height - 1*cm,
                       self.page_width - 2*cm, self.page_height - 1*cm)
        canvas_obj.line(self.page_width - 1*cm, self.page_height - 1*cm,
                       self.page_width - 1*cm, self.page_height - 2*cm)

        canvas_obj.restoreState()


# Export function for easy use
def export_to_pdf(storyboard_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Export storyboard to PDF

    Args:
        storyboard_data: Storyboard data dict
        output_path: Optional custom output path

    Returns:
        Path to generated PDF
    """

    if output_path is None:
        # Auto-generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'static/exports/aldar_kose_storyboard_{timestamp}.pdf'

    exporter = StoryboardPDFExporter()
    return exporter.export_storyboard(storyboard_data, output_path)
