import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# create a reference audio in the target style using the VoiceDesign model
design_model = Qwen3TTSModel.from_pretrained(
    "/mnt/fd9ef272-d51b-4896-bfc8-9beaa52ae4a5/dingfeng1/Qwen3-TTS-12Hz-1.7B-VoiceDesign/",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)

ref_text = "We need artificial intelligence that is as intelligent as humans. For some people, this is frightening, but for others, it is more of a hope, something that brings hope."
ref_instruct = "A mature, calm, scholarly Chinese male voice with French/European academic background tone characteristics"
ref_wavs, sr = design_model.generate_voice_design(
    text=ref_text,
    language="Chinese",
    instruct=ref_instruct
)
sf.write("voice_design_reference.wav", ref_wavs[0], sr)

# build a reusable clone prompt from the voice design reference
clone_model = Qwen3TTSModel.from_pretrained(
    "/mnt/fd9ef272-d51b-4896-bfc8-9beaa52ae4a5/dingfeng1/Qwen3-TTS-12Hz-1.7B-Base/",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)

voice_clone_prompt = clone_model.create_voice_clone_prompt(
    ref_audio=(ref_wavs[0], sr),   # or "voice_design_reference.wav"
    ref_text=ref_text,
)

sentences = [
    "This is a sample English text for voice cloning demonstration purposes. The Joint Embedding Predictive Architecture (JEPA) is a distillation method that works very well and trains quickly without requiring data augmentation beyond masking.",
    "To test the effectiveness of these methods, we train neural networks. One of the first experiments we conducted several years ago was to train neural networks contrastively or non-contrastively."
]

# reuse it for multiple single calls
wavs, sr = clone_model.generate_voice_clone(
    text=sentences[0],
    language="Chinese",
    voice_clone_prompt=voice_clone_prompt,
)
sf.write("clone_single_1.wav", wavs[0], sr)

wavs, sr = clone_model.generate_voice_clone(
    text=sentences[1],
    language="Chinese",
    voice_clone_prompt=voice_clone_prompt,
)
sf.write("clone_single_2.wav", wavs[0], sr)

# # or batch generate in one call
# wavs, sr = clone_model.generate_voice_clone(
#     text=sentences,
#     language=["English", "English"],
#     voice_clone_prompt=voice_clone_prompt,
# )
# for i, w in enumerate(wavs):
#     sf.write(f"clone_batch_{i}.wav", w, sr)
