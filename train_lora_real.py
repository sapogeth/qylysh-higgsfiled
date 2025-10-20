"""
Реальное обучение LoRA для генерации Алдар Косе
Использует PEFT (Parameter-Efficient Fine-Tuning) для обучения LoRA адаптера
"""

import torch
import torch.nn.functional as F
from diffusers import StableDiffusionXLPipeline, DDPMScheduler, UNet2DConditionModel
from transformers import CLIPTextModel, CLIPTokenizer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from PIL import Image
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
import config
from feature_analyzer import FeatureAnalyzer


class LoRATrainer:
    """
    Реальный тренер LoRA для Stable Diffusion XL
    """

    def __init__(self, reference_images: list, output_path: Path):
        """
        Инициализация тренера

        Args:
            reference_images: Список путей к референсным изображениям
            output_path: Путь для сохранения обученной LoRA
        """
        self.reference_images = reference_images
        self.output_path = output_path
        self.device = config.get_device()
        self.dtype = config.get_dtype()

        print("=" * 70)
        print("ИНИЦИАЛИЗАЦИЯ РЕАЛЬНОГО ОБУЧЕНИЯ LORA")
        print("=" * 70)
        print()

    def load_base_model(self):
        """Загрузка базовой SDXL модели"""
        print("[1/5] Загрузка базовой SDXL модели...")

        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            config.SDXL_MODEL_ID,
            torch_dtype=self.dtype,
            use_safetensors=True,
            variant="fp16" if self.dtype == torch.float16 else None
        )

        # Переносим на устройство
        self.pipe = self.pipe.to(self.device)

        # Оптимизации для M1
        if config.ENABLE_ATTENTION_SLICING:
            self.pipe.enable_attention_slicing()
        if config.ENABLE_VAE_SLICING:
            self.pipe.enable_vae_slicing()

        print("✓ SDXL модель загружена")
        print()

    def analyze_references(self):
        """Анализ референсных изображений для извлечения промпта"""
        print("[2/5] Анализ референсных изображений...")

        analyzer = FeatureAnalyzer()
        aggregated = analyzer.analyze_reference_images(self.reference_images)

        # Генерация промпта
        self.training_prompt = analyzer.generate_training_prompt(aggregated)

        # Сохранение анализа
        analysis_path = config.MODELS_DIR / "training_analysis.json"
        analyzer.save_analysis(aggregated, analysis_path)

        print(f"✓ Промпт для обучения: {self.training_prompt}")
        print()

        return self.training_prompt

    def setup_lora(self):
        """Настройка LoRA конфигурации"""
        print("[3/5] Настройка LoRA адаптера...")

        # LoRA конфигурация для UNet
        lora_config = LoraConfig(
            r=config.LORA_RANK,  # 16
            lora_alpha=config.LORA_ALPHA,  # 16
            target_modules=[
                "to_q", "to_k", "to_v", "to_out.0",
                "proj_in", "proj_out",
                "ff.net.0.proj", "ff.net.2"
            ],
            lora_dropout=0.1,
            bias="none",
        )

        # Применяем LoRA к UNet
        self.pipe.unet = get_peft_model(self.pipe.unet, lora_config)

        print(f"✓ LoRA настроена (rank={config.LORA_RANK}, alpha={config.LORA_ALPHA})")
        print(f"✓ Обучаемые параметры: {self.pipe.unet.get_nb_trainable_parameters()}")
        print()

    def prepare_training_data(self):
        """Подготовка тренировочных данных"""
        print("[4/5] Подготовка тренировочных данных...")

        self.images = []
        self.prompts = []

        for img_path in self.reference_images:
            # Загрузка и предобработка изображения
            img = Image.open(img_path).convert('RGB')
            img = img.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT), Image.Resampling.LANCZOS)

            self.images.append(img)
            # Используем один и тот же промпт для всех изображений
            self.prompts.append(self.training_prompt)

        print(f"✓ Загружено {len(self.images)} изображений")
        print()

    def train(self, num_epochs: int = 100, learning_rate: float = 1e-4):
        """
        Обучение LoRA

        Args:
            num_epochs: Количество эпох обучения
            learning_rate: Learning rate
        """
        print("[5/5] Начало обучения LoRA...")
        print(f"  Эпохи: {num_epochs}")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Устройство: {self.device}")
        print()

        # Оптимизатор (только для LoRA параметров)
        optimizer = torch.optim.AdamW(
            self.pipe.unet.parameters(),
            lr=learning_rate,
            betas=(0.9, 0.999),
            weight_decay=1e-2
        )

        # Scheduler для noise
        noise_scheduler = DDPMScheduler.from_pretrained(
            config.SDXL_MODEL_ID,
            subfolder="scheduler"
        )

        # Training loop
        self.pipe.unet.train()

        progress_bar = tqdm(range(num_epochs), desc="Обучение")

        for epoch in progress_bar:
            total_loss = 0

            for img, prompt in zip(self.images, self.prompts):
                # Конвертируем изображение в latent
                with torch.no_grad():
                    # Нормализация
                    img_tensor = torch.from_numpy(np.array(img)).float() / 255.0
                    img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)  # [1, 3, H, W]
                    img_tensor = img_tensor.to(self.device, dtype=self.dtype)

                    # Нормализация для VAE
                    img_tensor = (img_tensor - 0.5) * 2.0

                    # Encode в latent space
                    latents = self.pipe.vae.encode(img_tensor).latent_dist.sample()
                    latents = latents * self.pipe.vae.config.scaling_factor

                # Добавляем шум
                noise = torch.randn_like(latents)
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps,
                    (1,), device=self.device
                ).long()

                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                # Получаем text embeddings
                with torch.no_grad():
                    text_inputs = self.pipe.tokenizer(
                        prompt,
                        padding="max_length",
                        max_length=self.pipe.tokenizer.model_max_length,
                        truncation=True,
                        return_tensors="pt"
                    )
                    text_embeddings = self.pipe.text_encoder(
                        text_inputs.input_ids.to(self.device)
                    )[0]

                    # Для SDXL нужен второй text encoder
                    text_inputs_2 = self.pipe.tokenizer_2(
                        prompt,
                        padding="max_length",
                        max_length=self.pipe.tokenizer_2.model_max_length,
                        truncation=True,
                        return_tensors="pt"
                    )
                    text_embeddings_2 = self.pipe.text_encoder_2(
                        text_inputs_2.input_ids.to(self.device)
                    )[0]

                    # Объединяем embeddings
                    pooled_prompt_embeds = text_embeddings_2
                    prompt_embeds = torch.cat([text_embeddings, text_embeddings_2], dim=-1)

                # Предсказание noise
                model_pred = self.pipe.unet(
                    noisy_latents,
                    timesteps,
                    encoder_hidden_states=prompt_embeds,
                    added_cond_kwargs={
                        "text_embeds": pooled_prompt_embeds,
                        "time_ids": torch.zeros((1, 6), device=self.device, dtype=self.dtype)
                    }
                ).sample

                # Loss
                loss = F.mse_loss(model_pred, noise, reduction="mean")

                # Backward
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(self.images)
            progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})

            # Сохранение чекпоинта каждые 20 эпох
            if (epoch + 1) % 20 == 0:
                self.save_checkpoint(epoch + 1, avg_loss)

        print()
        print("✓ Обучение завершено!")
        print()

    def save_checkpoint(self, epoch: int, loss: float):
        """Сохранение чекпоинта LoRA"""
        checkpoint_path = self.output_path.parent / f"lora_checkpoint_epoch{epoch}.safetensors"

        # Сохраняем только LoRA веса
        self.pipe.unet.save_pretrained(checkpoint_path)

        print(f"  💾 Чекпоинт сохранён: {checkpoint_path} (epoch {epoch}, loss: {loss:.4f})")

    def save_final_model(self):
        """Сохранение финальной модели"""
        print("Сохранение финальной LoRA модели...")

        # Сохраняем LoRA веса
        self.pipe.unet.save_pretrained(self.output_path)

        # Сохраняем метаданные
        metadata = {
            "model_type": "LoRA for SDXL",
            "base_model": config.SDXL_MODEL_ID,
            "training_prompt": self.training_prompt,
            "trigger_word": config.LORA_TRIGGER_WORD,
            "lora_rank": config.LORA_RANK,
            "lora_alpha": config.LORA_ALPHA,
            "num_reference_images": len(self.reference_images),
            "reference_images": [str(p.name) for p in self.reference_images]
        }

        metadata_path = self.output_path.parent / "lora_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"✓ LoRA модель сохранена: {self.output_path}")
        print(f"✓ Метаданные сохранены: {metadata_path}")
        print()

    def generate_test_image(self, prompt: str) -> Image.Image:
        """Генерация тестового изображения с обученной LoRA"""
        print("Генерация тестового изображения...")

        self.pipe.unet.eval()

        with torch.no_grad():
            image = self.pipe(
                prompt=prompt,
                negative_prompt=config.NEGATIVE_PROMPT,
                num_inference_steps=config.NUM_INFERENCE_STEPS,
                guidance_scale=config.GUIDANCE_SCALE,
                height=config.IMAGE_HEIGHT,
                width=config.IMAGE_WIDTH
            ).images[0]

        test_image_path = config.OUTPUT_DIR / "lora_test_generation.png"
        image.save(test_image_path)

        print(f"✓ Тестовое изображение сохранено: {test_image_path}")
        print()

        return image


