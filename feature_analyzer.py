"""
Feature Analyzer - Система анализа ключевых факторов в изображениях
Анализирует референсные изображения и находит ключевые характеристики персонажа
"""

import torch
from PIL import Image
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
import json
from transformers import CLIPProcessor, CLIPModel
import config


class FeatureAnalyzer:
    """
    Анализатор ключевых характеристик изображений
    Использует CLIP для извлечения визуальных особенностей
    """

    def __init__(self):
        """Инициализация анализатора"""
        print("Загрузка CLIP модели для анализа изображений...")

        # Используем Hugging Face CLIP (более стабильно для M1)
        self.device = config.get_device()
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model = self.model.to(self.device)
        self.model.eval()

        print(f"✓ CLIP модель загружена на {self.device}")

        # Ключевые аспекты для анализа
        self.feature_categories = {
            "face_shape": [
                "round face",
                "oval face",
                "square face",
                "angular face",
                "friendly round face"
            ],
            "eyes": [
                "narrow eyes",
                "wide eyes",
                "almond-shaped eyes",
                "round eyes",
                "small eyes"
            ],
            "facial_hair": [
                "mustache",
                "thin mustache",
                "thick mustache",
                "beard",
                "clean shaven",
                "no facial hair"
            ],
            "hair_style": [
                "topknot",
                "bun",
                "short hair",
                "long hair",
                "black hair",
                "ponytail"
            ],
            "clothing_color": [
                "orange robe",
                "red robe",
                "blue robe",
                "brown robe",
                "yellow robe",
                "patterned robe"
            ],
            "art_style": [
                "2D illustration",
                "cartoon style",
                "realistic painting",
                "watercolor",
                "digital art",
                "children's book style"
            ],
            "expression": [
                "smiling",
                "laughing",
                "serious",
                "happy",
                "neutral expression"
            ],
            "background": [
                "steppe landscape",
                "outdoor scene",
                "plain background",
                "detailed background",
                "minimalist background"
            ]
        }

    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Анализ отдельного изображения

        Args:
            image_path: Путь к изображению

        Returns:
            Словарь с выявленными характеристиками
        """
        print(f"\nАнализ {image_path.name}...")

        # Загрузка изображения
        image = Image.open(image_path).convert('RGB')

        results = {}

        # Анализ каждой категории
        for category, options in self.feature_categories.items():
            scores = self._calculate_text_image_similarity(image, options)

            # Находим топ-2 наиболее вероятных характеристик
            top_indices = np.argsort(scores)[-2:][::-1]
            top_features = [(options[i], float(scores[i])) for i in top_indices]

            results[category] = {
                "top_match": top_features[0][0],
                "confidence": top_features[0][1],
                "alternatives": top_features
            }

            print(f"  {category}: {top_features[0][0]} (уверенность: {top_features[0][1]:.2f})")

        return results

    def _calculate_text_image_similarity(
        self,
        image: Image.Image,
        text_options: List[str]
    ) -> np.ndarray:
        """
        Вычисление similarity между изображением и текстовыми описаниями

        Args:
            image: PIL Image
            text_options: Список текстовых описаний

        Returns:
            Массив scores для каждого описания
        """
        # Подготовка входных данных
        inputs = self.processor(
            text=text_options,
            images=image,
            return_tensors="pt",
            padding=True
        )

        # Перемещение на устройство
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Вычисление similarity
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image  # image-text similarity
            probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]

        return probs

    def analyze_reference_images(
        self,
        image_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Анализ всех референсных изображений и агрегация результатов

        Args:
            image_paths: Список путей к референсным изображениям

        Returns:
            Агрегированные характеристики
        """
        print("=" * 70)
        print("АНАЛИЗ РЕФЕРЕНСНЫХ ИЗОБРАЖЕНИЙ")
        print("=" * 70)

        all_results = []

        # Анализ каждого изображения
        for img_path in image_paths:
            if img_path.exists():
                result = self.analyze_image(img_path)
                all_results.append(result)

        # Агрегация результатов
        print("\n" + "=" * 70)
        print("АГРЕГАЦИЯ РЕЗУЛЬТАТОВ")
        print("=" * 70)

        aggregated = self._aggregate_features(all_results)

        return aggregated

    def _aggregate_features(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Агрегация результатов анализа нескольких изображений

        Args:
            results: Список результатов анализа

        Returns:
            Консолидированные характеристики
        """
        aggregated = {}

        for category in self.feature_categories.keys():
            # Собираем все топовые матчи для каждой категории
            feature_counts = {}
            total_confidence = {}

            for result in results:
                if category in result:
                    feature = result[category]['top_match']
                    confidence = result[category]['confidence']

                    if feature not in feature_counts:
                        feature_counts[feature] = 0
                        total_confidence[feature] = 0.0

                    feature_counts[feature] += 1
                    total_confidence[feature] += confidence

            # Находим наиболее частую и уверенную характеристику
            if feature_counts:
                # Сортируем по количеству появлений, затем по средней уверенности
                sorted_features = sorted(
                    feature_counts.items(),
                    key=lambda x: (x[1], total_confidence[x[0]] / x[1]),
                    reverse=True
                )

                best_feature = sorted_features[0][0]
                avg_confidence = total_confidence[best_feature] / feature_counts[best_feature]

                aggregated[category] = {
                    "feature": best_feature,
                    "appearances": feature_counts[best_feature],
                    "avg_confidence": float(avg_confidence),
                    "all_detections": sorted_features
                }

                print(f"\n{category}:")
                print(f"  Основная характеристика: {best_feature}")
                print(f"  Встречается: {feature_counts[best_feature]}/{len(results)} раз")
                print(f"  Средняя уверенность: {avg_confidence:.2f}")

        return aggregated

    def generate_training_prompt(
        self,
        aggregated_features: Dict[str, Any]
    ) -> str:
        """
        Генерация оптимального промпта для обучения на основе анализа

        Args:
            aggregated_features: Агрегированные характеристики

        Returns:
            Текстовый промпт для обучения
        """
        prompt_parts = []

        # Извлекаем ключевые характеристики
        for category, info in aggregated_features.items():
            if info['avg_confidence'] > 0.15:  # Порог уверенности
                prompt_parts.append(info['feature'])

        # Формируем промпт
        prompt = ", ".join(prompt_parts)

        print("\n" + "=" * 70)
        print("СГЕНЕРИРОВАННЫЙ ПРОМПТ ДЛЯ ОБУЧЕНИЯ")
        print("=" * 70)
        print(prompt)
        print()

        return prompt

    def save_analysis(
        self,
        aggregated_features: Dict[str, Any],
        output_path: Path
    ):
        """
        Сохранение результатов анализа в JSON

        Args:
            aggregated_features: Агрегированные характеристики
            output_path: Путь для сохранения
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated_features, f, indent=2, ensure_ascii=False)

        print(f"✓ Результаты анализа сохранены: {output_path}")

    def extract_key_features_for_validation(
        self,
        aggregated_features: Dict[str, Any]
    ) -> List[str]:
        """
        Извлечение ключевых характеристик для валидации

        Args:
            aggregated_features: Агрегированные характеристики

        Returns:
            Список ключевых характеристик (с высокой уверенностью)
        """
        key_features = []

        # Приоритетные категории (наиболее важные для консистентности)
        priority_categories = [
            'face_shape',
            'eyes',
            'facial_hair',
            'clothing_color',
            'art_style'
        ]

        for category in priority_categories:
            if category in aggregated_features:
                info = aggregated_features[category]
                if info['avg_confidence'] > 0.2:  # Высокий порог для ключевых характеристик
                    key_features.append(info['feature'])

        return key_features


def test_analyzer():
    """Тестирование анализатора"""

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ FEATURE ANALYZER")
    print("=" * 70)
    print()

    # Инициализация анализатора
    analyzer = FeatureAnalyzer()

    # Анализ референсных изображений
    aggregated = analyzer.analyze_reference_images(config.REFERENCE_IMAGES)

    # Генерация промпта
    training_prompt = analyzer.generate_training_prompt(aggregated)

    # Извлечение ключевых характеристик
    key_features = analyzer.extract_key_features_for_validation(aggregated)
    print("Ключевые характеристики для валидации:")
    for i, feature in enumerate(key_features, 1):
        print(f"  {i}. {feature}")
    print()

    # Сохранение результатов
    output_path = config.MODELS_DIR / "aldar_feature_analysis.json"
    analyzer.save_analysis(aggregated, output_path)

    print("=" * 70)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 70)


if __name__ == "__main__":
    test_analyzer()
