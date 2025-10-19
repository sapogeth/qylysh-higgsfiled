"""
Storyboard Generator - Core Logic
Automatically injects Aldar Köse into any user prompt and generates storyboard frames
Uses local SDXL for high-quality image generation with character consistency
"""

import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import openai
from dotenv import load_dotenv

# Import local generation modules
try:
    from local_image_generator import LocalImageGenerator
    from quality_validator import QualityValidator
    import config
    LOCAL_GENERATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Local generation not available: {e}")
    print("   Falling back to DALL-E (if API key is available)")
    LOCAL_GENERATION_AVAILABLE = False

load_dotenv()


class StoryboardGenerator:
    """Generates Aldar Köse storyboards from any user prompt"""

    def __init__(self, progress_callback: Optional[Callable] = None, use_local: bool = True):
        """
        Initialize storyboard generator

        Args:
            progress_callback: Optional callback for progress updates
            use_local: Use local SDXL generation (True) or DALL-E (False)
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key

        self.progress_callback = progress_callback
        self.use_local = use_local and LOCAL_GENERATION_AVAILABLE

        # Initialize local generator if available
        self.local_generator = None
        self.quality_validator = None

        if self.use_local:
            try:
                self.local_generator = LocalImageGenerator(progress_callback=progress_callback)
                self.quality_validator = QualityValidator()
                print("✓ Using local SDXL image generation")
            except Exception as e:
                print(f"⚠️  Local generation failed to initialize: {e}")
                print("   Falling back to DALL-E")
                self.use_local = False

        # Aldar Köse character description (consistent across all frames)
        self.character_description = (
            "Aldar Köse, the clever Kazakh folk hero, wearing traditional Kazakh chapan robe, "
            "felt kalpak hat, with a distinctive mustache and friendly, mischievous expression"
        )

        # Available morals for Kazakh folk tales
        self.morals = ['kindness', 'justice', 'hospitality', 'wisdom', 'courage', 'generosity']

        # Available shot types
        self.shot_types = ['establishing', 'wide', 'medium', 'two-shot', 'close-up', 'over-shoulder']

    def generate(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate storyboard from user prompt
        Automatically creates an Aldar Köse story from any input
        """
        # Step 1: Create Aldar Köse story from user prompt
        aldar_story = self._create_aldar_story(user_prompt)

        # Step 2: Generate storyboard frames
        frames = self._generate_frames(aldar_story)

        # Step 3: Generate images for each frame
        frames_with_images = self._generate_images(frames)

        return {
            'storyboard': frames_with_images,
            'metadata': {
                'original_prompt': user_prompt,
                'aldar_story': aldar_story,
                'num_frames': len(frames_with_images),
                'generated_at': datetime.now().isoformat()
            }
        }

    def _create_aldar_story(self, user_prompt: str) -> str:
        """Convert any user prompt into an Aldar Köse story"""

        if not self.api_key:
            # Fallback: Manual injection
            return f"Алдар Көсе {user_prompt}"

        try:
            # Use GPT to create a proper Aldar Köse story
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=config.GPT_MODEL if LOCAL_GENERATION_AVAILABLE else "gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Kazakh folklore expert. "
                            "Transform any user input into a short Aldar Köse story (2-4 sentences). "
                            "Aldar Köse is a clever, witty, generous Kazakh folk hero who uses his intelligence "
                            "to help people, teach lessons, and outsmart the greedy or unjust. "
                            "Keep the story culturally authentic with Kazakh settings (steppe, yurts, bazaars). "
                            "Respond in the same language as the user's input (Kazakh, Russian, or English)."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Create an Aldar Köse story based on this idea: {user_prompt}"
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"GPT story creation failed: {e}")
            return f"Алдар Көсе {user_prompt}"

    def _generate_frames(self, story: str) -> List[Dict[str, Any]]:
        """Generate 6-10 storyboard frames from the story"""

        if not self.api_key:
            # Fallback: Template-based generation
            return self._generate_fallback_frames(story)

        try:
            # Use GPT to generate structured frames
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=config.GPT_MODEL if LOCAL_GENERATION_AVAILABLE else "gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_storyboard_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": story
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()

            # Extract JSON from response (in case there's extra text)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            frames = json.loads(content)
            return frames

        except Exception as e:
            print(f"GPT frame generation failed: {e}")
            return self._generate_fallback_frames(story)

    def _get_storyboard_system_prompt(self) -> str:
        """System prompt for GPT storyboard generation"""
        return """You are the Storyboard Planner for an Aldar Köse image generator.

GOAL:
Given any short story or description (2–4 sentences), create a coherent storyboard plan of 6–10 frames featuring the Kazakh folk hero Aldar Köse.
Each frame should describe one visual moment from the story, following the logic of a short animated sequence or children's picture book.

RESPONSE FORMAT:
Return ONLY a JSON array (no text before or after it) containing 6–10 objects.
Each object must have EXACTLY these 7 keys:

{
  "rhyme": "<one short rhymed line (max 100 characters, child-friendly)>",
  "moral": "<one of ['kindness','justice','hospitality','wisdom','courage','generosity']>",
  "shot_type": "<one of ['establishing','wide','medium','two-shot','close-up','over-shoulder']>",
  "setting": "<short phrase naming location and time, e.g., 'Kazakh steppe at sunrise'>",
  "key_objects": ["<3–5 nouns showing visual elements in the scene>"],
  "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
  "description": "<1–2 sentences (max 40 words) describing what is visually shown in this frame>"
}

REQUIREMENTS:
- Language: If the user's story is in Kazakh or Russian, generate all text in that same language; otherwise use English.
- Cultural respect: Aldar Köse is clever, generous, and witty. Keep his design consistent — Kazakh chapan robe, felt hat, mustache, and friendly expression.
- Include Kazakh elements such as yurts, dombra, tea, bread, steppe, etc.
- Do not repeat the same shot_type more than twice in a row.
- Keep lighting identical across all frames (use the exact string above for lighting_hint).
- Avoid any modern clothing, cars, or buildings unless the user's story specifically says so.
- The JSON must be valid and parseable — no comments, markdown, or text outside the array.

QUALITY HINTS:
- Ensure the story has a beginning → middle → end.
- Maintain emotional and visual continuity between frames.
- Keep Aldar Köse's appearance consistent throughout.

OUTPUT RULE:
Return ONLY the JSON array. No prose, no explanations."""

    def _generate_fallback_frames(self, story: str) -> List[Dict[str, Any]]:
        """Generate fallback frames when GPT is unavailable - more varied descriptions"""

        # Split story into sentences for better distribution
        story_parts = story.split('.')[:6]
        if not story_parts or story_parts[0].strip() == '':
            story_parts = [story[:100], story[100:200], story[200:]]

        # Diverse frame templates
        templates = [
            {
                "rhyme": "Aldar Köse walks the golden steppe with a smile",
                "moral": "wisdom",
                "shot_type": "establishing",
                "setting": "Vast Kazakh steppe at sunrise",
                "key_objects": ["steppe", "yurt", "horse", "sky"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"Aldar Köse, in his traditional chapan and felt hat, surveys the endless steppe as a new adventure begins."
            },
            {
                "rhyme": "A challenge appears before the clever hero",
                "moral": "courage",
                "shot_type": "two-shot",
                "setting": "Village entrance at midday",
                "key_objects": ["Aldar", "villager", "yurt", "path"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"Aldar Köse meets a troubled villager who seeks his wisdom and help."
            },
            {
                "rhyme": "With clever words he weaves his plan",
                "moral": "wisdom",
                "shot_type": "close-up",
                "setting": "Outside a merchant's yurt",
                "key_objects": ["face", "hands", "hat", "expression"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"Close view of Aldar's knowing smile as he devises a clever solution to outwit injustice."
            },
            {
                "rhyme": "The trickster teaches those who need to learn",
                "moral": "justice",
                "shot_type": "medium",
                "setting": "Marketplace at afternoon",
                "key_objects": ["goods", "people", "carpet", "bread"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"Aldar Köse demonstrates his plan, using wit rather than force to achieve justice."
            },
            {
                "rhyme": "Generosity flows from the lesson learned",
                "moral": "generosity",
                "shot_type": "wide",
                "setting": "Village square at late afternoon",
                "key_objects": ["crowd", "food", "celebration", "yurt"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"The greedy learn to share as Aldar's clever trick reveals the value of kindness."
            },
            {
                "rhyme": "Aldar rides away with wisdom shared",
                "moral": "hospitality",
                "shot_type": "wide",
                "setting": "Open steppe at dusk",
                "key_objects": ["horse", "steppe", "sunset", "horizon"],
                "lighting_hint": "sunlight from the left, warm daylight, soft shadows",
                "description": f"Aldar Köse departs on his horse, leaving behind a village changed by his clever wisdom and kindness."
            }
        ]

        # Return varied number of frames (6-8)
        num_frames = min(len(templates), random.randint(6, 8))
        return templates[:num_frames]

    def _generate_images(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate images for each frame using local SDXL or DALL-E fallback

        Args:
            frames: List of frame dictionaries

        Returns:
            Frames with added image information
        """

        if self.use_local and self.local_generator:
            # Use local parallel generation
            return self._generate_images_local(frames)
        else:
            # Fallback to DALL-E sequential generation
            return self._generate_images_dalle(frames)

    def _generate_images_local(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate images using local SDXL in parallel"""

        if self.progress_callback:
            self.progress_callback({
                'step': 'generating_images',
                'message': f'Generating {len(frames)} frames with local SDXL...',
                'current': 0,
                'total': len(frames)
            })

        try:
            # Generate all frames in parallel
            frames_with_images = self.local_generator.generate_from_frames(frames)

            # Validate quality and regenerate if needed
            if self.quality_validator and config.ENABLE_QUALITY_VALIDATION:
                frames_with_images = self._validate_and_regenerate(frames_with_images)

            return frames_with_images

        except Exception as e:
            print(f"❌ Local generation failed: {e}")
            print("   Falling back to DALL-E...")
            return self._generate_images_dalle(frames)

    def _validate_and_regenerate(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate image quality and regenerate poor images"""

        for idx, frame in enumerate(frames):
            if 'image' not in frame:
                continue

            # Validate image
            is_valid, metrics = self.quality_validator.validate(
                frame['image'],
                frame.get('description', '')
            )

            quality_score = self.quality_validator.get_quality_score(metrics)

            if not is_valid and config.MAX_REGENERATION_ATTEMPTS > 0:
                print(f"⚠️  Frame {idx + 1} quality too low ({quality_score:.1f}/100), regenerating...")

                # Regenerate with variation
                new_image = self.local_generator.regenerate_frame(frame, variation_type='composition')

                # Save regenerated image
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'frame_{idx + 1:03d}_{timestamp}_regen.png'
                filepath = config.OUTPUT_DIR / filename

                new_image.save(filepath, 'PNG', optimize=True)

                # Update frame
                frame['image'] = new_image
                frame['image_path'] = filepath
                frame['image_url'] = f'/static/generated/{filename}'
                frame['regenerated'] = True

                print(f"✓ Frame {idx + 1} regenerated successfully")

        return frames

    def _generate_images_dalle(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback: Generate images using DALL-E sequentially"""

        frames_with_images = []

        for idx, frame in enumerate(frames):
            frame_number = idx + 1

            if self.progress_callback:
                self.progress_callback({
                    'step': 'generating_images',
                    'message': f'Generating frame {frame_number} of {len(frames)} with DALL-E...',
                    'current': frame_number,
                    'total': len(frames)
                })

            # Build image prompt
            image_prompt = self._build_image_prompt(frame)

            # Generate image
            image_path = self._generate_single_image(image_prompt, frame_number)

            # Add image path to frame
            frame['image_url'] = f'/static/generated/{os.path.basename(image_path)}'
            frame['frame_number'] = frame_number

            frames_with_images.append(frame)

        return frames_with_images

    def _build_image_prompt(self, frame: Dict[str, Any]) -> str:
        """Build image prompt from frame description - optimized for both DALL-E and SDXL"""
        
        # Import config for consistency
        import config as _cfg
        
        # Core visual description (keep concise)
        description = frame['description']
        setting = frame['setting']
        shot_type = frame['shot_type']
        
        # Essential character traits (shortened)
        traits = _cfg.CHARACTER_TRAITS
        character = (
            f"Aldar Köse, {traits['eye_color']} eyes, {traits['hair']}, "
            f"{traits['facial_hair']}, wearing {traits['clothing']}"
        )
        
        # Compact style description
        style = (
            "2D cel-shaded anime style, smooth outlines, flat colors, "
            "soft shadows, warm palette, Kazakh folk art"
        )
        
        # Build prompt efficiently
        prompt = (
            f"{character}. "
            f"{description}. "
            f"Setting: {setting}. "
            f"Shot: {shot_type}. "
            f"{style}"
        )
        
        return prompt

    def _generate_single_image(self, prompt: str, frame_number: int) -> str:
        """Generate a single image using DALL-E 3"""

        output_dir = 'static/generated'
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f'frame_{frame_number:03d}_{timestamp}.png'
        image_path = os.path.join(output_dir, image_filename)

        if not self.api_key:
            # Create placeholder
            self._create_placeholder(image_path, frame_number)
            return image_path

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # Download and save image
            import requests
            image_url = response.data[0].url
            img_data = requests.get(image_url).content

            with open(image_path, 'wb') as f:
                f.write(img_data)

            print(f"Generated image {frame_number}: {image_filename}")
            return image_path

        except Exception as e:
            print(f"Image generation failed for frame {frame_number}: {e}")
            self._create_placeholder(image_path, frame_number)
            return image_path

    def _create_placeholder(self, image_path: str, frame_number: int):
        """Create a placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new('RGB', (1024, 1024), color=(240, 230, 200))
            draw = ImageDraw.Draw(img)

            # Draw text
            text = f"Frame {frame_number}\nAldar Köse\nStoryboard"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            position = ((1024 - text_width) // 2, (1024 - text_height) // 2)
            draw.text(position, text, fill=(100, 80, 60))

            img.save(image_path)

        except Exception as e:
            print(f"Placeholder creation failed: {e}")
