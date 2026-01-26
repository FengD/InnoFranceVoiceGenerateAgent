import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "/mnt/fd9ef272-d51b-4896-bfc8-9beaa52ae4a5/dingfeng1/Qwen3-TTS-12Hz-1.7B-CustomVoice/",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)

# single inference
wavs, sr = model.generate_custom_voice(
    text="Actually, I've realized that I'm particularly good at observing others' emotions.",
    language="Chinese", # Pass `Auto` (or omit) for auto language adaptive; if the target language is known, set it explicitly.
    speaker="Vivian",
    instruct="Say with a particularly angry tone", # Omit if not needed.
)
sf.write("output_custom_voice.wav", wavs[0], sr)

# batch inference
wavs, sr = model.generate_custom_voice(
    text=[
        "Actually, I've realized that I'm particularly good at observing others' emotions.",
        "She said she would be here by noon."
    ],
    language=["Chinese", "English"],
    speaker=["Vivian", "Ryan"],
    instruct=["", "Very happy."]
)
sf.write("output_custom_voice_1.wav", wavs[0], sr)
sf.write("output_custom_voice_2.wav", wavs[1], sr)
