#!/usr/bin/env python3
"""
Automated setup script for IndexTTS integration
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True


def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            return True
        else:
            logger.warning("CUDA not available, will use CPU")
            return False
    except ImportError:
        logger.warning("PyTorch not installed, CUDA check skipped")
        return False


def install_dependencies():
    """Install required dependencies"""
    logger.info("Installing dependencies...")

    # Update requirements.txt if needed
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        return False

    try:
        # Install from requirements.txt (excluding indextts which will be installed from source)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                       check=True, capture_output=True, text=True)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e.stderr}")
        return False


def init_submodule():
    """Initialize IndexTTS submodule"""
    logger.info("Initializing IndexTTS submodule...")

    try:
        result = subprocess.run(["git", "submodule", "update", "--init", "--recursive", "TTS/index-tts"],
                                capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("IndexTTS submodule initialized successfully")
            return True
        else:
            logger.error(f"Failed to initialize submodule: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error initializing submodule: {e}")
        return False


def install_index_tts_from_source():
    """Install IndexTTS from source code in submodule"""
    logger.info("Installing IndexTTS from source...")

    index_tts_path = Path("TTS/index-tts")
    if not index_tts_path.exists():
        logger.error("IndexTTS submodule not found")
        return False

    try:
        # Change to IndexTTS directory
        original_dir = os.getcwd()
        os.chdir(index_tts_path)

        # Install in development mode
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."],
                                capture_output=True, text=True)

        # Change back to original directory
        os.chdir(original_dir)

        if result.returncode == 0:
            logger.info("IndexTTS installed from source successfully")
            return True
        else:
            logger.error(
                f"Failed to install IndexTTS from source: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error installing IndexTTS from source: {e}")
        # Change back to original directory in case of error
        os.chdir(original_dir)
        return False


def create_directories():
    """Create necessary directories"""
    logger.info("Creating directories...")

    directories = [
        "TTS/models/index_tts",
        "TTS/models/index_tts/voices"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

    return True


def download_models():
    """Download IndexTTS models"""
    logger.info("Downloading IndexTTS models...")

    try:
        # Import and run download function
        sys.path.append("TTS")
        from download_index_tts import download_index_tts_models

        if download_index_tts_models("TTS/models/index_tts"):
            logger.info("Models downloaded successfully")
            return True
        else:
            logger.error("Failed to download models")
            return False

    except ImportError:
        logger.error("download_index_tts.py not found")
        return False
    except Exception as e:
        logger.error(f"Error downloading models: {e}")
        return False


def test_installation():
    """Test the installation"""
    logger.info("Testing installation...")

    try:
        # Test import
        sys.path.append("TTS")
        from IndexTTService import IndexTTService

        # Test initialization
        tts_service = IndexTTService(
            model_dir="TTS/models/index_tts",
            char="test"
        )

        logger.info("IndexTTS service initialized successfully")

        # Test available voices
        voices = tts_service.get_available_voices()
        logger.info(f"Available voices: {len(voices)}")

        return True

    except Exception as e:
        logger.error(f"Installation test failed: {e}")
        return False


def create_sample_voice():
    """Create a sample reference voice if none exists"""
    logger.info("Checking for reference voices...")

    voice_dir = Path("TTS/models/index_tts/voices")
    voice_files = list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3"))

    if not voice_files:
        logger.warning("No reference voices found")
        logger.info(
            "Please add reference voice files to TTS/models/index_tts/voices/")
        logger.info("Supported formats: .wav, .mp3, .flac, .m4a")
        logger.info(
            "Recommended: 5-30 seconds of clear speech without background noise")
        return False
    else:
        logger.info(f"Found {len(voice_files)} reference voice(s)")
        for voice in voice_files:
            logger.info(f"  - {voice.name}")
        return True


def main():
    """Main setup function"""
    logger.info("Starting IndexTTS setup...")
    logger.info("=" * 50)

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    check_cuda()

    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)

    # Initialize submodule
    if not init_submodule():
        logger.error("Failed to initialize submodule")
        sys.exit(1)

    # Install IndexTTS from source
    if not install_index_tts_from_source():
        logger.error("Failed to install IndexTTS from source")
        sys.exit(1)

    # Create directories
    if not create_directories():
        logger.error("Failed to create directories")
        sys.exit(1)

    # Download models
    if not download_models():
        logger.error("Failed to download models")
        sys.exit(1)

    # Test installation
    if not test_installation():
        logger.error("Installation test failed")
        sys.exit(1)

    # Check reference voices
    create_sample_voice()

    logger.info("=" * 50)
    logger.info("IndexTTS setup completed successfully!")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Add reference voice files to TTS/models/index_tts/voices/")
    logger.info("2. Run test: python TTS/test_index_tts.py")
    logger.info("3. Check examples: python TTS/example_usage.py")
    logger.info("")
    logger.info("For more information, see:")
    logger.info("- TTS/README_IndexTTS.md")
    logger.info("- TTS/migration_guide.md")


if __name__ == "__main__":
    main()
