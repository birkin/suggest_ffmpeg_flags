## inspects a video file with ffprobe, suggests preservation ffmpeg flags
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


def parse_video_stream(streams: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Returns the first video stream from the streams list."""
    for stream in streams:
        if stream.get("codec_type") == "video":
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
    video_stream: Optional[dict[str, Any]] = parse_video_stream(streams)
    if not video_stream:
        print("No video stream found.")
        return

    pix_fmt: str = video_stream.get("pix_fmt", "unknown")
    bits_per_raw_sample: str = video_stream.get("bits_per_raw_sample", "unknown")
    color: str = "YUV" if "yuv" in pix_fmt else "RGB" if "rgb" in pix_fmt else "Unknown"
    chroma: str = infer_chroma_from_pix_fmt(pix_fmt)

    print(f"Input file: {file_path}")
    print(f"  Pixel format (pix_fmt):      {pix_fmt}")
    print(f"  Color model:                {color}")
    print(f"  Bits per channel:           {bits_per_raw_sample}")
    print(f"  Chroma subsampling:         {chroma}")
    print()
    print("Recommended ffmpeg flags:")
    print(f"  -pix_fmt {pix_fmt}")
    # Optionally recommend audio flags if desired, based on additional stream info


if __name__ == "__main__":
    # Example usage: suggest_ffmpeg_flags('/path/to/video.mp4')
    import sys

    if len(sys.argv) != 2:
        print("Usage: python suggest_ffmpeg_flags.py /path/to/file")
    else:
        suggest_ffmpeg_flags(sys.argv[1])
