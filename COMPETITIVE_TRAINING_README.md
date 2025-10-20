# Конкурентная Система Обучения LoRA для Алдар Косе

## Описание

Это продвинутая система обучения LoRA моделей, которая автоматически сравнивает качество генерации с другими AI моделями и предоставляет обратную связь для улучшения.

## Как это работает

### Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                    КОНКУРЕНТНОЕ ОБУЧЕНИЕ                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │   1. АНАЛИЗ РЕФЕРЕНСОВ (CLIP)       │
        │   - Извлечение ключевых черт        │
        │   - Генерация оптимального промпта  │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   2. ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ          │
        │   ✓ LoRA (локальная)                │
        │   ✓ Freepik AI                      │
        │   ✓ DeepAI                          │
        │   ✓ Google Gemini (опционально)    │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   3. СРАВНЕНИЕ КАЧЕСТВА             │
        │   - CLIP similarity                 │
        │   - Feature matching                │
        │   - Structural similarity (SSIM)    │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   4. ОБРАТНАЯ СВЯЗЬ ДЛЯ LoRA       │
        │   - Анализ слабых мест              │
        │   - Рекомендации по улучшению       │
        │   - Автоматическая реитерация       │
        └─────────────────────────────────────┘
```

### Ключевые компоненты

1. **Feature Analyzer** ([feature_analyzer.py](feature_analyzer.py))
   - Анализирует референсные изображения с помощью CLIP
   - Извлекает ключевые визуальные характеристики персонажа
   - Генерирует оптимальные промпты для обучения

2. **AI Providers Manager** ([ai_providers.py](ai_providers.py))
   - **Deepseek API**: Генерация рассказов из промптов
   - **Freepik AI**: Генерация изображений
   - **DeepAI**: Альтернативный генератор изображений
   - **Google Gemini**: Опциональный провайдер

3. **Image Comparator** ([image_comparator.py](image_comparator.py))
   - Сравнивает изображения по трём метрикам:
     - **CLIP Similarity**: Семантическое сходство с референсами
     - **Feature Matching**: Соответствие ключевым характеристикам
     - **SSIM**: Структурное сходство
   - Ранжирует результаты всех AI моделей
   - Генерирует детальную обратную связь

4. **Competitive LoRA Trainer** ([train_lora_competitive.py](train_lora_competitive.py))
   - Управляет полным циклом обучения
   - Автоматически запускает итерации
   - Сохраняет историю и аналитику

## Установка

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Настройте API ключи

Отредактируйте файл `.env`:

```bash
# OpenAI (для генерации промптов)
OPENAI_API_KEY=ваш_ключ

