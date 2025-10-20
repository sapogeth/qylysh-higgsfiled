# Руководство по Обучению LoRA для Алдар Косе

## Что такое LoRA?

**LoRA (Low-Rank Adaptation)** - это техника machine learning для дообучения больших моделей с минимальными ресурсами.

```
Базовая модель (SDXL)     LoRA адаптер          Результат
     7 GB                   ~100 MB         Персонализированная модель
    ↓                          ↓                      ↓
[Общая генерация]  +  [Ваши данные]  =  [Генерация Алдар Косе]
```

## Зачем обучать LoRA?

### Без LoRA (только промпты):
```
Промпт: "Kazakh folk hero in orange robe"
Результат: Похоже, но НЕ точно Алдар Косе
Консистентность: 60-70%
```

### С обученной LoRA:
```
Промпт: "aldar_kose_character in the steppe"
Результат: ТОЧНО Алдар Косе из референсов
Консистентность: 95-98%
```

## 3 Способа Обучения LoRA

### Способ 1: Google Colab (РЕКОМЕНДУЕТСЯ) ⭐

**Преимущества:**
- ✅ Бесплатный GPU (Tesla T4)
- ✅ Быстро (30-60 минут)
- ✅ Высокое качество
- ✅ Не нагружает ваш компьютер

**Недостатки:**
- ❌ Требует Google аккаунт
- ❌ Ограничение по времени (12 часов)

**Как использовать:**

1. Откройте готовый Colab notebook:
   - См. файл `GOOGLE_COLAB_GUIDE.md`
   - Или создайте свой на основе скрипта ниже

2. Загрузите 5 референсных изображений в Colab

3. Запустите обучение (1 клик)

4. Скачайте обученную LoRA (~100 MB)

5. Поместите в `models/aldar_kose_lora.safetensors`

---

### Способ 2: Локальное Обучение (train_lora_real.py)

**Преимущества:**
- ✅ Полный контроль
- ✅ Приватность
- ✅ Неограниченное время

**Недостатки:**
- ❌ Медленно на M1 (2-4 часа)
- ❌ Требует ~10GB свободной памяти
- ❌ Нагревает MacBook

**Инструкции:**

```bash
# 1. Убедитесь что все зависимости установлены
pip install -r requirements.txt

# 2. Проверьте референсные изображения
ls aldar*.png
# Должно быть: aldar1.png, aldar2.png, ..., aldar5.png

# 3. Запустите обучение
python3 train_lora_real.py

# Процесс:
# [1/5] Загрузка SDXL модели...          (5-10 мин первый раз)
# [2/5] Анализ референсов...             (2-3 мин)
# [3/5] Настройка LoRA...                (1 мин)
# [4/5] Подготовка данных...             (1 мин)
# [5/5] Обучение (100 эпох)...           (2-4 часа)
#       Epoch 1/100: loss=0.5432
#       Epoch 20/100: loss=0.3214 [checkpoint saved]
#       ...
#       Epoch 100/100: loss=0.0987
# ✓ Обучение завершено!

# 4. Проверьте результат
ls models/aldar_kose_lora.safetensors
ls static/generated/lora_test_generation.png
```

**Настройка параметров обучения:**

Отредактируйте `train_lora_real.py`:

```python
# Количество эпох (больше = лучше качество, но дольше)
trainer.train(
    num_epochs=100,      # Измените на 200-500 для лучшего качества
    learning_rate=1e-4   # Уменьшите до 5e-5 если loss не падает
)
```

---

### Способ 3: Использовать Промпты (БЕЗ LoRA)

**Преимущества:**
- ✅ Мгновенно
- ✅ Не требует обучения
- ✅ Хорошее качество с правильными промптами

**Недостатки:**
- ❌ Меньшая консистентность (70-80% vs 95% с LoRA)
- ❌ Нужно каждый раз писать длинные промпты

**Ваша система УЖЕ настроена** для этого способа:

```python
# В config.py уже настроено:
TRAINING_CAPTION = (
    "2D storybook illustration of Kazakh folk hero, "
    "orange patterned chapan robe with traditional ornaments, "
    "friendly smiling expression with black mustache, "
    "small topknot hairstyle, round friendly face with narrow eyes, "
    "warm skin tone, simplified cartoon proportions"
)
```

Просто запустите:
```bash
python3 app.py
# Или
python3 train_lora_competitive.py
```

---

## Понимание Процесса Обучения LoRA

### Что происходит внутри:

```python
# 1. ЗАГРУЗКА БАЗОВОЙ МОДЕЛИ
SDXL = load_model("stabilityai/stable-diffusion-xl-base-1.0")
# SDXL знает: как рисовать людей, пейзажи, объекты...
# НО НЕ знает: кто такой Алдар Косе

# 2. АНАЛИЗ РЕФЕРЕНСОВ
for image in [aldar1, aldar2, aldar3, aldar4, aldar5]:
    features = analyze(image)
    # Извлекаем: форма лица, цвет одежды, прическа, стиль...

# 3. СОЗДАНИЕ LORA АДАПТЕРА
lora = create_lora_adapter(rank=16)
# LoRA - это маленькая нейросеть (100MB) которая "настраивает" SDXL

# 4. ОБУЧЕНИЕ (100-500 эпох)
for epoch in range(100):
    for image in references:
        # Показываем SDXL изображение
        generated = SDXL.generate(prompt)

        # Сравниваем с референсом
        loss = compare(generated, image)

        # Обновляем LoRA веса
        lora.update_weights(loss)

# 5. РЕЗУЛЬТАТ
# SDXL + LoRA теперь знают как рисовать Алдар Косе!
```

