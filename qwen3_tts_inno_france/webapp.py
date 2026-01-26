import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from qwen3_tts_inno_france.api import init_tts_engine, generated_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

# Initialize TTS engine
init_tts_engine()

@app.route('/')
def index():
    """Home page"""
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Static file service"""
    logger.info(f"Static file requested: {filename}")
    return send_from_directory(app.static_folder, filename)

@app.route('/<path:filename>')
def serve_generated_file(filename):
    """Serve generated files"""
    if filename in generated_files and os.path.exists(generated_files[filename]):
        return send_file(generated_files[filename])
    else:
        # Fallback to static files
        return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get("WEBAPP_PORT", 8000))
    logger.info(f"Starting Qwen3-TTS WebApp server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)