"""
Test script to verify Kazakh/Cyrillic prompt handling
"""

from prompt_enhancer import PromptEnhancer


def test_kazakh_prompts():
    """Test prompts with Kazakh text"""

    enhancer = PromptEnhancer()

    # Test cases with Kazakh text
    test_frames = [
        {
            'name': 'Kazakh text - marketplace',
            'frame': {
                'description': 'альдар көсе жәрмеңкеде, шапан мен тымақ киіп, адамдар арасында жүр',
                'shot_type': 'wide',
                'setting': 'ауыл базары'
            }
        },
        {
            'name': 'Kazakh text - rich man',
            'frame': {
                'description': 'бай жәрмеңкеде ең жақсы қойды сатып алуға дайындалып, көп ақша көрсетеді',
                'shot_type': 'medium',
                'setting': 'базар'
            }
        },
        {
            'name': 'English text',
            'frame': {
                'description': 'Aldar Kose walks through the marketplace wearing traditional Kazakh clothing',
                'shot_type': 'wide',
                'setting': 'Village marketplace'
            }
        }
    ]

    print("=" * 80)
    print("KAZAKH/CYRILLIC PROMPT TEST")
    print("=" * 80)
    print()

    for test_case in test_frames:
        name = test_case['name']
        frame = test_case['frame']

        print(f"\nTest: {name}")
        print("-" * 80)
        print(f"Original description:")
        print(f"  {frame['description']}")
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
    test_kazakh_prompts()
