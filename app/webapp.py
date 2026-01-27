import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from qwen3_tts_inno_france.api import init_tts_engine, generated_files, voice_design, voice_clone

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
    # Get response from api
    response = voice_design()
    
    # Debug: log response type and content
    logger.info(f"Response type: {type(response)}, content: {response}")
    
    # Check if response is a JSON response with status code
    if isinstance(response, tuple) and len(response) > 1 and isinstance(response[1], int):
        # This is a JSON response with status code
        data, status_code = response
        logger.info(f"Tuple response - data: {data}, status_code: {status_code}")
        if status_code == 200:
            # Convert to the format expected by frontend
            if hasattr(data, 'get_data'):
                json_data = json.loads(data.get_data(as_text=True))
            else:
                json_data = data if isinstance(data, dict) else json.loads(data)
            logger.info(f"Success response data: {json_data}")
            return jsonify({
                "success": True,
                "audio_url": "/" + json_data["filename"],
                "message": json_data["message"]
            })
        else:
            # Error response
            if hasattr(data, 'get_data'):
                json_data = json.loads(data.get_data(as_text=True))
            else:
                json_data = data if isinstance(data, dict) else json.loads(data)
            logger.info(f"Error response data: {json_data}")
            return jsonify({
                "success": False,
                "error": json_data["error"]
            }), status_code
    else:
        # Handle direct response
        logger.info(f"Direct response: {response}")
        # Try to parse as JSON if it's a string
        if isinstance(response, str):
            try:
                json_data = json.loads(response)
                if "filename" in json_data:
                    return jsonify({
                        "success": True,
                        "audio_url": "/" + json_data["filename"],
                        "message": json_data["message"]
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": json_data.get("error", "Unknown error")
                    })
            except json.JSONDecodeError:
                return response
        elif isinstance(response, dict):
            if "filename" in response:
                return jsonify({
                    "success": True,
                    "audio_url": "/" + response["filename"],
                    "message": response["message"]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": response.get("error", "Unknown error")
                })
        else:
            # Return as-is
            return response

@app.route('/voice_clone', methods=['POST'])
def voice_clone_route():
    """Voice clone endpoint"""
    # Get response from api
    response = voice_clone()
    
    # Debug: log response type and content
    logger.info(f"Clone response type: {type(response)}, content: {response}")
    
    # Check if response is a JSON response with status code
    if isinstance(response, tuple) and len(response) > 1 and isinstance(response[1], int):
        # This is a JSON response with status code
        data, status_code = response
        logger.info(f"Clone tuple response - data: {data}, status_code: {status_code}")
        if status_code == 200:
            # Convert to the format expected by frontend
            if hasattr(data, 'get_data'):
                json_data = json.loads(data.get_data(as_text=True))
            else:
                json_data = data if isinstance(data, dict) else json.loads(data)
            logger.info(f"Clone success response data: {json_data}")
            return jsonify({
                "success": True,
                "audio_url": "/" + json_data["filename"],
                "message": json_data["message"]
            })
        else:
            # Error response
            if hasattr(data, 'get_data'):
                json_data = json.loads(data.get_data(as_text=True))
            else:
                json_data = data if isinstance(data, dict) else json.loads(data)
            logger.info(f"Clone error response data: {json_data}")
            return jsonify({
                "success": False,
                "error": json_data["error"]
            }), status_code
    else:
        # Handle direct response
        logger.info(f"Clone direct response: {response}")
        # Try to parse as JSON if it's a string
        if isinstance(response, str):
            try:
                json_data = json.loads(response)
                if "filename" in json_data:
                    return jsonify({
                        "success": True,
                        "audio_url": "/" + json_data["filename"],
                        "message": json_data["message"]
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": json_data.get("error", "Unknown error")
                    })
            except json.JSONDecodeError:
                return response
        elif isinstance(response, dict):
            if "filename" in response:
                return jsonify({
                    "success": True,
                    "audio_url": "/" + response["filename"],
                    "message": response["message"]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": response.get("error", "Unknown error")
                })
        else:
            # Return as-is
            return response

@app.route('/static/<path:filename>')
def static_files(filename):
    """Static file service"""
    logger.info(f"Static file requested: {filename}")
    return send_from_directory(app.static_folder, filename)

@app.route('/<path:filename>')
def serve_generated_file(filename):
    """Serve generated files"""
    logger.info(f"Requested file: {filename}")
    logger.info(f"Available files: {list(generated_files.keys())}")
    if filename in generated_files and os.path.exists(generated_files[filename]):
        logger.info(f"Serving generated file: {generated_files[filename]}")
        return send_file(generated_files[filename])
    else:
        # Fallback to static files
        logger.info(f"Fallback to static file: {filename}")
        return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get("WEBAPP_PORT", 8000))
    logger.info(f"Starting Qwen3-TTS WebApp server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)