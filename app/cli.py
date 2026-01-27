import argparse
import json
import sys
import os
import logging
from core import Qwen3TTSInnoFrance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Inno France CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Voice Design CLI subcommand
    voice_design_parser = subparsers.add_parser('voice-design-cli', help='Voice design via CLI parameters')
    voice_design_parser.add_argument('--text', required=True, help='Text to synthesize')
    voice_design_parser.add_argument('--language', required=True, help='Language')
    voice_design_parser.add_argument('--instruct', required=True, help='Voice description instruction')
    voice_design_parser.add_argument('--output', default='output_voice_design.wav', help='Output file path')
    voice_design_parser.add_argument('--speed', type=float, default=1.0, help='Audio playback speed (1.0-2.0)')
    
    # Voice Design JSON subcommand
    voice_design_json_parser = subparsers.add_parser('voice-design-json', help='Voice design via JSON configuration file')
    voice_design_json_parser.add_argument('--config', required=True, help='JSON configuration file path')
    
    # Voice Clone subcommand
    voice_clone_parser = subparsers.add_parser('voice-clone', help='Voice cloning (supports multiple speakers)')
    voice_clone_parser.add_argument('--text-file', required=True, help='Path to text file')
    voice_clone_parser.add_argument('--speakers-config', required=True, help='Speaker configuration JSON file path')
    voice_clone_parser.add_argument('--output', default='output_voice_clone.wav', help='Output file path')
    voice_clone_parser.add_argument('--speed', type=float, default=1.0, help='Audio playback speed (1.0-2.0)')
    
    args = parser.parse_args()
    
    # Disable lazy loading for CLI to ensure models are loaded immediately
    tts = Qwen3TTSInnoFrance(lazy_load=False)
    
    if args.command == 'voice-design-cli':
        output_path = tts.voice_design_cli(
            text=args.text,
            language=args.language,
            instruct=args.instruct,
            output_path=args.output,
            speed=args.speed
        )
        logger.info(f"Voice design completed, output file: {output_path}")
        
    elif args.command == 'voice-design-json':
        output_path = tts.voice_design_json(args.config)
        logger.info(f"Voice design completed, output file: {output_path}")
        
    elif args.command == 'voice-clone':
        # Read text file
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Read speaker configurations
        with open(args.speakers_config, 'r', encoding='utf-8') as f:
            speaker_configs = json.load(f)
            
        output_path = tts.voice_clone_with_speakers(
            text=text,
            speaker_configs=speaker_configs,
            output_path=args.output,
            speed=args.speed
        )
        logger.info(f"Voice cloning completed, output file: {output_path}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()