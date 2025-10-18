"""
Local Image Generator using Stable Diffusion XL
Optimized for M1 MacBook Air with character consistency for Aldar Köse
"""

import torch
from diffusers import (
    StableDiffusionXLPipeline,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
    DDIMScheduler
)
from PIL import Image
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import config
from prompt_enhancer import PromptEnhancer


class LocalImageGenerator:
    """
    Local SDXL-based image generator with M1 optimization
    """

    def __init__(self, progress_callback: Optional[Callable] = None, lazy_load: bool = None):
        """
        Initialize the local image generator

        Args:
            progress_callback: Optional callback function for progress updates
            lazy_load: If True, only load model on first generation (default from config)
        """
        self.progress_callback = progress_callback
        self.pipe = None
        self.enhancer = PromptEnhancer()
        self.device = config.get_device()
        self.dtype = config.get_dtype()

        # Determine if we should lazy load
        self.lazy_load = lazy_load if lazy_load is not None else config.LAZY_LOAD_MODEL

        # Load model immediately if not lazy loading
        if not self.lazy_load:
            self._load_model()
        else:
            print("✓ Image generator initialized (model will load on first request)")

    def _log_progress(self, message: str, step: int = 0, total: int = 100):
        """Log progress message and call callback if provided"""
        print(message)
        if self.progress_callback:
            self.progress_callback({
                'message': message,
                'step': step,
                'total': total,
                'percentage': int((step / total) * 100) if total > 0 else 0
            })

    def _load_model(self):
        """Load the Stable Diffusion XL model with optimizations"""

        self._log_progress("Loading Stable Diffusion XL model...", 0, 100)

        try:
            # Load SDXL pipeline
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                config.SDXL_MODEL_ID,
                torch_dtype=self.dtype,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            )

            # Choose optimal scheduler based on config
            self._log_progress("Configuring scheduler...", 20, 100)
            if config.USE_FAST_SCHEDULER:
                scheduler_type = config.SCHEDULER_TYPE.lower()

                if scheduler_type == "euler_a":
                    # Euler Ancestral: Fast and high quality
                    scheduler_config = self.pipe.scheduler.config
                    if config.USE_KARRAS_SIGMAS:
                        scheduler_config.use_karras_sigmas = True

                    self.pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
                        scheduler_config
                    )
                    self._log_progress("✓ Using Euler Ancestral scheduler (fast, high quality)", 25, 100)
                    if config.USE_KARRAS_SIGMAS:
                        self._log_progress("✓ Enabled Karras sigmas (better noise schedule)", 30, 100)
                elif scheduler_type == "ddim":
                    # DDIM: Very fast, good quality
                    self.pipe.scheduler = DDIMScheduler.from_config(
                        self.pipe.scheduler.config
                    )
                    self._log_progress("✓ Using DDIM scheduler (very fast)", 25, 100)
                else:
                    # Default: DPM-Solver++ (balanced)
                    scheduler_config = self.pipe.scheduler.config
                    if config.USE_KARRAS_SIGMAS:
                        scheduler_config.use_karras_sigmas = True

                    self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                        scheduler_config
                    )
                    self._log_progress("✓ Using DPM-Solver++ scheduler (balanced)", 25, 100)
                    if config.USE_KARRAS_SIGMAS:
                        self._log_progress("✓ Enabled Karras sigmas (better noise schedule)", 30, 100)

            # Move to device
            self.pipe = self.pipe.to(self.device)
            self._log_progress("✓ Moved model to MPS device", 40, 100)

            # Apply M1 optimizations
            if config.ENABLE_ATTENTION_SLICING:
                self.pipe.enable_attention_slicing()
                self._log_progress("✓ Enabled attention slicing", 50, 100)

            if config.ENABLE_VAE_SLICING:
                self.pipe.enable_vae_slicing()
                self._log_progress("✓ Enabled VAE slicing", 60, 100)

            if config.ENABLE_VAE_TILING:
                self.pipe.enable_vae_tiling()
                self._log_progress("✓ Enabled VAE tiling", 70, 100)

            # Torch compile for M1 speed boost (PyTorch 2.0+)
            # Note: Currently disabled as torch.compile is not stable on MPS
            if config.ENABLE_TORCH_COMPILE and hasattr(torch, 'compile'):
                try:
                    self._log_progress("Compiling model with torch.compile...", 75, 100)
                    self.pipe.unet = torch.compile(self.pipe.unet, mode="reduce-overhead", backend="aot_eager")
                    self._log_progress("✓ Model compiled (15-25% faster generation)", 80, 100)
                except Exception as e:
                    self._log_progress(f"⚠️  Torch compile not available: {e}", 80, 100)

            # Check if LoRA exists and load it
            if config.LORA_PATH.exists():
                try:
                    self.pipe.load_lora_weights(str(config.LORA_PATH))
                    self._log_progress(f"✓ Loaded Aldar Köse LoRA (character consistency enabled)", 90, 100)
                except Exception as e:
                    self._log_progress(f"⚠️  LoRA loading failed: {e}", 90, 100)
            else:
                self._log_progress("⚠️  LoRA not found - will use base SDXL only", 90, 100)

            self._log_progress("✓ SDXL model loaded successfully!", 100, 100)

        except Exception as e:
            error_msg = f"Failed to load SDXL model: {e}"
            self._log_progress(f"❌ {error_msg}", 0, 100)
            raise RuntimeError(error_msg)

    def generate_single(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = None,
        guidance_scale: float = None,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Generate a single image from a prompt

        Args:
            prompt: Text prompt for image generation
            negative_prompt: Negative prompt (what to avoid)
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducibility

        Returns:
            PIL Image
        """

        # Lazy load model if not already loaded
        if self.pipe is None:
            print("Loading model for first generation...")
            self._load_model()

        # Use config defaults if not specified
        num_inference_steps = num_inference_steps or config.NUM_INFERENCE_STEPS
        guidance_scale = guidance_scale or config.GUIDANCE_SCALE
        negative_prompt = negative_prompt or config.NEGATIVE_PROMPT

        # Set seed for reproducibility
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None

        # Generate image
        with torch.no_grad():
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                height=config.IMAGE_HEIGHT,
                width=config.IMAGE_WIDTH,
            )

        return result.images[0]

    def generate_parallel(
        self,
        prompts: List[str],
        negative_prompts: Optional[List[str]] = None,
        batch_size: int = None
    ) -> List[Image.Image]:
        """
        Generate multiple images in parallel batches

        Args:
            prompts: List of text prompts
            negative_prompts: List of negative prompts (one per prompt)
            batch_size: Number of images to generate simultaneously

        Returns:
            List of PIL Images
        """

        # Lazy load model if not already loaded
        if self.pipe is None:
            print("Loading model for first generation...")
            self._load_model()

        batch_size = batch_size or config.PARALLEL_BATCH_SIZE
        num_prompts = len(prompts)

        # Use same negative prompt for all if not provided
        if negative_prompts is None:
            negative_prompts = [config.NEGATIVE_PROMPT] * num_prompts

        all_images = []

        # Process in batches
        for batch_start in range(0, num_prompts, batch_size):
            batch_end = min(batch_start + batch_size, num_prompts)
            batch_prompts = prompts[batch_start:batch_end]
            batch_negatives = negative_prompts[batch_start:batch_end]

            self._log_progress(
                f"Generating images {batch_start + 1}-{batch_end} of {num_prompts}...",
                batch_start,
                num_prompts
            )

            # Generate batch
            with torch.no_grad():
                # For M1, process one at a time in the batch to avoid memory issues
                batch_images = []
                for prompt, neg_prompt in zip(batch_prompts, batch_negatives):
                    img = self.generate_single(prompt, neg_prompt)
                    batch_images.append(img)

            all_images.extend(batch_images)

        self._log_progress(f"✓ Generated {num_prompts} images successfully!", num_prompts, num_prompts)

        return all_images

    def generate_from_frames(
        self,
        frames: List[Dict[str, Any]],
        save_dir: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate images for storyboard frames

        Args:
            frames: List of frame dictionaries from GPT-4
            save_dir: Optional directory to save images

        Returns:
            List of frames with added 'image' and 'image_path' keys
        """

        total_frames = len(frames)
        self._log_progress(f"Starting generation for {total_frames} frames...", 0, total_frames)

        # Enhance prompts
        enhanced_prompts = self.enhancer.enhance_batch(frames)

        # Extract positive and negative prompts
        positive_prompts = [p['positive'] for p in enhanced_prompts]
        negative_prompts = [p['negative'] for p in enhanced_prompts]

        # Track timing for ETA
        start_time = time.time()
        images = []

        # Generate images one by one with progress tracking
        for idx, (pos_prompt, neg_prompt) in enumerate(zip(positive_prompts, negative_prompts)):
            frame_start = time.time()

            # Log progress with ETA
            if idx > 0:
                elapsed = time.time() - start_time
                avg_time_per_frame = elapsed / idx
                remaining_frames = total_frames - idx
                eta_seconds = avg_time_per_frame * remaining_frames
                eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                self._log_progress(
                    f"Generating frame {idx + 1}/{total_frames} (ETA: {eta_str})...",
                    idx,
                    total_frames
                )
            else:
                self._log_progress(
                    f"Generating frame {idx + 1}/{total_frames}...",
                    idx,
                    total_frames
                )

            # Generate single image
            image = self.generate_single(pos_prompt, neg_prompt)
            images.append(image)

            # Log frame completion time
            frame_time = time.time() - frame_start
            self._log_progress(
                f"✓ Frame {idx + 1} complete ({frame_time:.1f}s)",
                idx + 1,
                total_frames
            )

        # Save images and update frames
        save_dir = save_dir or config.OUTPUT_DIR
        save_dir.mkdir(exist_ok=True, parents=True)

        for idx, (frame, image) in enumerate(zip(frames, images)):
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'frame_{idx + 1:03d}_{timestamp}.png'
            filepath = save_dir / filename

            # Save image
            image.save(filepath, 'PNG', optimize=True)

            # Update frame with image info
            frame['image'] = image
            frame['image_path'] = filepath
            frame['image_url'] = f'/static/generated/{filename}'
            frame['prompt_used'] = positive_prompts[idx]

        total_time = time.time() - start_time
        avg_time = total_time / total_frames
        self._log_progress(
            f"✓ All {total_frames} frames complete! Total: {total_time:.1f}s, Avg: {avg_time:.1f}s/frame",
            total_frames,
            total_frames
        )

        return frames

    def regenerate_frame(
        self,
        frame: Dict[str, Any],
        variation_type: str = 'angle'
    ) -> Image.Image:
        """
        Regenerate a single frame with variations

        Args:
            frame: Frame dictionary
            variation_type: Type of variation to apply

        Returns:
            New PIL Image
        """

        # Create variation prompt
        varied_prompt = self.enhancer.create_variation_prompt(frame, variation_type)
        negative_prompt = self.enhancer.get_negative_prompt()

        # Generate with different seed
        import random
        seed = random.randint(0, 2**32 - 1)

        return self.generate_single(varied_prompt, negative_prompt, seed=seed)

    def cleanup(self):
        """Clean up resources and free memory"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None

        # Clear CUDA/MPS cache
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()

        self._log_progress("✓ Cleaned up resources", 100, 100)


def test_generator():
    """Test the image generator with a sample prompt"""

    print("=" * 70)
    print("TESTING LOCAL IMAGE GENERATOR")
    print("=" * 70)
    print()

    def progress_callback(info):
        print(f"[{info['percentage']}%] {info['message']}")

    # Initialize generator
    generator = LocalImageGenerator(progress_callback=progress_callback)

    # Test frame
    test_frame = {
        'description': 'Aldar Köse walks across the vast golden steppe under a wide sky',
        'shot_type': 'establishing',
        'setting': 'Kazakh steppe at sunrise',
        'key_objects': ['steppe', 'grass', 'sky', 'horizon'],
        'lighting_hint': 'sunlight from the left, warm daylight, soft shadows'
    }

    print("\nTest Frame:")
    print(test_frame)
    print()

    # Generate image
    start_time = time.time()
    frames_with_images = generator.generate_from_frames([test_frame])
    elapsed = time.time() - start_time

    print()
    print(f"✓ Generation completed in {elapsed:.2f} seconds")
    print(f"✓ Image saved to: {frames_with_images[0]['image_path']}")
    print()

    # Cleanup
    generator.cleanup()

    print("=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    test_generator()
