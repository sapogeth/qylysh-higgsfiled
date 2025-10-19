#!/usr/bin/env python3
"""
Test PDF export with Cyrillic text
"""

from pdf_exporter import export_to_pdf
from datetime import datetime

# Test data with Cyrillic/Kazakh text
test_storyboard = {
    "metadata": {
        "original_prompt": "Алдар Көсе обманывает жадного бая",
        "aldar_story": "Алдар Көсе - знаменитый казахский народный герой, известный своей хитростью и умом. В этой истории он учит жадного бая щедрости.",
        "num_frames": 2,
        "generated_at": datetime.now().isoformat()
    },
    "storyboard": [
        {
            "description": "Алдар Көсе приходит в аул богатого бая",
            "dialogue": "Сәлеметсіз бе, ханым!",
            "setting": "Казахский аул, юрта бая",
            "shot_type": "Medium shot",
            "image_path": None
        },
        {
            "description": "Бай удивлённо смотрит на Алдара",
            "dialogue": "Что ты хочешь, бродяга?",
            "setting": "Внутри юрты",
            "shot_type": "Close-up",
            "image_path": None
        }
    ]
}

# Export to PDF
output_path = "static/exports/test_cyrillic.pdf"
result = export_to_pdf(test_storyboard, output_path)
print(f"✓ PDF exported successfully: {result}")
print("\nOpen the PDF to verify Cyrillic text appears correctly!")
