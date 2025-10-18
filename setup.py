#!/usr/bin/env python3
"""
Setup Script for Aldar Köse Storyboard Generator
Automates the installation and configuration process
"""

import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print()
    print("=" * 70)
    print(title.center(70))
    print("=" * 70)
    print()


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {command}")
    print()

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        print(result.stderr)
        return False

    print(f"✓ {description} completed successfully")
    print()
    return True


def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        print("   Please upgrade Python and try again")
        return False

    print("✓ Python version is compatible")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")

    print("This will install:")
    print("  - PyTorch (for M1 Mac)")
    print("  - Diffusers (Stable Diffusion XL)")
    print("  - Transformers, Accelerate, PEFT")
    print("  - Flask, OpenAI, and other utilities")
    print()
    print("Download size: ~3GB")
    print("This may take 10-15 minutes...")
    print()

    # Upgrade pip first
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ):
        return False

    # Install PyTorch for M1 Mac
    print("Installing PyTorch with M1 (MPS) support...")
    if not run_command(
        f"{sys.executable} -m pip install torch torchvision",
        "Installing PyTorch"
    ):
        return False

    # Install requirements
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements"
    ):
        return False

    return True


def setup_directories():
    """Create necessary directories"""
    print_header("Setting Up Directories")

    directories = [
        "models",
        "static/generated",
        "static/css",
        "static/js",
        "templates"
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}/")

    print()
    print("✓ All directories created successfully")
    return True


def check_reference_images():
    """Check if reference images exist"""
    print_header("Checking Reference Images")

    base_dir = Path(".")
    reference_images = [
        "aldar1.png",
        "aldar2.png",
        "aldar3.png",
        "aldar4.png",
        "aldar5.png"
    ]

    all_found = True

    for img in reference_images:
        path = base_dir / img
        if path.exists():
            print(f"✓ Found: {img}")
        else:
            print(f"❌ Missing: {img}")
            all_found = False

    if not all_found:
        print()
        print("⚠️  Warning: Some reference images are missing")
        print("   The system will work, but character consistency may be lower")
        print("   Please add the missing images for best results")

    return True  # Don't fail on missing references


def check_env_file():
    """Check if .env file exists with OpenAI API key"""
    print_header("Checking Environment Configuration")

    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found")
        print()
        print("Creating .env template...")

        with open(env_path, 'w') as f:
            f.write("# OpenAI API Key (required for story generation)\n")
            f.write("OPENAI_API_KEY=your_api_key_here\n")
            f.write("\n")
            f.write("# Debug mode (optional)\n")
            f.write("DEBUG=False\n")

        print("✓ Created .env template")
        print()
        print("⚠️  IMPORTANT: Please edit .env and add your OpenAI API key")
        print("   Get your key from: https://platform.openai.com/api-keys")
        return False

    # Check if API key is set
    with open(env_path, 'r') as f:
        content = f.read()

    if "your_api_key_here" in content or "OPENAI_API_KEY=" not in content:
        print("⚠️  OpenAI API key not configured in .env")
        print("   Please edit .env and add your API key")
        return False

    print("✓ .env file configured")
    return True


def run_character_setup():
    """Run the character configuration setup"""
    print_header("Configuring Aldar Köse Character")

    print("Running character setup script...")
    print("This will:")
    print("  1. Load SDXL model (~7GB download on first run)")
    print("  2. Create character configuration from reference images")
    print("  3. Test the setup")
    print()

    if not run_command(
        f"{sys.executable} train_aldar_lora.py",
        "Character setup"
    ):
        print("⚠️  Character setup encountered issues")
        print("   The system will still work with prompt-based consistency")
        return True  # Don't fail completely

    return True


def print_next_steps():
    """Print final instructions"""
    print_header("Setup Complete!")

    print("Your Aldar Köse Storyboard Generator is ready!")
    print()
    print("Next steps:")
    print()
    print("1. Start the server:")
    print("   python3 app.py")
    print()
    print("2. Open your browser:")
    print("   http://localhost:8080")
    print()
    print("3. Enter any story prompt and generate your first storyboard!")
    print()
    print("Tips:")
    print("  - First generation will download SDXL model (~7GB)")
    print("  - Each storyboard takes 30-60 seconds to generate")
    print("  - Images are saved in static/generated/")
    print("  - Character appearance is based on your 5 reference images")
    print()
    print("=" * 70)


def main():
    """Main setup workflow"""
    print_header("ALDAR KÖSE STORYBOARD GENERATOR SETUP")

    print("This script will set up your local SDXL-based storyboard generator")
    print("optimized for M1 MacBook Air.")
    print()

    steps = [
        ("Checking Python version", check_python_version),
        ("Setting up directories", setup_directories),
        ("Checking reference images", check_reference_images),
        ("Checking environment configuration", check_env_file),
        ("Installing dependencies", install_dependencies),
        ("Configuring character", run_character_setup),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)

    print()

    if failed_steps:
        print_header("Setup Completed with Warnings")
        print("The following steps had issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print()
        print("You may need to:")
        print("  1. Add your OpenAI API key to .env")
        print("  2. Manually install dependencies if needed")
        print("  3. Add missing reference images")
        print()
    else:
        print_next_steps()


if __name__ == "__main__":
    main()
