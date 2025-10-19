#!/usr/bin/env python3
"""
Test Prompt Enhancement
Shows how the new detailed prompts will look compared to old generic ones
"""

# Simulate the enhancement functions
def enhance_action_description(description: str, shot_type: str) -> str:
    """Enhanced action descriptions"""
    description_lower = description.lower()

    if any(word in description_lower for word in ['riding', 'мініп', 'есек', 'donkey', 'horse', 'at']):
        return (
            f"Dynamic full body shot showing Aldar Köse actively riding a small brown donkey, "
            f"seated on the donkey's back with motion and movement clearly visible, "
            f"traveling across the landscape"
        )

    if any(word in description_lower for word in ['talking', 'speaking', 'айтып', 'сөйлес', 'conversation']):
        return (
            f"Medium shot showing Aldar Köse engaged in animated conversation, "
            f"gesturing expressively with hands, interacting with others, "
            f"facial expressions showing engagement"
        )

    # DEFAULT
    return (
        f"Dynamic scene showing Aldar Köse in action: {description}, "
        f"clear body language and movement, active pose showing what is happening, "
        f"not just a portrait"
    )

def enhance_setting_description(setting: str, key_objects: list) -> str:
    """Enhanced setting descriptions"""
    setting_lower = setting.lower()

    if any(word in setting_lower for word in ['steppe', 'дала', 'grassland', 'prairie']):
        objects_str = ', '.join(key_objects) if key_objects else 'rolling hills, scattered yurts'
        return (
            f"Set in vast golden steppe landscape with endless horizons, "
            f"{objects_str} visible in the scene, "
            f"distant mountains on the horizon, clear blue sky, "
            f"traditional Kazakh environment"
        )

    if any(word in setting_lower for word in ['village', 'settlement', 'ауыл', 'yurt']):
        objects_str = ', '.join(key_objects) if key_objects else 'traditional yurts, people, livestock'
        return (
            f"Traditional Kazakh village setting with {objects_str}, "
            f"white felt yurts clustered together, communal atmosphere, "
            f"people and daily life activities visible, "
            f"warm community environment"
        )

    # DEFAULT
    objects_str = ', '.join(key_objects) if key_objects else 'environmental details'
    return (
        f"Scene set in {setting} with {objects_str} visible, "
        f"clear environmental context and atmosphere, "
        f"detailed background establishing the location"
    )


# Test cases based on user's example
test_cases = [
    {
        "name": "User's Example: Riding Donkey",
        "description": "Aldar Köse кішкентай есекке мініп, кең далада келе жатыр",
        "setting": "Golden steppe",
        "key_objects": ["mountains", "yurts"],
        "shot_type": "full body"
    },
    {
        "name": "Marketplace Scene",
        "description": "Aldar Köse talking with a merchant in a bazaar",
        "setting": "Bustling marketplace",
        "key_objects": ["colorful fabrics", "food stalls"],
        "shot_type": "medium shot"
    },
    {
        "name": "Village Conversation",
        "description": "Aldar Köse speaking with villagers near yurts",
        "setting": "Traditional village",
        "key_objects": ["yurts", "campfire"],
        "shot_type": "wide shot"
    }
]


print("=" * 80)
print("🎨 PROMPT ENHANCEMENT TEST")
print("=" * 80)
print()

for test in test_cases:
    print(f"📝 Test: {test['name']}")
    print("-" * 80)

    # OLD PROMPT (generic)
    old_prompt = (
        f"Aldar Köse. "
        f"{test['description']}. "
        f"Setting: {test['setting']}. "
        f"Shot: {test['shot_type']}."
    )

    # NEW PROMPT (detailed)
    action_detail = enhance_action_description(test['description'], test['shot_type'])
    setting_detail = enhance_setting_description(test['setting'], test['key_objects'])

    new_prompt = (
        f"{action_detail}, "
        f"featuring Aldar Köse. "
        f"{setting_detail}. "
        f"Camera angle: {test['shot_type']}."
    )

    print()
    print("❌ OLD (Generic):")
    print(f"   {old_prompt}")
    print()
    print("✅ NEW (Detailed):")
    print(f"   {new_prompt}")
    print()
    print("=" * 80)
    print()

print()
print("💡 KEY IMPROVEMENTS:")
print()
print("1. ✅ Actions are SPECIFIC - 'actively riding' not just 'with donkey'")
print("2. ✅ Body language described - 'seated on back', 'motion visible'")
print("3. ✅ Settings are VIVID - 'vast golden steppe' not just 'steppe'")
print("4. ✅ Composition guidance - 'full body shot', 'dynamic scene'")
print("5. ✅ Prevents portraits - emphasizes ACTION and MOVEMENT")
print()
print("=" * 80)
print()
print("🎯 Expected Result:")
print("   Images will now show the ACTUAL ACTION (riding, talking, etc.)")
print("   instead of just showing Aldar Köse's face with background scenery!")
print()
print("=" * 80)
