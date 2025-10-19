#!/usr/bin/env python3
"""
Test the fixes:
1. No white background/borders
2. Consistent style throughout (no "cartoon drift")
"""

from prompt_enhancer import PromptEnhancer
import config

# Test prompt enhancer with our fixes
enhancer = PromptEnhancer()

# Test frames (simulate beginning, middle, end of story)
test_frames = [
    {
        "description": "Aldar Köse arrives at a bustling village marketplace",
        "shot_type": "establishing",
        "setting": "Kazakh village marketplace at midday",
    },
    {
        "description": "Aldar Köse talks with a greedy merchant",
        "shot_type": "medium",
        "setting": "Village marketplace",
    },
    {
        "description": "Aldar Köse smiles cleverly as he walks away",
        "shot_type": "close-up",
        "setting": "Village street",
    }
]

print("=" * 80)
print("TESTING FIXES FOR:")
print("1. White background/borders")
print("2. Style consistency (no cartoon drift)")
print("=" * 80)
print()

for i, frame in enumerate(test_frames, 1):
    print(f"Frame {i}: {frame['description']}")
    print("-" * 80)

    enhanced = enhancer.enhance(frame)
    negative = enhancer.get_negative_prompt()

    print(f"\nPositive prompt ({enhancer._count_tokens(enhanced)} tokens):")
    print(enhanced)

    print(f"\nNegative prompt ({enhancer._count_tokens(negative)} tokens):")
    print(negative)

    # Check for fixes
    print("\n✓ Checks:")
    print(f"  - 'no white borders' in prompt: {'no white borders' in enhanced}")
    print(f"  - 'white background' in negative: {'white background' in negative}")
    print(f"  - 'IMPORTANT' in STYLE_LOCK: {'IMPORTANT' in config.STYLE_LOCK}")
    print(f"  - 'NO style drift' in STYLE_LOCK: {'NO style drift' in config.STYLE_LOCK}")
    print(f"  - 'overly cartoonish' in negative: {'overly cartoonish' in negative}")

    print("\n" + "=" * 80 + "\n")

print("✓ All frames tested!")
print("\nKey improvements:")
print("1. Added 'white background, white borders, white frame' to NEGATIVE_PROMPT")
print("2. Added 'full scene composition, no white borders' to positive prompts")
print("3. Strengthened STYLE_LOCK with 'IMPORTANT: maintain exact same style'")
print("4. Added 'overly cartoonish, chibi style' to NEGATIVE_PROMPT")
print("5. Added 'NO style drift' to STYLE_LOCK")
