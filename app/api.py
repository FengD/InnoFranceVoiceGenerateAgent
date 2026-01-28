import io
import json
import logging
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.core import Qwen3TTSInnoFrance
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize TTS engine
tts_engine = None

def init_tts_engine():
    """Initialize TTS engine"""
    global tts_engine
    if tts_engine is None:
        device = os.environ.get("DEVICE", "cuda:0")
        tts_engine = Qwen3TTSInnoFrance(device=device)
        logger.info("TTS engine initialized")


def _to_wav_response(audio_data, sample_rate, filename: str):
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, audio_data, sample_rate, format="WAV")
    wav_buffer.seek(0)
    safe_name = os.path.basename(filename) if filename else "output.wav"
    return send_file(
        wav_buffer,
        mimetype="audio/wav",
        as_attachment=True,
        download_name=safe_name,
    )

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
        data = request.get_json(silent=True) or {}
        
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
        
        # Execute voice design in memory
        audio_data, sample_rate = tts_engine.voice_design_cli_in_memory(
            text=text,
            language=language,
            instruct=instruct,
            speed=speed
        )

        logger.info("Voice design completed, returning audio data")
        return _to_wav_response(audio_data, sample_rate, output_path)
        
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
            
        file_content = file.read().decode('utf-8')
        try:
            config = json.loads(file_content)
        except json.JSONDecodeError:
            logger.warning("Invalid config JSON format")
            return jsonify({"error": "Invalid config JSON format"}), 400

        logger.info("Processing voice design from config file")
        text = config.get("text")
        language = config.get("language")
        instruct = config.get("instruct")
        if not all([text, language, instruct]):
            logger.warning("Missing required parameters in config: text, language, instruct")
            return jsonify({"error": "Missing required parameters: text, language, instruct"}), 400

        audio_data, sample_rate = tts_engine.voice_design_cli_in_memory(
            text=text,
            language=language,
            instruct=instruct,
            speed=config.get("speed", 1.0),
        )

        output_path = config.get("output_path", "output_voice_design.wav")
        logger.info("Voice design file processing completed, returning audio data")
        return _to_wav_response(audio_data, sample_rate, output_path)
        
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
        data = request.get_json(silent=True) or {}
        
        # Required parameters
        text = data.get('text')
        speaker_configs = data.get('speaker_configs')
        
        # Optional parameters
        output_path = data.get('output_path', 'output_voice_clone.wav')
        speed = data.get('speed', 1.0)
        
        if not all([text, speaker_configs]):
            logger.warning("Missing required parameters: text, speaker_configs")
            return jsonify({"error": "Missing required parameters: text, speaker_configs"}), 400
        
        # Parse speaker configs if provided as JSON string
        if isinstance(speaker_configs, str):
            try:
                speaker_configs = json.loads(speaker_configs)
            except json.JSONDecodeError:
                logger.warning("Invalid speaker_configs JSON format")
                return jsonify({"error": "Invalid speaker_configs JSON format"}), 400

        # Execute voice cloning in memory
        audio_data, sample_rate = tts_engine.voice_clone_with_speakers_in_memory(
            text=text,
            speaker_configs=speaker_configs,
            speed=speed
        )

        logger.info("Voice cloning completed, returning audio data")
        return _to_wav_response(audio_data, sample_rate, output_path)
        
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
            
        text = text_file.read().decode('utf-8')
        try:
            speaker_configs = json.loads(speakers_file.read().decode('utf-8'))
        except json.JSONDecodeError:
            logger.warning("Invalid speakers_config JSON format")
            return jsonify({"error": "Invalid speakers_config JSON format"}), 400

        # Optional parameters
        output_path = request.form.get('output_path', 'output_voice_clone.wav')
        speed = float(request.form.get('speed', 1.0))

        logger.info(f"Processing voice cloning with {len(speaker_configs)} speakers")
        audio_data, sample_rate = tts_engine.voice_clone_with_speakers_in_memory(
            text=text,
            speaker_configs=speaker_configs,
            speed=speed
        )

        logger.info("Voice cloning files processing completed, returning audio data")
        return _to_wav_response(audio_data, sample_rate, output_path)
        
    except Exception as e:
        logger.error(f"Voice cloning files error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Qwen3-TTS API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)