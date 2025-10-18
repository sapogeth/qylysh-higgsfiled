#!/usr/bin/env python3
"""
Test prompt token length to ensure it stays under 77 tokens
"""

from prompt_enhancer import PromptEnhancer

# Initialize
enhancer = PromptEnhancer()

# Use character-based estimate (1 token ≈ 4 characters for English)
encoding = None

# Test frames
test_frames = [
    {
        'description': 'Aldar Köse walks across the vast golden steppe under a wide sky',
        'shot_type': 'establishing',
        'setting': 'Kazakh steppe at sunrise',
        'key_objects': ['steppe', 'grass', 'sky', 'horizon'],
        'lighting_hint': 'sunlight from the left, warm daylight, soft shadows'
    },
    {
        'description': 'Aldar Köse, in his traditional chapan and felt hat, surveys the endless steppe as a new adventure begins',
        'shot_type': 'medium',
        'setting': 'Outside a merchant\'s yurt',
        'key_objects': ['face', 'hands', 'hat', 'expression'],
        'lighting_hint': 'sunlight from the left, warm daylight, soft shadows'
    },
    {
        'description': 'Close view of Aldar\'s knowing smile as he devises a clever solution to outwit injustice',
        'shot_type': 'close-up',
        'setting': 'Village marketplace at afternoon',
        'key_objects': ['goods', 'people', 'carpet', 'bread'],
        'lighting_hint': 'sunlight from the left, warm daylight, soft shadows'
    }
]

print("=" * 70)
print("TESTING PROMPT TOKEN LENGTH (CLIP Limit: 77 tokens)")
print("=" * 70)
print()

for idx, frame in enumerate(test_frames, 1):
    print(f"Test {idx}:")
    print(f"  Description: {frame['description'][:50]}...")
    print()

    # Generate enhanced prompt
    enhanced = enhancer.enhance(frame)

    # Count tokens
    if encoding:
        tokens = encoding.encode(enhanced)
        token_count = len(tokens)
    else:
        # Rough estimate: 1 token ≈ 4 characters
        token_count = len(enhanced) // 4

    # Display results
    print(f"  Enhanced Prompt ({len(enhanced)} chars, ~{token_count} tokens):")
    print(f"  {enhanced}")
    print()

    # Check if under limit
    if token_count <= 77:
        print(f"  ✓ PASS - Under 77 token limit")
    else:
        print(f"  ❌ FAIL - Exceeds 77 token limit by {token_count - 77} tokens")

    print()
    print("-" * 70)
    print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
