"""
Simple test script to verify the storyboard generator works
Run this before starting the web server to test the core functionality
"""

import os
from dotenv import load_dotenv
from storyboard_generator import StoryboardGenerator

def test_generator():
    """Test the storyboard generator with a simple prompt"""

    print("=" * 60)
    print("Testing Aldar Köse Storyboard Generator")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️  WARNING: OpenAI API key not configured!")
        print("The generator will work with fallback/placeholder mode.")
        print()
        print("To use full AI generation:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key")
        print("3. Get key from: https://platform.openai.com/api-keys")
        print()
        use_api = False
    else:
        print("✓ OpenAI API key found")
        use_api = True

    print()
    print("-" * 60)
    print("Test 1: Creating Aldar Köse story from user prompt")
    print("-" * 60)

    # Initialize generator
    generator = StoryboardGenerator()

    # Test prompt
    test_prompt = "A greedy merchant learns about sharing"
    print(f"Input: {test_prompt}")
    print()

    # Generate story
    aldar_story = generator._create_aldar_story(test_prompt)
    print(f"Aldar Köse Story:\n{aldar_story}")
    print()

    print("-" * 60)
    print("Test 2: Generating storyboard frames")
    print("-" * 60)

    # Generate frames
    frames = generator._generate_frames(aldar_story)
    print(f"Generated {len(frames)} frames")
    print()

    # Show first frame
    if frames:
        print("Sample Frame (Frame 1):")
        frame = frames[0]
        print(f"  Rhyme: {frame.get('rhyme', 'N/A')}")
        print(f"  Moral: {frame.get('moral', 'N/A')}")
        print(f"  Shot: {frame.get('shot_type', 'N/A')}")
        print(f"  Setting: {frame.get('setting', 'N/A')}")
        print(f"  Description: {frame.get('description', 'N/A')}")
        print()

    print("-" * 60)
    print("Test 3: Checking image generation capability")
    print("-" * 60)

    if use_api:
        print("✓ API key configured - will generate real images")
    else:
        print("⚠️  No API key - will generate placeholder images")

    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python app.py")
    print("2. Visit: http://localhost:5000")
    print("3. Enter any story prompt and see Aldar Köse in action!")
    print()

if __name__ == '__main__':
    test_generator()
