"""
Configuration for Aldar Köse Storyboard Generator
Optimized for M1 MacBook Air
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
REFERENCE_IMAGES_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "static" / "generated"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ===== STABLE DIFFUSION XL CONFIGURATION =====

# Model settings
SDXL_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
SDXL_REFINER_ID = None  # Optional: "stabilityai/stable-diffusion-xl-refiner-1.0"

# LoRA settings
LORA_PATH = MODELS_DIR / "aldar_kose_lora.safetensors"
LORA_TRIGGER_WORD = "aldar_kose_character"
LORA_SCALE = 0.85  # How strongly to apply character style (0.0-1.0)

# Reference images for LoRA training
REFERENCE_IMAGES = [
    REFERENCE_IMAGES_DIR / "aldar1.png",
    REFERENCE_IMAGES_DIR / "aldar2.png",
    REFERENCE_IMAGES_DIR / "aldar3.png",
    REFERENCE_IMAGES_DIR / "aldar4.png",
    REFERENCE_IMAGES_DIR / "aldar5.png",
]

# ===== DEVICE CONFIGURATION (M1 Optimization) =====

# Device settings
DEVICE = "mps"  # Metal Performance Shaders for M1/M2/M3 Macs
DTYPE = "float16"  # Use FP16 for 2x speed on M1

# Enable M1 optimizations
ENABLE_ATTENTION_SLICING = True  # Reduce memory usage
ENABLE_VAE_SLICING = True  # Faster VAE decoding
ENABLE_VAE_TILING = True  # Handle larger images efficiently

# ===== GENERATION SETTINGS =====

# Image generation parameters
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024
NUM_INFERENCE_STEPS = 35  # Higher = better quality (20-50 recommended)
GUIDANCE_SCALE = 7.5  # How closely to follow prompt (7-9 recommended)

# Parallel generation settings
PARALLEL_BATCH_SIZE = 2  # M1 Air with 8GB can handle 2 images at once
MAX_WORKERS = 2  # Number of parallel workers

# Quality settings
ENABLE_QUALITY_VALIDATION = True
MAX_REGENERATION_ATTEMPTS = 2  # How many times to retry failed generations

# ===== LORA TRAINING CONFIGURATION =====

# Training parameters
LORA_RANK = 16  # LoRA rank (higher = more detail, but slower)
LORA_ALPHA = 16  # LoRA alpha (typically same as rank)
TRAINING_STEPS = 1000  # Number of training steps
LEARNING_RATE = 1e-4  # Learning rate
TRAIN_BATCH_SIZE = 1  # Batch size for training (M1 limitation)
GRADIENT_ACCUMULATION_STEPS = 4  # Simulate larger batch size

# Caption for training images (describes Aldar Köse)
TRAINING_CAPTION = (
    "aldar_kose_character, 2D storybook illustration of Kazakh folk hero, "
    "orange patterned chapan robe with traditional ornaments, "
    "friendly smiling expression, small topknot hairstyle, "
    "round face, warm skin tone, simplified cartoon proportions, "
    "children's book art style, professional illustration"
)

# ===== PROMPT ENHANCEMENT SETTINGS =====

# Base style prompt (concise for 77 token limit)
BASE_STYLE_PROMPT = (
    "2D storybook art, warm colors, detailed, Kazakh folk style"
)

# Negative prompt (concise for 77 token limit)
NEGATIVE_PROMPT = (
    "3D, CGI, photo, modern clothes, text, watermark, "
    "blurry, ugly, deformed, extra limbs, duplicate"
)

# ===== STORYBOARD SETTINGS =====

# Frame generation
MIN_FRAMES = 5
MAX_FRAMES = 9
DEFAULT_FRAMES = 7

# Available shot types
SHOT_TYPES = [
    'establishing',
    'wide',
    'medium',
    'two-shot',
    'close-up',
    'over-shoulder'
]

# Available morals
MORALS = [
    'kindness',
    'justice',
    'hospitality',
    'wisdom',
    'courage',
    'generosity'
]

# Lighting hint (consistent across all frames)
LIGHTING_HINT = "sunlight from the left, warm daylight, soft shadows"

# ===== API SETTINGS =====

# OpenAI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_MODEL = "gpt-4o-mini"  # Use gpt-4o-mini (cheaper and available to all)
GPT_TEMPERATURE = 0.7
GPT_MAX_TOKENS_STORY = 300
GPT_MAX_TOKENS_FRAMES = 2000

# ===== PERFORMANCE SETTINGS =====

# Cache settings
ENABLE_MODEL_CACHING = True  # Keep model in memory between requests
CACHE_TIMEOUT = 3600  # Seconds to keep model cached (1 hour)

# Lazy loading
LAZY_LOAD_MODEL = True  # Only load model when first generation request comes in

# Progress tracking
ENABLE_PROGRESS_TRACKING = True
PROGRESS_UPDATE_INTERVAL = 1.0  # Seconds between progress updates

# ===== DEBUG SETTINGS =====

DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
SAVE_DEBUG_IMAGES = DEBUG_MODE
VERBOSE_LOGGING = DEBUG_MODE

# ===== HELPER FUNCTIONS =====

def get_device():
    """Get the appropriate device for the current system"""
    import torch

    if torch.backends.mps.is_available():
        return "mps"  # M1/M2/M3 Mac
    elif torch.cuda.is_available():
        return "cuda"  # NVIDIA GPU
    else:
        return "cpu"  # Fallback to CPU

def get_dtype():
    """Get the appropriate dtype for the current device"""
    import torch

    device = get_device()
    if device in ["mps", "cuda"]:
        return torch.float16  # FP16 for GPU acceleration
    else:
        return torch.float32  # FP32 for CPU

def validate_config():
    """Validate configuration and check for missing files"""
    issues = []

    # Check reference images
    for img_path in REFERENCE_IMAGES:
        if not img_path.exists():
            issues.append(f"Reference image not found: {img_path}")

    # Check OpenAI API key
    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY not set in .env file")

    # Check if LoRA exists (warning, not error)
    if not LORA_PATH.exists():
        print(f"⚠️  Warning: LoRA model not found at {LORA_PATH}")
        print("   Run train_aldar_lora.py to create it")

    return issues

# Validate on import
if __name__ != "__main__":
    config_issues = validate_config()
    if config_issues:
        print("Configuration issues detected:")
        for issue in config_issues:
            print(f"  - {issue}")
