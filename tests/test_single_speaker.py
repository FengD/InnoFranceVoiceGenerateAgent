#!/usr/bin/env python3
"""
Test script for single speaker scenario without speaker tags
"""

import os
import sys
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qwen3_tts_inno_france.core import Qwen3TTSInnoFrance

def test_single_speaker_without_tags():
    """Test single speaker without speaker tags in text"""
    print("Testing single speaker without speaker tags...")
    
    # Sample text without speaker tags
    text = "这是一个没有说话人标签的测试文本。我们将验证系统是否能正确处理这种情况，并使用第一个说话人配置来生成音频。"
    
    # Speaker config without speaker_tag (like sp4_beginning_speakers.json)
    speaker_configs = [
        {
            "ref_audio": "examples/voice_prompts/zh_young_man.wav",
            "ref_text": "对，这就是我，万人敬仰的太乙真人，虽然有点婴儿肥，但也掩不住我逼人的帅气。",
            "language": "Chinese"
        }
    ]
    
    # Initialize TTS engine
    tts = Qwen3TTSInnoFrance(device="cuda:0")
    
    try:
        # Test voice cloning
        output_path = tts.voice_clone_with_speakers(
            text=text,
            speaker_configs=speaker_configs,
            output_path="test_single_speaker_output.wav",
            speed=1.0
        )
        print(f"Success! Output saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multi_speaker_with_tags():
    """Test multi speaker with speaker tags in text"""
    print("\nTesting multi speaker with speaker tags...")
    
    # Sample text with speaker tags
    text = "[SPEAKER0]这是第一个说话人的内容。[SPEAKER1]这是第二个说话人的内容。"
    
    # Speaker configs with speaker_tag
    speaker_configs = [
        {
            "speaker_tag": "[SPEAKER0]",
            "ref_audio": "examples/voice_prompts/zh_old_man.wav",
            "ref_text": "世间万物皆有其规律，年轻人，切勿急躁。静下心来，你会听到花开的声音，也会明白时间的重量。",
            "language": "Chinese"
        },
        {
            "speaker_tag": "[SPEAKER1]",
            "design_text": "我是第二说话人，负责技术细节说明。",
            "design_instruct": "中年男性声音，语调沉稳，专业可信",
            "language": "Chinese"
        }
    ]
    
    # Initialize TTS engine
    tts = Qwen3TTSInnoFrance(device="cuda:0")
    
    try:
        # Test voice cloning
        output_path = tts.voice_clone_with_speakers(
            text=text,
            speaker_configs=speaker_configs,
            output_path="test_multi_speaker_output.wav",
            speed=1.0
        )
        print(f"Success! Output saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Running speaker tag tests...\n")
    
    success1 = test_single_speaker_without_tags()
    success2 = test_multi_speaker_with_tags()
    
    if success1 and success2:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
        sys.exit(1)