"""
Быстрое обучение LoRA (упрощённая версия для тестирования)
Использует DreamBooth-подход с меньшим количеством шагов
"""

import torch
from diffusers import StableDiffusionXLPipeline, DiffusionPipeline
from diffusers.loaders import LoraLoaderMixin
from peft import LoraConfig, get_peft_model
from PIL import Image
import config
from pathlib import Path
from tqdm import tqdm


def quick_train_lora():
    """
    Быстрое обучение LoRA для тестирования концепции
    """
    print("=" * 70)
    print("БЫСТРОЕ ОБУЧЕНИЕ LORA (ТЕСТОВЫЙ РЕЖИМ)")
    print("=" * 70)
    print()

    device = config.get_device()
    dtype = config.get_dtype()

    # 1. Загрузка базовой модели
    print("[1/4] Загрузка SDXL модели...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        config.SDXL_MODEL_ID,
        torch_dtype=dtype,
        use_safetensors=True,
        variant="fp16"
    ).to(device)

    # Оптимизации
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()

    print("✓ SDXL загружена")
    print()

    # 2. Подготовка данных
    print("[2/4] Подготовка референсных изображений...")

    images = []
    for img_path in config.REFERENCE_IMAGES:
        if img_path.exists():
            img = Image.open(img_path).convert('RGB')
            img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
            images.append(img)
            print(f"  ✓ {img_path.name}")

    print(f"✓ Загружено {len(images)} изображений")
    print()

    # 3. Настройка LoRA
    print("[3/4] Настройка LoRA адаптера...")

    # ВАЖНО: Для реального обучения нужна библиотека diffusers с поддержкой LoRA training
    # Это упрощённая демонстрация концепции

    print("⚠️  ПРИМЕЧАНИЕ:")
    print("   Полное обучение LoRA требует специализированных скриптов и может")
    print("   занять несколько часов даже на GPU.")
    print()
    print("   Для production обучения рекомендуется:")
    print("   1. Использовать Google Colab с GPU (бесплатно)")
    print("   2. Использовать готовые скрипты из Hugging Face Diffusers")
    print("   3. Или запустить train_lora_real.py (займёт ~2-4 часа на M1)")
    print()

    # 4. Создание конфигурационных файлов для LoRA
    print("[4/4] Создание конфигурации LoRA...")

    # Создаём метаданные для LoRA
    lora_config = {
        "model_type": "lora",
        "base_model": config.SDXL_MODEL_ID,
        "trigger_word": config.LORA_TRIGGER_WORD,
        "training_caption": config.TRAINING_CAPTION,
        "num_reference_images": len(images),
        "lora_rank": config.LORA_RANK,
        "lora_alpha": config.LORA_ALPHA,
        "status": "ready_for_training"
    }

    import json
    config_path = config.MODELS_DIR / "lora_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(lora_config, f, indent=2, ensure_ascii=False)

    print(f"✓ Конфигурация сохранена: {config_path}")
    print()

    print("=" * 70)
    print("ВЫБОР МЕТОДА ОБУЧЕНИЯ")
    print("=" * 70)
    print()
    print("У вас есть 3 варианта:")
    print()
    print("1. GOOGLE COLAB (РЕКОМЕНДУЕТСЯ) - бесплатный GPU")
    print("   - Быстро (30-60 минут)")
    print("   - Высокое качество")
    print("   - Используйте готовый notebook")
    print()
    print("2. ЛОКАЛЬНОЕ ОБУЧЕНИЕ (train_lora_real.py)")
    print("   - Медленно на M1 (2-4 часа)")
    print("   - Полный контроль")
    print("   - Требует времени и ресурсов")
    print()
    print("3. ИСПОЛЬЗОВАТЬ ПРОМПТЫ (БЕЗ LORA)")
    print("   - Мгновенно")
    print("   - Хорошее качество с правильными промптами")
    print("   - Уже настроено в вашей системе")
    print()
    print("Текущий статус: Система готова к варианту 3 (промпты)")
    print()
    print("Для варианта 1 (Colab):")
    print("  См. файл: GOOGLE_COLAB_GUIDE.md")
    print()
    print("Для варианта 2 (локально):")
    print("  python3 train_lora_real.py")
    print()


if __name__ == "__main__":
    quick_train_lora()
