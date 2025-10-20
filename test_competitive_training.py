"""
Тестовый скрипт для проверки системы конкурентного обучения LoRA
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ КОНКУРЕНТНОГО ОБУЧЕНИЯ LORA")
print("=" * 70)
print()

# Проверка зависимостей
print("Шаг 1: Проверка зависимостей...")
print()

required_modules = [
    ('torch', 'PyTorch'),
    ('PIL', 'Pillow'),
    ('transformers', 'Transformers'),
    ('diffusers', 'Diffusers'),
    ('numpy', 'NumPy'),
    ('requests', 'Requests'),
    ('dotenv', 'python-dotenv'),
    ('scipy', 'SciPy')
]

missing_modules = []
for module_name, package_name in required_modules:
    try:
        __import__(module_name)
        print(f"  ✓ {package_name}")
    except ImportError:
        print(f"  ✗ {package_name} - НЕ УСТАНОВЛЕН")
        missing_modules.append(package_name)

# Специальная проверка для scikit-image (импортируется как skimage)
try:
    from skimage import metrics
    print("  ✓ scikit-image")
except ImportError:
    print("  ✗ scikit-image - НЕ УСТАНОВЛЕН")
    missing_modules.append('scikit-image')

if missing_modules:
    print(f"\n❌ Отсутствуют модули: {', '.join(missing_modules)}")
    print("\nУстановите их командой:")
    print(f"pip install {' '.join(missing_modules)}")
    sys.exit(1)

print("\n✓ Все зависимости установлены")

# Проверка файлов проекта
print("\nШаг 2: Проверка файлов проекта...")
print()

required_files = [
    'ai_providers.py',
    'feature_analyzer.py',
    'image_comparator.py',
    'train_lora_competitive.py',
    'config.py',
    'local_image_generator.py',
    '.env'
]

missing_files = []
for filename in required_files:
    filepath = Path(filename)
    if filepath.exists():
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ {filename} - НЕ НАЙДЕН")
        missing_files.append(filename)

if missing_files:
    print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
    sys.exit(1)

print("\n✓ Все файлы проекта на месте")

# Проверка референсных изображений
print("\nШаг 3: Проверка референсных изображений...")
print()

import config

missing_refs = []
for img_path in config.REFERENCE_IMAGES:
    if img_path.exists():
        print(f"  ✓ {img_path.name}")
    else:
        print(f"  ✗ {img_path.name} - НЕ НАЙДЕН")
        missing_refs.append(img_path.name)

if missing_refs:
    print(f"\n❌ Отсутствуют референсные изображения: {', '.join(missing_refs)}")
    sys.exit(1)

print("\n✓ Все референсные изображения на месте")

# Проверка API ключей
print("\nШаг 4: Проверка API ключей...")
print()

from dotenv import load_dotenv
load_dotenv()

api_keys = {
    'OpenAI': os.getenv('OPENAI_API_KEY'),
    'Deepseek': os.getenv('DEEPSEEK_API_KEY'),
    'Freepik': os.getenv('FREEPIK_API_KEY'),
    'DeepAI': os.getenv('DEEPAI_API_KEY'),
    'Gemini': os.getenv('GEMINI_API_KEY')
}

configured_keys = 0
for name, key in api_keys.items():
    if key:
        print(f"  ✓ {name}: настроен")
        configured_keys += 1
    else:
        print(f"  ✗ {name}: НЕ НАСТРОЕН")

if configured_keys == 0:
    print("\n❌ Ни один API ключ не настроен!")
    print("Отредактируйте файл .env и добавьте хотя бы один ключ")
    sys.exit(1)

print(f"\n✓ Настроено {configured_keys}/5 API ключей")

# Тест модулей
print("\nШаг 5: Тестирование модулей...")
print()

# Тест AI Providers
print("[1/3] Тестирование AI Providers...")
try:
    from ai_providers import AIProvidersManager

    providers_config = {
        'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
        'freepik_api_key': os.getenv('FREEPIK_API_KEY'),
        'deepai_api_key': os.getenv('DEEPAI_API_KEY'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY')
    }

    manager = AIProvidersManager(providers_config)
    print("  ✓ AI Providers Manager инициализирован")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

# Тест Feature Analyzer
print("\n[2/3] Тестирование Feature Analyzer...")
try:
    from feature_analyzer import FeatureAnalyzer

    analyzer = FeatureAnalyzer()
    print("  ✓ Feature Analyzer инициализирован")

    # Анализ одного референса (быстрый тест)
    test_result = analyzer.analyze_image(config.REFERENCE_IMAGES[0])
    print(f"  ✓ Анализ изображения работает (найдено {len(test_result)} характеристик)")

except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

# Тест Image Comparator
print("\n[3/3] Тестирование Image Comparator...")
try:
    from image_comparator import ImageComparator
    from PIL import Image

    key_features = ["round face", "narrow eyes", "mustache", "orange robe"]
    comparator = ImageComparator(config.REFERENCE_IMAGES, key_features)
    print("  ✓ Image Comparator инициализирован")

    # Тест сравнения (с одним из референсов)
    test_img = Image.open(config.REFERENCE_IMAGES[0])
    comparison = comparator.compare_with_references(test_img, "test")
    print(f"  ✓ Сравнение работает (quality score: {comparison['quality_score']:.3f})")

except Exception as e:
    print(f"  ❌ Ошибка: {e}")
    sys.exit(1)

# Финальная проверка
print("\n" + "=" * 70)
print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
print("=" * 70)
print()
print("✓ Все зависимости установлены")
print("✓ Все файлы проекта на месте")
print("✓ Референсные изображения найдены")
print(f"✓ API ключи настроены ({configured_keys}/5)")
print("✓ Все модули работают корректно")
print()
print("=" * 70)
print("СИСТЕМА ГОТОВА К РАБОТЕ!")
print("=" * 70)
print()
print("Для запуска конкурентного обучения используйте:")
print("  python3 train_lora_competitive.py")
print()
print("Для тестирования отдельных компонентов:")
print("  python3 feature_analyzer.py      - Анализ референсов")
print("  python3 image_comparator.py      - Тест компаратора")
print("  python3 ai_providers.py          - Тест AI провайдеров")
print()