### Ключевые Параметры:

| Параметр | Значение | Что делает | Как изменять |
|----------|----------|------------|--------------|
| **num_epochs** | 100-500 | Сколько раз проходить по данным | ↑ = лучше качество, но дольше |
| **learning_rate** | 1e-4 | Скорость обучения | ↓ если loss не падает |
| **lora_rank** | 16 | Размер LoRA адаптера | ↑ = больше деталей, но больше файл |
| **lora_alpha** | 16 | Сила LoRA эффекта | Обычно = rank |

### Мониторинг Обучения:

```
Epoch 1/100: loss=0.5432   ← Высокий loss = плохое качество
Epoch 20/100: loss=0.3214  ← Loss падает = модель учится
Epoch 50/100: loss=0.1543  ← Хороший прогресс
Epoch 100/100: loss=0.0987 ← Низкий loss = хорошее качество
```

**Хороший loss:** < 0.15
**Отличный loss:** < 0.10
**Идеальный loss:** < 0.05

---

## Тестирование Обученной LoRA

После обучения проверьте качество:

```bash
# 1. Тестовая генерация
python3 -c "
from local_image_generator import LocalImageGenerator
gen = LocalImageGenerator()
img = gen.generate_single('aldar_kose_character in the steppe')
img.save('test.png')
print('✓ Тест сохранён: test.png')
"

# 2. Сравнение с конкурентами
python3 train_lora_competitive.py
# Система сравнит вашу LoRA с Freepik, DeepAI, Gemini
# И покажет где улучшать

# 3. Использование в приложении
python3 app.py
# Откройте http://localhost:8080
```

---

## Troubleshooting

### Проблема: "Out of memory"

**Решение:** Уменьшите batch size или используйте Colab

```python
# В train_lora_real.py
TRAIN_BATCH_SIZE = 1  # Уже минимальный
```

### Проблема: Loss не падает

**Решение 1:** Уменьшите learning rate
```python
trainer.train(learning_rate=5e-5)  # Было 1e-4
```

**Решение 2:** Увеличьте количество эпох
```python
trainer.train(num_epochs=200)  # Было 100
```

### Проблема: LoRA переобучилась (overfitting)

**Симптомы:** Генерирует ТОЧНЫЕ копии референсов, но плохо генерализует

**Решение:**
```python
# Уменьшите количество эпох
trainer.train(num_epochs=50)  # Было 100

# Или добавьте регуляризацию
lora_config = LoraConfig(
    lora_dropout=0.2  # Было 0.1
)
```

### Проблема: Генерация слишком долгая

**Решение:** Уменьшите inference steps
```python
# В config.py
NUM_INFERENCE_STEPS = 20  # Было 30
```

---

## Продвинутые Техники

### 1. Использование CLIP для валидации

```python
from feature_analyzer import FeatureAnalyzer

analyzer = FeatureAnalyzer()
score = analyzer.calculate_similarity(generated_image, reference_images)

if score < 0.8:
    print("Качество низкое, продолжаем обучение")
```

### 2. Динамический Learning Rate

```python
# Уменьшаем LR если loss перестал падать
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='min',
    factor=0.5,
    patience=10
)
```

### 3. Augmentation данных

```python
from torchvision import transforms

augment = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.RandomRotation(5)
])
```

---

## Сравнение Подходов

| Критерий | Colab GPU | Локально M1 | Только Промпты |
|----------|-----------|-------------|----------------|
| Скорость | 30-60 мин | 2-4 часа | Мгновенно |
| Качество | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Сложность | Средняя | Высокая | Низкая |
| Стоимость | Бесплатно | Бесплатно | Бесплатно |
| Консистентность | 95-98% | 95-98% | 70-80% |

## Рекомендации

**Для начинающих в ML:**
1. Начните со способа 3 (промпты) - запустите `python3 train_lora_competitive.py`
2. Посмотрите результаты
3. Если качество устраивает - готово!
4. Если нет - попробуйте Colab (способ 1)

**Для ML-специалистов:**
1. Запустите `python3 train_lora_real.py` локально
2. Экспериментируйте с параметрами
3. Мониторьте loss и качество
4. Используйте `train_lora_competitive.py` для валидации

---

## Следующие Шаги

После успешного обучения LoRA:

```bash
# 1. Проверьте что LoRA работает
ls models/aldar_kose_lora.safetensors

# 2. Запустите конкурентное сравнение
python3 train_lora_competitive.py

# 3. Используйте в приложении
python3 app.py

# 4. Генерируйте сториборды с вашей LoRA!
```

---

**Готовы начать настоящее machine learning обучение?**

Выберите один из способов выше и следуйте инструкциям! 🚀
