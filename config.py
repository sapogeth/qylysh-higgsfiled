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
NUM_INFERENCE_STEPS = 30  # Optimized: 30 steps = best quality/speed balance
GUIDANCE_SCALE = 8.0  # Increased for better prompt adherence with LoRA

# Scheduler settings (for speed optimization)
USE_FAST_SCHEDULER = True  # Use Euler Ancestral (faster, high quality)
SCHEDULER_TYPE = "euler_a"  # Options: "dpm", "euler_a", "ddim"

# Parallel generation settings
PARALLEL_BATCH_SIZE = 1  # M1 optimization: sequential is more stable
MAX_WORKERS = 1  # Single worker prevents memory issues

# Quality settings
ENABLE_QUALITY_VALIDATION = True
MAX_REGENERATION_ATTEMPTS = 2  # How many times to retry failed generations

# Speed optimizations
ENABLE_TORCH_COMPILE = False  # Disabled: torch.compile not stable on MPS yet
ENABLE_MODEL_CPU_OFFLOAD = False  # Keep model on MPS for speed
USE_KARRAS_SIGMAS = True  # Better noise schedule (quality improvement)

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
    "2D cel-shaded, anime-inspired illustration, smooth clean outlines, flat colors, soft shadows, "
    "warm palette, Kazakh folk style, child-friendly"
)

# Negative prompt (concise for 77 token limit)
NEGATIVE_PROMPT = (
    "3D, CGI, photorealistic, realistic, ray tracing, render, Unreal, Octane, 8k, HDR, "
    "hyper-detailed skin, glossy plastic look, harsh specular highlights, lens flare, depth of field, "
    "modern clothes, text, watermark, caption, logo, signature, "
    "blurry, ugly, deformed, extra limbs, duplicate, "
    "blue eyes, green eyes, grey eyes, blonde hair, white hair, red hair, no hat, missing hat, different hat, "
    "different clothing, wrong robe color, western clothing, jeans, t-shirt"
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

# Consistency settings
# A fixed set of traits and style cues that are injected into every image prompt
CHARACTER_TRAITS = {
    "name": "Aldar Kose",
    "eye_color": "dark brown",
    "hair": "black hair in a small topknot",
    "facial_hair": "distinct small mustache",
    "clothing": "orange patterned chapan robe with traditional Kazakh ornaments",
    "hat": "felt kalpak hat",
    "expression": "friendly, clever, mischievous",
}

STYLE_LOCK = (
    "consistent 2D cel-shaded anime-inspired style, smooth clean lineart, flat colors, "
    "soft ambient shading, warm earthy palette, consistent line thickness across frames"
)

# ===== IDENTITY LOCK SETTINGS (IP-Adapter) =====

# Enable IP-Adapter for stronger character consistency
USE_IDENTITY_LOCK = False  # Set to True to enable IP-Adapter reference-based generation

# Reference image to use for identity lock (when USE_IDENTITY_LOCK=True)
# Options: aldar1.png, aldar2.png, aldar3.png, aldar4.png, aldar5.png
IDENTITY_REFERENCE_IMAGE = "aldar1.png"

# IP-Adapter strength (0.0-1.0)
# Lower = more creative freedom, Higher = stronger match to reference
# Recommended: 0.5-0.7 for balance between consistency and scene variety
IP_ADAPTER_SCALE = 0.6

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

    # Note: LoRA is optional - no warning needed
    # Base SDXL works fine without it

    return issues

# Validate on import
if __name__ != "__main__":
    config_issues = validate_config()
    if config_issues:
        print("Configuration issues detected:")
        for issue in config_issues:
            print(f"  - {issue}")
