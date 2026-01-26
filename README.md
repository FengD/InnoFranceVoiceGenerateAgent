# Qwen3-TTS Inno France

A product-level implementation based on Qwen3-TTS, providing voice design and voice cloning capabilities.

## Features

1. **Voice Design**:
   - Support voice design via CLI parameters
   - Support voice design via JSON configuration files
   - Support generating WAV audio files and text output
   - Support adjusting audio playback speed (1.0-2.0x)

2. **Voice Clone**:
   - Support voice cloning for long texts
   - Support multiple speaker markers ([SPEAKER0], [SPEAKER1], etc.)
   - Support non-sequential speaker tags (e.g., [SPEAKER1], [SPEAKER3])
   - Automatic long text segmentation and audio concatenation
   - Support adjusting audio playback speed (1.0-2.0x)

3. **API Services**:
   - RESTful API for voice design and cloning
   - Web interface for easy interaction
   - Support for file uploads and batch processing

## Installation

```bash
pip install -e .
```

## Usage

### 1. Voice Design

#### CLI Parameters:
```bash
qwen3-tts-inno voice-design-cli --text "Hello, world!" --language "Chinese" --instruct "Young female voice, lively tone" --output output.wav --speed 1.2
```

#### JSON Configuration:
```bash
qwen3-tts-inno voice-design-json --config voice_design_config.json
```

JSON configuration file example:
```json
{
  "text": "Hello, world!",
  "language": "Chinese",
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

Speaker configuration file example (speakers.json):
```json
[
  {
    "speaker_tag": "[SPEAKER0]",
    "ref_audio": "speaker0.wav",
    "ref_text": "Reference audio text content",
    "language": "Chinese"
  },
  {
    "speaker_tag": "[SPEAKER1]",
    "ref_audio": "speaker1.wav",
    "ref_text_file": "speaker1_text.txt",
    "language": "Chinese"
  },
  {
    "speaker_tag": "[SPEAKER2]",
    "design_text": "Reference text for voice design",
    "design_instruct": "Male voice, steady tone",
    "language": "Chinese"
  }
]
```

**Note**: For voice cloning with existing audio, you can provide the reference text in two ways:
1. Directly in the `ref_text` field
2. Through a text file using the `ref_text_file` field (useful for long reference texts)

**Note**: The `speaker_tag` field is optional. If provided, the system will use it for exact matching. If not provided, it will use the configuration index for mapping.

## API Services

### Web API Server

Start the API server:
```bash
python -m qwen3_tts_inno_france.api
```

By default, the API server runs on port 5000. You can change the port by setting the `PORT` environment variable.

### 使用curl调用API服务

#### 1. 健康检查
```bash
curl http://localhost:5000/health
```

#### 2. 声音设计
```bash
curl -X POST http://localhost:5000/voice-design \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界！",
    "language": "Chinese",
    "instruct": "年轻女性声音，语调活泼",
    "output_path": "output.wav",
    "speed": 1.2
  }'
```

#### 3. 声音克隆
```bash
curl -X POST http://localhost:5000/voice-clone \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[SPEAKER0]第一个说话人的内容。[SPEAKER1]第二个说话人的内容。",
    "speaker_configs": [
      {
        "speaker_tag": "[SPEAKER0]",
        "ref_audio": "examples/voice_prompts/zh_old_man.wav",
        "ref_text": "世间万物皆有其规律，年轻人，切勿急躁。静下心来，你会听到花开的声音，也会明白时间的重量。",
        "language": "Chinese"
      },
      {
        "speaker_tag": "[SPEAKER1]",
        "design_text": "我是第二说话人，负责技术细节说明。",
        "design_instruct": "中年男性声音，语调沉稳，专业可信",
        "language": "Chinese"
      }
    ],
    "output_path": "output.wav",
    "speed": 1.1
  }'
```

#### API Endpoints

1. **Health Check**
   ```
   GET /health
   ```
   Returns: `{"status": "healthy", "service": "qwen3-tts-inno-france"}`

2. **Voice Design**
   ```
   POST /voice-design
   ```
   Request body (JSON):
   ```json
   {
     "text": "Hello, world!",
     "language": "Chinese",
     "instruct": "Young female voice, lively tone",
     "output_path": "output.wav",
     "speed": 1.2
   }
   ```

3. **Voice Design via File**
   ```
   POST /voice-design-file
   ```
   Upload a JSON configuration file with the key `config`.

4. **Voice Clone**
   ```
   POST /voice-clone
   ```
   Request body (JSON):
   ```json
   {
     "text": "[SPEAKER0]First speaker content.[SPEAKER1]Second speaker content.",
     "speaker_configs": [
       {
         "speaker_tag": "[SPEAKER0]",
         "ref_audio": "speaker0.wav",
         "ref_text": "Reference text",
         "language": "Chinese"
       },
       {
         "speaker_tag": "[SPEAKER1]",
         "design_text": "Design text",
         "design_instruct": "Male voice",
         "language": "Chinese"
       }
     ],
     "output_path": "output.wav",
     "speed": 1.1
   }
   ```

5. **Voice Clone via Files**
   ```
   POST /voice-clone-files
   ```
   Upload two files:
   - `text_file`: Text file containing speaker markers
   - `speakers_config`: JSON file with speaker configurations

### Web Interface

Start the web application:
```bash
python -m qwen3_tts_inno_france.webapp
```

By default, the web app runs on port 8000. You can change the port by setting the `WEBAPP_PORT` environment variable.

### 下载生成的音频文件

在使用API生成音频文件后，可以通过以下方式下载：
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
# CLI parameters
output_path = tts.voice_design_cli(
    text="Hello, world!",
    language="Chinese",
    instruct="Young female voice, lively tone",
    output_path="output.wav",
    speed=1.2
)

# JSON configuration
output_path = tts.voice_design_json("voice_design_config.json")
```

#### Voice Clone Methods
```python
speaker_configs = [
    {
        "speaker_tag": "[SPEAKER0]",
        "ref_audio": "speaker0.wav",
        "ref_text": "Reference audio text content",
        "language": "Chinese"
    },
    {
        "speaker_tag": "[SPEAKER1]",
        "design_text": "Reference text for voice design",
        "design_instruct": "Male voice, steady tone",
        "language": "Chinese"
    }
]

output_path = tts.voice_clone_with_speakers(
    text="[SPEAKER0]First speaker content.[SPEAKER1]Second speaker content.",
    speaker_configs=speaker_configs,
    output_path="output.wav",
    speed=1.1
)
```

### Speaker Tag Feature

The `speaker_tag` field in speaker configurations is optional but recommended for better speaker matching:

- **With speaker_tag**: Exact matching using the specified tag (e.g., `[SPEAKER1]`)
- **Without speaker_tag**: Index-based matching (first config for `[SPEAKER0]`, second for `[SPEAKER1]`, etc.)

This is particularly useful when dealing with non-sequential speaker tags like `[SPEAKER1]`, `[SPEAKER3]`.

## Environment Variables

- `VOICE_DESIGN_MODEL_PATH`: Voice design model path (default: "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
- `VOICE_CLONE_MODEL_PATH`: Voice clone model path (default: "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
- `ATTN_IMPLEMENTATION`: Attention implementation (default: "sdpa")
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