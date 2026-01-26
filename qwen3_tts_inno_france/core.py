import torch
import soundfile as sf
import os
import logging
from typing import List, Dict, Tuple, Union
from qwen_tts import Qwen3TTSModel
import numpy as np
import json
import re
from scipy.signal import resample

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Qwen3TTSInnoFrance:
    def __init__(self, device="cuda:0", dtype=torch.bfloat16, lazy_load=False):
        """
        Initialize Qwen3TTSInnoFrance class
        
        Args:
            device: Device type, default is cuda:0
            dtype: Data type, default is torch.bfloat16
            lazy_load: Whether to load models lazily, default is False
        """
        self.device = device
        self.dtype = dtype
        self.lazy_load = lazy_load or os.environ.get("LAZY_LOAD_MODELS", "false").lower() == "true"
        
        # Model paths and attn_implementation parameter
        self.voice_design_model_path = os.environ.get("VOICE_DESIGN_MODEL_PATH", "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
        self.voice_clone_model_path = os.environ.get("VOICE_CLONE_MODEL_PATH", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
        self.attn_implementation = os.environ.get("ATTN_IMPLEMENTATION", "sdpa")
        
        # Models will be loaded on demand if lazy_load is True
        self.voice_design_model = None
        self.voice_clone_model = None
        
        # Load models immediately if not lazy loading
        if not self.lazy_load:
            self._load_models()
        else:
            logger.info("Lazy loading enabled. Models will be loaded on demand.")
    
    def _load_models(self):
        """Load models if not already loaded"""
        if self.voice_design_model is None:
            logger.info(f"Loading VoiceDesign model from {self.voice_design_model_path}")
            self.voice_design_model = Qwen3TTSModel.from_pretrained(
                self.voice_design_model_path,
                device_map=self.device,
                dtype=self.dtype,
                attn_implementation=self.attn_implementation,
            )
            
        if self.voice_clone_model is None:
            logger.info(f"Loading VoiceClone model from {self.voice_clone_model_path}")
            self.voice_clone_model = Qwen3TTSModel.from_pretrained(
                self.voice_clone_model_path,
                device_map=self.device,
                dtype=self.dtype,
                attn_implementation=self.attn_implementation,
            )
            
        logger.info("Models loaded successfully")

    def voice_design_cli(self, text: str, language: str, instruct: str, output_path: str = "output_voice_design.wav", speed: float = 1.0) -> str:
        """
        Voice design via CLI parameters
        
        Args:
            text: Text to synthesize
            language: Language
            instruct: Voice description instruction
            output_path: Output file path
            speed: Audio playback speed, range 1.0-2.0
            
        Returns:
            Output file path
        """
        # Load models if lazy loading is enabled
        if self.lazy_load:
            self._load_models()
            
        logger.info(f"Starting voice design for text: {text[:50]}...")
        wavs, sr = self.voice_design_model.generate_voice_design(
            text=text,
            language=language,
            instruct=instruct,
        )
        
        # Adjust audio speed
        if speed != 1.0:
            logger.info(f"Adjusting audio speed to {speed}x")
            wavs[0] = self._adjust_audio_speed(wavs[0], speed)
        
        sf.write(output_path, wavs[0], sr)
        logger.info(f"Voice design completed, output file: {output_path}")
        return output_path

    def voice_design_json(self, config_path: str) -> str:
        """
        Voice design via JSON configuration file
        
        Args:
            config_path: JSON configuration file path
            
        Returns:
            Output file path
        """
        logger.info(f"Loading voice design configuration from {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        logger.info(f"Starting voice design for text: {config['text'][:50]}...")
        # Load models if lazy loading is enabled
        if self.lazy_load:
            self._load_models()
            
        wavs, sr = self.voice_design_model.generate_voice_design(
            text=config['text'],
            language=config['language'],
            instruct=config['instruct'],
        )
        
        # Adjust audio speed
        speed = config.get('speed', 1.0)
        if speed != 1.0:
            logger.info(f"Adjusting audio speed to {speed}x")
            wavs[0] = self._adjust_audio_speed(wavs[0], speed)
        
        output_path = config.get('output_path', 'output_voice_design.json.wav')
        sf.write(output_path, wavs[0], sr)
        logger.info(f"Voice design completed, output file: {output_path}")
        return output_path

    def _split_long_text(self, text: str, max_length: int = 300) -> List[str]:
        """
        Split long text into smaller chunks
        
        Args:
            text: Input text
            max_length: Maximum characters per chunk
            
        Returns:
            List of split text chunks
        """
        # If text length is less than or equal to max length, return directly
        if len(text) <= max_length:
            return [text]
            
        # Split text by sentences
        sentences = re.split(r'[.!?。！？]', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding current sentence exceeds max length, save current chunk and start new chunk
            if len(current_chunk) + len(sentence) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + ("." if sentence != sentences[-1] else "")
                
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def _extract_speakers(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract speaker markers and corresponding text from the text
        
        Args:
            text: Text containing speaker markers
            
        Returns:
            (Speaker list, Corresponding text list)
        """
        # Find all speaker markers
        speaker_pattern = r'\[SPEAKER\d+\]'
        speakers = re.findall(speaker_pattern, text)
        
        # If no speakers found, treat entire text as one segment with default speaker
        if not speakers:
            return ["[SPEAKER0]"], [text.strip()]
        
        # Split text
        parts = re.split(speaker_pattern, text)
        
        # Remove first empty element (if exists)
        if parts and parts[0].strip() == "":
            parts = parts[1:]
            
        # Clean text parts
        texts = [part.strip() for part in parts]
        
        logger.info(f"Extracted {len(speakers)} speakers: {set(speakers)}")
        return speakers, texts

    def _adjust_audio_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """
        Adjust audio playback speed with improved quality for higher speeds
        Uses a modified speed curve to prevent excessive pitch changes at high speeds
        
        Args:
            audio: Audio data
            speed: Playback speed, range 1.0-2.0
            
        Returns:
            Speed-adjusted audio data
        """
        if speed < 1.0 or speed > 2.0:
            raise ValueError("Playback speed must be in range 1.0-2.0")
            
        if speed == 1.0:
            return audio
            
        # Apply a gentler speed curve to prevent excessive pitch changes
        # For speeds > 1.0, we apply a logarithmic scaling to reduce the effect
        if speed > 1.0:
            adjusted_speed = 1.0 + (speed - 1.0) * 0.7  # Reduce the speed effect for high values
        else:
            adjusted_speed = speed
            
        # Calculate new length
        new_length = int(len(audio) / adjusted_speed)
        
        # Use resampling to adjust speed
        adjusted_audio = resample(audio, new_length)
        
        logger.info(f"Adjusted audio speed from 1.0x to {speed}x (effective: {adjusted_speed:.2f}x)")
        return adjusted_audio

    def voice_clone_with_speakers(self, text: str, speaker_configs: List[Dict], output_path: str = "output_voice_clone.wav", speed: float = 1.0) -> str:
        """
        Voice cloning for long texts with multiple speakers support
        
        Args:
            text: Text to synthesize, can contain [SPEAKER0] markers
            speaker_configs: Speaker configuration list, each config contains voice information
            output_path: Output file path
            speed: Audio playback speed, range 1.0-2.0
            
        Returns:
            Output file path
        """
        # Extract speaker markers
        speakers, texts = self._extract_speakers(text)
        
        # Validate speaker count match
        if len(speakers) != len(texts):
            raise ValueError(f"Speaker count ({len(speakers)}) does not match text segment count ({len(texts)})")
            
        unique_speakers = list(set(speakers))
        
        # Handle case where no speaker tags are provided in text but we have speaker configs
        if not speakers and len(speaker_configs) > 0:
            # Use first speaker config for the entire text
            unique_speakers = ["[SPEAKER0]"]
        
        # Create speaker mapping with improved logic
        speaker_mapping = {}
        
        # First, try to map by explicit speaker_tag in configs
        for i, speaker_tag in enumerate(unique_speakers):
            # Extract speaker number from tag
            speaker_num = int(re.search(r'\d+', speaker_tag).group()) if re.search(r'\d+', speaker_tag) else None
            
            # Try to find matching config by speaker_tag
            matched = False
            for config_idx, config in enumerate(speaker_configs):
                if 'speaker_tag' in config and config['speaker_tag'] == speaker_tag:
                    speaker_mapping[speaker_tag] = config_idx
                    matched = True
                    break
            
            # If no explicit match, try by speaker number
            if not matched and speaker_num is not None:
                for config_idx, config in enumerate(speaker_configs):
                    if 'speaker_tag' not in config and config_idx == speaker_num:
                        speaker_mapping[speaker_tag] = config_idx
                        matched = True
                        break
            
            # If still no match, use cyclic mapping or default to first config
            if not matched:
                if len(speaker_configs) > 0:
                    speaker_mapping[speaker_tag] = min(i, len(speaker_configs) - 1)
                else:
                    speaker_mapping[speaker_tag] = 0
            
        # Create voice clone prompts for each speaker
        speaker_prompts = {}
        speaker_languages = {}
        for speaker_tag in unique_speakers:
            config_index = speaker_mapping[speaker_tag]
            speaker_config = speaker_configs[config_index]
            speaker_languages[speaker_tag] = speaker_config.get('language', 'English')
            
            # Voice cloning based on existing audio
            if 'ref_audio' in speaker_config:
                # Get ref_text from config or file
                ref_text = speaker_config.get('ref_text', '')
                ref_text_file = speaker_config.get('ref_text_file')
                
                # If ref_text_file is provided, read ref_text from file
                if ref_text_file:
                    try:
                        with open(ref_text_file, 'r', encoding='utf-8') as f:
                            ref_text = f.read().strip()
                    except Exception as e:
                        logger.warning(f"Failed to read ref_text from file {ref_text_file}: {e}. Using empty string.")
                
                prompt = self.voice_clone_model.create_voice_clone_prompt(
                    ref_audio=speaker_config['ref_audio'],
                    ref_text=ref_text,
                    x_vector_only_mode=speaker_config.get('x_vector_only_mode', False),
                )
            # Voice cloning based on voice design
            elif 'design_text' in speaker_config and 'design_instruct' in speaker_config:
                # First generate reference audio through voice design
                ref_wavs, sr = self.voice_design_model.generate_voice_design(
                    text=speaker_config['design_text'],
                    language=speaker_config.get('language', 'English'),
                    instruct=speaker_config['design_instruct'],
                )
                
                # Create clone prompt using designed voice
                prompt = self.voice_clone_model.create_voice_clone_prompt(
                    ref_audio=(ref_wavs[0], sr),
                    ref_text=speaker_config['design_text'],
                )
            else:
                raise ValueError(f"Invalid speaker configuration: {speaker_config}")
                
            speaker_prompts[speaker_tag] = prompt
            
        # Generate audio for each text segment
        audio_segments = []
        for speaker_tag, segment_text in zip(speakers, texts):
            # If speaker_tag is not in speaker_prompts (which can happen when no tags in text), use default
            if speaker_tag not in speaker_prompts:
                if "[SPEAKER0]" in speaker_prompts:
                    speaker_tag = "[SPEAKER0]"
                else:
                    # Use the first available speaker
                    speaker_tag = list(speaker_prompts.keys())[0] if speaker_prompts else None
                    if speaker_tag is None:
                        raise ValueError("No speaker configurations available")
                
            # Load models if lazy loading is enabled
            if self.lazy_load:
                self._load_models()
                
            # Split long text
            text_chunks = self._split_long_text(segment_text)
            
            # Generate audio for each text chunk
            for chunk in text_chunks:
                if chunk.strip():  # Process only non-empty text
                    logger.info(f"Generating audio for speaker {speaker_tag} with text chunk: {chunk}")
                    wavs, sr = self.voice_clone_model.generate_voice_clone(
                        text=chunk,
                        language=speaker_languages[speaker_tag],
                        voice_clone_prompt=speaker_prompts[speaker_tag],
                    )
                    audio_segments.append(wavs[0])
                    
        # Concatenate all audio segments
        if audio_segments:
            final_audio = np.concatenate(audio_segments)
            
            # Adjust audio speed
            if speed != 1.0:
                final_audio = self._adjust_audio_speed(final_audio, speed)
                
            sf.write(output_path, final_audio, sr)
            
        return output_path