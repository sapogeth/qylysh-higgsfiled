#!/usr/bin/env python3
"""
Quick test script for local image generation
Tests the full pipeline without needing the web interface
"""

from storyboard_generator import StoryboardGenerator
import json

print("=" * 70)
print("TESTING LOCAL ALDAR KÖSE STORYBOARD GENERATION")
print("=" * 70)
print()

# Create generator
print("Initializing generator...")
generator = StoryboardGenerator()
print("✓ Generator initialized")
print()

# Test prompt
test_prompt = "A greedy merchant learns about sharing"
print(f"Test prompt: '{test_prompt}'")
print()

# Generate storyboard
print("Starting generation...")
print("(This will take 1-2 min on first run to download SDXL model)")
print()

try:
    result = generator.generate(test_prompt)

    print()
    print("=" * 70)
    print("GENERATION COMPLETE!")
    print("=" * 70)
    print()

    print("Story:")
    print(result['metadata']['aldar_story'])
    print()

    print(f"Generated {result['metadata']['num_frames']} frames:")
    print()

    for idx, frame in enumerate(result['storyboard'], 1):
        print(f"Frame {idx}:")
        print(f"  Rhyme: {frame.get('rhyme', 'N/A')}")
        print(f"  Description: {frame.get('description', 'N/A')}")
        print(f"  Image: {frame.get('image_url', 'N/A')}")
        print()

    print("=" * 70)
    print("✓ TEST PASSED!")
    print("=" * 70)
    print()
    print("Your system is working correctly!")
    print("You can now run: python3 app.py")
    print()

except Exception as e:
    print()
    print("=" * 70)
    print("❌ TEST FAILED")
    print("=" * 70)
    print()
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check that your OpenAI API key is valid and has credits")
    print("2. Ensure you have enough disk space (~10GB)")
    print("3. Check your internet connection")
    print()
    import traceback
    traceback.print_exc()
