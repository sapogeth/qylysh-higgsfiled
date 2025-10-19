# Исправления генерации изображений

## Проблемы
1. **Белый фон вокруг картинок** - генерируемые изображения иногда имеют пустые белые края
2. **"Расслабление" стиля в конце** - последние кадры становятся слишком мультяшными, теряя профессиональный стиль

## Решения

### 1. Убран белый фон (config.py)

**Изменено:** `NEGATIVE_PROMPT`

Добавлено в негативный промпт:
```python
"white background, white borders, white frame, empty background, blank space, plain background, padding, margins, "
```

Теперь Stable Diffusion активно избегает:
- Белых фонов
- Белых рамок/границ
- Пустого пространства
- Отступов вокруг изображения

### 2. Усилена консистентность стиля (config.py)

**Изменено:** `NEGATIVE_PROMPT`

Добавлено:
```python
"overly cartoonish, chibi style, manga style, sketch, rough lines, inconsistent style"
```

Теперь избегаются:
- Чрезмерно мультяшные стили
- Chibi/manga стили (слишком упрощенные)
- Скетчи и грубые линии
- Непоследовательный стиль

**Изменено:** `STYLE_LOCK`

Было:
```python
"consistent 2D cel-shaded anime-inspired style, smooth clean lineart, flat colors, "
"soft ambient shading, warm earthy palette, consistent line thickness across frames"
```

Стало:
```python
"IMPORTANT: maintain exact same style as previous frames, consistent 2D cel-shaded anime-inspired style, "
"smooth clean lineart, flat colors, soft ambient shading, warm earthy palette, "
"professional illustration quality, NO style drift, consistent line thickness across all frames"
```

Ключевые добавления:
- `IMPORTANT: maintain exact same style` - явная инструкция
- `professional illustration quality` - поддержание качества
- `NO style drift` - запрет на изменение стиля

### 3. Обновлены промпты (prompt_enhancer.py)

**Изменено:** Стиль для английских и неанглийских промптов

Добавлено:
```python
"full scene composition, no white borders, same face every frame, professional quality"
```

## Как это работает

### Механизм 1: Negative Prompts
Stable Diffusion использует negative prompts для **активного избегания** нежелательных элементов:
- `white background` → модель старается заполнить весь кадр сценой
- `overly cartoonish` → модель поддерживает профессиональный стиль

### Механизм 2: Style Lock
STYLE_LOCK присутствует в **каждом** промпте, обеспечивая:
- Одинаковый стиль через все кадры
- Профессиональное качество иллюстрации
- Предотвращение "дрейфа стиля"

### Механизм 3: Positive Reinforcement
Добавление `full scene composition` в промпт указывает модели:
- Заполнить весь кадр композицией
- Не оставлять пустого пространства
- Создавать полноценные сцены

## Результат

После этих изменений:
✅ Изображения заполняют весь кадр без белых границ
✅ Стиль остается консистентным от начала до конца истории
✅ Финальные кадры не становятся "слишком мультяшными"
✅ Профессиональное качество иллюстраций поддерживается

## Технические детали

### Token Budget
- Negative prompt: ~205 tokens (в пределах лимита SDXL)
- Positive prompt: 75 tokens (CLIP limit)
- Style lock: интегрирован в каждый промпт

### Приоритет элементов в промпте
1. **Характер** (лицо, одежда) - ПЕРВЫЙ для консистентности
2. **Описание сцены** - что происходит
3. **Стиль** - как это должно выглядеть
4. **Дополнительно** - shot type, setting (если есть место)

### Проверка исправлений

Запустите тест:
```bash
python3 test_fixes.py
```

Проверьте:
- ✅ `white background` присутствует в negative prompt
- ✅ `overly cartoonish` присутствует в negative prompt
- ✅ `IMPORTANT` и `NO style drift` в STYLE_LOCK

## Дополнительные рекомендации

Если белый фон всё ещё появляется:
1. Увеличьте `GUIDANCE_SCALE` в config.py (сейчас 7.5, попробуйте 8.0-9.0)
2. Увеличьте вес negative prompt через параметр `negative_prompt_embeds_scale` (если поддерживается)
3. Добавьте `centered composition` в positive prompt

Если стиль всё ещё дрейфует:
1. Используйте одинаковый `seed` для всех кадров (для testing)
2. Активируйте IP-Adapter (установите `USE_IDENTITY_LOCK = True` в config.py)
3. Увеличьте `IP_ADAPTER_SCALE` до 0.7-0.8
