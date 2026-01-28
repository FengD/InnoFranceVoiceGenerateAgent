import json
import os
from pathlib import Path

import click

from app.core import Qwen3TTSInnoFrance


def _build_tts(device: str, lazy_load: bool) -> Qwen3TTSInnoFrance:
    return Qwen3TTSInnoFrance(device=device, lazy_load=lazy_load)


@click.group()
def main() -> None:
    """Qwen3-TTS Inno France CLI."""


@main.command("voice-design")
@click.option("--text", required=True, help="Text to synthesize")
@click.option("--language", required=True, help="Language")
@click.option("--instruct", required=True, help="Voice description instruction")
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    default=Path("output_voice_design.wav"),
    help="Output WAV file path",
)
@click.option("--speed", type=float, default=1.0, show_default=True, help="Audio speed (1.0-2.0)")
@click.option("--device", default=os.getenv("DEVICE", "cuda:0"), show_default=True, help="Inference device")
@click.option("--lazy-load/--no-lazy-load", default=False, show_default=True, help="Lazy model loading")
def voice_design(text: str, language: str, instruct: str, output_path: Path, speed: float, device: str, lazy_load: bool) -> None:
    """Design a voice from text and instructions."""
    tts = _build_tts(device, lazy_load)
    output = tts.voice_design_cli(
        text=text,
        language=language,
        instruct=instruct,
        output_path=str(output_path),
        speed=speed,
    )
    click.echo(f"Audio saved to {Path(output).resolve()}")


@main.command("voice-design-json")
@click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the voice design JSON configuration file",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional output WAV file path override",
)
@click.option("--device", default=os.getenv("DEVICE", "cuda:0"), show_default=True, help="Inference device")
@click.option("--lazy-load/--no-lazy-load", default=False, show_default=True, help="Lazy model loading")
def voice_design_json(config_path: Path, output_path: Path, device: str, lazy_load: bool) -> None:
    """Design a voice using a JSON configuration file."""
    tts = _build_tts(device, lazy_load)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if output_path:
        config["output_path"] = str(output_path)
    required = ["text", "language", "instruct"]
    if not all(config.get(key) for key in required):
        raise click.ClickException("Config must include text, language, and instruct")

    output = tts.voice_design_cli(
        text=config["text"],
        language=config["language"],
        instruct=config["instruct"],
        output_path=config.get("output_path", "output_voice_design.wav"),
        speed=config.get("speed", 1.0),
    )
    click.echo(f"Audio saved to {Path(output).resolve()}")


@main.command("voice-clone")
@click.option(
    "--text-file",
    "text_file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the input text file",
)
@click.option(
    "--speakers-config",
    "speakers_config",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the speaker configuration JSON file",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    default=Path("output_voice_clone.wav"),
    help="Output WAV file path",
)
@click.option("--speed", type=float, default=1.0, show_default=True, help="Audio speed (1.0-2.0)")
@click.option("--device", default=os.getenv("DEVICE", "cuda:0"), show_default=True, help="Inference device")
@click.option("--lazy-load/--no-lazy-load", default=False, show_default=True, help="Lazy model loading")
def voice_clone(
    text_file: Path,
    speakers_config: Path,
    output_path: Path,
    speed: float,
    device: str,
    lazy_load: bool,
) -> None:
    """Clone voices from text and speaker configuration."""
    tts = _build_tts(device, lazy_load)
    text = text_file.read_text(encoding="utf-8")
    speaker_configs = json.loads(speakers_config.read_text(encoding="utf-8"))
    output = tts.voice_clone_with_speakers(
        text=text,
        speaker_configs=speaker_configs,
        output_path=str(output_path),
        speed=speed,
    )
    click.echo(f"Audio saved to {Path(output).resolve()}")


if __name__ == "__main__":
    main()