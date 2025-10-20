"""
Competitive LoRA Training System
Обучение LoRA с автоматическим сравнением качества с другими AI моделями
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image

import config
from feature_analyzer import FeatureAnalyzer
from image_comparator import ImageComparator
from ai_providers import AIProvidersManager
from local_image_generator import LocalImageGenerator


class CompetitiveLoRATrainer:
    """
    Система обучения LoRA с конкурентным сравнением
    """

    def __init__(self):
        """Инициализация тренера"""
        print("=" * 70)
        print("КОНКУРЕНТНАЯ СИСТЕМА ОБУЧЕНИЯ LORA")
        print("=" * 70)
        print()

        # Директории для результатов
        self.output_dir = Path("lora_training_results")
        self.output_dir.mkdir(exist_ok=True)

        self.comparisons_dir = self.output_dir / "comparisons"
        self.comparisons_dir.mkdir(exist_ok=True)

        self.feedback_dir = self.output_dir / "feedback"
        self.feedback_dir.mkdir(exist_ok=True)

        # История обучения
        self.training_history = []

    def step1_analyze_references(self) -> Dict[str, Any]:
        """
        Шаг 1: Анализ референсных изображений
        """
        print("\n" + "=" * 70)
        print("ШАГ 1: АНАЛИЗ РЕФЕРЕНСНЫХ ИЗОБРАЖЕНИЙ")
        print("=" * 70)

        analyzer = FeatureAnalyzer()
        aggregated_features = analyzer.analyze_reference_images(config.REFERENCE_IMAGES)

        # Генерация промпта
        training_prompt = analyzer.generate_training_prompt(aggregated_features)

        # Извлечение ключевых характеристик
        key_features = analyzer.extract_key_features_for_validation(aggregated_features)

        # Сохранение анализа
        analysis_path = config.MODELS_DIR / "aldar_feature_analysis.json"
        analyzer.save_analysis(aggregated_features, analysis_path)

        return {
            "aggregated_features": aggregated_features,
            "training_prompt": training_prompt,
            "key_features": key_features
        }

    def step2_generate_test_images(
        self,
        test_prompt: str,
        ai_providers_config: Dict[str, str]
    ) -> Dict[str, Optional[Image.Image]]:
        """
        Шаг 2: Генерация тестовых изображений от всех провайдеров
        """
        print("\n" + "=" * 70)
        print("ШАГ 2: ГЕНЕРАЦИЯ ТЕСТОВЫХ ИЗОБРАЖЕНИЙ")
        print("=" * 70)

        results = {}

        # 1. Генерация через LoRA (локальная модель)
        print("\n[LORA] Генерация через локальную LoRA модель...")
        try:
            lora_generator = LocalImageGenerator()
            lora_image = lora_generator.generate_single(
                prompt=test_prompt,
                negative_prompt=config.NEGATIVE_PROMPT
            )
            results['lora'] = lora_image
            print("✓ LoRA: успешно")
        except Exception as e:
            print(f"❌ LoRA: {e}")
            results['lora'] = None

        # 2. Генерация через другие AI провайдеры
        providers_manager = AIProvidersManager(ai_providers_config)
        other_results = providers_manager.generate_images_from_all_providers(
            test_prompt,
            config.NEGATIVE_PROMPT
        )

        results.update(other_results)

        # Сохранение изображений
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for provider, img in results.items():
            if img:
                save_path = self.comparisons_dir / f"{provider}_{timestamp}.png"
                img.save(save_path)
                print(f"✓ Сохранено: {save_path}")

        return results

    def step3_compare_quality(
        self,
        generated_images: Dict[str, Optional[Image.Image]],
        key_features: list
    ) -> Dict[str, Any]:
        """
        Шаг 3: Сравнение качества изображений
        """
        print("\n" + "=" * 70)
        print("ШАГ 3: СРАВНЕНИЕ КАЧЕСТВА")
        print("=" * 70)

        # Инициализация компаратора
        comparator = ImageComparator(config.REFERENCE_IMAGES, key_features)

        # Сравнение всех провайдеров
        comparison_report = comparator.compare_providers(generated_images)

        # Сохранение отчета
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.comparisons_dir / f"comparison_report_{timestamp}.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            # Конвертируем в сериализуемый формат
            serializable_report = {
                "timestamp": timestamp,
                "comparisons": comparison_report['comparisons'],
                "ranking": comparison_report['ranking'],
                "best_provider": comparison_report['best_provider'],
                "best_score": comparison_report['best_score']
            }
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Отчет сохранен: {report_path}")

        return comparison_report

    def step4_generate_feedback(
        self,
        comparison_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Шаг 4: Генерация обратной связи для LoRA
        """
        print("\n" + "=" * 70)
        print("ШАГ 4: ГЕНЕРАЦИЯ ОБРАТНОЙ СВЯЗИ")
        print("=" * 70)

        comparisons = comparison_report['comparisons']

        if 'lora' not in comparisons:
            print("⚠️  LoRA не сгенерировала изображение, обратная связь невозможна")
            return {"error": "LoRA generation failed"}

        lora_result = comparisons['lora']

        # Находим лучшего конкурента (не LoRA)
        competitors = {k: v for k, v in comparisons.items() if k != 'lora'}

        if not competitors:
            print("⚠️  Нет конкурентов для сравнения")
            return {"error": "No competitors"}

        best_competitor_name = max(
            competitors.keys(),
            key=lambda k: competitors[k]['quality_score']
        )
        best_competitor_result = competitors[best_competitor_name]

        # Генерация feedback
        key_features = ["round face", "narrow eyes", "mustache", "orange robe", "2D illustration"]
        comparator = ImageComparator(config.REFERENCE_IMAGES, key_features)

        feedback = comparator.generate_feedback_for_lora(
            lora_result,
            best_competitor_result,
            best_competitor_name
        )

        # Сохранение feedback
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        feedback_path = self.feedback_dir / f"feedback_{timestamp}.json"

        with open(feedback_path, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Feedback сохранен: {feedback_path}")

        return feedback

    def run_training_cycle(
        self,
        test_prompt: str,
        ai_providers_config: Dict[str, str],
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Полный цикл обучения и тестирования

        Args:
            test_prompt: Промпт для тестовой генерации
            ai_providers_config: Конфигурация AI провайдеров
            iteration: Номер итерации

        Returns:
            Результаты цикла
        """
        print("\n" + "=" * 70)
        print(f"ИТЕРАЦИЯ {iteration}")
        print("=" * 70)

        cycle_start = time.time()

        # Шаг 1: Анализ референсов (только в первой итерации)
        if iteration == 1:
            analysis = self.step1_analyze_references()
        else:
            # Загружаем существующий анализ
            analysis_path = config.MODELS_DIR / "aldar_feature_analysis.json"
            with open(analysis_path, 'r', encoding='utf-8') as f:
                aggregated_features = json.load(f)

            analyzer = FeatureAnalyzer()
            key_features = analyzer.extract_key_features_for_validation(aggregated_features)
            training_prompt = analyzer.generate_training_prompt(aggregated_features)

            analysis = {
                "aggregated_features": aggregated_features,
                "training_prompt": training_prompt,
                "key_features": key_features
            }

        # Шаг 2: Генерация тестовых изображений
        generated_images = self.step2_generate_test_images(test_prompt, ai_providers_config)

        # Шаг 3: Сравнение качества
        comparison_report = self.step3_compare_quality(
            generated_images,
            analysis['key_features']
        )

        # Шаг 4: Генерация feedback
        feedback = self.step4_generate_feedback(comparison_report)

        cycle_time = time.time() - cycle_start

        # Сохранение в историю
        cycle_result = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "test_prompt": test_prompt,
            "comparison_report": comparison_report,
            "feedback": feedback,
            "cycle_time_seconds": cycle_time
        }

        self.training_history.append(cycle_result)

        # Сохранение истории
        history_path = self.output_dir / "training_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print(f"ИТЕРАЦИЯ {iteration} ЗАВЕРШЕНА")
        print(f"Время: {cycle_time:.1f}с")
        print("=" * 70)

        return cycle_result

    def should_continue_training(self, feedback: Dict[str, Any]) -> bool:
        """
        Определение необходимости продолжения обучения

        Args:
            feedback: Результаты обратной связи

        Returns:
            True если нужно продолжить обучение
        """
        if "error" in feedback:
            return False

        # Продолжаем, если LoRA отстает от конкурентов
        return feedback.get('needs_improvement', False)


def main():
    """Основная функция запуска"""

    print("=" * 70)
    print("ЗАПУСК КОНКУРЕНТНОГО ОБУЧЕНИЯ LORA")
    print("=" * 70)
    print()

    # Загрузка API ключей
    from dotenv import load_dotenv
    load_dotenv()

    ai_providers_config = {
        'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
        'freepik_api_key': os.getenv('FREEPIK_API_KEY'),
        'deepai_api_key': os.getenv('DEEPAI_API_KEY'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY')
    }

    # Проверка наличия ключей
    print("Проверка API ключей:")
    available_providers = []
    for key, value in ai_providers_config.items():
        provider_name = key.replace('_api_key', '')
        if value:
            print(f"  ✓ {provider_name}")
            available_providers.append(provider_name)
        else:
            print(f"  ✗ {provider_name} (не настроен)")

    if not available_providers:
        print("\n⚠️  ВНИМАНИЕ: Ни один внешний AI провайдер не настроен!")
        print("   Сравнение будет только с локальной LoRA моделью")
        print()

    # Инициализация тренера
    trainer = CompetitiveLoRATrainer()

    # Тестовый промпт
    test_prompt = (
        "Aldar Kose, Kazakh folk hero, traditional orange chapan robe, "
        "friendly smiling face, mustache, topknot hairstyle, "
        "steppe landscape background, 2D children's book illustration style"
    )

    print(f"\nТестовый промпт: {test_prompt}\n")

    # Параметры обучения
    max_iterations = 3
    current_iteration = 1

    # Цикл обучения
    while current_iteration <= max_iterations:
        result = trainer.run_training_cycle(
            test_prompt,
            ai_providers_config,
            current_iteration
        )

        # Проверка необходимости продолжения
        if current_iteration < max_iterations:
            if trainer.should_continue_training(result['feedback']):
                print(f"\n🔄 LoRA требует улучшения. Переход к итерации {current_iteration + 1}...")
                current_iteration += 1
            else:
                print("\n✓ LoRA показывает отличные результаты! Обучение завершено.")
                break
        else:
            print(f"\n✓ Достигнуто максимальное количество итераций ({max_iterations})")
            break

    # Итоговый отчет
    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)

    if trainer.training_history:
        print(f"\nВсего итераций: {len(trainer.training_history)}")

        for i, cycle in enumerate(trainer.training_history, 1):
            print(f"\nИтерация {i}:")
            if 'lora' in cycle['comparison_report']['comparisons']:
                lora_score = cycle['comparison_report']['comparisons']['lora']['quality_score']
                print(f"  LoRA Score: {lora_score:.3f}")

            print(f"  Лучший провайдер: {cycle['comparison_report']['best_provider']}")
            print(f"  Лучший score: {cycle['comparison_report']['best_score']:.3f}")

        print(f"\nРезультаты сохранены в: {trainer.output_dir}")

    print("\n" + "=" * 70)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 70)


if __name__ == "__main__":
    main()
