"""Shared local audio transcription helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.settings import get_settings


class AudioTranscriptionError(RuntimeError):
    """Raised when local audio transcription fails."""


def _resolve_whisper_device(device_setting: str) -> str:
    try:
        import torch
    except ImportError as exc:
        raise AudioTranscriptionError("Torch is required for Whisper") from exc

    if device_setting != "auto":
        return device_setting

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "cpu"
    return "cpu"


@lru_cache
def _load_whisper_model(model_name: str, device: str):
    try:
        import whisper
    except ImportError as exc:
        raise AudioTranscriptionError("Whisper is not installed") from exc

    return whisper.load_model(model_name, device=device)


def _load_audio_samples(audio_path: Path):
    try:
        import whisper
    except ImportError as exc:
        raise AudioTranscriptionError("Whisper is not installed") from exc

    try:
        return whisper.load_audio(str(audio_path))
    except Exception as exc:
        raise AudioTranscriptionError(f"Failed to decode audio: {exc}") from exc


def transcribe_audio(
    audio_path: Path,
    model_name: str,
    *,
    error_cls: type[RuntimeError] = AudioTranscriptionError,
) -> str:
    """Transcribe audio locally using Whisper."""

    if not audio_path.exists():
        raise error_cls("Audio file missing for Whisper")
    if audio_path.stat().st_size == 0:
        raise error_cls("Audio file is empty")

    try:
        audio = _load_audio_samples(audio_path)
        if not hasattr(audio, "__len__") or len(audio) == 0:
            raise error_cls("Audio decode returned no samples")

        settings = get_settings()
        device = _resolve_whisper_device(settings.whisper_device)
        model = _load_whisper_model(model_name, device)
        try:
            result = model.transcribe(
                str(audio_path),
                fp16=device != "cpu",
                language=None,
                task="transcribe",
                verbose=False,
            )
        except RuntimeError as exc:
            message = str(exc).lower()
            if "cannot reshape tensor of 0 elements" in message:
                raise error_cls("Whisper failed on empty audio") from exc
            if ("mps" in message or "sparse" in message or "_sparse_coo_tensor" in message) and (
                device != "cpu"
            ):
                cpu_model = _load_whisper_model(model_name, "cpu")
                result = cpu_model.transcribe(
                    str(audio_path),
                    fp16=False,
                    language=None,
                    task="transcribe",
                    verbose=False,
                )
            else:
                raise error_cls(f"Whisper failed: {exc}") from exc
    except AudioTranscriptionError as exc:
        raise error_cls(str(exc)) from exc

    text = result.get("text", "") if isinstance(result, dict) else ""
    return text.strip()
