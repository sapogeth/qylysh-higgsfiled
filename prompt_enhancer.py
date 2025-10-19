"""
Prompt Enhancement System for Aldar Köse Storyboard Generator
Transforms GPT-4 frame descriptions into optimized SDXL prompts with character consistency
"""

import json
from pathlib import Path
from typing import Dict, Any
import config

# Import CLIP tokenizer for accurate token counting
try:
    from transformers import CLIPTokenizer
    TOKENIZER = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
    TOKENIZER_AVAILABLE = True
except Exception as e:
    print(f"Warning: CLIP tokenizer not available: {e}")
    TOKENIZER = None
    TOKENIZER_AVAILABLE = False


class PromptEnhancer:
    """Enhances storyboard frame descriptions for optimal SDXL image generation"""

    def __init__(self):
        """Initialize the prompt enhancer with character details"""

        # Load character configuration
        self.character_config = self._load_character_config()

        # CLIP token limit
        self.MAX_TOKENS = 75  # Safe limit (CLIP allows 77, but we use 75 for safety)

        # Shot type mappings to visual descriptions (short forms)
        self.shot_type_prompts = {
            'establishing': 'wide landscape',
            'wide': 'full body',
            'medium': 'waist-up',
            'two-shot': 'two people',
            'close-up': 'face portrait',
            'over-shoulder': 'over shoulder'
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

    def _count_tokens(self, text: str) -> int:
        """
        Count the number of CLIP tokens in a text string

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens
        """
        if TOKENIZER_AVAILABLE and TOKENIZER is not None:
            tokens = TOKENIZER.encode(text, add_special_tokens=False)
            return len(tokens)
        else:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4

    def _truncate_to_token_limit(self, text: str, max_tokens: int = None) -> str:
        """
        Truncate text to fit within token limit

        Args:
            text: The text to truncate
            max_tokens: Maximum number of tokens (defaults to self.MAX_TOKENS)

        Returns:
            Truncated text that fits within token limit
        """
        if max_tokens is None:
            max_tokens = self.MAX_TOKENS

        if not TOKENIZER_AVAILABLE or TOKENIZER is None:
            # Fallback: character-based truncation
            max_chars = max_tokens * 4
            return text[:max_chars]

        # Tokenize the text
        tokens = TOKENIZER.encode(text, add_special_tokens=False)

        # If already within limit, return as is
        if len(tokens) <= max_tokens:
            return text

        # Truncate tokens and decode back
        truncated_tokens = tokens[:max_tokens]
        truncated_text = TOKENIZER.decode(truncated_tokens)

        return truncated_text

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
        Keeps prompt under 75 tokens for CLIP compatibility

        Args:
            frame: Dictionary containing frame details (description, shot_type, setting, etc.)

        Returns:
            Enhanced prompt string optimized for SDXL (under 75 tokens)
        """

        # Extract frame details
        description = frame.get('description', '')
        shot_type = frame.get('shot_type', 'medium')
        setting = frame.get('setting', 'Kazakh steppe')

        # Detect if text is non-English (Cyrillic/Kazakh takes 2-3x more tokens)
        is_non_english = self._is_non_english(description)

        # For non-English text, use MUCH simpler prompts
        if is_non_english:
            # Translate key elements to English for SDXL
            core_scene = self._translate_to_english_description(description)
            ct = config.CHARACTER_TRAITS
            character = (
                f"Aldar Kose, {ct['eye_color']} eyes, {ct['hair']}, {ct['facial_hair']}, "
                f"wearing {ct['clothing']} and {ct['hat']}"
            )
            style = (
                "2D cel-shaded anime-style, smooth clean outlines, flat colors, soft shadows, warm palette, Kazakh folk art"
            )

            # Very concise for non-English, but still enforce consistency
            prompt_parts = [core_scene, character, style, config.STYLE_LOCK]
            current_prompt = ", ".join(prompt_parts)
        else:
            # English text - use full enhancement
            # 1. ESSENTIAL: Core scene description (most important)
            core_scene = self._simplify_description(description)

            # 2. ESSENTIAL: Character identification (compact)
            # Inject consistent character traits
            ct = config.CHARACTER_TRAITS
            character = (
                f"Aldar Kose, {ct['eye_color']} eyes, {ct['hair']}, {ct['facial_hair']}, "
                f"wearing {ct['clothing']} and {ct['hat']}"
            )

            # 3. ESSENTIAL: Visual style (compact)
            style = (
                "2D cel-shaded anime-style, smooth clean outlines, flat colors, soft shadows, warm palette, Kazakh folk art"
            )

            # 4. OPTIONAL: Shot type (if space allows)
            shot = self.shot_type_prompts.get(shot_type, 'medium')

            # 5. OPTIONAL: Setting (if space allows)
            setting_brief = self._simplify_setting(setting)

            # 6. OPTIONAL: Quality tags (if space allows)
            # Style lock to enforce consistent look
            quality = f"masterpiece, clean lines, {config.STYLE_LOCK}"

            # Build prompt with priority order
            # Start with essentials
            prompt_parts = [core_scene, character, style]
            current_prompt = ", ".join(prompt_parts)

            # Add optional parts if they fit
            for optional_part in [shot, setting_brief, quality]:
                test_prompt = current_prompt + ", " + optional_part
                token_count = self._count_tokens(test_prompt)

                if token_count <= self.MAX_TOKENS:
                    current_prompt = test_prompt
                else:
                    # If we can't add more, stop here
                    break

        # Clean up the prompt
        enhanced_prompt = self._clean_prompt(current_prompt)

        # Final safety check - truncate if still over limit
        final_token_count = self._count_tokens(enhanced_prompt)
        if final_token_count > self.MAX_TOKENS:
            print(f"⚠️  Prompt has {final_token_count} tokens, truncating to {self.MAX_TOKENS} tokens")
            enhanced_prompt = self._truncate_to_token_limit(enhanced_prompt, self.MAX_TOKENS)
            # Re-clean after truncation
            enhanced_prompt = self._clean_prompt(enhanced_prompt)
            print(f"✓ Truncated prompt: {enhanced_prompt}")

        return enhanced_prompt

    def _is_non_english(self, text: str) -> bool:
        """
        Detect if text contains non-English characters (Cyrillic, etc.)

        Args:
            text: Text to check

        Returns:
            True if text contains non-English characters
        """
        # Check for Cyrillic characters (Kazakh, Russian, etc.)
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        return cyrillic_chars > len(text) * 0.3  # If 30%+ Cyrillic, treat as non-English

    def _translate_to_english_description(self, description: str) -> str:
        """
        Extract visual concepts from non-English description
        Use simple English keywords that SDXL understands well

        Args:
            description: Original description (any language)

        Returns:
            Simple English visual description
        """
        # Common Kazakh story elements mapped to English
        keywords = {
            'жәрмеңке': 'marketplace',
            'базар': 'market',
            'ауыл': 'village',
            'дала': 'steppe',
            'шапан': 'robe',
            'тымақ': 'hat',
            'бай': 'rich man',
            'қой': 'sheep',
            'ат': 'horse',
            'киіз үй': 'yurt',
            'көше': 'street',
            'адам': 'person',
            'адамдар': 'people',
        }

        # Extract English keywords from description
        english_parts = []
        description_lower = description.lower()

        for kazakh, english in keywords.items():
            if kazakh in description_lower:
                english_parts.append(english)

        # If we found keywords, use them
        if english_parts:
            # Limit to first 3 keywords to stay under token limit
            return ", ".join(english_parts[:3])

        # Fallback: generic scene
        return "Kazakh folk scene"

    def _simplify_description(self, description: str) -> str:
        """
        Simplify a long description to essential visual elements

        Args:
            description: Original description

        Returns:
            Simplified description
        """
        # Remove filler words and keep key visual elements
        filler_words = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had']

        # Split into words
        words = description.split()

        # If description is already short, return as is
        if len(words) <= 15:
            return description

        # Keep first 15 words (usually contains the core action/scene)
        simplified = ' '.join(words[:15])

        return simplified

    def _simplify_setting(self, setting: str) -> str:
        """
        Simplify setting to just the location (remove time of day)

        Args:
            setting: Full setting description

        Returns:
            Simplified setting
        """
        # Remove time indicators
        setting_parts = setting.split(' at ')
        location = setting_parts[0]

        # Further simplify if needed
        location = location.replace('traditional ', '').replace('typical ', '')

        return location

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
