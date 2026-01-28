import io
import json
import logging
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core import Qwen3TTSInnoFrance
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Initialize TTS engine
tts_engine = None

def init_tts_engine():
    """Initialize TTS engine"""
    global tts_engine
    if tts_engine is None:
        device = os.environ.get("DEVICE", "cuda:0")
        tts_engine = Qwen3TTSInnoFrance(device=device)
        logger.info("TTS engine initialized")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page"""
    logger.info("Home page accessed")
    return templates.TemplateResponse("index_fastapi.html", {"request": request})

@router.post('/voice-design')
async def voice_design(
    text: str = Form(...),
    language: str = Form(...),
    instruct: str = Form(...),
    speed: float = Form(1.0)
):
    """Voice design endpoint"""
    try:
        logger.info("Voice design request received")
        # Initialize TTS engine
        init_tts_engine()
        
        if not all([text, language, instruct]):
            logger.warning("Missing required parameters: text, language, instruct")
            raise HTTPException(status_code=400, detail="Missing required parameters: text, language, instruct")
        
        # Execute voice design in memory
        audio_data, sample_rate = tts_engine.voice_design_cli_in_memory(
            text=text,
            language=language,
            instruct=instruct,
            speed=speed
        )
        
        logger.info("Voice design completed, returning audio data")
        
        # Convert numpy array to WAV bytes
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
        wav_buffer.seek(0)
        
        # Return audio file directly using StreamingResponse
        return StreamingResponse(
            wav_buffer,
            media_type='audio/wav',
            headers={"Content-Disposition": "attachment; filename=output_voice_design.wav"}
        )
        
    except Exception as e:
        logger.error(f"Voice design error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/voice-design-file')
async def voice_design_file(config: UploadFile = File(...)):
    """Voice design via file endpoint"""
    try:
        logger.info("Voice design file request received")
        # Initialize TTS engine
        init_tts_engine()
        
        if not config:
            logger.warning("Missing configuration file")
            raise HTTPException(status_code=400, detail="Missing configuration file")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            # Read file content
            file_content = await config.read()
            temp_file.write(file_content.decode('utf-8'))
            temp_file_path = temp_file.name
        
        logger.info(f"Processing voice design from file: {temp_file_path}")
        # Execute voice design in memory
        audio_data, sample_rate = tts_engine.voice_design_json_in_memory(temp_file_path)
        
        # Delete temporary file
        os.unlink(temp_file_path)
        
        logger.info("Voice design file processing completed, returning audio data")
        
        # Convert numpy array to WAV bytes
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
        wav_buffer.seek(0)
        
        # Return audio file directly using StreamingResponse
        return StreamingResponse(
            wav_buffer,
            media_type='audio/wav',
            headers={"Content-Disposition": "attachment; filename=output_voice_design.wav"}
        )
        
    except Exception as e:
        logger.error(f"Voice design file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/voice-clone')
async def voice_clone(
    text: str = Form(...),
    speaker_configs: str = Form(...),
    speed: float = Form(1.0)
):
    """Voice cloning endpoint"""
    try:
        logger.info("Voice cloning request received")
        # Initialize TTS engine
        init_tts_engine()
        
        if not all([text, speaker_configs]):
            logger.warning("Missing required parameters: text, speaker_configs")
            raise HTTPException(status_code=400, detail="Missing required parameters: text, speaker_configs")
        
        # Parse speaker configs
        try:
            speaker_configs_parsed = json.loads(speaker_configs)
        except json.JSONDecodeError as e:
            logger.warning("Invalid speaker_configs JSON format")
            raise HTTPException(status_code=400, detail="Invalid speaker_configs JSON format")
        
        # Execute voice cloning in memory
        audio_data, sample_rate = tts_engine.voice_clone_with_speakers_in_memory(
            text=text,
            speaker_configs=speaker_configs_parsed,
            speed=speed
        )
        
        logger.info("Voice cloning completed, returning audio data")
        
        # Convert numpy array to WAV bytes
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
        wav_buffer.seek(0)
        
        # Return audio file directly using StreamingResponse
        return StreamingResponse(
            wav_buffer,
            media_type='audio/wav',
            headers={"Content-Disposition": "attachment; filename=output_voice_clone.wav"}
        )
        
    except Exception as e:
        logger.error(f"Voice cloning error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/voice-clone-files')
async def voice_clone_files(
    text_file: UploadFile = File(...),
    speakers_config: UploadFile = File(...),
    speed: float = Form(1.0)
):
    """Voice cloning via files endpoint"""
    try:
        logger.info("Voice cloning files request received")
        # Initialize TTS engine
        init_tts_engine()
        
        if not text_file or not speakers_config:
            logger.warning("Missing required files: text_file or speakers_config")
            raise HTTPException(status_code=400, detail="Missing required files: text_file or speakers_config")
        
        # Save uploaded files to temporary location
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_text_file:
            text_content = await text_file.read()
            temp_text_file.write(text_content.decode('utf-8'))
            temp_text_file_path = temp_text_file.name
            
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_speakers_file:
            speakers_content = await speakers_config.read()
            temp_speakers_file.write(speakers_content.decode('utf-8'))
            temp_speakers_file_path = temp_speakers_file.name
        
        # Read text content
        with open(temp_text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Read speaker configurations
        with open(temp_speakers_file_path, 'r', encoding='utf-8') as f:
            speaker_configs = json.load(f)
            
        # Delete temporary files
        os.unlink(temp_text_file_path)
        os.unlink(temp_speakers_file_path)
        
        logger.info(f"Processing voice cloning with {len(speaker_configs)} speakers")
        # Execute voice cloning in memory
        audio_data, sample_rate = tts_engine.voice_clone_with_speakers_in_memory(
            text=text,
            speaker_configs=speaker_configs,
            speed=speed
        )
        
        logger.info("Voice cloning files processing completed, returning audio data")
        
        # Convert numpy array to WAV bytes
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_data, sample_rate, format='WAV')
        wav_buffer.seek(0)
        
        # Return audio file directly using StreamingResponse
        return StreamingResponse(
            wav_buffer,
            media_type='audio/wav',
            headers={"Content-Disposition": "attachment; filename=output_voice_clone.wav"}
        )
        
    except Exception as e:
        logger.error(f"Voice cloning files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/health')
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "qwen3-tts-inno-france"}
