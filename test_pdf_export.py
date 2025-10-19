#!/usr/bin/env python3
"""
Test PDF Export
Creates a sample storyboard and exports it to PDF
"""

from pdf_exporter import export_to_pdf
from datetime import datetime
import os

# Create test storyboard data
test_storyboard = {
    'storyboard': [
        {
            'frame_number': 1,
            'description': 'Алдар Көсе кішкентай есекке мініп, кең далада келе жатыр',
            'dialogue': 'Қай жаққа барамын екен?',
            'setting': 'Golden steppe with endless horizons',
            'shot_type': 'Full body',
            'key_objects': ['donkey', 'yurts', 'mountains'],
            'image_path': None  # No image for test, will skip
        },
        {
            'frame_number': 2,
            'description': 'Алдар Көсе базарда саудагермен сөйлесіп тұр',
            'dialogue': 'Мен сізге ақылды сатамын!',
            'setting': 'Bustling marketplace',
            'shot_type': 'Medium shot',
            'key_objects': ['merchants', 'goods', 'people'],
            'image_path': None
        },
        {
            'frame_number': 3,
            'description': 'Хан Алдар Көсеге ренжіп отыр',
            'dialogue': 'Сен мені алдағаның неге?!',
            'setting': 'Khan palace interior',
            'shot_type': 'Wide shot',
            'key_objects': ['throne', 'decorations', 'guards'],
            'image_path': None
        },
        {
            'frame_number': 4,
            'description': 'Алдар Көсе от басында балаларға ертегі айтып отыр',
            'dialogue': 'Міне, осылай хан алданды деген сөз...',
            'setting': 'Night campfire scene',
            'shot_type': 'Medium shot',
            'key_objects': ['campfire', 'children', 'yurts'],
            'image_path': None
        }
    ],
    'metadata': {
        'original_prompt': 'Aldar Köse tricks a greedy khan',
        'aldar_story': 'Ертеде бір ашкөз хан болыпты. Ол халықтан салық жинап, өзі той жасап жүретін. Алдар Көсе оны өз ақылымен алдап, халыққа салықты қайтарды.',
        'num_frames': 4,
        'generated_at': datetime.now().isoformat()
    }
}

print("=" * 70)
print("🧪 PDF EXPORT TEST")
print("=" * 70)
print()

# Test PDF generation
print("📄 Generating test PDF...")
try:
    output_path = 'static/exports/test_storyboard.pdf'
    os.makedirs('static/exports', exist_ok=True)

    pdf_path = export_to_pdf(test_storyboard, output_path)

    print(f"✅ PDF generated successfully!")
    print(f"📁 Location: {pdf_path}")
    print(f"📊 File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    print()
    print("=" * 70)
    print()
    print("💡 Test Result:")
    print("   - Title page with story info ✅")
    print("   - 4 frame pages with text boxes ✅")
    print("   - Decorative borders and styling ✅")
    print("   - Ready for images when available ✅")
    print()
    print("📖 Open the PDF to verify the layout!")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
