import logging
from flask import Flask, render_template, send_from_directory
from app.api import init_tts_engine, voice_design, voice_clone

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

@app.route('/voice_design', methods=['POST'])
def voice_design_route():
    """Voice design endpoint"""
    return voice_design()

@app.route('/voice_clone', methods=['POST'])
def voice_clone_route():
    """Voice clone endpoint"""
    return voice_clone()

@app.route('/static/<path:filename>')
def static_files(filename):
    """Static file service"""
    logger.info(f"Static file requested: {filename}")
    return send_from_directory(app.static_folder, filename)

@app.route('/<path:filename>')
def serve_generated_file(filename):
    """Serve generated files"""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get("WEBAPP_PORT", 8000))
    logger.info(f"Starting Qwen3-TTS WebApp server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)