"""
AI Providers Integration Module
Интеграция с различными AI сервисами для генерации изображений и текста
"""

import os
import requests
import time
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Dict, Any
import json


class DeepseekTextGenerator:
    """
    Deepseek API для конвертации промптов в короткие рассказы
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def generate_story(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Генерация короткого рассказа из промпта

        Args:
            prompt: Базовый промпт/идея для рассказа
            max_tokens: Максимальное количество токенов

        Returns:
            Сгенерированный рассказ
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты опытный казахский сказитель. Создавай короткие, увлекательные истории про Алдар Косе в стиле народных казахских сказок. Истории должны быть поучительными и подходящими для детей."
                },
                {
                    "role": "user",
                    "content": f"Создай короткий рассказ (3-5 предложений) про Алдар Косе на основе этой идеи: {prompt}"
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.8
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            story = data['choices'][0]['message']['content']

            print(f"✓ Deepseek сгенерировал рассказ ({len(story)} символов)")
            return story

        except Exception as e:
            print(f"❌ Ошибка Deepseek API: {e}")
            return prompt  # Возвращаем оригинальный промпт в случае ошибки


class FreepikImageGenerator:
    """
    Freepik AI Image Generator API
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.freepik.com/v1/ai/text-to-image"

    def generate_image(self, prompt: str, negative_prompt: str = "") -> Optional[Image.Image]:
        """
        Генерация изображения через Freepik AI

        Args:
            prompt: Текстовый промпт
            negative_prompt: Негативный промпт

        Returns:
            PIL Image или None при ошибке
        """
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "guidance_scale": 7.5,
            "num_images": 1,
            "image": {
                "size": "square_1_1"  # 1024x1024
            }
        }

        try:
            # Запрос на генерацию
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Freepik может возвращать URL или base64
            if 'data' in data and len(data['data']) > 0:
                image_data = data['data'][0]

                if 'url' in image_data:
                    # Скачиваем изображение
                    img_response = requests.get(image_data['url'], timeout=30)
                    img = Image.open(BytesIO(img_response.content))
                elif 'b64_json' in image_data:
                    # Декодируем base64
                    img_bytes = base64.b64decode(image_data['b64_json'])
                    img = Image.open(BytesIO(img_bytes))
                else:
                    print("❌ Freepik: неизвестный формат ответа")
                    return None

                print(f"✓ Freepik сгенерировал изображение {img.size}")
                return img
            else:
                print("❌ Freepik: пустой ответ")
                return None

        except Exception as e:
            print(f"❌ Ошибка Freepik API: {e}")
            return None


class DeepAIImageGenerator:
    """
    DeepAI Text2Img API
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepai.org/api/text2img"

    def generate_image(self, prompt: str) -> Optional[Image.Image]:
        """
        Генерация изображения через DeepAI

        Args:
            prompt: Текстовый промпт

        Returns:
            PIL Image или None при ошибке
        """
        headers = {
            "api-key": self.api_key
        }

        data = {
            "text": prompt,
            "grid_size": "1",  # Одно изображение
            "width": 1024,
            "height": 1024
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=data, timeout=60)
            response.raise_for_status()

            result = response.json()

            if 'output_url' in result:
                # Скачиваем изображение
                img_response = requests.get(result['output_url'], timeout=30)
                img = Image.open(BytesIO(img_response.content))

                # Изменяем размер до 1024x1024 если нужно
                if img.size != (1024, 1024):
                    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)

                print(f"✓ DeepAI сгенерировал изображение {img.size}")
                return img
            else:
                print("❌ DeepAI: отсутствует output_url")
                return None

        except Exception as e:
            print(f"❌ Ошибка DeepAI API: {e}")
            return None


class GeminiImageGenerator:
    """
    Google Gemini AI для генерации изображений
    Используем Imagen через Vertex AI
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Gemini пока не поддерживает прямую генерацию изображений через простой API
        # Будем использовать Imagen 2 через Vertex AI REST API
        self.base_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagegeneration:predict"

    def generate_image(self, prompt: str, negative_prompt: str = "") -> Optional[Image.Image]:
        """
        Генерация изображения через Google Imagen

        Args:
            prompt: Текстовый промпт
            negative_prompt: Негативный промпт

        Returns:
            PIL Image или None при ошибке
        """

        # Примечание: Для Google Imagen нужен project_id и более сложная настройка
        # Здесь базовая реализация, которая может потребовать доработки

        try:
            print("⚠️  Google Gemini/Imagen требует дополнительной настройки Google Cloud")
            print("   Используйте gcloud auth или service account для аутентификации")
            print("   Пропускаем генерацию Gemini для упрощения")
            return None

        except Exception as e:
            print(f"❌ Ошибка Gemini API: {e}")
            return None


