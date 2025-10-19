#!/usr/bin/env python3
"""
Test Speed Optimization
Measures generation speed and validates optimizations
"""

import time
import config
from local_image_generator import LocalImageGenerator

def test_speed():
    """Test image generation speed with current config"""
    print("=" * 70)
    print("🚀 ТЕСТ СКОРОСТИ ГЕНЕРАЦИИ")
    print("=" * 70)
    print()

    # Show current config
    print("📊 Текущая Конфигурация:")
    print(f"   NUM_INFERENCE_STEPS: {config.NUM_INFERENCE_STEPS}")
    print(f"   GUIDANCE_SCALE: {config.GUIDANCE_SCALE}")
    print(f"   USE_IDENTITY_LOCK: {config.USE_IDENTITY_LOCK}")
    print(f"   IP_ADAPTER_SCALE: {config.IP_ADAPTER_SCALE if config.USE_IDENTITY_LOCK else 'N/A'}")
    print(f"   SCHEDULER_TYPE: {config.SCHEDULER_TYPE}")
    print(f"   ENABLE_ATTENTION_SLICING: {config.ENABLE_ATTENTION_SLICING}")
    print(f"   ENABLE_CHANNELS_LAST: {getattr(config, 'ENABLE_CHANNELS_LAST', False)}")
    print(f"   SKIP_SAFETY_CHECKER: {config.SKIP_SAFETY_CHECKER}")
    print()

    # Initialize generator
    print("⏳ Загрузка модели (это займёт ~60-120 секунд при первом запуске)...")
    generator = LocalImageGenerator()

    # Test prompt
    test_prompt = "Aldar Kose smiling in a village marketplace"

    print()
    print("=" * 70)
    print("🎨 ТЕСТ 1: Одно изображение БЕЗ IP-Adapter")
    print("=" * 70)

    start_time = time.time()
    try:
        # Generate without IP-Adapter
        img1 = generator.generate_single(
            prompt=test_prompt,
            negative_prompt=config.NEGATIVE_PROMPT,
            ref_image=None,  # No IP-Adapter
        )
        elapsed1 = time.time() - start_time
        print(f"✅ Сгенерировано за: {elapsed1:.2f} секунд")
        print(f"   Размер: {img1.size}")
    except Exception as e:
        elapsed1 = None
        print(f"❌ Ошибка: {e}")

    print()
    print("=" * 70)
    print("🎨 ТЕСТ 2: Одно изображение С IP-Adapter")
    print("=" * 70)

    if config.USE_IDENTITY_LOCK:
        from PIL import Image
        import os

        # Load reference image
        ref_path = os.path.join(os.path.dirname(__file__), config.IDENTITY_REFERENCE_IMAGE)
        if os.path.exists(ref_path):
            ref_image = Image.open(ref_path).convert('RGB')

            start_time = time.time()
            try:
                img2 = generator.generate_single(
                    prompt=test_prompt,
                    negative_prompt=config.NEGATIVE_PROMPT,
                    ref_image=ref_image,
                    ip_adapter_scale=config.IP_ADAPTER_SCALE
                )
                elapsed2 = time.time() - start_time
                print(f"✅ Сгенерировано за: {elapsed2:.2f} секунд")
                print(f"   Размер: {img2.size}")

                if elapsed1:
                    overhead = ((elapsed2 - elapsed1) / elapsed1) * 100
                    print(f"   IP-Adapter overhead: +{overhead:.1f}%")
            except Exception as e:
                elapsed2 = None
                print(f"❌ Ошибка: {e}")
        else:
            print(f"⚠️  Референсное изображение не найдено: {ref_path}")
            elapsed2 = None
    else:
        print("⚠️  IP-Adapter отключён в конфигурации")
        elapsed2 = None

    print()
    print("=" * 70)
    print("🎨 ТЕСТ 3: 3 изображения (стандартный сториборд)")
    print("=" * 70)

    test_prompts = [
        "Aldar Kose riding a donkey across the steppe",
        "Aldar Kose talking with a merchant in a bazaar",
        "Aldar Kose laughing with children by a yurt"
    ]

    start_time = time.time()
    try:
        # Load reference if needed
        ref_image = None
        if config.USE_IDENTITY_LOCK:
            ref_path = os.path.join(os.path.dirname(__file__), config.IDENTITY_REFERENCE_IMAGE)
            if os.path.exists(ref_path):
                ref_image = Image.open(ref_path).convert('RGB')

        images = []
        for i, prompt in enumerate(test_prompts, 1):
            print(f"   Генерация {i}/3... ", end='', flush=True)
            img_start = time.time()
            img = generator.generate_single(
                prompt=prompt,
                negative_prompt=config.NEGATIVE_PROMPT,
                ref_image=ref_image,
                ip_adapter_scale=config.IP_ADAPTER_SCALE if ref_image else None
            )
            img_elapsed = time.time() - img_start
            images.append(img)
            print(f"✓ {img_elapsed:.2f}s")

        total_elapsed = time.time() - start_time
        avg_per_image = total_elapsed / len(test_prompts)

        print()
        print(f"✅ Все 3 изображения сгенерированы за: {total_elapsed:.2f} секунд")
        print(f"   Среднее время на изображение: {avg_per_image:.2f} секунд")

        # Estimate for full storyboard
        full_storyboard_time = avg_per_image * 6
        print(f"   📊 Ожидаемое время для 6 изображений: {full_storyboard_time:.1f} секунд (~{full_storyboard_time/60:.1f} минут)")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print()
    print("=" * 70)
    print("📈 ОЦЕНКА СКОРОСТИ")
    print("=" * 70)

    if elapsed1:
        print(f"🚀 Одно изображение (без IP-Adapter): {elapsed1:.2f} секунд")

        if elapsed1 < 3:
            rating = "ОТЛИЧНО! 🏆"
        elif elapsed1 < 5:
            rating = "ХОРОШО ✅"
        elif elapsed1 < 8:
            rating = "ПРИЕМЛЕМО ⚠️"
        else:
            rating = "МЕДЛЕННО ❌"

        print(f"   Оценка: {rating}")

        # Calculate improvements
        old_time_estimate = 6.5  # Previous average
        improvement = ((old_time_estimate - elapsed1) / old_time_estimate) * 100

        if improvement > 0:
            print(f"   Улучшение: ~{improvement:.1f}% быстрее предыдущей версии!")

    if elapsed2:
        print(f"🎯 Одно изображение (с IP-Adapter): {elapsed2:.2f} секунд")

    print()
    print("=" * 70)
    print("✅ ТЕСТ ЗАВЕРШЁН")
    print("=" * 70)
    print()

    # Recommendations
    print("💡 Рекомендации:")
    if elapsed1 and elapsed1 > 5:
        print("   • Попробуйте уменьшить NUM_INFERENCE_STEPS до 10 для ещё большей скорости")
        print("   • Рассмотрите отключение IP-Adapter (USE_IDENTITY_LOCK = False)")
    elif elapsed1 and elapsed1 < 3:
        print("   • Отлично! Можно увеличить NUM_INFERENCE_STEPS для лучшего качества")
        print("   • Или увеличить IP_ADAPTER_SCALE для большей консистентности лица")
    else:
        print("   • Баланс скорость/качество оптимален!")

    print()

if __name__ == "__main__":
    try:
        test_speed()
    except KeyboardInterrupt:
        print("\n\n⚠️  Тест прерван пользователем")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
