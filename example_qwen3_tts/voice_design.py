import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "/mnt/fd9ef272-d51b-4896-bfc8-9beaa52ae4a5/dingfeng1/Qwen3-TTS-12Hz-1.7B-VoiceDesign/",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)

# single inference
wavs, sr = model.generate_voice_design(
    text="Brother, you're back! I've been waiting for you for such a long time, give me a hug!",
    language="Chinese",
    instruct="Express a coquettish and childish girl's voice, with a high pitch and obvious fluctuations, creating an auditory effect of being clingy, artificial, and deliberately cute.",
)
sf.write("output_voice_design.wav", wavs[0], sr)

# batch inference
wavs, sr = model.generate_voice_design(
    text=[
      "Brother, you're back! I've been waiting for you for such a long time, give me a hug!",
      "It's in the top drawer... wait, it's empty? No way, that's impossible! I'm sure I put it there!"
    ],
    language=["Chinese", "English"],
    instruct=[
      "Express a coquettish and childish girl's voice, with a high pitch and obvious fluctuations, creating an auditory effect of being clingy, artificial, and deliberately cute.",
      "Speak in an incredulous tone, but with a hint of panic beginning to creep into your voice."
    ]
)
sf.write("output_voice_design_1.wav", wavs[0], sr)
sf.write("output_voice_design_2.wav", wavs[1], sr)
