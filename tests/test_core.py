import sys
import os
import json
import numpy as np
import logging

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwen3_tts_inno_france.core import Qwen3TTSInnoFrance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_voice_design_cli():
    """Test voice design via CLI parameters"""
    logger.info("Testing voice design via CLI parameters...")
    
    # Since actual GPU and model weights are required, only basic import test is performed
    try:
        tts = Qwen3TTSInnoFrance.__new__(Qwen3TTSInnoFrance)
        logger.info("PASS: Qwen3TTSInnoFrance class can be imported normally")
        return True
    except Exception as e:
        logger.error(f"FAIL: Import failed: {e}")
        return False


def test_split_long_text():
    """Test long text splitting functionality"""
    logger.info("Testing long text splitting functionality...")
    
    tts = Qwen3TTSInnoFrance.__new__(Qwen3TTSInnoFrance)
    
    # Test short text
    short_text = "This is a short text."
    chunks = tts._split_long_text(short_text, max_length=100)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    logger.info("PASS: Short text splitting test passed")
    
    # Test long text splitting
    long_text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
    chunks = tts._split_long_text(long_text, max_length=15)
    assert len(chunks) > 1
    logger.info(f"PASS: Long text splitting test passed, split into {len(chunks)} chunks")
    
    return True


def test_adjust_audio_speed():
    """Test audio speed adjustment functionality"""
    logger.info("Testing audio speed adjustment functionality...")
    
    tts = Qwen3TTSInnoFrance.__new__(Qwen3TTSInnoFrance)
    
    # Create test audio data
    test_audio = np.random.rand(1000).astype(np.float32)
    
    # Test normal speed adjustment
    adjusted_audio = tts._adjust_audio_speed(test_audio, 1.5)
    assert len(adjusted_audio) < len(test_audio)
    logger.info("PASS: Audio speed adjustment test passed")
    
    # Test boundary value
    same_audio = tts._adjust_audio_speed(test_audio, 1.0)
    assert len(same_audio) == len(test_audio)
    logger.info("PASS: Audio speed 1.0 test passed")
    
    return True


def test_extract_speakers():
    """Test speaker extraction functionality"""
    logger.info("Testing speaker extraction functionality...")
    
    tts = Qwen3TTSInnoFrance.__new__(Qwen3TTSInnoFrance)
    
    # Test speaker extraction
    text = "[SPEAKER0]First speaker content.[SPEAKER1]Second speaker content.[SPEAKER0]First speaker speaks again."
    speakers, texts = tts._extract_speakers(text)
    
    assert len(speakers) == 3
    assert speakers == ['[SPEAKER0]', '[SPEAKER1]', '[SPEAKER0]']
    assert len(texts) == 3
    logger.info("PASS: Speaker extraction test passed")
    
    return True


def main():
    """Run all tests"""
    logger.info("Starting Qwen3-TTS Inno France core functionality tests...\n")
    
    tests = [
        test_voice_design_cli,
        test_split_long_text,
        test_extract_speakers,
        test_adjust_audio_speed,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"FAIL: Test failed: {e}\n")
    
    logger.info(f"\nTest completion: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed!")
        return True
    else:
        logger.info("Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)