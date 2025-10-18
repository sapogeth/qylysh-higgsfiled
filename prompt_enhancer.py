"""
Prompt Enhancement System for Aldar Köse Storyboard Generator
Transforms GPT-4 frame descriptions into optimized SDXL prompts with character consistency
"""

import json
from pathlib import Path
from typing import Dict, Any
import config


class PromptEnhancer:
    """Enhances storyboard frame descriptions for optimal SDXL image generation"""

    def __init__(self):
        """Initialize the prompt enhancer with character details"""

        # Load character configuration
        self.character_config = self._load_character_config()

        # Shot type mappings to visual descriptions
        self.shot_type_prompts = {
            'establishing': 'wide establishing shot, panoramic view, showing full scene and environment',
            'wide': 'wide shot, full body visible, showing character and surroundings',
            'medium': 'medium shot, waist-up view, showing upper body and facial expression',
            'two-shot': 'two-shot composition, two characters in frame, conversational framing',
            'close-up': 'close-up portrait, face and shoulders, detailed facial expression',
            'over-shoulder': 'over-shoulder shot, view from behind one character looking at another'
        }

        # Kazakh cultural elements to emphasize
        self.cultural_keywords = [
            'traditional Kazakh',
            'folk art style',
            'ornamental patterns',
            'steppe landscape',
            'yurt',
            'dombra',
            'chapan robe',
            'felt hat',
            'warm earthy colors',
            'cultural authenticity'
        ]

    def _load_character_config(self) -> Dict:
        """Load character configuration from JSON file"""
        config_path = config.MODELS_DIR / "aldar_character_config.json"

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Fallback default configuration
            return {
                "trigger_word": config.LORA_TRIGGER_WORD,
                "description": config.TRAINING_CAPTION,
                "appearance": {
                    "clothing": "orange patterned chapan robe with traditional Kazakh ornaments",
                    "hairstyle": "small topknot hairstyle, black hair",
                    "face": "round friendly face, warm smile, narrow eyes, warm skin tone",
                    "proportions": "simplified cartoon proportions",
                    "style": "2D storybook illustration"
                }
            }

    def enhance(self, frame: Dict[str, Any]) -> str:
        """
        Enhance a frame description into an optimized SDXL prompt
        Keeps prompt under 77 tokens for CLIP compatibility

        Args:
            frame: Dictionary containing frame details (description, shot_type, setting, etc.)

        Returns:
            Enhanced prompt string optimized for SDXL (under 77 tokens)
        """

        # Extract frame details
        description = frame.get('description', '')
        shot_type = frame.get('shot_type', 'medium')
        setting = frame.get('setting', 'Kazakh steppe')
        key_objects = frame.get('key_objects', [])

        # Build concise prompt components (optimized for 77 token limit)
        components = []

        # 1. Core scene (most important)
        # Shorten description to essential elements
        core_scene = description[:80] if len(description) > 80 else description
        components.append(core_scene)

        # 2. Character essentials (compact)
        components.append("Kazakh folk hero, orange chapan robe, topknot hair")

        # 3. Shot type (short form)
        shot_mapping = {
            'establishing': 'wide landscape',
            'wide': 'full body shot',
            'medium': 'waist-up',
            'two-shot': 'two characters',
            'close-up': 'face portrait',
            'over-shoulder': 'over shoulder view'
        }
        components.append(shot_mapping.get(shot_type, 'medium shot'))

        # 4. Setting (brief)
        components.append(setting.split(' at ')[0])  # Just location, not time

        # 5. Style (compact)
        components.append("2D storybook art, warm colors, Kazakh folk style")

        # 6. Quality (minimal)
        components.append("detailed, masterpiece")

        # Combine all components
        enhanced_prompt = ", ".join(components)

        # Clean up
        enhanced_prompt = self._clean_prompt(enhanced_prompt)

        # Final token check - if still too long, truncate intelligently
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = 77 * 4  # ~308 characters for safety
        if len(enhanced_prompt) > max_chars:
            # Keep first part (most important) and add style at end
            enhanced_prompt = enhanced_prompt[:max_chars-30] + ", storybook art, detailed"

        return enhanced_prompt

    def _clean_prompt(self, prompt: str) -> str:
        """Clean and optimize the prompt string"""

        # Remove multiple spaces
        prompt = " ".join(prompt.split())

        # Remove duplicate commas
        prompt = prompt.replace(",,", ",")

        # Ensure no leading/trailing commas
        prompt = prompt.strip(", ")

        return prompt

    def get_negative_prompt(self) -> str:
        """
        Get the negative prompt (what to avoid)

        Returns:
            Negative prompt string
        """
        return config.NEGATIVE_PROMPT

    def enhance_batch(self, frames: list[Dict[str, Any]]) -> list[Dict[str, str]]:
        """
        Enhance multiple frames at once

        Args:
            frames: List of frame dictionaries

        Returns:
            List of dictionaries with 'positive' and 'negative' prompts
        """

        enhanced_prompts = []

        for frame in frames:
            enhanced_prompts.append({
                'positive': self.enhance(frame),
                'negative': self.get_negative_prompt()
            })

        return enhanced_prompts

    def analyze_prompt_quality(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze the quality of a generated prompt

        Args:
            prompt: The prompt string to analyze

        Returns:
            Dictionary with quality metrics
        """

        metrics = {
            'length': len(prompt),
            'has_character_trigger': self.character_config['trigger_word'] in prompt.lower(),
            'has_style_keywords': any(keyword in prompt.lower() for keyword in ['illustration', 'storybook', '2d']),
            'has_cultural_elements': any(keyword in prompt.lower() for keyword in ['kazakh', 'chapan', 'steppe']),
            'has_lighting': 'light' in prompt.lower() or 'shadow' in prompt.lower(),
            'word_count': len(prompt.split()),
            'quality_score': 0.0
        }

        # Calculate quality score (0-100)
        score = 0

        if metrics['has_character_trigger']:
            score += 30
        if metrics['has_style_keywords']:
            score += 20
        if metrics['has_cultural_elements']:
            score += 20
        if metrics['has_lighting']:
            score += 10
        if 50 <= metrics['word_count'] <= 150:  # Optimal length
            score += 20

        metrics['quality_score'] = score

        return metrics

    def create_variation_prompt(self, base_frame: Dict[str, Any], variation_type: str = 'angle') -> str:
        """
        Create a variation of a frame prompt (useful for regeneration)

        Args:
            base_frame: Original frame dictionary
            variation_type: Type of variation ('angle', 'lighting', 'composition')

        Returns:
            Varied prompt string
        """

        # Get base enhanced prompt
        base_prompt = self.enhance(base_frame)

        # Add variation modifiers
        if variation_type == 'angle':
            variations = [
                "slightly different camera angle",
                "alternative perspective",
                "shifted viewpoint"
            ]
        elif variation_type == 'lighting':
            variations = [
                "softer lighting",
                "slightly different time of day",
                "warmer color temperature"
            ]
        elif variation_type == 'composition':
            variations = [
                "reframed composition",
                "adjusted framing",
                "alternative composition"
            ]
        else:
            variations = ["slight variation"]

        import random
        variation_modifier = random.choice(variations)

        varied_prompt = f"{base_prompt}, {variation_modifier}"

        return varied_prompt

    def extract_key_elements(self, description: str) -> Dict[str, list]:
        """
        Extract key visual elements from a description

        Args:
            description: Frame description text

        Returns:
            Dictionary with categorized elements
        """

        # Simple keyword extraction (can be enhanced with NLP)
        elements = {
            'characters': [],
            'objects': [],
            'locations': [],
            'actions': []
        }

        # Character keywords
        character_keywords = ['aldar', 'köse', 'merchant', 'villager', 'person', 'people', 'character']
        for keyword in character_keywords:
            if keyword.lower() in description.lower():
                elements['characters'].append(keyword)

        # Object keywords
        object_keywords = ['yurt', 'horse', 'dombra', 'bread', 'tea', 'carpet', 'hat', 'robe']
        for keyword in object_keywords:
            if keyword.lower() in description.lower():
                elements['objects'].append(keyword)

        # Location keywords
        location_keywords = ['steppe', 'village', 'marketplace', 'bazaar', 'road', 'path', 'yurt']
        for keyword in location_keywords:
            if keyword.lower() in description.lower():
                elements['locations'].append(keyword)

        # Action keywords (verbs)
        action_keywords = ['walk', 'ride', 'sit', 'stand', 'talk', 'smile', 'play', 'give', 'take']
        for keyword in action_keywords:
            if keyword.lower() in description.lower():
                elements['actions'].append(keyword)

        return elements


# Helper function for quick testing
def test_prompt_enhancer():
    """Test the prompt enhancer with sample frames"""

    enhancer = PromptEnhancer()

    # Sample frame
    sample_frame = {
        'description': 'Aldar Köse walks across the vast golden steppe under a wide sky',
        'shot_type': 'establishing',
        'setting': 'Kazakh steppe at sunrise',
        'key_objects': ['steppe', 'grass', 'sky', 'horizon'],
        'lighting_hint': 'sunlight from the left, warm daylight, soft shadows'
    }

    print("Sample Frame:")
    print(json.dumps(sample_frame, indent=2))
    print()

    enhanced = enhancer.enhance(sample_frame)
    print("Enhanced Prompt:")
    print(enhanced)
    print()

    negative = enhancer.get_negative_prompt()
    print("Negative Prompt:")
    print(negative)
    print()

    quality = enhancer.analyze_prompt_quality(enhanced)
    print("Quality Analysis:")
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    test_prompt_enhancer()