class AIProvidersManager:
    """
    Менеджер для управления всеми AI провайдерами
    """

    def __init__(self, config: Dict[str, str]):
        """
        Инициализация всех доступных провайдеров

        Args:
            config: Словарь с API ключами
                {
                    'deepseek_api_key': '...',
                    'freepik_api_key': '...',
                    'deepai_api_key': '...',
                    'gemini_api_key': '...'
                }
        """
        self.providers = {}

        # Инициализация Deepseek для генерации текста
        if config.get('deepseek_api_key'):
            self.providers['deepseek'] = DeepseekTextGenerator(config['deepseek_api_key'])
            print("✓ Deepseek Text Generator инициализирован")

        # Инициализация генераторов изображений
        if config.get('freepik_api_key'):
            self.providers['freepik'] = FreepikImageGenerator(config['freepik_api_key'])
            print("✓ Freepik Image Generator инициализирован")

        if config.get('deepai_api_key'):
            self.providers['deepai'] = DeepAIImageGenerator(config['deepai_api_key'])
            print("✓ DeepAI Image Generator инициализирован")

        if config.get('gemini_api_key'):
            self.providers['gemini'] = GeminiImageGenerator(config['gemini_api_key'])
            print("✓ Google Gemini Generator инициализирован (требует настройки)")

    def get_text_generator(self) -> Optional[DeepseekTextGenerator]:
        """Получить текстовый генератор (Deepseek)"""
        return self.providers.get('deepseek')

    def get_image_generators(self) -> Dict[str, Any]:
        """Получить все доступные генераторы изображений"""
        generators = {}
        for name in ['freepik', 'deepai', 'gemini']:
            if name in self.providers:
                generators[name] = self.providers[name]
        return generators

    def generate_story_from_prompt(self, prompt: str) -> str:
        """
        Генерация рассказа из промпта

        Args:
            prompt: Базовая идея

        Returns:
            Расширенный рассказ
        """
        deepseek = self.get_text_generator()
        if deepseek:
            return deepseek.generate_story(prompt)
        else:
            print("⚠️  Deepseek не настроен, используется оригинальный промпт")
            return prompt

    def generate_images_from_all_providers(
        self,
        prompt: str,
        negative_prompt: str = ""
    ) -> Dict[str, Optional[Image.Image]]:
        """
        Генерация изображений от всех доступных провайдеров

        Args:
            prompt: Текстовый промпт
            negative_prompt: Негативный промпт

        Returns:
            Словарь {provider_name: PIL.Image или None}
        """
        results = {}
        generators = self.get_image_generators()

        print(f"\n🎨 Генерация изображений от {len(generators)} провайдеров...")

        for name, generator in generators.items():
            print(f"\n[{name.upper()}]")
            try:
                if name == 'freepik':
                    img = generator.generate_image(prompt, negative_prompt)
                else:
                    img = generator.generate_image(prompt)
                results[name] = img
            except Exception as e:
                print(f"❌ Ошибка при генерации от {name}: {e}")
                results[name] = None

        return results


def test_providers():
    """Тестирование AI провайдеров"""

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ AI ПРОВАЙДЕРОВ")
    print("=" * 70)
    print()

    # Загрузка конфига из .env
    from dotenv import load_dotenv
    load_dotenv()

    config = {
        'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
        'freepik_api_key': os.getenv('FREEPIK_API_KEY'),
        'deepai_api_key': os.getenv('DEEPAI_API_KEY'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY')
    }

    # Проверка наличия ключей
    print("Проверка API ключей:")
    for key, value in config.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {'настроен' if value else 'отсутствует'}")
    print()

    # Инициализация менеджера
    manager = AIProvidersManager(config)
    print()

    # Тест генерации рассказа
    test_prompt = "Алдар Косе обманывает жадного бая"
    print(f"Тестовый промпт: {test_prompt}")
    print()

    story = manager.generate_story_from_prompt(test_prompt)
    print(f"Сгенерированный рассказ:\n{story}")
    print()

    # Тест генерации изображений
    image_prompt = "Aldar Kose, Kazakh folk hero, traditional orange robe, smiling, steppe background, 2D illustration"
    negative_prompt = "3D, realistic, photo, modern"

    print(f"Тест генерации изображений...")
    print(f"Промпт: {image_prompt}")
    print()

    images = manager.generate_images_from_all_providers(image_prompt, negative_prompt)

    print()
    print("Результаты генерации:")
    for provider, img in images.items():
        if img:
            print(f"  ✓ {provider}: {img.size}")
        else:
            print(f"  ✗ {provider}: не удалось сгенерировать")

    print()
    print("=" * 70)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 70)


if __name__ == "__main__":
    test_providers()
