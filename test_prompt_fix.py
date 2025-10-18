"""
Test script to verify prompt length fix
Tests various prompt lengths to ensure they stay under 75 tokens
"""

from prompt_enhancer import PromptEnhancer


def test_prompt_lengths():
    """Test prompts of various lengths"""

    enhancer = PromptEnhancer()

    # Test cases with varying complexity
    test_frames = [
        {
            'name': 'Short prompt',
            'frame': {
                'description': 'Aldar walks across the steppe',
                'shot_type': 'wide',
                'setting': 'Kazakh steppe'
            }
        },
        {
            'name': 'Medium prompt',
            'frame': {
                'description': 'Aldar Köse stands in the bustling village marketplace, surrounded by merchants and villagers',
                'shot_type': 'medium',
                'setting': 'Village marketplace at midday'
            }
        },
        {
            'name': 'Long prompt (original problematic one)',
            'frame': {
                'description': 'Aldar Köse arrives at a bustling village marketplace filled with merchants and eager customers. He stands confidently among colorful stalls laden with fruits, textiles, and handmade crafts, his orange chapan catching the sunlight. The village folk eye him curiously as he surveys the scene with his characteristic clever smile.',
                'shot_type': 'establishing',
                'setting': 'Traditional Kazakh village marketplace at midday'
            }
        },
        {
            'name': 'Very long prompt',
            'frame': {
                'description': 'In the golden hour of sunset, Aldar Köse rides his trusty horse across the vast Kazakh steppe, the endless grasslands stretching to the horizon in every direction. The warm amber light casts long shadows across the rolling hills, while distant mountains frame the scene. Traditional yurts dot the landscape, smoke rising from their chimneys. Aldar sits tall in his saddle, his orange chapan billowing in the wind, his topknot hair catching the last rays of sunlight. His face shows determination mixed with his trademark clever smile as he embarks on yet another adventure.',
                'shot_type': 'establishing',
                'setting': 'Vast Kazakh steppe landscape at golden hour sunset with mountains in the distance'
            }
        },
        {
            'name': 'Extreme length prompt',
            'frame': {
                'description': 'Aldar Köse, the legendary trickster hero of Kazakh folklore, stands in the center of a traditional Kazakh village during the height of a busy market day. The scene is alive with activity as villagers in colorful traditional dress browse countless stalls overflowing with fresh produce, handwoven carpets, intricate jewelry, aromatic spices, and all manner of goods. Children run between the stalls playing traditional games, while elderly villagers sit in the shade sharing stories and sipping tea from ornate ceramic cups. Aldar himself is dressed in his signature bright orange chapan robe adorned with traditional Kazakh ornamental patterns in gold and red, his hair styled in his characteristic topknot. His expression shows a mixture of mischief and wisdom as he surveys the marketplace, clearly planning his next clever scheme. The sun hangs high in a brilliant blue sky, casting warm golden light across the entire scene and creating a festive, energetic atmosphere.',
                'shot_type': 'wide',
                'setting': 'Traditional Kazakh village marketplace during peak afternoon trading hours with mountain backdrop'
            }
        }
    ]

    print("=" * 80)
    print("PROMPT LENGTH TEST RESULTS")
    print("=" * 80)
    print()

    for test_case in test_frames:
        name = test_case['name']
        frame = test_case['frame']

        print(f"\nTest: {name}")
        print("-" * 80)
        print(f"Original description ({len(frame['description'])} chars):")
        print(f"  {frame['description'][:100]}..." if len(frame['description']) > 100 else f"  {frame['description']}")
        print()

        # Generate enhanced prompt
        enhanced_prompt = enhancer.enhance(frame)

        # Count tokens
        token_count = enhancer._count_tokens(enhanced_prompt)

        # Display results
        print(f"Enhanced prompt ({len(enhanced_prompt)} chars, {token_count} tokens):")
        print(f"  {enhanced_prompt}")
        print()

        # Check if within limits
        if token_count <= 75:
            print(f"✓ PASS: {token_count}/75 tokens")
        else:
            print(f"✗ FAIL: {token_count}/75 tokens (OVER LIMIT!)")

        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_prompt_lengths()
