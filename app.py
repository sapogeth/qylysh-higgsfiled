"""
Aldar Köse Storyboard Generator - Web Application
Generates visual storyboards from any user prompt, automatically featuring the Kazakh legend Aldar Köse
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from storyboard_generator import StoryboardGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure output directories exist
os.makedirs('static/generated', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize the storyboard generator
generator = StoryboardGenerator()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_storyboard():
    """
    Generate storyboard from user prompt
    Expects JSON: {"prompt": "user's story idea"}
    Returns JSON with storyboard frames
    """
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()

        if not user_prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400

        # Generate storyboard (automatically includes Aldar Köse)
        result = generator.generate(user_prompt)

        return jsonify({
            'success': True,
            'storyboard': result['storyboard'],
            'metadata': result['metadata']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/static/generated/<path:filename>')
def serve_generated_image(filename):
    """Serve generated images"""
    return send_from_directory('static/generated', filename)


if __name__ == '__main__':
    # Use port 8080 to avoid conflict with macOS AirPlay Receiver on port 5000
    port = 8080
    print("=" * 70)
    print("ALDAR KÖSE STORYBOARD GENERATOR")
    print("=" * 70)
    print()
    print("✓ Using LOCAL Stable Diffusion XL for image generation")
    print("✓ Character consistency based on reference images")
    print("✓ Optimized for M1 MacBook Air")
    print()
    print("📝 Note: Model will load on first generation request (~1-2 min)")
    print("    Subsequent generations will be much faster (30-60 sec)")
    print()
    print("=" * 70)
    print(f"🚀 Server starting on http://localhost:{port}")
    print("=" * 70)
    print()
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