def main():
    """Основная функция обучения"""

    print("=" * 70)
    print("РЕАЛЬНОЕ ОБУЧЕНИЕ LORA ДЛЯ АЛДАР КОСЕ")
    print("=" * 70)
    print()

    # Инициализация тренера
    trainer = LoRATrainer(
        reference_images=config.REFERENCE_IMAGES,
        output_path=config.LORA_PATH
    )

    # Загрузка базовой модели
    trainer.load_base_model()

    # Анализ референсов
    training_prompt = trainer.analyze_references()

    # Настройка LoRA
    trainer.setup_lora()

    # Подготовка данных
    trainer.prepare_training_data()

    # Обучение
    # ВАЖНО: для M1 MacBook Air рекомендуется меньше эпох (100-200)
    # Для более мощных систем можно увеличить до 500-1000
    trainer.train(
        num_epochs=100,  # Начните с малого для тестирования
        learning_rate=1e-4
    )

    # Сохранение модели
    trainer.save_final_model()

    # Генерация тестового изображения
    test_prompt = f"{config.LORA_TRIGGER_WORD}, {training_prompt}"
    trainer.generate_test_image(test_prompt)

    print("=" * 70)
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 70)
    print()
    print("Следующие шаги:")
    print("  1. Проверьте тестовое изображение в static/generated/lora_test_generation.png")
    print("  2. Запустите конкурентное сравнение: python3 train_lora_competitive.py")
    print("  3. Используйте обученную LoRA в приложении: python3 app.py")
    print()


if __name__ == "__main__":
    main()
