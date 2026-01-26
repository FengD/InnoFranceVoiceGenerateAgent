import soundfile as sf
from qwen_tts import Qwen3TTSTokenizer

tokenizer = Qwen3TTSTokenizer.from_pretrained(
    "/mnt/fd9ef272-d51b-4896-bfc8-9beaa52ae4a5/dingfeng1/Qwen3-TTS-12Hz-1.7B-Base/speech_tokenizer/",
    device_map="cuda:0",
)

enc = tokenizer.encode("https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/tokenizer_demo_1.wav")
wavs, sr = tokenizer.decode(enc)
sf.write("decode_output.wav", wavs[0], sr)