# AI Providers для конкурентного обучения
DEEPSEEK_API_KEY=sk-2ce976ae9f1a4c8583b707c236fa6139
FREEPIK_API_KEY=FPSX193caafa0683767de2a873582de96305
DEEPAI_API_KEY=bceb509d99484191608a4c615530003a8c9a8e99cd87bc98b500f293bd19be75
GEMINI_API_KEY=AIzaSyBKZihsdTcixwCcYgiGDK696lUsaJ8cEbs
```

**Важно**: Вы указали свои ключи:
- Deepseek: `sk-2ce976ae9f1a4c8583b707c236fa6139`
- Freepik: `FPSX193caafa0683767de2a873582de96305`
- DeepAI: `bceb509d99484191608a4c615530003a8c9a8e99cd87bc98b500f293bd19be75`
- Gemini: `AIzaSyBKZihsdTcixwCcYgiGDK696lUsaJ8cEbs`

### 3. Проверьте систему

```bash
python3 test_competitive_training.py
```

Этот скрипт проверит:
- ✓ Все зависимости установлены
- ✓ Файлы проекта на месте
- ✓ Референсные изображения найдены
- ✓ API ключи настроены
- ✓ Модули работают корректно

## Использование

### Быстрый старт

```bash
python3 train_lora_competitive.py
```

Система автоматически:
1. Проанализирует референсные изображения `aldar1.png` - `aldar5.png`
2. Сгенерирует изображения через LoRA и конкурентов
3. Сравнит качество
4. Предоставит обратную связь
5. Повторит цикл при необходимости (до 3 итераций)

### Тестирование отдельных компонентов

#### Анализ референсных изображений

```bash
python3 feature_analyzer.py
```

Результат:
- Анализ каждого референса
- Агрегированные характеристики
- Оптимальный промпт для обучения
- Сохранение в `models/aldar_feature_analysis.json`

#### Тестирование Image Comparator

```bash
python3 image_comparator.py
```

Проверяет систему сравнения качества на референсном изображении.

#### Тестирование AI Providers

```bash
python3 ai_providers.py
```

Тестирует:
- Генерацию рассказов через Deepseek
- Генерацию изображений через все настроенные провайдеры

## Результаты

Все результаты сохраняются в директорию `lora_training_results/`:

```
lora_training_results/
├── comparisons/              # Сгенерированные изображения
│   ├── lora_20241020_153022.png
│   ├── freepik_20241020_153022.png
│   ├── deepai_20241020_153022.png
│   └── comparison_report_20241020_153022.json
├── feedback/                 # Обратная связь для LoRA
│   └── feedback_20241020_153022.json
└── training_history.json     # Полная история обучения
```

### Интерпретация результатов

#### Quality Score (0-1)

Общий показатель качества, состоящий из:
- **40%** CLIP Similarity (семантическое сходство)
- **40%** Feature Matching (соответствие характеристикам)
- **20%** SSIM (структурное сходство)

**Оценка:**
- **0.8 - 1.0**: Отлично! LoRA идеально воспроизводит персонажа
- **0.6 - 0.8**: Хорошо, небольшие улучшения возможны
- **0.4 - 0.6**: Средне, требуется доработка
- **< 0.4**: Плохо, требуется серьёзная доработка

#### Пример отчета обратной связи

```json
{
  "lora_score": 0.742,
  "best_competitor": "freepik",
  "competitor_score": 0.819,
  "score_gap": 0.077,
  "needs_improvement": true,
  "recommendations": [
    {
      "area": "clip_similarity",
      "message": "Улучшить семантическое сходство с референсами (отставание: 0.085)",
      "priority": "high"
    },
    {
      "area": "feature_matching",
      "message": "Улучшить соответствие ключевым характеристикам (отставание: 0.042)",
      "priority": "medium"
    }
  ]
}
```

## Понимание ключевых факторов

Система автоматически анализирует референсы и извлекает:

### Категории характеристик

1. **Форма лица**: round face, oval face, square face
2. **Глаза**: narrow eyes, almond-shaped eyes, round eyes
3. **Усы/борода**: thin mustache, thick mustache, no facial hair
4. **Прическа**: topknot, short hair, black hair
5. **Цвет одежды**: orange robe, patterned robe
6. **Стиль**: 2D illustration, cartoon style, children's book style
7. **Выражение**: smiling, friendly, happy
8. **Фон**: steppe landscape, plain background

### Как система ищет характеристики

Для каждого фрейма система:

1. **Извлекает CLIP embeddings** изображения
2. **Сравнивает с текстовыми описаниями** всех характеристик
3. **Вычисляет cosine similarity** для каждой характеристики
4. **Выбирает наиболее подходящие** (top-2 для каждой категории)
5. **Агрегирует результаты** по всем референсам
6. **Формирует финальный список** ключевых характеристик

## Расширенная настройка

### Изменение количества итераций

В файле `train_lora_competitive.py`:

```python
max_iterations = 3  # Измените на нужное значение
```

### Изменение тестового промпта

```python
test_prompt = "Ваш кастомный промпт здесь"
```

### Настройка весов метрик качества

В файле `image_comparator.py`, метод `compare_with_references`:

```python
quality_score = (
    0.4 * avg_clip_similarity +    # Вес CLIP similarity
    0.4 * feature_score +           # Вес feature matching
    0.2 * avg_ssim                  # Вес SSIM
)
```

## Поддержка разных AI провайдеров

### Добавление нового провайдера

1. Создайте класс в `ai_providers.py`:

```python
class NewProviderImageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "..."

    def generate_image(self, prompt: str) -> Optional[Image.Image]:
        # Ваша реализация
        pass
```

2. Добавьте в `AIProvidersManager`:

```python
if config.get('newprovider_api_key'):
    self.providers['newprovider'] = NewProviderImageGenerator(
        config['newprovider_api_key']
    )
```

3. Добавьте ключ в `.env`:

```
NEWPROVIDER_API_KEY=ваш_ключ
```

## Troubleshooting

### Проблема: "LoRA generation failed"

**Решение**: Убедитесь, что:
1. SDXL модель загружена: `python3 setup.py`
2. Достаточно памяти (минимум 8GB RAM для M1)
3. MPS доступен: `import torch; print(torch.backends.mps.is_available())`

### Проблема: "No competitors for comparison"

**Решение**: Настройте хотя бы один внешний API ключ в `.env`

### Проблема: Медленная генерация

**Решение**:
1. Уменьшите `NUM_INFERENCE_STEPS` в `config.py`
2. Включите `USE_LCM = True` для ультра-быстрой генерации
3. Используйте Google Colab для ускорения

### Проблема: CLIP модель не загружается

**Решение**:
```bash
pip install --upgrade transformers
```

## Вопросы и поддержка

Если у вас возникли вопросы:

1. Проверьте логи выполнения
2. Запустите `test_competitive_training.py`
3. Проверьте файлы в `lora_training_results/`

## Лицензия

Этот проект создан для обучения и генерации изображений Алдар Косе.

---

**Удачи в обучении LoRA!** 🚀
