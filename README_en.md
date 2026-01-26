# Qwen3-TTS Inno France

A product-level implementation of Qwen3-TTS, providing voice design and voice cloning capabilities.

## Features

1. **Voice Design**:
   - Support voice design via CLI parameters
   - Support voice design via JSON configuration files
   - Support generating WAV audio files and text output
   - Support adjusting audio playback speed (1.0-2.0x)

2. **Voice Clone**:
   - Support voice cloning for long texts
   - Support multiple speaker markers ([SPEAKER0], [SPEAKER1], etc.)
   - Automatic handling of long text segmentation and audio concatenation
   - Support adjusting audio playback speed (1.0-2.0x)

## Installation

```bash
pip install -e .
```

## Usage

### 1. Voice Design

#### Via CLI parameters:
```bash
qwen3-tts-inno voice-design-cli --text "Hello, world!" --language "English" --instruct "Young male voice, british accent" --output output.wav --speed 1.2
```

#### Via JSON configuration:
```bash
qwen3-tts-inno voice-design-json --config voice_design_config.json
```

JSON configuration example:
```json
{
  "text": "Hello, world!",
  "language": "English",
  "instruct": "Young female voice, lively tone",
  "output_path": "output.json.wav",
  "speed": 1.2
}
```

### 2. Voice Clone

```bash
qwen3-tts-inno voice-clone --text-file input.txt --speakers-config speakers.json --output output.wav --speed 1.1
```

Text file example (input.txt):
```
[SPEAKER0]This is the first speaker's content.
[SPEAKER1]This is the second speaker's content.
[SPEAKER0]First speaker speaks again.
```

Speaker configuration example (speakers.json):
```json
[
  {
    "speaker_tag": "[SPEAKER0]",
    "ref_audio": "speaker0.wav",
    "ref_text": "Reference audio text content",
    "language": "English"
  },
  {
    "speaker_tag": "[SPEAKER1]",
    "ref_audio": "speaker1.wav",
    "ref_text_file": "speaker1_text.txt",
    "language": "English"
  },
  {
    "speaker_tag": "[SPEAKER2]",
    "design_text": "Reference text for voice design",
    "design_instruct": "Male voice, steady tone",
    "language": "English"
  }
]
```

**Note**: For voice cloning with existing audio, you can provide the reference text in two ways:
1. Directly in the `ref_text` field
2. Through a text file using the `ref_text_file` field (useful for long reference texts)

## API Documentation

### Starting the API Service

Start the API server:
```bash
python -m qwen3_tts_inno_france.api
```

By default, the API server runs on port 5000. You can change the port by setting the `PORT` environment variable.

### Calling the API with curl

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Voice Design
```bash
curl -X POST http://localhost:5000/voice-design \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "language": "English",
    "instruct": "Young female voice, lively tone",
    "output_path": "output.wav",
    "speed": 1.2
  }'
```

#### 3. Voice Cloning
```bash
curl -X POST http://localhost:5000/voice-clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[SPEAKER0]This is the first speaker content.[SPEAKER1]This is the second speaker content.",
    "speaker_configs": [
      {
        "ref_audio": "examples/voice_prompts/en_woman.wav",
        "ref_text": "Reference audio text content",
        "language": "English"
      },
      {
        "design_text": "Reference text for voice design",
        "design_instruct": "Middle-aged male voice, steady tone",
        "language": "English"
      }
    ],
    "output_path": "output.wav",
    "speed": 1.1
  }'
```

### Downloading Generated Audio Files

After generating audio files with the API, you can download them with:
```bash
curl -O http://localhost:5000/output.wav
```

### Core Class: Qwen3TTSInnoFrance

#### Initialization
```python
from qwen3_tts_inno_france.core import Qwen3TTSInnoFrance

tts = Qwen3TTSInnoFrance(device="cuda:0", dtype=torch.bfloat16)
```

#### Voice Design Methods
```python
# Via CLI parameters
output_path = tts.voice_design_cli(
    text="Hello, world!", 
    language="English", 
    instruct="Young female voice, lively tone", 
    output_path="output.wav",
    speed=1.2
)

# Via JSON configuration
output_path = tts.voice_design_json("voice_design_config.json")
```

#### Voice Clone Methods
```python
speaker_configs = [
    {
        "ref_audio": "speaker0.wav",
        "ref_text": "Reference audio text content",
        "language": "English"
    },
    {
        "design_text": "Reference text for voice design",
        "design_instruct": "Male voice, steady tone",
        "language": "English"
    }
]

output_path = tts.voice_clone_with_speakers(
    text="[SPEAKER0]This is the first speaker's content.[SPEAKER1]This is the second speaker's content.",
    speaker_configs=speaker_configs,
    output_path="output.wav",
    speed=1.1
)
```

## Environment Variables

- `VOICE_DESIGN_MODEL_PATH`: Voice design model path (default: "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
- `VOICE_CLONE_MODEL_PATH`: Voice clone model path (default: "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
- `ATTN_IMPLEMENTATION`: Attention mechanism implementation (default: "sdpa")
- `DEVICE`: Device for model inference (default: "cuda:0")
- `PORT`: API server port (default: 5000)
- `WEBAPP_PORT`: Web application port (default: 8000)
- `LAZY_LOAD_MODELS`: Whether to load models on demand (default: "false"). Set to "true" to enable lazy loading.

## Dependencies

- qwen-tts
- torch>=2.0.0
- soundfile>=0.12.0
- numpy>=1.21.0
- scipy>=1.7.0
- flask>=2.0.0
- flask-cors>=3.0.0

## License

MIT