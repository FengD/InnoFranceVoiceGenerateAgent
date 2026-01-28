#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qwen3-TTS Inno France Usage Examples
"""

import os
import json
import logging
from app.core import Qwen3TTSInnoFrance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_voice_design():
    """Voice design example"""
    logger.info("=== Voice Design Example ===")
    
    # Initialize TTS engine
    tts = Qwen3TTSInnoFrance(device="cuda:0")
    
    # Example 1: Voice design via CLI parameters
    logger.info("1. Voice design via CLI parameters...")
    output_path = tts.voice_design_cli(
        text="Welcome to the Qwen3-TTS Inno France project, a product-level implementation based on Qwen3-TTS.",
        language="Chinese",
        instruct="Professional announcer voice, clear and bright, moderate speech rate",
        output_path="examples/demo_output_voice_design_cli.wav",
        speed=1.2
    )
    logger.info(f"   Output file: {output_path}")
    
    # Example 2: Voice design via JSON configuration file
    logger.info("2. Voice design via JSON configuration file...")
    
    # Create configuration file
    config = {
        "text": "This is an example of voice design via JSON configuration file.",
        "language": "Chinese",
        "instruct": "Young female voice, lively tone, full of enthusiasm",
        "output_path": "examples/demo_output_voice_design_json.wav",
        "speed": 1.1
    }
    
    config_path = "examples/demo_voice_design_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    output_path = tts.voice_design_json(config_path)
    logger.info(f"   Output file: {output_path}")


def demo_voice_clone():
    """Voice cloning example"""
    logger.info("\n=== Voice Cloning Example ===")
    
    # Initialize TTS engine
    tts = Qwen3TTSInnoFrance(device="cuda:0")
    
    # Example: Multi-speaker voice cloning
    logger.info("1. Multi-speaker voice cloning...")
    
    # Text content
    text = """[SPEAKER0]Welcome to our podcast. Today we will discuss the development trends of AI technology.
[SPEAKER1]Yes, AI technology has developed rapidly in recent years, especially in natural language processing and computer vision.
[SPEAKER0]That's right, and with the emergence of large models, AI application scenarios are becoming more and more extensive.
[SPEAKER1]However, we also need to pay attention to the ethical and social issues brought by AI technology."""

    # Speaker configurations
    speaker_configs = [
        {
            "design_text": "Hello everyone, I'm today's host.",
            "design_instruct": "Young female voice, lively tone, full of enthusiasm",
            "language": "Chinese"
        },
        {
            "design_text": "Good afternoon, dear listeners.",
            "design_instruct": "Middle-aged male voice, steady tone, professional and reliable",
            "language": "Chinese"
        }
    ]
    
    output_path = tts.voice_clone_with_speakers(
        text=text,
        speaker_configs=speaker_configs,
        output_path="examples/demo_output_voice_clone_multi.wav",
        speed=1.1
    )
    logger.info(f"   Output file: {output_path}")


def main():
    """Main function"""
    logger.info("Qwen3-TTS Inno France Usage Examples")
    logger.info("=" * 50)
    
    try:
        # Create output directory
        os.makedirs("examples", exist_ok=True)
        
        # Run voice design example
        demo_voice_design()
        
        # Run voice cloning example
        demo_voice_clone()
        
        logger.info("\nAll examples completed!")
        logger.info("Please check the generated audio files in the examples directory.")
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")


if __name__ == "__main__":
    main()