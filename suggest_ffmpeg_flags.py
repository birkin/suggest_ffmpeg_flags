## inspects a video file with ffprobe, suggests preservation ffmpeg flags for video and audio
import json
import subprocess
from pathlib import Path
from typing import Any, Optional


def run_ffprobe(file_path: str | Path) -> dict[str, Any]:
    """Runs ffprobe and returns the parsed JSON output."""
    cmd: list[str] = [
        "ffprobe",
        "-show_streams",
        "-v",
        "error",
        "-of",
        "json",
        str(file_path),
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )
    return json.loads(result.stdout)


def parse_stream_by_type(
    streams: list[dict[str, Any]], stream_type: str
) -> Optional[dict[str, Any]]:
    """Returns the first stream of a given type (e.g., "video" or "audio") from the streams list."""
    for stream in streams:
        if stream.get("codec_type") == stream_type:
            return stream
    return None


def infer_chroma_from_pix_fmt(pix_fmt: str) -> str:
    """Infers chroma subsampling from a pix_fmt string."""
    if pix_fmt.startswith("yuv420"):
        return "4:2:0"
    if pix_fmt.startswith("yuv422"):
        return "4:2:2"
    if pix_fmt.startswith("yuv444"):
        return "4:4:4"
    if pix_fmt.startswith("rgb"):
        return "None (RGB)"
    return "Unknown"


def suggest_ffmpeg_flags(file_path: str | Path) -> None:
    """Inspects the video file and prints recommended ffmpeg flags for preservation."""
    info: dict[str, Any] = run_ffprobe(file_path)
    streams: list[dict[str, Any]] = info.get("streams", [])

    video_stream: Optional[dict[str, Any]] = parse_stream_by_type(streams, "video")
    audio_stream: Optional[dict[str, Any]] = parse_stream_by_type(streams, "audio")

    print(f"Input file: {file_path}")

    if video_stream:
        pix_fmt: str = video_stream.get("pix_fmt", "unknown")
        bits_per_raw_sample: str = video_stream.get("bits_per_raw_sample", "unknown")
        color: str = (
            "YUV" if "yuv" in pix_fmt else "RGB" if "rgb" in pix_fmt else "Unknown"
        )
        chroma: str = infer_chroma_from_pix_fmt(pix_fmt)

        print("--- Video Stream ---")
        print(f"  Pixel format (pix_fmt):      {pix_fmt}")
        print(f"  Color model:                {color}")
        print(f"  Bits per channel:           {bits_per_raw_sample}")
        print(f"  Chroma subsampling:         {chroma}")
        print(f"  Recommended ffmpeg flag:    -pix_fmt {pix_fmt}")
    else:
        print("No video stream found.")

    print()

    if audio_stream:
        sample_rate: str = audio_stream.get("sample_rate", "unknown")
        print("--- Audio Stream ---")
        print(f"  Sample rate:                {sample_rate}")
        print(f"  Recommended ffmpeg flag:    -ar {sample_rate}")
    else:
        print("No audio stream found.")


if __name__ == "__main__":
    # Example usage: suggest_ffmpeg_flags('/path/to/video.mp4')
    import sys

    if len(sys.argv) != 2:
        print("Usage: python suggest_ffmpeg_flags.py /path/to/file")
    else:
        suggest_ffmpeg_flags(sys.argv[1])
