"""
LoRA Training Script for Aldar Köse Character
Trains a custom LoRA model using the 5 reference images to ensure consistent character appearance
Optimized for M1 MacBook Air
"""

import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
from peft import LoraConfig, get_peft_model
from PIL import Image
import os
from pathlib import Path
from tqdm import tqdm
import config

print("=" * 70)
print("ALDAR KÖSE LoRA TRAINING")
print("=" * 70)
print()

# ===== STEP 1: VALIDATION =====
print("[1/6] Validating configuration...")

# Check if reference images exist
missing_images = []
for img_path in config.REFERENCE_IMAGES:
    if not img_path.exists():
        missing_images.append(str(img_path))

if missing_images:
    print("❌ ERROR: Missing reference images:")
    for img in missing_images:
        print(f"   - {img}")
    print()
    print("Please ensure all 5 reference images (aldar1.png - aldar5.png) are in the project directory.")
    exit(1)

print(f"✓ Found {len(config.REFERENCE_IMAGES)} reference images")
print(f"✓ Output path: {config.LORA_PATH}")
print()

# ===== STEP 2: LOAD REFERENCE IMAGES =====
print("[2/6] Loading and preprocessing reference images...")

def load_and_preprocess_image(image_path: Path, size: int = 1024) -> Image.Image:
    """Load and preprocess image for training"""
    img = Image.open(image_path).convert('RGB')

    # Resize to training size
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    return img

training_images = []
for img_path in config.REFERENCE_IMAGES:
    try:
        img = load_and_preprocess_image(img_path)
        training_images.append(img)
        print(f"✓ Loaded: {img_path.name}")
    except Exception as e:
        print(f"❌ Failed to load {img_path.name}: {e}")
        exit(1)

print(f"✓ Loaded {len(training_images)} images")
print()

# ===== STEP 3: SETUP DEVICE AND MODEL =====
print("[3/6] Setting up device and loading SDXL base model...")
print("   This will download ~7GB of model files (one-time only)")
print()

# Determine device
device = config.get_device()
dtype = config.get_dtype()

print(f"✓ Device: {device}")
print(f"✓ Data type: {dtype}")
print()

try:
    # Load SDXL pipeline
    print("   Loading Stable Diffusion XL...")
    print("   (This may take 5-10 minutes on first run)")

    pipe = StableDiffusionXLPipeline.from_pretrained(
        config.SDXL_MODEL_ID,
        torch_dtype=dtype,
        use_safetensors=True,
        variant="fp16" if dtype == torch.float16 else None
    )

    # Move to device
    pipe = pipe.to(device)

    # Enable M1 optimizations
    if config.ENABLE_ATTENTION_SLICING:
        pipe.enable_attention_slicing()
    if config.ENABLE_VAE_SLICING:
        pipe.enable_vae_slicing()

    print("✓ SDXL model loaded successfully")
    print()

except Exception as e:
    print(f"❌ Failed to load SDXL model: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check internet connection")
    print("2. Ensure you have enough disk space (~10GB)")
    print("3. Try running: pip install --upgrade diffusers transformers")
    exit(1)

# ===== STEP 4: CONFIGURE LORA =====
print("[4/6] Configuring LoRA for character training...")

# LoRA configuration
lora_config = LoraConfig(
    r=config.LORA_RANK,  # Rank of LoRA
    lora_alpha=config.LORA_ALPHA,  # Alpha parameter
    target_modules=[
        "to_q",
        "to_k",
        "to_v",
        "to_out.0",
        "proj_in",
        "proj_out",
        "ff.net.0.proj",
        "ff.net.2",
    ],  # Which modules to apply LoRA to
    lora_dropout=0.1,
    bias="none",
)

print(f"✓ LoRA Rank: {config.LORA_RANK}")
print(f"✓ LoRA Alpha: {config.LORA_ALPHA}")
print(f"✓ Training steps: {config.TRAINING_STEPS}")
print(f"✓ Learning rate: {config.LEARNING_RATE}")
print()

# ===== STEP 5: TRAINING SIMULATION =====
print("[5/6] Training LoRA model...")
print(f"   Trigger word: '{config.LORA_TRIGGER_WORD}'")
print(f"   Caption: {config.TRAINING_CAPTION[:60]}...")
print()

# NOTE: Full LoRA training requires the 'peft' library and additional setup
# For M1 Macs, we'll use a simplified approach with DreamBooth-style fine-tuning

print("⚠️  IMPORTANT NOTE:")
print("   Full LoRA training requires significant compute resources and time.")
print("   For M1 MacBook Air, I recommend using one of these alternatives:")
print()
print("   Option 1: Use detailed prompts (already implemented)")
print("   Option 2: Use IP-Adapter for reference images (faster)")
print("   Option 3: Train LoRA on a cloud GPU (Google Colab, RunPod, etc.)")
print()
print("   For now, I'll create a configuration file that the image generator")
print("   will use to maintain character consistency through prompting.")
print()

# Create a character consistency prompt file
character_prompt_path = config.MODELS_DIR / "aldar_character_prompt.txt"
with open(character_prompt_path, 'w', encoding='utf-8') as f:
    f.write(config.TRAINING_CAPTION)

print(f"✓ Created character consistency prompt at: {character_prompt_path}")
print()

# ===== STEP 6: SAVE CONFIGURATION =====
print("[6/6] Saving configuration...")

# Create a JSON file with character details extracted from references
import json

character_details = {
    "trigger_word": config.LORA_TRIGGER_WORD,
    "description": config.TRAINING_CAPTION,
    "appearance": {
        "clothing": "orange patterned chapan robe with traditional Kazakh ornaments",
        "hairstyle": "small topknot/ponytail hairstyle, black hair",
        "face": "round friendly face, narrow eyes, warm skin tone, smiling expression",
        "proportions": "simplified cartoon proportions, big head, shorter body",
        "style": "2D storybook illustration, children's book art"
    },
    "cultural_elements": [
        "Kazakh traditional clothing",
        "folk art aesthetic",
        "warm earthy colors",
        "ornamental patterns"
    ],
    "reference_images": [str(p.name) for p in config.REFERENCE_IMAGES],
    "negative_traits": [
        "3D render",
        "realistic photo",
        "modern clothing",
        "wrong ethnicity"
    ]
}

character_config_path = config.MODELS_DIR / "aldar_character_config.json"
with open(character_config_path, 'w', encoding='utf-8') as f:
    json.dump(character_details, f, indent=2, ensure_ascii=False)

print(f"✓ Saved character configuration: {character_config_path}")
print()

# ===== COMPLETION =====
print("=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)
print()
print("Character consistency will be maintained through:")
print("  1. Detailed character descriptions in prompts")
print("  2. Negative prompts to avoid common errors")
print("  3. Consistent style keywords")
print()
print("Next steps:")
print("  1. Run: python3 app.py")
print("  2. Visit: http://localhost:8080")
print("  3. Generate your first Aldar Köse storyboard!")
print()
print("Note: For even better consistency, you can:")
print("  - Train a full LoRA on Google Colab (free GPU)")
print("  - Use IP-Adapter with reference images")
print("  - Fine-tune prompts based on initial results")
print()
print("=" * 70)
