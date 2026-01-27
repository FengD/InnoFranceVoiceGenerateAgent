import os
import json
import tempfile
import logging
import threading
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from qwen3_tts_inno_france.core import Qwen3TTSInnoFrance
import soundfile as sf
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Store generated files for download
generated_files = {}

# Store temporary files for cleanup
temporary_files = []

# Lock for thread-safe operations
files_lock = threading.Lock()

# Initialize TTS engine
tts_engine = None

def cleanup_temporary_files():
    """Clean up temporary files periodically"""
    while True:
        time.sleep(300)  # 每5分钟检查一次
        with files_lock:
            cleaned_files = []
            for file_path in temporary_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up temporary file: {file_path}")
                        cleaned_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {str(e)}")
            
            # 从列表中移除已清理的文件
            for file_path in cleaned_files:
                if file_path in temporary_files:
                    temporary_files.remove(file_path)

# 启动后台清理线程
cleanup_thread = threading.Thread(target=cleanup_temporary_files, daemon=True)
cleanup_thread.start()

def init_tts_engine():
    """Initialize TTS engine"""
    global tts_engine
    if tts_engine is None:
        device = os.environ.get("DEVICE", "cuda:0")
        tts_engine = Qwen3TTSInnoFrance(device=device)
        logger.info("TTS engine initialized")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "service": "qwen3-tts-inno-france"})

@app.route('/voice-design', methods=['POST'])
def voice_design():
    """Voice design endpoint"""
    try:
        logger.info("Voice design request received")
        # Initialize TTS engine
        init_tts_engine()
        
        # Get request data
        data = request.get_json()
        
        # Required parameters
        text = data.get('text')
        language = data.get('language')
        instruct = data.get('instruct')
        
        # Optional parameters
        output_path = data.get('output_path', 'output_voice_design.wav')
        speed = data.get('speed', 1.0)
        
        if not all([text, language, instruct]):
            logger.warning("Missing required parameters: text, language, instruct")
            return jsonify({"error": "Missing required parameters: text, language, instruct"}), 400
        
        # Execute voice design
        result_path = tts_engine.voice_design_cli(
            text=text,
            language=language,
            instruct=instruct,
            output_path=output_path,
            speed=speed
        )
        
        logger.info(f"Voice design completed, output path: {result_path}")
        # Store file info for later access
        generated_files[os.path.basename(result_path)] = result_path
        
        # Add to temporary files for cleanup
        with files_lock:
            temporary_files.append(result_path)
        
        # Return audio file as attachment (data stream)
        return send_file(result_path, as_attachment=True, download_name=os.path.basename(result_path))
        
    except Exception as e:
        logger.error(f"Voice design error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/voice-design-file', methods=['POST'])
def voice_design_file():
    """Voice design via file endpoint"""
    try:
        logger.info("Voice design file request received")
        # Initialize TTS engine
        init_tts_engine()
        
        # Check if file is uploaded
        if 'config' not in request.files:
            logger.warning("Missing configuration file")
            return jsonify({"error": "Missing configuration file"}), 400
            
        file = request.files['config']
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({"error": "No file selected"}), 400
            
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            # Read file content
            file_content = file.read().decode('utf-8')
            temp_file.write(file_content)
            temp_file_path = temp_file.name
            
        logger.info(f"Processing voice design from file: {temp_file_path}")
        # Execute voice design
        result_path = tts_engine.voice_design_json(temp_file_path)
        
        # Delete temporary file
        os.unlink(temp_file_path)
        
        logger.info(f"Voice design file processing completed, output path: {result_path}")
        # Store file info for later access
        generated_files[os.path.basename(result_path)] = result_path
        
        # Return result file
        return send_file(result_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Voice design file error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/voice-clone', methods=['POST'])
def voice_clone():
    """Voice cloning endpoint"""
    try:
        logger.info("Voice cloning request received")
        # Initialize TTS engine
        init_tts_engine()
        
        # Get request data
        data = request.get_json()
        
        # Required parameters
        text = data.get('text')
        speaker_configs = data.get('speaker_configs')
        
        # Optional parameters
        output_path = data.get('output_path', 'output_voice_clone.wav')
        speed = data.get('speed', 1.0)
        
        if not all([text, speaker_configs]):
            logger.warning("Missing required parameters: text, speaker_configs")
            return jsonify({"error": "Missing required parameters: text, speaker_configs"}), 400
        
        # Execute voice cloning
        result_path = tts_engine.voice_clone_with_speakers(
            text=text,
            speaker_configs=speaker_configs,
            output_path=output_path,
            speed=speed
        )
        
        logger.info(f"Voice cloning completed, output path: {result_path}")
        # Store file info for later access
        generated_files[os.path.basename(result_path)] = result_path
        
        # Add to temporary files for cleanup
        with files_lock:
            temporary_files.append(result_path)
        
        # Return audio file as attachment (data stream)
        return send_file(result_path, as_attachment=True, download_name=os.path.basename(result_path))
        
    except Exception as e:
        logger.error(f"Voice cloning error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/voice-clone-files', methods=['POST'])
def voice_clone_files():
    """Voice cloning via files endpoint"""
    try:
        logger.info("Voice cloning files request received")
        # Initialize TTS engine
        init_tts_engine()
        
        # Check required files
        if 'text_file' not in request.files or 'speakers_config' not in request.files:
            logger.warning("Missing required files: text_file or speakers_config")
            return jsonify({"error": "Missing required files: text_file or speakers_config"}), 400
            
        text_file = request.files['text_file']
        speakers_file = request.files['speakers_config']
        
        if text_file.filename == '' or speakers_file.filename == '':
            logger.warning("No file selected")
            return jsonify({"error": "No file selected"}), 400
            
        # Save uploaded files to temporary location
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_text_file:
            temp_text_file.write(text_file.read().decode('utf-8'))
            temp_text_file_path = temp_text_file.name
            
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_speakers_file:
            temp_speakers_file.write(speakers_file.read().decode('utf-8'))
            temp_speakers_file_path = temp_speakers_file.name
            
        # Read text content
        with open(temp_text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Read speaker configurations
        with open(temp_speakers_file_path, 'r', encoding='utf-8') as f:
            speaker_configs = json.load(f)
            
        # Optional parameters
        output_path = request.form.get('output_path', 'output_voice_clone.wav')
        speed = float(request.form.get('speed', 1.0))
        
        logger.info(f"Processing voice cloning with {len(speaker_configs)} speakers")
        # Execute voice cloning
        result_path = tts_engine.voice_clone_with_speakers(
            text=text,
            speaker_configs=speaker_configs,
            output_path=output_path,
            speed=speed
        )
        
        # Delete temporary files
        os.unlink(temp_text_file_path)
        os.unlink(temp_speakers_file_path)
        
        logger.info(f"Voice cloning files processing completed, output path: {result_path}")
        # Store file info for later access
        generated_files[os.path.basename(result_path)] = result_path
        
        # Return result file
        return send_file(result_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Voice cloning files error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/<path:filename>')
def serve_generated_file(filename):
    """Serve generated files"""
    if filename in generated_files and os.path.exists(generated_files[filename]):
        return send_file(generated_files[filename])
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Qwen3-TTS API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)