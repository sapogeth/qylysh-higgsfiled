"""
Aldar Köse Storyboard Generator - Web Application
Generates visual storyboards from any user prompt, automatically featuring the Kazakh legend Aldar Köse
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import os
import json
from datetime import datetime
from storyboard_generator import StoryboardGenerator
import config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure output directories exist
os.makedirs('static/generated', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize the storyboard generator
# Use local SDXL for image generation
generator = StoryboardGenerator(use_local=True)


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


@app.route('/api/generate/stream', methods=['POST'])
def generate_storyboard_stream():
    """
    Stream storyboard generation as NDJSON events so the UI can render
    each frame immediately when it's ready.

    Events (one JSON object per line):
      {"type":"story", "aldar_story": str, "total_frames": int}
      {"type":"frame", "frame": {..frame data..}, "index": i, "total": n}
      {"type":"complete", "success": true}
      {"type":"error", "message": str}
    """
    try:
        data = request.get_json(silent=True) or {}
        user_prompt = (data.get('prompt') or '').strip()

        if not user_prompt:
            # Return a single-line NDJSON error
            return Response(
                json.dumps({"type": "error", "message": "Prompt cannot be empty"}) + "\n",
                mimetype='application/x-ndjson',
                headers={"X-Accel-Buffering": "no"}
            )

        def ndjson_stream():
            try:
                # Step 1: story
                aldar_story = generator._create_aldar_story(user_prompt)
                # Step 2: frames (structure only)
                frames = generator._generate_frames(aldar_story)

                yield json.dumps({
                    "type": "story",
                    "aldar_story": aldar_story,
                    "total_frames": len(frames)
                }) + "\n"

                # Step 3: images per-frame
                # Check if identity lock is enabled in config
                local_gen = None
                ref_img = None
                
                if config.USE_IDENTITY_LOCK:
                    try:
                        # Try to import and initialize the local generator on-demand
                        from local_image_generator import LocalImageGenerator as _LocalGen
                        # Reuse existing if available; else create a fresh instance for this request
                        local_gen = getattr(generator, 'local_generator', None) or _LocalGen()

                        # Load reference image from project root (PNG files provided)
                        from PIL import Image as _Image
                        ref_path = os.path.join(os.getcwd(), config.IDENTITY_REFERENCE_IMAGE)
                        if os.path.exists(ref_path):
                            try:
                                ref_img = _Image.open(ref_path).convert('RGB')
                                print(f"✓ Using identity lock with {config.IDENTITY_REFERENCE_IMAGE} (scale={config.IP_ADAPTER_SCALE})")
                            except Exception as _e:
                                print(f"Failed to load reference image {ref_path}: {_e}")
                        else:
                            print(f"Reference image not found: {ref_path}")
                    except Exception as _e:
                        # Local stack not available; will fall back to API path below
                        print(f"Identity lock requested, but local generator unavailable: {_e}")

                for idx, frame in enumerate(frames):
                    frame_number = idx + 1

                    # Prefer local generation if identity lock is enabled and local generator is ready
                    if local_gen is not None:
                        # Local SDXL generation (LoRA will be applied automatically if present)
                        from datetime import datetime as _dt
                        
                        # Build base prompt
                        base_prompt = generator._build_image_prompt(frame)
                        
                        # Enhance prompt to fit within 75 token limit
                        # Use the enhancer to properly condense the prompt
                        enhanced_prompt = local_gen.enhancer.enhance(frame)
                        
                        # Generate with enhanced prompt
                        img = local_gen.generate_single(
                            prompt=enhanced_prompt,
                            ref_image=ref_img,
                            ip_adapter_scale=config.IP_ADAPTER_SCALE if ref_img is not None else None
                        )

                        # Save image
                        output_dir = 'static/generated'
                        os.makedirs(output_dir, exist_ok=True)
                        ts = _dt.now().strftime('%Y%m%d_%H%M%S')
                        filename = f'frame_{frame_number:03d}_{ts}.png'
                        image_path = os.path.join(output_dir, filename)
                        try:
                            img.save(image_path, 'PNG', optimize=True)
                        except Exception:
                            # Fallback save without optimize if pillow complains
                            img.save(image_path, 'PNG')
                    else:
                        # DALL·E (or placeholder) path
                        image_prompt = generator._build_image_prompt(frame)
                        image_path = generator._generate_single_image(image_prompt, frame_number)

                    # Emit event
                    frame['image_url'] = f"/static/generated/{os.path.basename(image_path)}"
                    frame['frame_number'] = frame_number

                    yield json.dumps({
                        "type": "frame",
                        "frame": frame,
                        "index": idx,
                        "total": len(frames)
                    }) + "\n"

                yield json.dumps({"type": "complete", "success": True}) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"

        resp = Response(ndjson_stream(), mimetype='application/x-ndjson')
        # Disable proxy buffering where applicable and allow CORS from same origin
        resp.headers['X-Accel-Buffering'] = 'no'
        resp.headers['Cache-Control'] = 'no-cache'
        resp.headers['Connection'] = 'keep-alive'
        return resp

    except Exception as e:
        # As a last resort, return a one-line error
        return Response(
            json.dumps({"type": "error", "message": str(e)}) + "\n",
            mimetype='application/x-ndjson',
            headers={"X-Accel-Buffering": "no"}
        )


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


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    # Use port 8080 to avoid conflict with macOS AirPlay Receiver on port 5000
    port = 8080
    print("=" * 70)
    print("ALDAR KÖSE STORYBOARD GENERATOR")
    print("=" * 70)
    print()
    # Print actual generation mode
    if getattr(generator, 'use_local', False):
        print("✓ Using LOCAL Stable Diffusion XL for image generation")
        print("✓ Character consistency based on reference images")
        print("✓ Optimized for M1 MacBook Air")
    else:
        if os.getenv('OPENAI_API_KEY'):
            print("✓ Using OpenAI DALL-E fallback for image generation")
            print("✓ No local model required; internet connection needed")
        else:
            print("✓ Using placeholder images (no OPENAI_API_KEY set)")
            print("✓ You can still test the storyboard flow and UI")
    print()
    print("📝 Note: Model will load on first generation request (~1-2 min)")
    print("    Subsequent generations will be much faster (30-60 sec)")
    print()
    print("=" * 70)
    print(f"🚀 Server starting on http://localhost:{port}")
    print("=" * 70)
    print()
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
