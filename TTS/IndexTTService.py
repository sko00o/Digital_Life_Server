import sys
import time
import os
import logging
import torch
import soundfile as sf
import numpy as np
from pathlib import Path

# Set environment variables for IndexTTS
os.environ["PYTORCH_JIT"] = "0"

# Import IndexTTS
try:
    from indextts.infer import IndexTTS
    logger = logging.getLogger(__name__)
except ImportError:
    print("IndexTTS not found. Please ensure either:")
    print("1. Submodule is initialized: git submodule update --init --recursive")
    print("2. Or install via pip: pip install indextts")
    sys.exit(1)

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


class IndexTTService:
    def __init__(self, model_dir="TTS/models/index_tts", config_path=None, char="default"):
        """
        Initialize IndexTTS service

        Args:
            model_dir: Directory containing IndexTTS model files
            config_path: Path to config.yaml file
            char: Character name (for compatibility with original TTService)
        """
        logging.info(f'Initializing IndexTTS Service for {char}...')

        self.model_dir = Path(model_dir)
        self.char = char

        # Set default config path if not provided
        if config_path is None:
            config_path = self.model_dir / "config.yaml"

        # Check if model files exist
        required_files = [
            "config.yaml",
            "bigvgan_discriminator.pth",
            "bigvgan_generator.pth",
            "bpe.model",
            "dvae.pth",
            "gpt.pth",
            "unigram_12000.vocab"
        ]

        missing_files = []
        for file in required_files:
            if not (self.model_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            logging.error(f"Missing IndexTTS model files: {missing_files}")
            logging.info("Please download IndexTTS models using:")
            logging.info("huggingface-cli download IndexTeam/IndexTTS-1.5 \\")
            logging.info(
                "  config.yaml bigvgan_discriminator.pth bigvgan_generator.pth bpe.model dvae.pth gpt.pth unigram_12000.vocab \\")
            logging.info(f"  --local-dir {self.model_dir}")
            raise FileNotFoundError(
                f"Missing IndexTTS model files: {missing_files}")

        # Initialize IndexTTS
        try:
            self.tts = IndexTTS(
                model_dir=str(self.model_dir),
                cfg_path=str(config_path)
            )
            logging.info("IndexTTS initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize IndexTTS: {e}")
            raise

    def read_savefile(self, text, output_path,  reference_voice_path=None):
        """
        Generate speech from text using IndexTTS

        Args:
            text: Text to synthesize
            reference_voice_path: Path to reference voice file (optional)

        Returns:
            numpy.ndarray: Audio data
        """
        try:
            # If no reference voice provided, use a default one or raise error
            if reference_voice_path is None:
                reference_voice_path = str(
                    Path(self.model_dir / f"{self.char}.wav"))
                logging.info(
                    f"Using default reference voice: {reference_voice_path}")

            self.tts.infer(
                audio_prompt=reference_voice_path,
                text=text,
                output_path=output_path
            )

        except Exception as e:
            logging.error(f"Error generating speech: {e}")
            raise

    def read_save(self, text, filename, sr=22050, reference_voice_path=None):
        """
        Generate speech from text and save to file

        Args:
            text: Text to synthesize
            filename: Output file path
            sr: Sample rate (default 22050 for IndexTTS)
            reference_voice_path: Path to reference voice file
        """
        stime = time.time()

        try:
            self.read_savefile(text, filename, reference_voice_path)

            logging.info(
                f'IndexTTS Synth Done, time used {time.time() - stime:.2f}s')

        except Exception as e:
            logging.error(f"Error in read_save: {e}")
            raise

    def get_available_voices(self):
        """
        Get list of available reference voices in the model directory

        Returns:
            list: List of voice file paths
        """
        voice_files = []
        for ext in ['*.wav', '*.mp3', '*.flac', '*.m4a']:
            voice_files.extend(self.model_dir.glob(ext))
        return [str(f) for f in voice_files]


def download_index_tts_models(model_dir="TTS/models/index_tts"):
    """
    Download IndexTTS models from HuggingFace

    Args:
        model_dir: Directory to save models
    """
    import subprocess
    import os

    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Downloading IndexTTS models...")

    try:
        # Use huggingface-cli to download models
        cmd = [
            "huggingface-cli", "download", "IndexTeam/IndexTTS-1.5",
            "config.yaml", "bigvgan_discriminator.pth", "bigvgan_generator.pth",
            "bpe.model", "dvae.pth", "gpt.pth", "unigram_12000.vocab",
            "--local-dir", str(model_dir)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logging.info("IndexTTS models downloaded successfully")
        else:
            logging.error(f"Failed to download models: {result.stderr}")
            raise Exception("Model download failed")

    except FileNotFoundError:
        logging.error("huggingface-cli not found. Please install it first:")
        logging.error("pip install huggingface-hub")
        raise
    except Exception as e:
        logging.error(f"Error downloading models: {e}")
        raise


if __name__ == "__main__":
    # Test the service
    try:
        # Initialize service
        tts_service = IndexTTService()

        # Test text
        test_text = "大家好，我现在正在测试 IndexTTS 语音合成系统。"

        # Generate and save audio
        tts_service.read_save(test_text, "test_output.wav")

        print("IndexTTS test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        print("Please make sure IndexTTS models are downloaded and installed correctly.")
