"""
Image Comparator - Система сравнения качества изображений
Сравнивает изображения от LoRA и других AI моделей с референсами
"""

import torch
from PIL import Image
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json
from transformers import CLIPProcessor, CLIPModel
from skimage.metrics import structural_similarity as ssim
from scipy.spatial.distance import cosine
import config


class ImageComparator:
    """
    Система сравнения качества изображений на основе:
    1. CLIP embeddings similarity (семантическое сходство)
    2. Structural similarity (структурное сходство)
    3. Feature matching (соответствие ключевым характеристикам)
    """

    def __init__(self, reference_images: List[Path], key_features: List[str]):
        """
        Инициализация компаратора

        Args:
            reference_images: Список путей к референсным изображениям
            key_features: Список ключевых характеристик (из FeatureAnalyzer)
        """
        print("Инициализация Image Comparator...")

        self.reference_images = reference_images
        self.key_features = key_features

        # Загрузка CLIP модели
        self.device = config.get_device()
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model = self.model.to(self.device)
        self.model.eval()

        # Предвычисление embeddings референсов
        print("Вычисление embeddings референсных изображений...")
        self.reference_embeddings = self._compute_reference_embeddings()

        # Предвычисление embeddings ключевых характеристик
        print("Вычисление embeddings ключевых характеристик...")
        self.feature_embeddings = self._compute_feature_embeddings()

        print("✓ Image Comparator готов к работе")

    def _compute_reference_embeddings(self) -> torch.Tensor:
        """Вычисление CLIP embeddings для всех референсов"""
        embeddings = []

        for img_path in self.reference_images:
            if img_path.exists():
                image = Image.open(img_path).convert('RGB')
                embedding = self._get_image_embedding(image)
                embeddings.append(embedding)

        return torch.stack(embeddings)

    def _compute_feature_embeddings(self) -> torch.Tensor:
        """Вычисление CLIP text embeddings для ключевых характеристик"""
        inputs = self.processor(
            text=self.key_features,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            text_embeddings = self.model.get_text_features(**inputs)
            text_embeddings = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)

        return text_embeddings

    def _get_image_embedding(self, image: Image.Image) -> torch.Tensor:
        """Получение CLIP embedding для изображения"""
        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            image_embedding = self.model.get_image_features(**inputs)
            image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)

        return image_embedding.squeeze(0)

    def compare_with_references(
        self,
        generated_image: Image.Image,
        provider_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Сравнение сгенерированного изображения с референсами

        Args:
            generated_image: Сгенерированное изображение
            provider_name: Имя провайдера (lora, freepik, deepai, etc.)

        Returns:
            Словарь с метриками качества
        """
        print(f"\n[{provider_name.upper()}] Сравнение с референсами...")

        # 1. CLIP Similarity с референсами
        gen_embedding = self._get_image_embedding(generated_image)

        clip_similarities = []
        for ref_emb in self.reference_embeddings:
            similarity = torch.cosine_similarity(
                gen_embedding.unsqueeze(0),
                ref_emb.unsqueeze(0)
            ).item()
            clip_similarities.append(similarity)

        avg_clip_similarity = float(np.mean(clip_similarities))
        max_clip_similarity = float(np.max(clip_similarities))

        print(f"  CLIP similarity: avg={avg_clip_similarity:.3f}, max={max_clip_similarity:.3f}")

        # 2. Feature Matching Score
        feature_score = self._calculate_feature_matching(gen_embedding)
        print(f"  Feature matching: {feature_score:.3f}")

        # 3. Structural Similarity (со всеми референсами)
        ssim_scores = []
        for img_path in self.reference_images:
            if img_path.exists():
                ref_image = Image.open(img_path).convert('RGB')
                ssim_score = self._calculate_ssim(generated_image, ref_image)
                ssim_scores.append(ssim_score)

        avg_ssim = float(np.mean(ssim_scores)) if ssim_scores else 0.0
        print(f"  Structural similarity (SSIM): {avg_ssim:.3f}")

        # 4. Общий Quality Score (weighted average)
        quality_score = (
            0.4 * avg_clip_similarity +
            0.4 * feature_score +
            0.2 * avg_ssim
        )

        print(f"  📊 Общий Quality Score: {quality_score:.3f}")

        return {
            "provider": provider_name,
            "clip_similarity_avg": avg_clip_similarity,
            "clip_similarity_max": max_clip_similarity,
            "feature_matching_score": feature_score,
            "ssim_avg": avg_ssim,
            "quality_score": quality_score,
            "individual_clip_scores": clip_similarities,
            "individual_ssim_scores": ssim_scores
        }

    def _calculate_feature_matching(self, image_embedding: torch.Tensor) -> float:
        """
        Вычисление score соответствия ключевым характеристикам

        Args:
            image_embedding: CLIP embedding изображения

        Returns:
            Feature matching score (0-1)
        """
        # Вычисляем cosine similarity между изображением и каждой характеристикой
        similarities = []

        for feature_emb in self.feature_embeddings:
            similarity = torch.cosine_similarity(
                image_embedding.unsqueeze(0),
                feature_emb.unsqueeze(0)
            ).item()
            similarities.append(similarity)

        # Средний score по всем ключевым характеристикам
        avg_score = float(np.mean(similarities))

        return avg_score

    def _calculate_ssim(
        self,
        img1: Image.Image,
        img2: Image.Image
    ) -> float:
        """
        Вычисление Structural Similarity Index

        Args:
            img1: Первое изображение
            img2: Второе изображение

        Returns:
            SSIM score (0-1)
        """
        # Приводим к одному размеру
        size = (256, 256)  # Для ускорения вычислений
        img1_resized = img1.resize(size, Image.Resampling.LANCZOS)
        img2_resized = img2.resize(size, Image.Resampling.LANCZOS)

        # Конвертируем в grayscale numpy arrays
        img1_gray = np.array(img1_resized.convert('L'))
        img2_gray = np.array(img2_resized.convert('L'))

        # Вычисляем SSIM
        score = ssim(img1_gray, img2_gray)

        return float(score)

    def compare_providers(
        self,
        provider_results: Dict[str, Image.Image]
    ) -> Dict[str, Any]:
        """
        Сравнение результатов от разных провайдеров

        Args:
            provider_results: Словарь {provider_name: generated_image}

        Returns:
            Сравнительный отчет
        """
        print("\n" + "=" * 70)
        print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ ОТ ВСЕХ ПРОВАЙДЕРОВ")
        print("=" * 70)

        comparisons = {}

        for provider, image in provider_results.items():
            if image is not None:
                comparison = self.compare_with_references(image, provider)
                comparisons[provider] = comparison

        # Ранжирование по quality score
        ranked = sorted(
            comparisons.items(),
            key=lambda x: x[1]['quality_score'],
            reverse=True
        )

        print("\n" + "=" * 70)
        print("ИТОГОВЫЙ РЕЙТИНГ")
        print("=" * 70)

        for rank, (provider, metrics) in enumerate(ranked, 1):
            print(f"{rank}. {provider.upper()}: {metrics['quality_score']:.3f}")

        return {
            "comparisons": comparisons,
            "ranking": [(provider, metrics['quality_score']) for provider, metrics in ranked],
            "best_provider": ranked[0][0] if ranked else None,
            "best_score": ranked[0][1]['quality_score'] if ranked else 0.0
        }

    def generate_feedback_for_lora(
        self,
        lora_result: Dict[str, Any],
        best_competitor: Dict[str, Any],
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Генерация обратной связи для улучшения LoRA

        Args:
            lora_result: Результаты LoRA
            best_competitor: Результаты лучшего конкурента
            competitor_name: Имя лучшего конкурента

        Returns:
            Feedback с рекомендациями
        """
        print("\n" + "=" * 70)
        print("АНАЛИЗ И ОБРАТНАЯ СВЯЗЬ ДЛЯ LORA")
        print("=" * 70)

        feedback = {
            "lora_score": lora_result['quality_score'],
            "best_competitor": competitor_name,
            "competitor_score": best_competitor['quality_score'],
            "score_gap": best_competitor['quality_score'] - lora_result['quality_score'],
            "needs_improvement": best_competitor['quality_score'] > lora_result['quality_score'],
            "recommendations": []
        }

        # Анализируем разницу по метрикам
        print(f"\nLoRA Score: {lora_result['quality_score']:.3f}")
        print(f"Лучший конкурент ({competitor_name}): {best_competitor['quality_score']:.3f}")
        print(f"Разница: {feedback['score_gap']:.3f}")

        if feedback['needs_improvement']:
            print("\n⚠️  LoRA нуждается в улучшении!")
            print("\nРекомендации:")

            # Анализ по каждой метрике
            if best_competitor['clip_similarity_avg'] > lora_result['clip_similarity_avg']:
                gap = best_competitor['clip_similarity_avg'] - lora_result['clip_similarity_avg']
                rec = f"Улучшить семантическое сходство с референсами (отставание: {gap:.3f})"
                feedback['recommendations'].append({
                    "area": "clip_similarity",
                    "message": rec,
                    "priority": "high" if gap > 0.1 else "medium"
                })
                print(f"  • {rec}")

            if best_competitor['feature_matching_score'] > lora_result['feature_matching_score']:
                gap = best_competitor['feature_matching_score'] - lora_result['feature_matching_score']
                rec = f"Улучшить соответствие ключевым характеристикам (отставание: {gap:.3f})"
                feedback['recommendations'].append({
                    "area": "feature_matching",
                    "message": rec,
                    "priority": "high" if gap > 0.1 else "medium"
                })
                print(f"  • {rec}")

            if best_competitor['ssim_avg'] > lora_result['ssim_avg']:
                gap = best_competitor['ssim_avg'] - lora_result['ssim_avg']
                rec = f"Улучшить структурное сходство (отставание: {gap:.3f})"
                feedback['recommendations'].append({
                    "area": "structural_similarity",
                    "message": rec,
                    "priority": "medium" if gap > 0.05 else "low"
                })
                print(f"  • {rec}")

            # Общие рекомендации
            if feedback['score_gap'] > 0.15:
                feedback['recommendations'].append({
                    "area": "training",
                    "message": "Рекомендуется увеличить количество шагов обучения или изменить learning rate",
                    "priority": "high"
                })
                print("  • Рекомендуется увеличить количество шагов обучения")

        else:
            print("\n✓ LoRA показывает лучшие результаты!")

        return feedback


def test_comparator():
    """Тестирование компаратора"""

    print("=" * 70)
    print("ТЕСТИРОВАНИЕ IMAGE COMPARATOR")
    print("=" * 70)
    print()

    # Загрузка анализа характеристик
    feature_analysis_path = config.MODELS_DIR / "aldar_feature_analysis.json"

    if feature_analysis_path.exists():
        with open(feature_analysis_path, 'r', encoding='utf-8') as f:
            aggregated_features = json.load(f)

        # Извлечение ключевых характеристик
        key_features = []
        for category, info in aggregated_features.items():
            if info['avg_confidence'] > 0.2:
                key_features.append(info['feature'])
    else:
        print("⚠️  Сначала запустите feature_analyzer.py для создания анализа")
        # Используем дефолтные характеристики
        key_features = [
            "round friendly face",
            "narrow eyes",
            "mustache",
            "orange robe",
            "2D illustration"
        ]

    print(f"Ключевые характеристики: {key_features}")
    print()

    # Инициализация компаратора
    comparator = ImageComparator(config.REFERENCE_IMAGES, key_features)

    # Тестируем на одном из референсов
    test_image = Image.open(config.REFERENCE_IMAGES[0])

    result = comparator.compare_with_references(test_image, "test")

    print("\n" + "=" * 70)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 70)


if __name__ == "__main__":
    test_comparator()
