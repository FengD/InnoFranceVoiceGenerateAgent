#!/usr/bin/env python3
"""
Test script to verify CLI fix
"""

import subprocess
import sys
import os

def test_cli_command():
    """Test CLI command with lazy loading disabled"""
    print("Testing CLI command...")
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Test command
    cmd = [
        "python", "-m", "qwen3_tts_inno_france.cli",
        "voice-clone",
        "--text-file", "examples/test_speaker_text.txt",
        "--speakers-config", "examples/speakers.json",
        "--output", "test_cli_output.wav",
        "--speed", "1.1"
    ]
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
        
        if result.returncode == 0:
            print("CLI command executed successfully!")
            return True
        else:
            print("CLI command failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("CLI command timed out!")
        return False
    except Exception as e:
        print(f"Error running CLI command: {e}")
        return False

if __name__ == "__main__":
    print("Running CLI fix test...\n")
    
    success = test_cli_command()
    
    if success:
        print("\nTest passed!")
    else:
        print("\nTest failed!")
        sys.exit(1)