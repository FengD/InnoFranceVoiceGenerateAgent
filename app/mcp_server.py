"""
MCP server for Qwen3-TTS Inno France.
"""
import argparse
import base64
import io
import json
import os
from pathlib import Path
from typing import Optional

import soundfile as sf
from mcp.server.fastmcp import FastMCP

from app.core import Qwen3TTSInnoFrance

tts_engine = None


def _get_engine() -> Qwen3TTSInnoFrance:
    global tts_engine
    if tts_engine is None:
        device = os.getenv("DEVICE", "cuda:0")
        tts_engine = Qwen3TTSInnoFrance(device=device)
    return tts_engine


def _encode_wav(audio_data, sample_rate: int) -> str:
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format="WAV")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def _save_wav(audio_data, sample_rate: int, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio_data, sample_rate)
    return str(path)


def create_mcp(host: str, port: int) -> FastMCP:
    mcp = FastMCP("Qwen3-TTS Inno France", json_response=True, host=host, port=port)

    @mcp.tool()
    def design_voice(
        text: str,
        language: str,
        instruct: str,
        speed: float = 1.0,
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Design a voice from text and instruction.

        Returns base64 WAV data and optional output file path.
        """
        try:
            engine = _get_engine()
            audio_data, sample_rate = engine.voice_design_cli_in_memory(
                text=text,
                language=language,
                instruct=instruct,
                speed=speed,
            )
            encoded = _encode_wav(audio_data, sample_rate)
            saved_path = None
            if output_path:
                saved_path = _save_wav(audio_data, sample_rate, output_path)
            return {
                "success": True,
                "audio_base64": encoded,
                "sample_rate": sample_rate,
                "output_path": saved_path,
            }
        except Exception as exc:
            return {"success": False, "error": f"Voice design failed: {str(exc)}"}

    @mcp.tool()
    def design_voice_from_config(
        config_json: str,
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Design a voice from JSON configuration.

        Returns base64 WAV data and optional output file path.
        """
        try:
            config = json.loads(config_json)
            text = config.get("text")
            language = config.get("language")
            instruct = config.get("instruct")
            if not all([text, language, instruct]):
                raise ValueError("Config must include text, language, and instruct")

            engine = _get_engine()
            audio_data, sample_rate = engine.voice_design_cli_in_memory(
                text=text,
                language=language,
                instruct=instruct,
                speed=config.get("speed", 1.0),
            )
            encoded = _encode_wav(audio_data, sample_rate)
            final_output = output_path or config.get("output_path")
            saved_path = None
            if final_output:
                saved_path = _save_wav(audio_data, sample_rate, final_output)
            return {
                "success": True,
                "audio_base64": encoded,
                "sample_rate": sample_rate,
                "output_path": saved_path,
            }
        except Exception as exc:
            return {"success": False, "error": f"Voice design failed: {str(exc)}"}

    @mcp.tool()
    def clone_voice(
        text: str,
        speaker_configs_json: str,
        speed: float = 1.0,
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Clone voices from text and speaker configuration.

        Returns base64 WAV data and optional output file path.
        """
        try:
            speaker_configs = json.loads(speaker_configs_json)
            engine = _get_engine()
            audio_data, sample_rate = engine.voice_clone_with_speakers_in_memory(
                text=text,
                speaker_configs=speaker_configs,
                speed=speed,
            )
            encoded = _encode_wav(audio_data, sample_rate)
            saved_path = None
            if output_path:
                saved_path = _save_wav(audio_data, sample_rate, output_path)
            return {
                "success": True,
                "audio_base64": encoded,
                "sample_rate": sample_rate,
                "output_path": saved_path,
            }
        except Exception as exc:
            return {"success": False, "error": f"Voice clone failed: {str(exc)}"}

    @mcp.tool()
    def clone_voice_from_files(
        text_path: str,
        speaker_configs_path: str,
        speed: float = 1.0,
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Clone voices from text and speaker config files.

        Returns base64 WAV data and optional output file path.
        """
        try:
            text = Path(text_path).read_text(encoding="utf-8")
            speaker_configs = json.loads(Path(speaker_configs_path).read_text(encoding="utf-8"))
            engine = _get_engine()
            audio_data, sample_rate = engine.voice_clone_with_speakers_in_memory(
                text=text,
                speaker_configs=speaker_configs,
                speed=speed,
            )
            encoded = _encode_wav(audio_data, sample_rate)
            saved_path = None
            if output_path:
                saved_path = _save_wav(audio_data, sample_rate, output_path)
            return {
                "success": True,
                "audio_base64": encoded,
                "sample_rate": sample_rate,
                "output_path": saved_path,
            }
        except Exception as exc:
            return {"success": False, "error": f"Voice clone failed: {str(exc)}"}

    return mcp


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Qwen3-TTS Inno France MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport to use (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for SSE transport (default: 8000)",
    )
    return parser.parse_args(argv)


def run_server(transport: str, host: str, port: int) -> None:
    mcp = create_mcp(host=host, port=port)
    if transport == "stdio":
        mcp.run()
        return
    if transport == "sse":
        mcp.run(transport="sse")
        return
    raise ValueError(f"Unsupported transport: {transport}")


def main(argv: Optional[list[str]] = None) -> None:
    args = _parse_args(argv)
    run_server(args.transport, args.host, args.port)


if __name__ == "__main__":
    main()
