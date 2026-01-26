import sys
import os
import json
import time
import subprocess
import requests
import threading
import logging

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qwen3_tts_inno_france.core import Qwen3TTSInnoFrance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_core_functionality():
    """Test core functionality"""
    logger.info("Starting core functionality test...")
    
    try:
        # Since actual GPU and model weights are required, only basic import test is performed
        tts = Qwen3TTSInnoFrance.__new__(Qwen3TTSInnoFrance)
        logger.info("PASS: Qwen3TTSInnoFrance class can be imported normally")
        
        # Test long text splitting
        long_text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."
        chunks = tts._split_long_text(long_text, max_length=15)
        assert len(chunks) > 1
        logger.info(f"PASS: Long text splitting test passed, split into {len(chunks)} chunks")
        
        # Test speaker extraction
        text = "[SPEAKER0]First speaker content.[SPEAKER1]Second speaker content.[SPEAKER0]First speaker speaks again."
        speakers, texts = tts._extract_speakers(text)
        assert len(speakers) == 3
        assert speakers == ['[SPEAKER0]', '[SPEAKER1]', '[SPEAKER0]']
        assert len(texts) == 3
        logger.info("PASS: Speaker extraction test passed")
        
        # Test audio speed adjustment
        import numpy as np
        test_audio = np.random.rand(1000).astype(np.float32)
        adjusted_audio = tts._adjust_audio_speed(test_audio, 1.5)
        assert len(adjusted_audio) < len(test_audio)
        logger.info("PASS: Audio speed adjustment test passed")
        
        return True
    except Exception as e:
        logger.error(f"FAIL: Core functionality test failed: {e}")
        return False


def start_api_server():
    """Start API server"""
    try:
        # Set environment variables
        env = os.environ.copy()
        env['ATTN_IMPLEMENTATION'] = 'sdpa'
        env['DEVICE'] = 'cpu'  # Use CPU for testing
        env['PORT'] = '5001'   # Use different port to avoid conflicts
        
        # Start API server process
        process = subprocess.Popen([
            sys.executable, '-m', 'qwen3_tts_inno_france.api'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        return process
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        return None


def test_api_endpoints():
    """Test API endpoints"""
    logger.info("Starting API endpoint tests...")
    
    api_process = None
    try:
        # Start API server
        api_process = start_api_server()
        if not api_process:
            logger.error("FAIL: Unable to start API server")
            return False
            
        # Wait for server to fully start
        time.sleep(2)
        
        base_url = "http://localhost:5001"
        
        # Test health check endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("PASS: Health check endpoint test passed")
            else:
                logger.error(f"FAIL: Health check endpoint returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"FAIL: Health check endpoint request failed: {e}")
            return False
            
        logger.info("PASS: API endpoint tests passed")
        return True
        
    except Exception as e:
        logger.error(f"FAIL: API endpoint test failed: {e}")
        return False
    finally:
        # Close API server
        if api_process:
            api_process.terminate()
            api_process.wait()


def main():
    """Run all integration tests"""
    logger.info("Starting Qwen3-TTS Inno France integration tests...\n")
    
    tests = [
        ("Core functionality test", test_core_functionality),
        ("API endpoint test", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n=== {test_name} ===")
        try:
            if test_func():
                passed += 1
                logger.info(f"PASS: {test_name} passed")
            else:
                logger.info(f"FAIL: {test_name} failed")
        except Exception as e:
            logger.error(f"FAIL: {test_name} exception: {e}")
    
    logger.info(f"\n=== Test Summary ===")
    logger.info(f"Test completion: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All integration tests passed!")
        return True
    else:
        logger.info("Some integration tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)